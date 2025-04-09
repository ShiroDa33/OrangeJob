from django.db import models

# Create your models here.

class Company(models.Model):
    """公司信息模型"""
    name = models.CharField(max_length=200, verbose_name='公司名称')
    industry = models.CharField(max_length=100, verbose_name='所属行业', null=True, blank=True)
    
    class Meta:
        verbose_name = '公司'
        verbose_name_plural = '公司'
        
    def __str__(self):
        return self.name

class Job(models.Model):
    """职位信息模型"""
    title = models.CharField(max_length=200, verbose_name='职位名称')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='jobs', verbose_name='所属公司')
    job_type = models.CharField(max_length=100, verbose_name='岗位类型', null=True, blank=True)
    salary_min = models.IntegerField(verbose_name='最低薪资(元/月)', null=True, blank=True)
    salary_max = models.IntegerField(verbose_name='最高薪资(元/月)', null=True, blank=True)
    province = models.CharField(max_length=50, verbose_name='省份', null=True, blank=True)
    city = models.CharField(max_length=50, verbose_name='城市', null=True, blank=True)
    description = models.TextField(verbose_name='职位描述', null=True, blank=True)
    requirement = models.TextField(verbose_name='职位要求', null=True, blank=True)
    publish_date = models.DateField(verbose_name='发布日期', null=True, blank=True)
    source_url = models.URLField(verbose_name='来源链接', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '职位'
        verbose_name_plural = '职位'
        ordering = ['-publish_date']
        
    def __str__(self):
        return f"{self.title} - {self.company.name}"

class JobAnalysis(models.Model):
    """职位数据分析结果模型"""
    analysis_date = models.DateField(auto_now_add=True, verbose_name='分析日期')
    analysis_type = models.CharField(max_length=50, verbose_name='分析类型')  # 如：地区分布、薪资分布、行业分布等
    analysis_data = models.JSONField(verbose_name='分析数据')  # 存储JSON格式的分析结果
    
    class Meta:
        verbose_name = '职位分析'
        verbose_name_plural = '职位分析'
        
    def __str__(self):
        return f"{self.analysis_type} - {self.analysis_date}"
