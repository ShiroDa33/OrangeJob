import logging
from django.db import transaction
from datetime import datetime
import concurrent.futures
from .job_crawler import JobCrawler
from ..models import Company, Job

logger = logging.getLogger(__name__)

class CrawlerManager:
    """爬虫管理器，负责爬取数据并存储到数据库"""
    
    def __init__(self, max_workers=5):
        self.crawler = JobCrawler(max_workers=max_workers)
        self.max_workers = max_workers
        
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
    
    def process_and_save_job(self, raw_job):
        """处理并保存单个职位信息，用于并发处理
        
        Args:
            raw_job: 原始职位数据
            
        Returns:
            bool: 是否成功保存
        """
        try:
            job_info = self.crawler.extract_job_info(raw_job)
            self.save_job_to_db(job_info)
            return True
        except Exception as e:
            logger.error(f"保存职位数据失败: {e}")
            return False
    
    def crawl_and_save(self, job_type=1, max_pages=10, max_workers=None):
        """并发爬取职位数据并保存到数据库
        
        Args:
            job_type: 职位类型 (1=全职, 2=实习, 3=兼职)
            max_pages: 最大爬取页数
            max_workers: 最大工作线程数，None表示使用默认值
            
        Returns:
            int: 成功保存的职位数量
        """
        if max_workers is None:
            max_workers = self.max_workers
            
        logger.info(f"开始爬取职位数据，类型: {job_type}，最大页数: {max_pages}，并发线程数: {max_workers}")
        
        # 并发爬取数据
        raw_jobs = self.crawler.fetch_all_jobs(job_type=job_type, max_pages=max_pages, max_workers=max_workers)
        logger.info(f"爬取完成，共获取 {len(raw_jobs)} 条职位数据")
        
        if not raw_jobs:
            logger.warning("没有获取到职位数据")
            return 0
            
        # 并发处理和保存数据
        saved_count = 0
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 提交所有职位的处理任务
            future_to_job = {
                executor.submit(self.process_and_save_job, raw_job): i 
                for i, raw_job in enumerate(raw_jobs)
            }
            
            # 处理完成的任务
            for future in concurrent.futures.as_completed(future_to_job):
                job_index = future_to_job[future]
                try:
                    if future.result():
                        saved_count += 1
                        if saved_count % 10 == 0:  # 每保存10个职位打印一次日志
                            logger.info(f"已保存 {saved_count}/{len(raw_jobs)} 条职位数据")
                except Exception as e:
                    logger.error(f"处理第 {job_index+1} 个职位时出错: {e}")
        
        logger.info(f"数据保存完成，成功保存 {saved_count}/{len(raw_jobs)} 条职位数据")
        return saved_count 