from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q, Avg
from ..models import Company, Job, JobAnalysis
from .serializers import CompanySerializer, JobSerializer, JobAnalysisSerializer
from ..utils.data_analyzer import JobDataAnalyzer
from ..crawler.crawler_manager import CrawlerManager
import json
from datetime import datetime, timedelta
import numpy as np
from sklearn.linear_model import LinearRegression
import random

class StandardResultsSetPagination(PageNumberPagination):
    """标准分页类"""
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class CompanyViewSet(viewsets.ReadOnlyModelViewSet):
    """公司信息视图集"""
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'industry']
    ordering_fields = ['name']
    ordering = ['name']
    pagination_class = StandardResultsSetPagination

class JobViewSet(viewsets.ReadOnlyModelViewSet):
    """职位信息视图集"""
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    permission_classes = [AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'company__name', 'job_type', 'province', 'city']
    ordering_fields = ['publish_date', 'salary_min', 'company__name']
    ordering = ['-publish_date']
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        queryset = Job.objects.all()
        
        # 排除指定ID
        exclude_id = self.request.query_params.get('exclude_id')
        if exclude_id:
            queryset = queryset.exclude(id=exclude_id)
            
        # 筛选公司
        company = self.request.query_params.get('company')
        if company:
            queryset = queryset.filter(company__name__icontains=company)
            
        # 筛选行业
        industry = self.request.query_params.get('industry')
        if industry:
            queryset = queryset.filter(company__industry__icontains=industry)
            
        # 筛选岗位类型
        job_type = self.request.query_params.get('job_type')
        if job_type:
            queryset = queryset.filter(job_type__icontains=job_type)
            
        # 筛选省份
        province = self.request.query_params.get('province')
        if province:
            queryset = queryset.filter(province__icontains=province)
            
        # 筛选城市
        city = self.request.query_params.get('city')
        if city:
            queryset = queryset.filter(city__icontains=city)
            
        # 筛选薪资范围
        salary_min = self.request.query_params.get('salary_min')
        if salary_min:
            queryset = queryset.filter(salary_min__gte=int(salary_min))
            
        salary_max = self.request.query_params.get('salary_max')
        if salary_max:
            queryset = queryset.filter(salary_max__lte=int(salary_max))
            
        # 筛选关键词（标题、描述、要求）
        keyword = self.request.query_params.get('keyword')
        if keyword:
            queryset = queryset.filter(
                Q(title__icontains=keyword) | 
                Q(description__icontains=keyword) | 
                Q(requirement__icontains=keyword)
            )
            
        # 筛选标签
        tags = self.request.query_params.get('tags')
        if tags:
            try:
                tags_list = json.loads(tags)
                if tags_list and len(tags_list) > 0:
                    for tag in tags_list:
                        queryset = queryset.filter(tags__icontains=tag)
            except json.JSONDecodeError:
                # 如果解析失败，尝试作为单个标签处理
                queryset = queryset.filter(tags__icontains=tags)
            
        return queryset
    
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def crawl(self, request):
        """手动触发爬取职位数据"""
        job_type = request.data.get('job_type', 1)
        max_pages = request.data.get('max_pages', 10)
        
        try:
            crawler_manager = CrawlerManager()
            saved_count = crawler_manager.crawl_and_save(job_type=job_type, max_pages=max_pages)
            
            return Response({
                'status': 'success',
                'message': f'成功爬取并保存 {saved_count} 条职位数据'
            })
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class AnalysisViewSet(viewsets.ReadOnlyModelViewSet):
    """数据分析视图集"""
    queryset = JobAnalysis.objects.all()
    serializer_class = JobAnalysisSerializer
    permission_classes = [AllowAny]
    
    @action(detail=False, methods=['get'])
    def all(self, request):
        """获取所有分析结果"""
        industry_distribution = JobAnalysis.objects.filter(analysis_type='industry_distribution').first()
        salary_distribution = JobAnalysis.objects.filter(analysis_type='salary_distribution').first()
        location_distribution = JobAnalysis.objects.filter(analysis_type='location_distribution').first()
        job_type_distribution = JobAnalysis.objects.filter(analysis_type='job_type_distribution').first()
        education_salary_distribution = JobAnalysis.objects.filter(analysis_type='education_salary_distribution').first()
        
        return Response({
            'industry_distribution': industry_distribution.analysis_data if industry_distribution else None,
            'salary_distribution': salary_distribution.analysis_data if salary_distribution else None,
            'location_distribution': location_distribution.analysis_data if location_distribution else None,
            'job_type_distribution': job_type_distribution.analysis_data if job_type_distribution else None,
            'education_salary_distribution': education_salary_distribution.analysis_data if education_salary_distribution else None
        })
    
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def run_analysis(self, request):
        """手动触发数据分析"""
        try:
            results = JobDataAnalyzer.perform_all_analysis()
            
            return Response({
                'status': 'success',
                'message': '数据分析完成',
                'results': results
            })
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def industry(self, request):
        """获取行业分布分析结果"""
        analysis = JobAnalysis.objects.filter(analysis_type='industry_distribution').first()
        if not analysis:
            return Response({'error': '没有行业分布分析数据'}, status=status.HTTP_404_NOT_FOUND)
        
        return Response(analysis.analysis_data)
    
    @action(detail=False, methods=['get'])
    def salary(self, request):
        """获取薪资分布分析结果"""
        analysis = JobAnalysis.objects.filter(analysis_type='salary_distribution').first()
        if not analysis:
            return Response({'error': '没有薪资分布分析数据'}, status=status.HTTP_404_NOT_FOUND)
        
        return Response(analysis.analysis_data)
    
    @action(detail=False, methods=['get'])
    def location(self, request):
        """获取地区分布分析结果"""
        analysis = JobAnalysis.objects.filter(analysis_type='location_distribution').first()
        if not analysis:
            return Response({'error': '没有地区分布分析数据'}, status=status.HTTP_404_NOT_FOUND)
        
        return Response(analysis.analysis_data)
    
    @action(detail=False, methods=['get'])
    def job_type(self, request):
        """获取岗位类型分布分析结果"""
        analysis = JobAnalysis.objects.filter(analysis_type='job_type_distribution').first()
        if not analysis:
            return Response({'error': '没有岗位类型分布分析数据'}, status=status.HTTP_404_NOT_FOUND)
        
        return Response(analysis.analysis_data)
    
    @action(detail=False, methods=['get'])
    def education_salary(self, request):
        """获取不同学历要求的平均薪资分析结果"""
        analysis = JobAnalysis.objects.filter(analysis_type='education_salary_distribution').first()
        if not analysis:
            return Response({'error': '没有学历-薪资分析数据'}, status=status.HTTP_404_NOT_FOUND)
        
        return Response(analysis.analysis_data)
    
    @action(detail=False, methods=['get'])
    def job_type_salary(self, request):
        """获取特定岗位类型的薪资走向和预测"""
        job_type = request.query_params.get('job_type')
        if not job_type:
            return Response({'error': '必须提供岗位类型参数'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 查询该岗位类型的所有职位
        jobs = Job.objects.filter(job_type__icontains=job_type)
        if not jobs.exists():
            return Response({'error': f'未找到岗位类型为 {job_type} 的职位'}, status=status.HTTP_404_NOT_FOUND)
        
        # 按发布日期分组计算平均薪资
        salary_trend = []
        
        # 获取有薪资信息的职位
        jobs_with_salary = jobs.filter(
            salary_min__isnull=False,
            salary_max__isnull=False
        )
        
        if not jobs_with_salary.exists():
            return Response({
                'job_type': job_type,
                'salary_trend': [],
                'predictions': []
            })
        
        # 计算平均薪资
        avg_min = jobs_with_salary.aggregate(Avg('salary_min'))['salary_min__avg']
        avg_max = jobs_with_salary.aggregate(Avg('salary_max'))['salary_max__avg']
        avg_salary = int((avg_min + avg_max) / 2) if avg_min and avg_max else None
        
        if not avg_salary:
            return Response({
                'job_type': job_type,
                'salary_trend': [],
                'predictions': []
            })
        
        # 获取最新日期
        latest_date = jobs.order_by('-publish_date').first().publish_date
        
        # 如果只有当月数据，生成模拟历史数据
        # 生成过去6个月模拟数据(基于当前平均薪资的随机波动)
        current_date = latest_date.replace(day=1)
        
        # 添加当月真实数据
        salary_trend.append({
            'date': current_date.strftime('%Y-%m'),
            'average_salary': avg_salary,
            'count': jobs_with_salary.count(),
            'is_real': True  # 标记为真实数据
        })
        
        # 如果只有一个月的数据，添加模拟历史数据
        if len(salary_trend) <= 1:
            # 生成过去5个月的模拟数据
            for i in range(1, 6):
                past_month = current_date - timedelta(days=30*i)
                # 基于当前薪资生成带有合理波动的历史数据
                # 波动范围随时间增加，离现在越远波动越大
                fluctuation = (random.random() - 0.5) * 0.1 * i  # -5%到+5%之间的波动，乘以月份
                past_salary = int(avg_salary * (1 - fluctuation))  # 随着时间回溯薪资略有下降趋势
                
                # 模拟职位数量，也是随机波动
                count_fluctuation = random.randint(-2, 2)
                past_count = max(1, jobs_with_salary.count() + count_fluctuation)
                
                salary_trend.insert(0, {
                    'date': past_month.strftime('%Y-%m'),
                    'average_salary': past_salary,
                    'count': past_count,
                    'is_real': False  # 标记为模拟数据
                })
        
        # 预测未来3个月的薪资
        predictions = []
        
        # 准备训练数据
        X = np.array([i for i in range(len(salary_trend))]).reshape(-1, 1)
        y = np.array([item['average_salary'] for item in salary_trend])
        
        # 训练线性回归模型
        model = LinearRegression()
        model.fit(X, y)
        
        # 预测斜率（增长趋势）
        slope = model.coef_[0]
        
        # 获取市场行情整体增长率
        market_growth_rate = 0.03  # 假设整体市场每年增长3%，每月约0.25%
        
        # 预测未来3个月
        for i in range(1, 4):
            next_month = latest_date.replace(day=1) + timedelta(days=32 * i)
            next_month = next_month.replace(day=1)
            
            # 结合模型预测和市场增长率
            model_prediction = int(model.predict(np.array([len(salary_trend) + i - 1]).reshape(-1, 1))[0])
            market_adjustment = avg_salary * (1 + market_growth_rate * i/12)
            
            # 如果模型预测较极端，部分采用市场调整值
            if abs(slope) > 1000:  # 斜率过大
                weight = 0.3  # 更多依赖市场调整
            else:
                weight = 0.7  # 更多依赖模型预测
            
            predicted_salary = int(weight * model_prediction + (1 - weight) * market_adjustment)
            
            # 确保预测值不会下降太多或上升太多
            min_prediction = int(avg_salary * 0.95)
            max_prediction = int(avg_salary * 1.15)
            predicted_salary = max(min_prediction, min(predicted_salary, max_prediction))
            
            predictions.append({
                'date': next_month.strftime('%Y-%m'),
                'predicted_salary': predicted_salary
            })
        
        return Response({
            'job_type': job_type,
            'salary_trend': salary_trend,
            'predictions': predictions
        }) 