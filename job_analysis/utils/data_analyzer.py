import logging
from collections import Counter, defaultdict
from django.db.models import Avg, Count, Q, F
from ..models import Job, Company, JobAnalysis

logger = logging.getLogger(__name__)

class JobDataAnalyzer:
    """职位数据分析器"""
    
    @staticmethod
    def analyze_industry_distribution():
        """分析行业分布
        
        Returns:
            dict: 行业分布数据
        """
        # 获取公司行业分布
        industries = Company.objects.values('industry').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # 过滤掉空行业
        industries = [item for item in industries if item['industry']]
        
        # 取前10个主要行业
        top_industries = industries[:10]
        
        # 如果超过10个行业，将其他行业归为"其他"类别
        if len(industries) > 10:
            other_count = sum(item['count'] for item in industries[10:])
            top_industries.append({
                'industry': '其他',
                'count': other_count
            })
            
        return {
            'categories': [item['industry'] for item in top_industries],
            'data': [item['count'] for item in top_industries]
        }
    
    @staticmethod
    def analyze_salary_distribution():
        """分析薪资分布
        
        Returns:
            dict: 薪资分布数据
        """
        # 排除没有薪资信息的职位
        jobs_with_salary = Job.objects.filter(
            salary_min__isnull=False,
            salary_max__isnull=False
        )
        
        # 计算平均薪资并按范围分组
        salary_ranges = [
            {'min': 0, 'max': 5000, 'label': '5K以下'},
            {'min': 5000, 'max': 10000, 'label': '5K-10K'},
            {'min': 10000, 'max': 15000, 'label': '10K-15K'},
            {'min': 15000, 'max': 20000, 'label': '15K-20K'},
            {'min': 20000, 'max': 30000, 'label': '20K-30K'},
            {'min': 30000, 'max': 1000000, 'label': '30K以上'}
        ]
        
        # 统计每个薪资范围的职位数
        salary_distribution = []
        for salary_range in salary_ranges:
            count = jobs_with_salary.filter(
                salary_min__gte=salary_range['min'],
                salary_min__lt=salary_range['max']
            ).count()
            
            salary_distribution.append({
                'range': salary_range['label'],
                'count': count
            })
            
        return {
            'categories': [item['range'] for item in salary_distribution],
            'data': [item['count'] for item in salary_distribution]
        }
    
    @staticmethod
    def analyze_location_distribution():
        """分析地区分布
        
        Returns:
            dict: 地区分布数据
        """
        # 按省份分组
        province_distribution = Job.objects.values('province').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # 过滤掉空省份
        province_distribution = [item for item in province_distribution if item['province']]
        
        # 取前10个主要省份
        top_provinces = province_distribution[:10]
        
        # 如果超过10个省份，将其他省份归为"其他"类别
        if len(province_distribution) > 10:
            other_count = sum(item['count'] for item in province_distribution[10:])
            top_provinces.append({
                'province': '其他',
                'count': other_count
            })
            
        # 获取城市分布（只考虑前10个省份的城市）
        city_distribution = {}
        provinces = [item['province'] for item in top_provinces if item['province'] != '其他']
        
        for province in provinces:
            cities = Job.objects.filter(province=province).values('city').annotate(
                count=Count('id')
            ).order_by('-count')
            
            # 过滤掉空城市
            cities = [item for item in cities if item['city']]
            
            # 取前5个主要城市
            top_cities = cities[:5]
            
            # 如果超过5个城市，将其他城市归为"其他"类别
            if len(cities) > 5:
                other_count = sum(item['count'] for item in cities[5:])
                top_cities.append({
                    'city': '其他',
                    'count': other_count
                })
                
            city_distribution[province] = {
                'categories': [item['city'] for item in top_cities],
                'data': [item['count'] for item in top_cities]
            }
            
        return {
            'province': {
                'categories': [item['province'] for item in top_provinces],
                'data': [item['count'] for item in top_provinces]
            },
            'city': city_distribution
        }
    
    @staticmethod
    def analyze_job_type_distribution():
        """分析岗位类型分布
        
        Returns:
            dict: 岗位类型分布数据
        """
        # 按岗位类型分组
        job_types = Job.objects.values('job_type').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # 过滤掉空岗位类型
        job_types = [item for item in job_types if item['job_type']]
        
        # 取前10个主要岗位类型
        top_job_types = job_types[:10]
        
        # 如果超过10个岗位类型，将其他岗位类型归为"其他"类别
        if len(job_types) > 10:
            other_count = sum(item['count'] for item in job_types[10:])
            top_job_types.append({
                'job_type': '其他',
                'count': other_count
            })
            
        return {
            'categories': [item['job_type'] for item in top_job_types],
            'data': [item['count'] for item in top_job_types]
        }
    
    @staticmethod
    def analyze_education_salary_distribution():
        """分析不同学历要求的平均薪资分布
        
        Returns:
            dict: 学历-薪资分布数据
        """
        # 排除没有薪资信息或描述的职位
        jobs_with_salary = Job.objects.filter(
            salary_min__isnull=False,
            salary_max__isnull=False,
            description__isnull=False
        )
        
        # 定义常见学历关键词和优先级，用于识别和归类
        education_patterns = [
            r'博士及以上', r'博士', r'博士学历', 
            r'硕士及以上', r'硕士', r'硕士学历', 
            r'研究生及以上', r'研究生', r'研究生学历',
            r'本科及以上', r'本科', r'本科学历', r'大学本科',
            r'大专及以上', r'大专', r'专科', r'专科及以上', 
            r'高中及以上', r'高中', r'中专及以上', r'中专', r'职高',
            r'初中及以上', r'初中',
            r'学历不限'
        ]
        
        # 初始化结果存储
        education_salary_data = {}
        
        # 遍历职位，提取学历要求并计算平均薪资
        for job in jobs_with_salary:
            # 计算平均薪资
            avg_salary = (job.salary_min + job.salary_max) / 2
            
            # 从职位描述中提取学历要求
            education_requirement = None
            description = job.description or ""
            
            # 尝试查找各种学历表述
            for pattern in education_patterns:
                if pattern in description:
                    education_requirement = pattern
                    break
            
            # 如果没有找到明确的学历要求，则标记为"未标明"
            if not education_requirement:
                education_requirement = "未标明"
            
            # 更新统计数据
            if education_requirement not in education_salary_data:
                education_salary_data[education_requirement] = {
                    'count': 0, 
                    'total_salary': 0
                }
            
            education_salary_data[education_requirement]['count'] += 1
            education_salary_data[education_requirement]['total_salary'] += avg_salary
        
        # 计算每种学历要求的平均薪资并格式化结果
        result = []
        for edu, data in education_salary_data.items():
            if data['count'] > 0:
                avg_salary = round(data['total_salary'] / data['count'])
                result.append({
                    'education': edu,
                    'avg_salary': avg_salary,
                    'count': data['count']
                })
        
        # 按平均薪资从高到低排序
        result.sort(key=lambda x: x['avg_salary'], reverse=True)
        
        # 如果结果超过10个类别，只保留前10个
        if len(result) > 10:
            result = result[:10]
        
        return {
            'categories': [item['education'] for item in result],
            'data': [item['avg_salary'] for item in result],
            'counts': [item['count'] for item in result]
        }
    
    @classmethod
    def perform_all_analysis(cls):
        """执行所有分析并保存结果
        
        Returns:
            dict: 所有分析结果
        """
        try:
            # 分析行业分布
            industry_distribution = cls.analyze_industry_distribution()
            JobAnalysis.objects.update_or_create(
                analysis_type='industry_distribution',
                defaults={'analysis_data': industry_distribution}
            )
            
            # 分析薪资分布
            salary_distribution = cls.analyze_salary_distribution()
            JobAnalysis.objects.update_or_create(
                analysis_type='salary_distribution',
                defaults={'analysis_data': salary_distribution}
            )
            
            # 分析地区分布
            location_distribution = cls.analyze_location_distribution()
            JobAnalysis.objects.update_or_create(
                analysis_type='location_distribution',
                defaults={'analysis_data': location_distribution}
            )
            
            # 分析岗位类型分布
            job_type_distribution = cls.analyze_job_type_distribution()
            JobAnalysis.objects.update_or_create(
                analysis_type='job_type_distribution',
                defaults={'analysis_data': job_type_distribution}
            )
            
            # 分析不同学历要求的平均薪资分布
            education_salary_distribution = cls.analyze_education_salary_distribution()
            JobAnalysis.objects.update_or_create(
                analysis_type='education_salary_distribution',
                defaults={'analysis_data': education_salary_distribution}
            )
            
            logger.info("所有数据分析完成并保存")
            
            return {
                'industry_distribution': industry_distribution,
                'salary_distribution': salary_distribution,
                'location_distribution': location_distribution,
                'job_type_distribution': job_type_distribution,
                'education_salary_distribution': education_salary_distribution
            }
        except Exception as e:
            logger.error(f"执行数据分析时出错: {e}")
            raise 