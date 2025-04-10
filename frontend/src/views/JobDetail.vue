<template>
  <div class="job-detail-container">
    <el-card v-if="loading" class="loading-card">
      <div class="loading-container">
        <el-skeleton :rows="15" animated />
      </div>
    </el-card>
    
    <div v-else-if="!job" class="not-found">
      <el-result
        icon="error"
        title="职位未找到"
        sub-title="您查找的职位信息不存在或已被删除">
        <template slot="extra">
          <el-button type="primary" @click="$router.push('/jobs')">返回职位列表</el-button>
        </template>
      </el-result>
    </div>
    
    <div v-else>
      <!-- 职位基本信息 -->
      <el-card class="job-basic-card">
        <div class="job-header">
          <div class="job-title-section">
            <h1 class="job-title">{{ job.title }}</h1>
            <div class="job-company">{{ job.company_name }}</div>
          </div>
          <div class="job-salary">
            <template v-if="job.salary_min && job.salary_max">
              {{ formatSalary(job.salary_min) }}-{{ formatSalary(job.salary_max) }}
            </template>
            <template v-else>薪资面议</template>
          </div>
        </div>
        
        <el-divider></el-divider>
        
        <div class="job-meta">
          <div class="meta-item">
            <i class="el-icon-office-building"></i>
            <span>{{ job.job_type || '未知类型' }}</span>
          </div>
          <div class="meta-item">
            <i class="el-icon-location"></i>
            <span>{{ job.province }} {{ job.city }}</span>
          </div>
          <div class="meta-item">
            <i class="el-icon-date"></i>
            <span>{{ job.publish_date || '未知日期' }}</span>
          </div>
          <div class="meta-item">
            <i class="el-icon-collection-tag"></i>
            <span>{{ job.industry || '未知行业' }}</span>
          </div>
        </div>
        
        <div class="job-actions">
          <el-button type="primary" icon="el-icon-link" @click="openSourceUrl">查看原始职位</el-button>
          <el-button icon="el-icon-back" @click="$router.go(-1)">返回</el-button>
        </div>
      </el-card>
      
      <!-- 职位详细信息 -->
      <el-card class="job-detail-card">
        <el-tabs v-model="activeTab">
          <el-tab-pane label="职位描述" name="description">
            <div class="tab-content" v-html="formattedDescription"></div>
          </el-tab-pane>
          <el-tab-pane label="职位要求" name="requirement">
            <div class="tab-content" v-html="formattedRequirement"></div>
          </el-tab-pane>
          <el-tab-pane label="公司信息" name="company">
            <div class="tab-content">
              <h3>公司名称</h3>
              <p>{{ job.company_name }}</p>
              
              <h3>所属行业</h3>
              <p>{{ job.industry || '未提供' }}</p>
              
              <h3>公司简介</h3>
              <p>暂无详细信息</p>
            </div>
          </el-tab-pane>
        </el-tabs>
      </el-card>
      
      <!-- 相似职位推荐 -->
      <el-card class="similar-jobs-card">
        <div slot="header">
          <span>相似职位推荐（{{ job.job_type }}）</span>
        </div>
        <div v-if="!similarJobs.length" class="empty-data">
          <el-empty description="暂无相似职位推荐"></el-empty>
        </div>
        <div v-else class="similar-jobs-list">
          <div 
            v-for="item in similarJobs" 
            :key="item.id" 
            class="similar-job-item"
            @click="goToJob(item.id)"
          >
            <div class="similar-job-title">{{ item.title }}</div>
            <div class="similar-job-company">{{ item.company_name }}</div>
            <div class="similar-job-meta">
              <span>{{ item.province }} {{ item.city }}</span>
              <span class="similar-job-salary">
                <template v-if="item.salary_min && item.salary_max">
                  {{ formatSalary(item.salary_min) }}-{{ formatSalary(item.salary_max) }}
                </template>
                <template v-else>薪资面议</template>
              </span>
            </div>
          </div>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script>
import { mapGetters } from 'vuex'

export default {
  name: 'JobDetailPage',
  
  data() {
    return {
      activeTab: 'description',
      similarJobs: []
    }
  },
  
  computed: {
    ...mapGetters(['jobDetail', 'isLoading']),
    
    jobId() {
      return this.$route.params.id
    },
    
    job() {
      return this.jobDetail
    },
    
    loading() {
      return this.isLoading
    },
    
    formattedDescription() {
      if (!this.job || !this.job.description) return '暂无描述'
      return this.formatContent(this.job.description)
    },
    
    formattedRequirement() {
      if (!this.job || !this.job.requirement) return '暂无要求'
      return this.formatContent(this.job.requirement)
    }
  },
  
  created() {
    this.fetchJobDetail()
  },
  
  watch: {
    // 监听路由参数变化，当ID变化时重新获取数据
    '$route.params.id': function(newId, oldId) {
      if (newId !== oldId) {
        this.fetchJobDetail()
      }
    }
  },
  
  methods: {
    async fetchJobDetail() {
      try {
        await this.$store.dispatch('fetchJobDetail', this.jobId)
        this.fetchSimilarJobs()
      } catch (error) {
        this.$message.error(error.message || '获取职位详情失败')
      }
    },
    
    async fetchSimilarJobs() {
      if (!this.job || !this.job.job_type) {
        this.similarJobs = [];
        return;
      }
      
      try {
        // 使用当前职位的dalei_id_name属性获取相似职位
        const response = await this.$api.getSimilarJobs(this.jobId, this.job.job_type, 3);
        
        // 处理API响应
        if (Array.isArray(response)) {
          this.similarJobs = response;
        } else if (response.results && Array.isArray(response.results)) {
          this.similarJobs = response.results;
        } else {
          this.similarJobs = [];
        }
        
        console.log('获取到相似职位:', this.similarJobs);
      } catch (error) {
        console.error('获取相似职位失败:', error);
        this.similarJobs = [];
      }
    },
    
    formatSalary(salary) {
      if (!salary) return '面议'
      return salary >= 1000 ? (salary / 1000).toFixed(1) + 'K' : salary
    },
    
    formatContent(content) {
      if (!content) return ''
      
      // 替换换行符为<br>
      let formatted = content.replace(/\n/g, '<br>')
      
      // 添加简单的格式化
      formatted = formatted
        .replace(/【([^】]+)】/g, '<strong>$1</strong>')  // 【文字】替换为加粗
        .replace(/\*([^*]+)\*/g, '<em>$1</em>')  // *文字*替换为斜体
        
      return formatted
    },
    
    openSourceUrl() {
      if (this.job && this.job.source_url) {
        window.open(this.job.source_url, '_blank')
      } else {
        this.$message.warning('原始职位链接不可用')
      }
    },
    
    goToJob(id) {
      if (id === parseInt(this.jobId)) return
      
      // 切换到相似职位详情
      this.$router.push(`/jobs/${id}`)
      
      // 滚动到页面顶部
      window.scrollTo(0, 0)
    }
  }
}
</script>

<style scoped>
.job-detail-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.loading-card, .job-basic-card, .job-detail-card, .similar-jobs-card {
  margin-bottom: 20px;
}

.loading-container {
  padding: 20px;
}

.not-found {
  padding: 40px 0;
}

.job-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20px;
}

.job-title {
  margin: 0 0 10px 0;
  font-size: 24px;
  color: #303133;
}

.job-company {
  color: #606266;
  font-size: 16px;
}

.job-salary {
  color: #ff9900;
  font-size: 20px;
  font-weight: bold;
}

.job-meta {
  display: flex;
  flex-wrap: wrap;
  margin-bottom: 20px;
}

.meta-item {
  margin-right: 20px;
  margin-bottom: 10px;
  color: #606266;
}

.meta-item i {
  margin-right: 5px;
}

.job-actions {
  margin-top: 20px;
}

.tab-content {
  padding: 20px 0;
  line-height: 1.8;
}

.empty-data {
  padding: 40px 0;
  text-align: center;
}

.similar-jobs-list {
  display: flex;
  flex-wrap: wrap;
  margin: -10px;
}

.similar-job-item {
  flex: 1;
  min-width: 300px;
  margin: 10px;
  padding: 15px;
  border: 1px solid #ebeef5;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s;
}

.similar-job-item:hover {
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  border-color: #dcdfe6;
}

.similar-job-title {
  font-weight: bold;
  margin-bottom: 8px;
  color: #303133;
}

.similar-job-company {
  color: #606266;
  margin-bottom: 8px;
  font-size: 14px;
}

.similar-job-meta {
  display: flex;
  justify-content: space-between;
  color: #909399;
  font-size: 14px;
}

.similar-job-salary {
  color: #ff9900;
}
</style> 