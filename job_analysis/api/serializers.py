from rest_framework import serializers
from ..models import Company, Job, JobAnalysis

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = '__all__'

class JobSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source='company.name', read_only=True)
    industry = serializers.CharField(source='company.industry', read_only=True)
    
    class Meta:
        model = Job
        fields = [
            'id', 'title', 'company', 'company_name', 'industry',
            'job_type', 'salary_min', 'salary_max', 'province', 'city',
            'description', 'requirement', 'publish_date', 'source_url',
            'created_at', 'updated_at'
        ]

class JobAnalysisSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobAnalysis
        fields = '__all__' 