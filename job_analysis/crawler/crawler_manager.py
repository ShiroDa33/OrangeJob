import logging
from django.db import transaction
from datetime import datetime
from .job_crawler import JobCrawler
from ..models import Company, Job

logger = logging.getLogger(__name__)

class CrawlerManager:
    """爬虫管理器，负责爬取数据并存储到数据库"""
    
    def __init__(self):
        self.crawler = JobCrawler()
        
    @transaction.atomic
    def save_job_to_db(self, job_info):
        """保存单个职位信息到数据库
        
        Args:
            job_info: 职位信息字典
            
        Returns:
            Job: 保存的职位对象
        """
        # 获取或创建公司
        company, _ = Company.objects.get_or_create(
            name=job_info['company_name'],
            defaults={
                'industry': job_info['industry']
            }
        )
        
        # 创建或更新职位
        job, created = Job.objects.update_or_create(
            title=job_info['title'],
            company=company,
            source_url=job_info['source_url'],
            defaults={
                'job_type': job_info['job_type'],
                'salary_min': job_info['salary_min'],
                'salary_max': job_info['salary_max'],
                'province': job_info['province'],
                'city': job_info['city'],
                'description': job_info['description'],
                'requirement': job_info['requirement'],
                'publish_date': job_info['publish_date']
            }
        )
        
        if created:
            logger.info(f"创建新职位: {job}")
        else:
            logger.info(f"更新职位: {job}")
            
        return job
    
    def crawl_and_save(self, job_type=1, max_pages=10):
        """爬取职位数据并保存到数据库
        
        Args:
            job_type: 职位类型 (1=全职, 2=实习, 3=兼职)
            max_pages: 最大爬取页数
            
        Returns:
            int: 成功保存的职位数量
        """
        logger.info(f"开始爬取职位数据，类型: {job_type}，最大页数: {max_pages}")
        
        # 爬取数据
        raw_jobs = self.crawler.fetch_all_jobs(job_type=job_type, max_pages=max_pages)
        logger.info(f"爬取完成，共获取 {len(raw_jobs)} 条职位数据")
        
        # 处理并保存数据
        saved_count = 0
        for raw_job in raw_jobs:
            try:
                job_info = self.crawler.extract_job_info(raw_job)
                self.save_job_to_db(job_info)
                saved_count += 1
            except Exception as e:
                logger.error(f"保存职位数据失败: {e}")
                
        logger.info(f"数据保存完成，成功保存 {saved_count} 条职位数据")
        return saved_count 