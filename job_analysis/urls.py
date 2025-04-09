from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api.views import CompanyViewSet, JobViewSet, AnalysisViewSet

# 创建路由器
router = DefaultRouter()
router.register(r'companies', CompanyViewSet)
router.register(r'jobs', JobViewSet)
router.register(r'analysis', AnalysisViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
] 