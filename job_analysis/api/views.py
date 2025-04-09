from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q
from ..models import Company, Job, JobAnalysis
from .serializers import CompanySerializer, JobSerializer, JobAnalysisSerializer
from ..utils.data_analyzer import JobDataAnalyzer
from ..crawler.crawler_manager import CrawlerManager
import json

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
        
        return Response({
            'industry_distribution': industry_distribution.analysis_data if industry_distribution else None,
            'salary_distribution': salary_distribution.analysis_data if salary_distribution else None,
            'location_distribution': location_distribution.analysis_data if location_distribution else None,
            'job_type_distribution': job_type_distribution.analysis_data if job_type_distribution else None
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