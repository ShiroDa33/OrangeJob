from django.core.management.base import BaseCommand
from django.db import transaction
from job_analysis.models import Company, Job
from datetime import datetime
import requests
import json
import random
import time
import concurrent.futures

class Command(BaseCommand):
    help = '从成都大学就业网抓取招聘数据'

    def add_arguments(self, parser):
        parser.add_argument(
            '--pages',
            type=int,
            default=5,
            help='最大爬取页数'
        )
        parser.add_argument(
            '--workers',
            type=int,
            default=5,
            help='并发线程数'
        )
        parser.add_argument(
            '--type',
            type=int,
            default=1,
            help='职位类型 (1=全职, 2=实习, 3=兼职)'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            default=False,
            help='是否清空现有数据'
        )

    def handle(self, *args, **options):
        self.stdout.write('开始抓取招聘数据...')
        
        # 获取参数
        max_pages = options['pages']
        max_workers = options['workers']
        job_type = options['type']
        clear_data = options['clear']
        
        # 清空现有数据
        if clear_data:
            self.stdout.write('清空现有数据...')
            Job.objects.all().delete()
            Company.objects.all().delete()
        
        self.stdout.write(self.style.SUCCESS(f"开始爬取职位信息，类型: {job_type}，最大页数: {max_pages}，并发线程数: {max_workers}"))
        
        # 获取第一页数据，确定总页数
        self.stdout.write('获取第1页数据以确定总页数...')
        first_page_data = self.fetch_jobs_data(1, job_type)
        
        if not first_page_data:
            self.stdout.write(self.style.ERROR('获取第1页数据失败，停止爬取'))
            return
        
        # 处理第一页数据
        first_page_count = self.process_jobs_data(first_page_data)
        self.stdout.write(f'已处理第1页数据，获取{first_page_count}个职位')
        
        total_jobs = first_page_count
        
        # 确定实际需要爬取的页数
        # 如果返回的数据不足一页，说明已到达最后一页
        if first_page_count < 20:
            self.stdout.write('数据不足一页，结束爬取')
            self.stdout.write(self.style.SUCCESS(f'数据抓取完成! 共获取{total_jobs}个职位'))
            return
        
        # 并发爬取剩余页面（从第2页开始）
        remaining_pages = min(max_pages, 20) - 1  # 限制最大页数为20，避免过度爬取
        if remaining_pages > 0:
            self.stdout.write(f'开始并发爬取剩余{remaining_pages}页数据...')
            
            failed_pages = []  # 记录失败的页码
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                # 创建爬取任务
                future_to_page = {
                    executor.submit(self.fetch_jobs_data, page, job_type): page 
                    for page in range(2, remaining_pages + 2)
                }
                
                # 处理爬取结果
                for future in concurrent.futures.as_completed(future_to_page):
                    page = future_to_page[future]
                    try:
                        jobs_data = future.result()
                        if jobs_data:
                            # 并发处理每页的职位数据
                            jobs_count = self.process_jobs_data(jobs_data)
                            total_jobs += jobs_count
                            self.stdout.write(f'已处理第{page}页数据，获取{jobs_count}个职位')
                            
                            # 如果返回的数据不足一页，可能已到达最后页
                            if jobs_count < 20:
                                self.stdout.write(f'第{page}页数据不足一页，可能已到达最后页')
                        else:
                            self.stdout.write(self.style.WARNING(f'第{page}页数据获取失败'))
                            failed_pages.append(page)
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f'处理第{page}页时出错: {str(e)}'))
                        failed_pages.append(page)
            
            # 如果有失败的页面，尝试串行重试一次
            if failed_pages:
                self.stdout.write(f'有 {len(failed_pages)} 个页面爬取失败，尝试重新爬取...')
                for page in failed_pages:
                    try:
                        self.stdout.write(f'重新爬取第 {page} 页...')
                        retry_jobs_data = self.fetch_jobs_data(page, job_type)
                        if retry_jobs_data:
                            retry_count = self.process_jobs_data(retry_jobs_data)
                            total_jobs += retry_count
                            self.stdout.write(f'重试成功：第{page}页获取{retry_count}个职位')
                        else:
                            self.stdout.write(self.style.WARNING(f'重试失败：第{page}页仍无法获取数据'))
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f'重试第{page}页时出错: {str(e)}'))
        
        self.stdout.write(self.style.SUCCESS(f'数据抓取完成! 共获取{total_jobs}个职位'))
    
    def fetch_jobs_data(self, page, job_type=1):
        """从成都大学就业网获取招聘数据"""
        url = 'https://a.jiuyeb.cn/mobile.php/job/getlist'
        
        headers = {
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'auth': 'Baisc MTAyNDY6MTAyNDY=',
            'cache-control': 'no-cache',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'origin': 'https://jy.cdu.edu.cn',
            'pragma': 'no-cache',
            'referer': 'https://jy.cdu.edu.cn/',
            'sec-ch-ua': '"Microsoft Edge";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'cross-site',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36 Edg/135.0.0.0'
        }
        
        data = {
            'jobtype': str(job_type),
            'isunion': '2',
            'school_id': '92727a49-c69a-6814-7231-a90bbbe287a7',
            'page': str(page),
            'size': '20',
            'province_id': '0',
            'city_id': '0',
            'dalei_id': '0',
            'cate_id1': '0',
            'salary_floor': '',
            'salay_ceil': '',
            'day': '0',
            'login_user_id': '1',
            'login_admin_school_code': '11079',
            'login_admin_school_id': '92727a49-c69a-6814-7231-a90bbbe287a7'
        }
        
        self.stdout.write(f"正在爬取第 {page} 页数据...")
        try:
            response = requests.post(url, headers=headers, data=data, timeout=10)
            response.raise_for_status()  # 如果状态码不是200，引发异常
            
            # 避免请求过快
            time.sleep(0.5)
            
            result = response.json()
            
            # 输出更详细的调试信息
            self.stdout.write(f"第 {page} 页API返回状态码: {result.get('code')}")
            self.stdout.write(f"第 {page} 页API返回消息: {result.get('msg')}")
            
            # API特殊情况：状态码为0但实际上是成功的
            # 检查返回的数据结构
            if 'data' in result:
                self.stdout.write(f"第 {page} 页数据结构: {str(result['data'].keys())[:100]}...")
                if 'list' in result['data']:
                    job_list = result['data']['list']
                    self.stdout.write(f"第 {page} 页获取到 {len(job_list)} 条职位数据")
                    return job_list
            
            # 尝试直接从result中获取list字段
            if 'list' in result:
                job_list = result['list']
                self.stdout.write(f"直接从result获取到 {len(job_list)} 条职位数据")
                return job_list
            
            # 尝试遍历所有字段查找列表数据
            for key, value in result.items():
                if isinstance(value, list) and len(value) > 0:
                    # 检查列表的第一个元素是否包含职位相关字段
                    first_item = value[0]
                    if isinstance(first_item, dict) and ('work_name' in first_item or 'com_id_name' in first_item):
                        self.stdout.write(f"从字段 {key} 中找到疑似职位列表，包含 {len(value)} 条数据")
                        return value
            
            # 如果以上方法都无法获取数据，输出完整的返回结构帮助调试
            self.stdout.write(f"完整的返回结构: {str(result)[:500]}...")
            self.stdout.write(self.style.ERROR(f'无法从返回数据中提取职位列表，第 {page} 页爬取失败'))
            return None
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'请求第 {page} 页数据失败: {str(e)}'))
            return None
    
    @transaction.atomic
    def process_jobs_data(self, jobs_data):
        """处理招聘数据并保存到数据库"""
        count = 0
        
        for job_data in jobs_data:
            try:
                # 提取公司和职位信息
                company_name = job_data.get('com_id_name', '')
                if not company_name:
                    continue
                
                # 提取行业信息
                industry = job_data.get('industry_id_name', '')
                
                # 查找或创建公司
                company, created = Company.objects.get_or_create(
                    name=company_name,
                    defaults={'industry': industry}
                )
                
                # 提取职位基本信息
                title = job_data.get('work_name', '')
                if not title:
                    continue
                
                # 提取职位类型
                job_type = job_data.get('cate_id1_name', '') or job_data.get('dalei_id_name', '')
                
                # 提取发布日期
                # 优先使用examine_time时间戳
                publish_date = None
                if job_data.get('examine_time'):
                    try:
                        # 将时间戳转换为日期
                        timestamp = int(job_data.get('examine_time'))
                        publish_date = datetime.fromtimestamp(timestamp).date()
                    except Exception as e:
                        pass
                
                # 如果examine_time解析失败，尝试使用addtime1
                if not publish_date and job_data.get('addtime1'):
                    try:
                        publish_date = datetime.strptime(job_data.get('addtime1'), '%Y-%m-%d').date()
                    except Exception as e:
                        pass
                
                # 如果还是失败，尝试使用addtime时间戳
                if not publish_date and job_data.get('addtime'):
                    try:
                        timestamp = int(job_data.get('addtime'))
                        publish_date = datetime.fromtimestamp(timestamp).date()
                    except Exception as e:
                        pass
                
                # 提取薪资信息
                salary_min = None
                salary_max = None
                
                # 优先使用API返回的薪资范围
                if job_data.get('salary_floor') is not None:
                    try:
                        salary_min = int(job_data.get('salary_floor'))
                    except:
                        pass
                
                if job_data.get('salay_ceil') is not None:
                    try:
                        salary_max = int(job_data.get('salay_ceil'))
                    except:
                        pass
                
                # 如果API返回的薪资无效，尝试解析薪资文本
                if (salary_min is None or salary_max is None) and job_data.get('xinzi'):
                    salary_text = job_data.get('xinzi', '')
                    parsed_min, parsed_max = self.parse_salary(salary_text)
                    
                    if salary_min is None:
                        salary_min = parsed_min
                    
                    if salary_max is None:
                        salary_max = parsed_max
                
                # 提取地区信息
                province = job_data.get('province_id_name', '')
                city = job_data.get('city_id_name', '')
                
                # 构建描述和要求
                description = f"职位名称：{title}\n"
                description += f"公司名称：{company_name}\n"
                if job_data.get('workplace', ''):
                    description += f"工作地点：{job_data.get('workplace', '')}\n"
                if job_data.get('xueli_id_name', ''):
                    description += f"学历要求：{job_data.get('xueli_id_name', '')}\n"
                if job_data.get('person_count', ''):
                    description += f"招聘人数：{job_data.get('person_count', '')}\n"
                if job_data.get('zhuanye', ''):
                    description += f"专业要求：{job_data.get('zhuanye', '')}\n"
                
                requirement = "岗位职责与要求：\n"
                if job_data.get('content', ''):
                    requirement += job_data.get('content', '')
                
                # 源链接
                source_url = f"https://jy.cdu.edu.cn/Zhaopin/zhiweiDetail.html?id={job_data.get('id', '')}"
                
                # 提取福利标签
                tags = []
                
                # 从tagsList字段获取福利标签
                tag_list = job_data.get('tagsList', [])
                if tag_list and isinstance(tag_list, list):
                    for tag_item in tag_list:
                        if isinstance(tag_item, dict) and 'title' in tag_item:
                            tags.append(tag_item['title'])
                
                # 创建职位
                Job.objects.create(
                    title=title,
                    company=company,
                    job_type=job_type,
                    salary_min=salary_min,
                    salary_max=salary_max,
                    province=province,
                    city=city,
                    description=description,
                    requirement=requirement,
                    publish_date=publish_date,
                    source_url=source_url,
                    tags=tags
                )
                
                count += 1
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'处理职位数据失败: {str(e)}'))
                continue
        
        return count
    
    def parse_salary(self, salary_text):
        """解析薪资文本，返回最低和最高薪资"""
        if not salary_text or salary_text == '面议':
            return None, None
        
        try:
            # 处理"3000-5000"这样的格式
            if '-' in salary_text:
                parts = salary_text.replace('元/月', '').replace('/月', '').split('-')
                min_salary = self.convert_to_int(parts[0])
                max_salary = self.convert_to_int(parts[1])
                return min_salary, max_salary
            
            # 处理"3000以上"这样的格式
            if '以上' in salary_text:
                min_salary = self.convert_to_int(salary_text.replace('以上', '').replace('元/月', '').replace('/月', ''))
                max_salary = min_salary * 1.5  # 估算一个最高值
                return min_salary, max_salary
            
            # 处理"3000以下"这样的格式
            if '以下' in salary_text:
                max_salary = self.convert_to_int(salary_text.replace('以下', '').replace('元/月', '').replace('/月', ''))
                min_salary = max_salary * 0.7  # 估算一个最低值
                return min_salary, max_salary
            
            # 处理单个数值
            salary = self.convert_to_int(salary_text.replace('元/月', '').replace('/月', ''))
            return salary, salary
        except:
            return None, None
    
    def convert_to_int(self, text):
        """将薪资文本转换为整数"""
        # 处理'3k'这样的格式
        if 'k' in text.lower() or 'K' in text:
            return int(float(text.lower().replace('k', '')) * 1000)
        
        # 处理普通数字
        return int(float(text)) 