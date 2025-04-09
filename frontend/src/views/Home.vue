<template>
  <div class="home-container">
    <el-card class="welcome-card">
      <h1 class="welcome-title">欢迎使用<span class="orange-color">橙子就业</span>分析平台</h1>
      <p class="welcome-desc">
        橙子就业是一个针对学校就业网招聘信息的数据分析平台，提供行业分布、薪资范围、地区分布等可视化分析，
        帮助学生了解就业市场动态，为职业规划提供参考。
      </p>
      <div class="action-buttons">
        <el-button type="primary" @click="$router.push('/jobs')">浏览职位</el-button>
        <el-button type="success" @click="$router.push('/analysis')">查看分析</el-button>
      </div>
    </el-card>
    
    <el-card class="latest-jobs-card">
      <div slot="header">
        <span>最新职位</span>
        <el-button style="float: right;" type="text" @click="$router.push('/jobs')">查看更多</el-button>
      </div>
      <el-table v-loading="loading" :data="jobs" @row-click="row => $router.push(`/jobs/${row.id}`)">
        <el-table-column prop="title" label="职位名称"></el-table-column>
        <el-table-column prop="company_name" label="公司名称"></el-table-column>
        <el-table-column prop="job_type" label="岗位类型" width="120"></el-table-column>
        <el-table-column label="薪资" width="120">
          <template slot-scope="scope">
            <span v-if="scope.row.salary_min && scope.row.salary_max">
              {{ formatSalary(scope.row.salary_min) }}-{{ formatSalary(scope.row.salary_max) }}
            </span>
            <span v-else>面议</span>
          </template>
        </el-table-column>
        <el-table-column label="地区" width="120">
          <template slot-scope="scope">
            {{ scope.row.city || scope.row.province || '未知' }}
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script>
import { mapGetters } from 'vuex'

export default {
  name: 'HomePage',
  
  computed: {
    ...mapGetters(['jobList', 'isLoading']),
    jobs() {
      return this.jobList.slice(0, 5) // 只显示前5条
    },
    loading() {
      return this.isLoading
    }
  },
  
  created() {
    this.$store.dispatch('fetchJobs')
  },
  
  methods: {
    formatSalary(salary) {
      if (!salary) return '面议'
      return salary >= 1000 ? (salary / 1000).toFixed(1) + 'K' : salary
    }
  }
}
</script>

<style scoped>
.home-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.welcome-card {
  margin-bottom: 20px;
  text-align: center;
  padding: 20px;
}

.welcome-title {
  font-size: 28px;
  margin-bottom: 20px;
}

.welcome-desc {
  margin-bottom: 30px;
  color: #606266;
  line-height: 1.6;
}

.action-buttons {
  margin: 20px 0;
}

.action-buttons .el-button {
  margin: 0 10px;
}

.latest-jobs-card {
  margin-bottom: 20px;
}
</style> 