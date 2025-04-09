import logging
from django.core.management.base import BaseCommand
from job_analysis.utils.data_analyzer import JobDataAnalyzer

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = '分析数据库中的职位信息并生成统计结果'
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("开始分析职位数据..."))
        
        try:
            results = JobDataAnalyzer.perform_all_analysis()
            
            # 输出分析结果概要
            self.stdout.write(self.style.SUCCESS("分析完成！"))
            self.stdout.write("行业分布分析：")
            for i, industry in enumerate(results['industry_distribution']['categories'][:5]):
                count = results['industry_distribution']['data'][i]
                self.stdout.write(f"  - {industry}: {count}家公司")
                
            self.stdout.write("薪资分布分析：")
            for i, salary_range in enumerate(results['salary_distribution']['categories']):
                count = results['salary_distribution']['data'][i]
                self.stdout.write(f"  - {salary_range}: {count}个职位")
                
            self.stdout.write("地区分布分析：")
            for i, province in enumerate(results['location_distribution']['province']['categories'][:5]):
                count = results['location_distribution']['province']['data'][i]
                self.stdout.write(f"  - {province}: {count}个职位")
                
            self.stdout.write("职位类型分析：")
            for i, job_type in enumerate(results['job_type_distribution']['categories'][:5]):
                count = results['job_type_distribution']['data'][i]
                self.stdout.write(f"  - {job_type}: {count}个职位")
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"分析过程中出错: {e}")) 