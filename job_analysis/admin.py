from django.contrib import admin
from .models import Company, Job, JobAnalysis

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'industry')
    search_fields = ('name', 'industry')
    list_filter = ('industry',)

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('title', 'company', 'job_type', 'salary_min', 'salary_max', 'province', 'city', 'publish_date')
    search_fields = ('title', 'company__name', 'job_type', 'province', 'city')
    list_filter = ('job_type', 'province', 'publish_date')
    date_hierarchy = 'publish_date'
    readonly_fields = ('created_at', 'updated_at')

@admin.register(JobAnalysis)
class JobAnalysisAdmin(admin.ModelAdmin):
    list_display = ('analysis_type', 'analysis_date')
    list_filter = ('analysis_type', 'analysis_date')
    date_hierarchy = 'analysis_date'
