from django.core.management.base import BaseCommand
from job_analysis.models import Job

class Command(BaseCommand):
    help = '删除所有职位数据'

    def handle(self, *args, **options):
        # 获取当前职位数量
        job_count = Job.objects.count()
        self.stdout.write(f'当前数据库中有 {job_count} 个职位')
        
        # 删除所有职位
        Job.objects.all().delete()
        
        # 确认删除成功
        new_count = Job.objects.count()
        self.stdout.write(self.style.SUCCESS(f'成功删除所有职位数据，当前数据库中有 {new_count} 个职位'))
        self.stdout.write(self.style.SUCCESS('请使用 load_test_data 或其他爬虫命令重新添加职位数据')) 