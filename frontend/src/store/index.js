import Vue from 'vue'
import Vuex from 'vuex'
import api from '../api'

Vue.use(Vuex)

export default new Vuex.Store({
  state: {
    jobs: [],
    job: null,
    loading: false,
    error: null,
    filters: {
      keyword: '',
      province: '',
      city: '',
      industry: '',
      jobType: '',
      salaryMin: null,
      salaryMax: null
    },
    pagination: {
      currentPage: 1,
      pageSize: 10,
      total: 0
    },
    analysisData: {
      industry: null,
      salary: null,
      location: null,
      jobType: null
    }
  },
  
  mutations: {
    SET_LOADING(state, status) {
      state.loading = status
    },
    SET_ERROR(state, error) {
      state.error = error
    },
    SET_JOBS(state, jobs) {
      state.jobs = jobs
    },
    SET_JOB(state, job) {
      state.job = job
    },
    SET_PAGINATION(state, pagination) {
      state.pagination = { ...state.pagination, ...pagination }
    },
    SET_FILTERS(state, filters) {
      state.filters = { ...state.filters, ...filters }
    },
    SET_ANALYSIS_DATA(state, { key, data }) {
      state.analysisData[key] = data
    }
  },
  
  actions: {
    // 获取职位列表
    async fetchJobs({ commit, state }) {
      try {
        commit('SET_LOADING', true)
        commit('SET_ERROR', null)
        
        // 构建查询参数
        const params = {
          page: state.pagination.currentPage,
          page_size: state.pagination.pageSize,
          ...state.filters
        }
        
        console.log('请求职位列表，参数:', params)
        const response = await api.getJobs(params)
        console.log('职位列表响应:', response)
        
        // 检查响应数据格式
        if (!response) {
          throw new Error('返回了空的响应数据')
        }
        
        // 适配不同的响应格式
        let jobs = []
        let total = 0
        
        if (Array.isArray(response)) {
          // 如果响应直接是数组
          jobs = response
          total = response.length
        } else if (response.results && Array.isArray(response.results)) {
          // Django REST Framework 的默认分页格式
          jobs = response.results
          total = response.count || jobs.length
        } else if (typeof response === 'object') {
          // 其他格式，尝试提取数据
          console.log('尝试解析未知格式的响应:', response)
          if (response.data && Array.isArray(response.data)) {
            jobs = response.data
            total = response.total || jobs.length
          } else {
            // 尝试将响应对象转换为数组
            const possibleJobs = Object.values(response).find(val => Array.isArray(val))
            if (possibleJobs) {
              jobs = possibleJobs
              total = jobs.length
            }
          }
        }
        
        console.log('处理后的职位数据:', jobs, '总数:', total)
        commit('SET_JOBS', jobs)
        commit('SET_PAGINATION', { total })
        
        return response
      } catch (error) {
        console.error('获取职位列表失败:', error)
        commit('SET_ERROR', error.message || '获取职位列表失败')
        return Promise.reject(error)
      } finally {
        commit('SET_LOADING', false)
      }
    },
    
    // 获取职位详情
    async fetchJobDetail({ commit }, jobId) {
      try {
        commit('SET_LOADING', true)
        commit('SET_ERROR', null)
        
        const response = await api.getJobDetail(jobId)
        commit('SET_JOB', response)
        
        return response
      } catch (error) {
        commit('SET_ERROR', error.message || '获取职位详情失败')
        return Promise.reject(error)
      } finally {
        commit('SET_LOADING', false)
      }
    },
    
    // 设置筛选条件
    setFilters({ commit, dispatch }, filters) {
      commit('SET_FILTERS', filters)
      commit('SET_PAGINATION', { currentPage: 1 }) // 重置到第一页
      return dispatch('fetchJobs')
    },
    
    // 设置分页
    setPagination({ commit, dispatch }, pagination) {
      commit('SET_PAGINATION', pagination)
      return dispatch('fetchJobs')
    },
    
    // 获取所有分析数据
    async fetchAllAnalysisData({ commit }) {
      try {
        commit('SET_LOADING', true)
        commit('SET_ERROR', null)
        
        console.log('请求分析数据')
        const response = await api.getAllAnalysisData()
        console.log('分析数据响应:', response)
        
        // 检查响应格式
        if (!response) {
          throw new Error('返回了空的分析数据')
        }
        
        // 设置各个分析数据
        if (response.industry_distribution) {
          console.log('设置行业分布数据:', response.industry_distribution)
          commit('SET_ANALYSIS_DATA', { key: 'industry', data: response.industry_distribution })
        }
        
        if (response.salary_distribution) {
          console.log('设置薪资分布数据:', response.salary_distribution)
          commit('SET_ANALYSIS_DATA', { key: 'salary', data: response.salary_distribution })
        }
        
        if (response.location_distribution) {
          console.log('设置地区分布数据:', response.location_distribution)
          commit('SET_ANALYSIS_DATA', { key: 'location', data: response.location_distribution })
        }
        
        if (response.job_type_distribution) {
          console.log('设置岗位类型数据:', response.job_type_distribution)
          commit('SET_ANALYSIS_DATA', { key: 'jobType', data: response.job_type_distribution })
        }
        
        // 直接尝试解析JSON字符串
        if (typeof response === 'string') {
          try {
            const parsedData = JSON.parse(response)
            console.log('解析JSON字符串:', parsedData)
            
            if (parsedData.industry_distribution) {
              commit('SET_ANALYSIS_DATA', { key: 'industry', data: parsedData.industry_distribution })
            }
            
            if (parsedData.salary_distribution) {
              commit('SET_ANALYSIS_DATA', { key: 'salary', data: parsedData.salary_distribution })
            }
            
            if (parsedData.location_distribution) {
              commit('SET_ANALYSIS_DATA', { key: 'location', data: parsedData.location_distribution })
            }
            
            if (parsedData.job_type_distribution) {
              commit('SET_ANALYSIS_DATA', { key: 'jobType', data: parsedData.job_type_distribution })
            }
          } catch (e) {
            console.error('解析JSON字符串失败:', e)
          }
        }
        
        return response
      } catch (error) {
        console.error('获取分析数据失败:', error)
        commit('SET_ERROR', error.message || '获取分析数据失败')
        return Promise.reject(error)
      } finally {
        commit('SET_LOADING', false)
      }
    }
  },
  
  getters: {
    isLoading: state => state.loading,
    hasError: state => !!state.error,
    errorMessage: state => state.error,
    jobList: state => state.jobs,
    jobDetail: state => state.job,
    currentFilters: state => state.filters,
    currentPagination: state => state.pagination,
    industryAnalysis: state => state.analysisData.industry,
    salaryAnalysis: state => state.analysisData.salary,
    locationAnalysis: state => state.analysisData.location,
    jobTypeAnalysis: state => state.analysisData.jobType
  }
}) 