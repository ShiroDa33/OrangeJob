import logging
from django.core.management.base import BaseCommand
from job_analysis.crawler.crawler_manager import CrawlerManager

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = '爬取招聘网站的职位信息并保存到数据库'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--type',
            type=int,
            default=1,
            help='职位类型 (1=全职, 2=实习, 3=兼职)'
        )
        parser.add_argument(
            '--pages',
            type=int,
            default=10,
            help='最大爬取页数'
        )
        parser.add_argument(
            '--workers',
            type=int,
            default=5,
            help='并发线程数'
        )
        
    def handle(self, *args, **options):
        job_type = options['type']
        max_pages = options['pages']
        max_workers = options['workers']
        
        self.stdout.write(self.style.SUCCESS(
            f"开始爬取职位信息，类型: {job_type}，最大页数: {max_pages}，并发线程数: {max_workers}"
        ))
        
        crawler_manager = CrawlerManager(max_workers=max_workers)
        saved_count = crawler_manager.crawl_and_save(
            job_type=job_type, 
            max_pages=max_pages,
            max_workers=max_workers
        )
        
        self.stdout.write(self.style.SUCCESS(f"爬取完成，成功保存 {saved_count} 条职位信息")) 