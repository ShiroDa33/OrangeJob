import axios from 'axios'

// 创建axios实例
const service = axios.create({
  baseURL: 'http://localhost:8000/api', // API基础路径
  timeout: 10000 // 请求超时时间
})

// 请求拦截器
service.interceptors.request.use(
  config => {
    // 可以在这里添加请求头、认证信息等
    return config
  },
  error => {
    console.error('请求错误:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
service.interceptors.response.use(
  response => {
    // 添加响应内容的详细日志
    console.log('API响应成功:', response.config.url, response.data)
    return response.data
  },
  error => {
    console.error('响应错误:', error)
    
    // 打印完整错误信息
    if (error.response) {
      console.error('错误状态:', error.response.status)
      console.error('错误数据:', error.response.data)
      console.error('错误请求URL:', error.config.url)
    }
    
    // 处理错误响应
    let errorMessage = '未知错误'
    if (error.response) {
      const { status, data } = error.response
      
      // 根据状态码处理错误
      switch (status) {
        case 400:
          errorMessage = data.detail || '请求参数错误'
          break
        case 401:
          errorMessage = '未授权，请登录'
          break
        case 403:
          errorMessage = '禁止访问'
          break
        case 404:
          errorMessage = '请求的资源不存在'
          break
        case 500:
          errorMessage = '服务器内部错误'
          break
        default:
          errorMessage = `请求失败(${status})`
      }
    } else if (error.request) {
      errorMessage = '服务器未响应'
    } else {
      errorMessage = error.message
    }
    
    return Promise.reject(new Error(errorMessage))
  }
)

// API接口
export default {
  // 职位相关接口
  getJobs(params) {
    return service.get('/jobs/', { params })
  },
  
  getJobDetail(id) {
    return service.get(`/jobs/${id}/`)
  },
  
  // 公司相关接口
  getCompanies(params) {
    return service.get('/companies/', { params })
  },
  
  getCompanyDetail(id) {
    return service.get(`/companies/${id}/`)
  },
  
  // 分析相关接口
  getAllAnalysisData() {
    return service.get('/analysis/all/')
  },
  
  getIndustryAnalysis() {
    return service.get('/analysis/industry/')
  },
  
  getSalaryAnalysis() {
    return service.get('/analysis/salary/')
  },
  
  getLocationAnalysis() {
    return service.get('/analysis/location/')
  },
  
  getJobTypeAnalysis() {
    return service.get('/analysis/job_type/')
  }
} 