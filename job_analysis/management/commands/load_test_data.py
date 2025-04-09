from django.core.management.base import BaseCommand
from job_analysis.models import Company, Job
from datetime import date, timedelta
import random

class Command(BaseCommand):
    help = '向数据库中添加测试数据'

    def handle(self, *args, **options):
        # 清空现有数据
        self.stdout.write('清空现有数据...')
        Job.objects.all().delete()
        Company.objects.all().delete()
        
        # 行业列表
        industries = [
            '互联网/IT/软件', '金融/银行/保险', '教育/培训', 
            '医疗/健康', '制造业', '房地产/建筑', '消费品/零售', 
            '文化/传媒/娱乐', '物流/运输'
        ]
        
        # 职位类型
        job_types = [
            '后端开发', '前端开发', '移动开发', '测试', '运维', 
            '设计', '产品经理', '项目经理', '数据分析', '人力资源',
            '市场营销', '销售', '财务', '客服', '行政'
        ]
        
        # 省份和城市
        locations = {
            '北京': ['海淀区', '朝阳区', '东城区', '西城区', '丰台区'],
            '上海': ['浦东新区', '徐汇区', '静安区', '黄浦区', '长宁区'],
            '广东': ['深圳', '广州', '佛山', '珠海', '东莞'],
            '江苏': ['南京', '苏州', '无锡', '常州', '南通'],
            '浙江': ['杭州', '宁波', '温州', '绍兴', '嘉兴'],
            '四川': ['成都', '绵阳', '德阳', '自贡', '宜宾'],
        }
        
        # 创建公司
        self.stdout.write('创建公司数据...')
        companies = []
        company_names = [
            '橙子科技有限公司', '蓝天网络科技', '绿叶软件开发', '红日信息技术', 
            '紫光教育集团', '金辉金融服务', '银河通信技术', '星辰医疗集团',
            '云端数据科技', '山海文化传媒', '未来智能科技', '轻舟物流有限公司'
        ]
        
        for name in company_names:
            company = Company.objects.create(
                name=name,
                industry=random.choice(industries)
            )
            companies.append(company)
            self.stdout.write(f'创建公司: {company.name}')
        
        # 创建职位
        self.stdout.write('创建职位数据...')
        
        for i in range(50):  # 创建50个职位
            company = random.choice(companies)
            job_type = random.choice(job_types)
            province = random.choice(list(locations.keys()))
            city = random.choice(locations[province])
            
            # 随机薪资范围
            if random.random() < 0.8:  # 80%的职位有薪资范围
                base_salary = random.randint(5, 25) * 1000
                salary_min = base_salary
                salary_max = base_salary + random.randint(5, 15) * 1000
            else:
                salary_min = None
                salary_max = None
            
            # 随机发布日期（过去3个月内）
            days_ago = random.randint(0, 90)
            publish_date = date.today() - timedelta(days=days_ago)
            
            # 创建职位
            job = Job.objects.create(
                title=f"{job_type}工程师" if "开发" in job_type else job_type,
                company=company,
                job_type=job_type,
                salary_min=salary_min,
                salary_max=salary_max,
                province=province,
                city=city,
                description=f"这是一个{job_type}职位的描述。我们正在寻找有经验的{job_type}人才加入我们的团队。",
                requirement=f"【岗位要求】\n1. 相关专业本科及以上学历\n2. 具有2年以上{job_type}相关经验\n3. 良好的沟通能力和团队协作精神",
                publish_date=publish_date,
                source_url=f"https://example.com/jobs/{i+1}"
            )
            
            self.stdout.write(f'创建职位: {job.title} - {job.company.name}')
        
        self.stdout.write(self.style.SUCCESS('数据导入完成!')) 