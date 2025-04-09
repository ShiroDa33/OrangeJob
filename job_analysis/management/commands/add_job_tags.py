from django.core.management.base import BaseCommand
from job_analysis.models import Job
import random

class Command(BaseCommand):
    help = '为现有职位添加福利标签'

    def handle(self, *args, **options):
        # 获取所有职位
        jobs = Job.objects.all()
        self.stdout.write(f'找到 {jobs.count()} 个职位需要添加标签')
        
        # 可能的福利标签列表
        benefits = [
            '五险一金', '年终奖', '带薪年假', '节日福利', '免费班车', 
            '定期体检', '员工旅游', '餐补', '房补', '通讯补贴',
            '弹性工作', '股票期权', '交通补贴', '高温补贴', '全勤奖',
            '加班补助', '团队建设', '免费培训', '晋升空间', '免费零食'
        ]
        
        # 为每个职位随机添加2-5个福利标签
        updated_count = 0
        for job in jobs:
            # 随机选择2-5个福利标签
            tag_count = random.randint(2, 5)
            job_benefits = random.sample(benefits, tag_count)
            
            # 更新职位的tags字段
            job.tags = job_benefits
            job.save()
            updated_count += 1
            
            if updated_count % 50 == 0:
                self.stdout.write(f'已处理 {updated_count} 个职位')
        
        self.stdout.write(self.style.SUCCESS(f'成功为 {updated_count} 个职位添加了福利标签！')) 