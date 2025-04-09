<template>
  <div class="job-list-container">
    <el-card class="filter-card">
      <el-form :inline="true" :model="filters" class="filter-form">
        <el-form-item label="关键词">
          <el-input v-model="filters.keyword" placeholder="职位名称/公司名称" clearable></el-input>
        </el-form-item>
        <el-form-item label="地区">
          <el-select v-model="filters.province" placeholder="选择省份" clearable>
            <el-option
              v-for="item in provinces"
              :key="item.value"
              :label="item.label"
              :value="item.value">
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="岗位类型">
          <el-select v-model="filters.jobType" placeholder="选择岗位类型" clearable>
            <el-option
              v-for="item in jobTypes"
              :key="item.value"
              :label="item.label"
              :value="item.value">
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="薪资范围">
          <el-select v-model="filters.salaryRange" placeholder="选择薪资范围" clearable>
            <el-option
              v-for="item in salaryRanges"
              :key="item.value"
              :label="item.label"
              :value="item.value">
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="job-list-card">
      <div slot="header">
        <span>职位列表</span>
        <el-select 
          v-model="sortBy" 
          style="float: right; width: 150px;" 
          placeholder="排序方式"
          @change="handleSortChange">
          <el-option label="最新发布" value="publish_date"></el-option>
          <el-option label="薪资从高到低" value="-salary_min"></el-option>
          <el-option label="薪资从低到高" value="salary_min"></el-option>
        </el-select>
      </div>
      
      <div v-if="loading" class="loading-container">
        <el-skeleton :rows="10" animated />
      </div>
      <div v-else>
        <div v-if="jobs.length === 0" class="empty-container">
          <el-empty description="暂无匹配的职位信息"></el-empty>
        </div>
        <div v-else>
          <div v-for="job in jobs" :key="job.id" class="job-item" @click="handleJobClick(job)">
            <div class="job-header">
              <h3 class="job-title">{{ job.title }}</h3>
              <span class="job-salary">
                <template v-if="job.salary_min && job.salary_max">
                  {{ formatSalary(job.salary_min) }}-{{ formatSalary(job.salary_max) }}
                </template>
                <template v-else>面议</template>
              </span>
            </div>
            <div class="job-company">{{ job.company_name }}</div>
            <div class="job-info">
              <el-tag size="small">{{ job.job_type || '未知' }}</el-tag>
              <span class="job-location">{{ job.city || job.province || '未知地区' }}</span>
              <span class="job-date">{{ formatDate(job.publish_date) }}</span>
            </div>
            <div class="job-tags" v-if="job.tags && job.tags.length">
              <el-tag 
                v-for="(tag, index) in parseTags(job.tags)" 
                :key="index"
                size="mini" 
                type="success" 
                effect="plain"
                class="job-tag">
                {{ tag }}
              </el-tag>
            </div>
          </div>
          
          <div class="pagination-container">
            <el-pagination
              background
              layout="prev, pager, next"
              :total="pagination.total"
              :page-size="pagination.pageSize"
              :current-page="pagination.currentPage"
              @current-change="handlePageChange">
            </el-pagination>
          </div>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script>
import { mapGetters } from 'vuex'

export default {
  name: 'JobList',
  
  data() {
    return {
      sortBy: 'publish_date',
      filters: {
        keyword: '',
        province: '',
        jobType: '',
        salaryRange: ''
      },
      provinces: [
        { value: '北京', label: '北京' },
        { value: '上海', label: '上海' },
        { value: '广东', label: '广东' },
        { value: '四川', label: '四川' },
        { value: '浙江', label: '浙江' }
      ],
      jobTypes: [
        { value: '技术', label: '技术' },
        { value: '产品', label: '产品' },
        { value: '设计', label: '设计' },
        { value: '运营', label: '运营' },
        { value: '市场', label: '市场' },
        { value: '销售', label: '销售' }
      ],
      salaryRanges: [
        { value: '0,5000', label: '5K以下' },
        { value: '5000,10000', label: '5K-10K' },
        { value: '10000,15000', label: '10K-15K' },
        { value: '15000,20000', label: '15K-20K' },
        { value: '20000,30000', label: '20K-30K' },
        { value: '30000,999999', label: '30K以上' }
      ]
    }
  },
  
  computed: {
    ...mapGetters([
      'jobList',
      'isLoading',
      'currentPagination'
    ]),
    
    jobs() {
      return this.jobList
    },
    
    loading() {
      return this.isLoading
    },
    
    pagination() {
      return this.currentPagination
    }
  },
  
  created() {
    this.fetchJobs()
  },
  
  methods: {
    fetchJobs() {
      this.$store.dispatch('fetchJobs')
    },
    
    formatSalary(salary) {
      if (!salary) return '面议'
      
      // 确保数值格式化为数字
      const salaryNum = Number(salary)
      if (isNaN(salaryNum)) return salary
      
      // 如果薪资大于等于1000，则显示为xK格式
      if (salaryNum >= 1000) {
        return (salaryNum / 1000).toFixed(1) + 'K'
      }
      
      return salary
    },
    
    handleSearch() {
      // 处理薪资范围
      let salaryMin, salaryMax
      if (this.filters.salaryRange) {
        [salaryMin, salaryMax] = this.filters.salaryRange.split(',')
      }
      
      // 构建筛选条件
      const filters = {
        keyword: this.filters.keyword,
        province: this.filters.province,
        job_type: this.filters.jobType,
        salary_min: salaryMin,
        salary_max: salaryMax
      }
      
      // 设置排序
      if (this.sortBy) {
        filters.ordering = this.sortBy
      }
      
      this.$store.dispatch('setFilters', filters)
    },
    
    handleReset() {
      this.filters = {
        keyword: '',
        province: '',
        jobType: '',
        salaryRange: ''
      }
      this.sortBy = 'publish_date'
      this.$store.dispatch('setFilters', {})
    },
    
    handleSortChange() {
      this.handleSearch()
    },
    
    handlePageChange(page) {
      this.$store.dispatch('setPagination', { currentPage: page })
    },
    
    handleJobClick(job) {
      this.$router.push(`/jobs/${job.id}`)
    },
    
    formatDate(date) {
      if (!date) return '未知日期'
      const formattedDate = new Date(date).toLocaleDateString()
      return formattedDate
    },
    
    parseTags(tags) {
      // 处理标签数据，可能是字符串或数组
      if (!tags) return []
      
      if (typeof tags === 'string') {
        try {
          // 尝试解析JSON字符串
          return JSON.parse(tags)
        } catch (e) {
          // 如果不是有效的JSON，则当做单个标签处理
          return [tags]
        }
      } else if (Array.isArray(tags)) {
        return tags
      }
      
      return []
    }
  }
}
</script>

<style scoped>
.job-list-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.filter-card {
  margin-bottom: 20px;
}

.filter-form {
  display: flex;
  flex-wrap: wrap;
}

.job-list-card {
  margin-bottom: 20px;
}

.loading-container {
  padding: 20px;
}

.empty-container {
  padding: 40px 0;
  text-align: center;
}

.job-item {
  padding: 20px;
  border-bottom: 1px solid #ebeef5;
  cursor: pointer;
  transition: background-color 0.3s;
}

.job-item:hover {
  background-color: #f5f7fa;
}

.job-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.job-title {
  margin: 0;
  font-size: 18px;
  color: #303133;
}

.job-salary {
  color: #ff9900;
  font-size: 16px;
  font-weight: bold;
}

.job-company {
  color: #606266;
  margin-bottom: 10px;
}

.job-info {
  display: flex;
  align-items: center;
}

.job-tags {
  margin-top: 10px;
}

.job-tag {
  margin-right: 5px;
  margin-bottom: 5px;
}

.job-location, .job-date {
  margin-left: 15px;
  color: #909399;
  font-size: 14px;
}

.pagination-container {
  padding: 20px 0;
  text-align: center;
}
</style> 