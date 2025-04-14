import requests
import json
from datetime import datetime
import time
import logging
import concurrent.futures

logger = logging.getLogger(__name__)

class JobCrawler:
    """职位信息爬虫"""
    
    def __init__(self, max_workers=5):
        self.base_url = 'https://a.jiuyeb.cn/mobile.php/job/getlist'
        self.headers = {
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'auth': 'Baisc MTAyNDY6MTAyNDY=',
            'cache-control': 'no-cache',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'origin': 'https://jy.cdu.edu.cn',
            'pragma': 'no-cache',
            'priority': 'u=1, i',
            'referer': 'https://jy.cdu.edu.cn/',
            'sec-ch-ua': '"Microsoft Edge";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'cross-site',
            'token': '',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36 Edg/135.0.0.0'
        }
        self.max_workers = max_workers
        
    def fetch_jobs(self, page=1, size=20, job_type=1):
        """获取职位列表
        
        Args:
            page: 页码
            size: 每页数量
            job_type: 职位类型 (1=全职, 2=实习, 3=兼职)
            
        Returns:
            dict: 包含职位列表的响应数据
        """
        data = {
            'jobtype': job_type,
            'isunion': 2,
            'school_id': '92727a49-c69a-6814-7231-a90bbbe287a7',
            'page': page,
            'size': size,
            'province_id': 0,
            'city_id': 0,
            'dalei_id': 0,
            'cate_id1': 0,
            'salary_floor': '',
            'salay_ceil': '',
            'day': 0,
            'login_user_id': 1,
            'login_admin_school_code': '11079',
            'login_admin_school_id': '92727a49-c69a-6814-7231-a90bbbe287a7'
        }
        
        try:
            response = requests.post(self.base_url, headers=self.headers, data=data)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"获取职位列表失败: {e}")
            return {"data": {"list": []}, "code": -1, "message": str(e)}
    
    def fetch_page(self, page, job_type):
        """爬取单页数据，用于并发爬取
        
        Args:
            page: 页码
            job_type: 职位类型
            
        Returns:
            list: 该页的职位列表
        """
        logger.info(f"正在爬取第 {page} 页数据...")
        result = self.fetch_jobs(page=page, job_type=job_type)
        
        if result.get('code') != 200:
            logger.error(f"获取第 {page} 页数据失败: {result.get('message')}")
            return []
            
        jobs = result.get('data', {}).get('list', [])
        if not jobs:
            logger.warning(f"第 {page} 页没有数据")
            
        # 短暂延迟避免请求过快
        time.sleep(0.5)
        return jobs
            
    def fetch_all_jobs(self, job_type=1, max_pages=10, max_workers=None):
        """并发获取所有职位信息
        
        Args:
            job_type: 职位类型
            max_pages: 最大爬取页数，防止无限爬取
            max_workers: 最大线程数，默认使用初始化时设置的值
            
        Returns:
            list: 职位信息列表
        """
        all_jobs = []
        
        # 先获取第一页，以确定总页数
        logger.info("正在获取第1页数据以确定总页数...")
        result = self.fetch_jobs(page=1, job_type=job_type)
        
        if result.get('code') != 200:
            logger.error(f"获取数据失败: {result.get('message')}")
            return all_jobs
        
        # 提取第一页的职位信息
        jobs = result.get('data', {}).get('list', [])
        if jobs:
            all_jobs.extend(jobs)
        else:
            logger.warning("第一页没有数据，终止爬取")
            return all_jobs
        
        # 计算总页数
        total_count = result.get('data', {}).get('total_count', 0)
        total_pages = min((total_count + 19) // 20, max_pages)  # 向上取整，且不超过max_pages
        logger.info(f"总共有 {total_count} 条数据，{total_pages} 页")
        
        # 如果只有一页数据，直接返回
        if total_pages <= 1:
            return all_jobs
        
        # 设置并发线程数
        if max_workers is None:
            max_workers = self.max_workers
        
        # 使用线程池并发爬取剩余页面（从第2页开始）
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 提交所有页面的爬取任务
            future_to_page = {
                executor.submit(self.fetch_page, page, job_type): page 
                for page in range(2, total_pages + 1)
            }
            
            # 处理完成的任务
            for future in concurrent.futures.as_completed(future_to_page):
                page = future_to_page[future]
                try:
                    page_jobs = future.result()
                    all_jobs.extend(page_jobs)
                    logger.info(f"第 {page} 页爬取成功，获取 {len(page_jobs)} 条数据")
                except Exception as e:
                    logger.error(f"处理第 {page} 页时出错: {e}")
        
        logger.info(f"并发爬取完成，共获取 {len(all_jobs)} 条职位数据")
        return all_jobs
    
    def parse_salary(self, salary_text):
        """解析薪资范围
        
        Args:
            salary_text: 薪资文本，如"8K-12K"、"面议"等
            
        Returns:
            tuple: (最低薪资, 最高薪资)，单位为元/月
        """
        if not salary_text or salary_text == '面议':
            return None, None
            
        try:
            # 处理 "8K-12K" 格式
            if 'K' in salary_text or 'k' in salary_text:
                salary_text = salary_text.upper().replace('K', '')
                if '-' in salary_text:
                    min_salary, max_salary = salary_text.split('-')
                    return int(float(min_salary) * 1000), int(float(max_salary) * 1000)
                else:
                    salary = int(float(salary_text) * 1000)
                    return salary, salary
                    
            # 处理 "8000-12000" 格式
            elif '-' in salary_text:
                min_salary, max_salary = salary_text.split('-')
                return int(float(min_salary)), int(float(max_salary))
            
            # 处理单个数字
            else:
                salary = int(float(salary_text))
                return salary, salary
        except Exception as e:
            logger.warning(f"解析薪资失败: {salary_text}, 错误: {e}")
            return None, None
    
    def extract_job_info(self, job_data):
        """从原始数据中提取职位信息
        
        Args:
            job_data: API返回的原始职位数据
            
        Returns:
            dict: 提取并处理后的职位信息
        """
        # 解析薪资
        salary_min, salary_max = self.parse_salary(job_data.get('salary', ''))
        
        # 提取发布日期
        try:
            publish_date = datetime.strptime(job_data.get('fbsj', ''), '%Y-%m-%d').date()
        except:
            publish_date = None
            
        return {
            'title': job_data.get('name', ''),
            'company_name': job_data.get('company_name', ''),
            'job_type': job_data.get('zhiwei_type_name', ''),
            'salary_min': salary_min,
            'salary_max': salary_max,
            'province': job_data.get('province', ''),
            'city': job_data.get('city', ''),
            'description': job_data.get('description', ''),
            'requirement': job_data.get('content', ''),
            'publish_date': publish_date,
            'source_url': f"https://jy.cdu.edu.cn/Zhaopin/zhiweidetail.html?id={job_data.get('id')}&jobtype=1",
            'industry': job_data.get('industry_name', ''),
        } 