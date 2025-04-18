# Generated by Django 5.0.2 on 2025-04-09 15:02

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Company',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='公司名称')),
                ('industry', models.CharField(blank=True, max_length=100, null=True, verbose_name='所属行业')),
            ],
            options={
                'verbose_name': '公司',
                'verbose_name_plural': '公司',
            },
        ),
        migrations.CreateModel(
            name='JobAnalysis',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('analysis_date', models.DateField(auto_now_add=True, verbose_name='分析日期')),
                ('analysis_type', models.CharField(max_length=50, verbose_name='分析类型')),
                ('analysis_data', models.JSONField(verbose_name='分析数据')),
            ],
            options={
                'verbose_name': '职位分析',
                'verbose_name_plural': '职位分析',
            },
        ),
        migrations.CreateModel(
            name='Job',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200, verbose_name='职位名称')),
                ('job_type', models.CharField(blank=True, max_length=100, null=True, verbose_name='岗位类型')),
                ('salary_min', models.IntegerField(blank=True, null=True, verbose_name='最低薪资(元/月)')),
                ('salary_max', models.IntegerField(blank=True, null=True, verbose_name='最高薪资(元/月)')),
                ('province', models.CharField(blank=True, max_length=50, null=True, verbose_name='省份')),
                ('city', models.CharField(blank=True, max_length=50, null=True, verbose_name='城市')),
                ('description', models.TextField(blank=True, null=True, verbose_name='职位描述')),
                ('requirement', models.TextField(blank=True, null=True, verbose_name='职位要求')),
                ('publish_date', models.DateField(blank=True, null=True, verbose_name='发布日期')),
                ('source_url', models.URLField(blank=True, null=True, verbose_name='来源链接')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='jobs', to='job_analysis.company', verbose_name='所属公司')),
            ],
            options={
                'verbose_name': '职位',
                'verbose_name_plural': '职位',
                'ordering': ['-publish_date'],
            },
        ),
    ]
