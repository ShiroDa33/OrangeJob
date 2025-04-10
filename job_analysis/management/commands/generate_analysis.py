from django.core.management.base import BaseCommand
from job_analysis.models import Job, JobAnalysis
from django.db.models import Count, Avg
from collections import Counter
import json
import re

class Command(BaseCommand):
    help = '生成职位分析数据'

    def handle(self, *args, **options):
        self.stdout.write('开始生成分析数据...')
        
        # 清空现有分析数据
        JobAnalysis.objects.all().delete()
        
        # 1. 行业分布分析
        self.generate_industry_analysis()
        
        # 2. 薪资分布分析
        self.generate_salary_analysis()
        
        # 3. 地区分布分析
        self.generate_location_analysis()
        
        # 4. 岗位类型分析
        self.generate_job_type_analysis()
        
        # 5. 学历-薪资分析
        self.generate_education_salary_analysis()
        
        self.stdout.write(self.style.SUCCESS('分析数据生成完成!'))
    
    def generate_industry_analysis(self):
        # 按行业统计职位数量
        industry_data = Job.objects.values('company__industry').annotate(count=Count('id')).order_by('-count')
        
        # 格式化结果
        categories = []
        data = []
        
        for item in industry_data:
            industry = item['company__industry'] or '其他'
            categories.append(industry)
            data.append(item['count'])
        
        # 创建分析记录
        JobAnalysis.objects.create(
            analysis_type='industry_distribution',
            analysis_data={
                'categories': categories,
                'data': data
            }
        )
        
        self.stdout.write(f'已生成行业分布分析，共{len(categories)}个行业')
    
    def generate_salary_analysis(self):
        # 获取所有有薪资的职位
        jobs_with_salary = Job.objects.exclude(salary_min__isnull=True).exclude(salary_max__isnull=True)
        
        # 定义薪资范围
        salary_ranges = [
            '3k以下', '3k-5k', '5k-7k', '7k-10k', '10k-15k', 
            '15k-20k', '20k-30k', '30k-50k', '50k以上'
        ]
        
        # 初始化计数器
        range_counter = {r: 0 for r in salary_ranges}
        
        # 统计各薪资范围的职位数量
        for job in jobs_with_salary:
            # 使用平均薪资进行范围判断
            avg_salary = (job.salary_min + job.salary_max) / 2
            
            if avg_salary < 3000:
                range_counter['3k以下'] += 1
            elif avg_salary < 5000:
                range_counter['3k-5k'] += 1
            elif avg_salary < 7000:
                range_counter['5k-7k'] += 1
            elif avg_salary < 10000:
                range_counter['7k-10k'] += 1
            elif avg_salary < 15000:
                range_counter['10k-15k'] += 1
            elif avg_salary < 20000:
                range_counter['15k-20k'] += 1
            elif avg_salary < 30000:
                range_counter['20k-30k'] += 1
            elif avg_salary < 50000:
                range_counter['30k-50k'] += 1
            else:
                range_counter['50k以上'] += 1
        
        # 创建分析记录
        JobAnalysis.objects.create(
            analysis_type='salary_distribution',
            analysis_data={
                'categories': salary_ranges,
                'data': [range_counter[r] for r in salary_ranges]
            }
        )
        
        self.stdout.write('已生成薪资分布分析')
    
    def generate_location_analysis(self):
        # 按省份统计职位数量
        province_data = Job.objects.values('province').annotate(count=Count('id')).order_by('-count')
        
        # 格式化省份数据
        province_categories = []
        province_counts = []
        
        for item in province_data:
            if not item['province']:
                continue
            province_categories.append(item['province'])
            province_counts.append(item['count'])
        
        # 按城市统计职位数量并按省份分组
        city_data_by_province = {}
        
        # 获取所有省份
        all_provinces = Job.objects.values_list('province', flat=True).distinct()
        
        for province in all_provinces:
            if not province:
                continue
                
            # 获取该省份的所有城市数据
            cities = Job.objects.filter(province=province).values('city').annotate(count=Count('id')).order_by('-count')
            
            city_categories = []
            city_counts = []
            
            for city in cities:
                if not city['city']:
                    continue
                city_categories.append(city['city'])
                city_counts.append(city['count'])
            
            if city_categories:
                city_data_by_province[province] = {
                    'categories': city_categories,
                    'data': city_counts
                }
        
        # 创建地区分析记录
        JobAnalysis.objects.create(
            analysis_type='location_distribution',
            analysis_data={
                'province': {
                    'categories': province_categories,
                    'data': province_counts
                },
                'city': city_data_by_province
            }
        )
        
        self.stdout.write(f'已生成地区分布分析，包含{len(province_categories)}个省份和{len(city_data_by_province)}个城市分组')
    
    def generate_job_type_analysis(self):
        # 按岗位类型统计职位数量
        job_type_data = Job.objects.values('job_type').annotate(count=Count('id')).order_by('-count')
        
        # 格式化结果
        categories = []
        data = []
        
        for item in job_type_data:
            job_type = item['job_type'] or '其他'
            categories.append(job_type)
            data.append(item['count'])
        
        # 创建分析记录
        JobAnalysis.objects.create(
            analysis_type='job_type_distribution',
            analysis_data={
                'categories': categories,
                'data': data
            }
        )
        
        self.stdout.write(f'已生成岗位类型分析，共{len(categories)}种岗位类型')
        
    def generate_education_salary_analysis(self):
        """分析不同学历要求的平均薪资分布"""
        # 排除没有薪资信息或描述的职位
        jobs_with_salary = Job.objects.filter(
            salary_min__isnull=False,
            salary_max__isnull=False,
            description__isnull=False
        )
        
        # 常见学历类型
        education_keywords = {
            '博士及以上': ['博士及以上', '博士', '博士学历'],
            '硕士及以上': ['硕士及以上', '硕士', '硕士学历', '研究生及以上', '研究生', '研究生学历'],
            '本科及以上': ['本科及以上', '本科', '本科学历', '大学本科'],
            '专科': ['大专及以上', '大专', '专科', '专科及以上'],
            '高中': ['高中及以上', '高中', '中专及以上', '中专', '职高'],
            '初中': ['初中及以上', '初中'],
            '未标明': ['学历不限', '']
        }
        
        # 初始化各学历类型的职位数量和薪资总和
        education_data = {edu: {'count': 0, 'salary_sum': 0} for edu in education_keywords.keys()}
        
        # 遍历职位，判断学历要求并统计薪资
        for job in jobs_with_salary:
            description = job.description.lower() if job.description else ''
            requirement = job.requirement.lower() if job.requirement else ''
            text = description + ' ' + requirement
            
            # 识别职位所属的学历类型
            education_type = '未标明'
            for edu_type, keywords in education_keywords.items():
                for keyword in keywords:
                    if keyword in text:
                        education_type = edu_type
                        break
                if education_type != '未标明':
                    break
            
            # 计算平均薪资
            avg_salary = (job.salary_min + job.salary_max) / 2
            
            # 更新统计数据
            education_data[education_type]['count'] += 1
            education_data[education_type]['salary_sum'] += avg_salary
        
        # 计算各学历类型的平均薪资并整理结果
        result = []
        for edu_type, data in education_data.items():
            if data['count'] > 0:
                avg_salary = data['salary_sum'] / data['count']
                result.append({
                    'education': edu_type,
                    'avg_salary': int(avg_salary),
                    'count': data['count']
                })
        
        # 按平均薪资降序排序
        result.sort(key=lambda x: x['avg_salary'], reverse=True)
        
        # 创建分析记录
        JobAnalysis.objects.create(
            analysis_type='education_salary_distribution',
            analysis_data={
                'categories': [item['education'] for item in result],
                'data': [item['avg_salary'] for item in result],
                'counts': [item['count'] for item in result]
            }
        )
        
        self.stdout.write(f'已生成学历-薪资分析，共{len(result)}种学历类型') 