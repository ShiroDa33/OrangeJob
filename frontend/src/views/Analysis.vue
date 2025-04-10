<template>
  <div class="analysis-container">
    <h1 class="page-title">招聘数据分析</h1>
    
    <div v-if="loading" class="loading-container">
      <el-skeleton :rows="20" animated />
    </div>
    <div v-else>
      <!-- 学历-薪资分布分析（替换行业分布分析） -->
      <el-card class="chart-card">
        <div slot="header" class="chart-header">
          <span>学历要求-薪资分布分析</span>
          <el-select v-model="educationSalaryChartType" size="small" style="width: 120px;">
            <el-option label="柱状图" value="bar"></el-option>
            <el-option label="折线图" value="line"></el-option>
          </el-select>
        </div>
        <div class="chart-container">
          <div v-if="!educationSalaryData" class="empty-data">
            <el-empty description="暂无学历-薪资分布数据"></el-empty>
          </div>
          <div v-else ref="educationSalaryChart" class="chart"></div>
        </div>
      </el-card>
      
      <!-- 薪资分布分析 -->
      <el-card class="chart-card">
        <div slot="header">
          <span>薪资分布分析</span>
        </div>
        <div class="chart-container">
          <div v-if="!salaryData" class="empty-data">
            <el-empty description="暂无薪资分布数据"></el-empty>
          </div>
          <div v-else ref="salaryChart" class="chart"></div>
        </div>
      </el-card>
      
      <!-- 地区分布分析 -->
      <el-card class="chart-card">
        <div slot="header" class="chart-header">
          <span>地区分布分析</span>
          <el-select v-model="selectedProvince" size="small" style="width: 120px;">
            <el-option label="全部省份" value=""></el-option>
            <el-option 
              v-for="province in provinceOptions" 
              :key="province" 
              :label="province" 
              :value="province">
            </el-option>
          </el-select>
        </div>
        <div class="chart-container">
          <div v-if="!locationData" class="empty-data">
            <el-empty description="暂无地区分布数据"></el-empty>
          </div>
          <template v-else>
            <div class="chart-row">
              <div ref="provinceChart" class="chart" style="height: 400px;"></div>
              <div v-if="selectedProvince && cityData" ref="cityChart" class="chart" style="height: 400px;"></div>
            </div>
          </template>
        </div>
      </el-card>
      
      <!-- 岗位类型分析 -->
      <el-card class="chart-card">
        <div slot="header">
          <span>岗位类型分析</span>
        </div>
        <div class="chart-container">
          <div v-if="!jobTypeData" class="empty-data">
            <el-empty description="暂无岗位类型数据"></el-empty>
          </div>
          <div v-else ref="jobTypeChart" class="chart"></div>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script>
import { mapGetters } from 'vuex'
import * as echarts from 'echarts'

export default {
  name: 'AnalysisView',
  
  data() {
    return {
      educationSalaryChartType: 'bar',
      selectedProvince: '',
      charts: {
        educationSalary: null,
        salary: null,
        province: null,
        city: null,
        jobType: null
      }
    }
  },
  
  computed: {
    ...mapGetters([
      'educationSalaryAnalysis',
      'salaryAnalysis',
      'locationAnalysis',
      'jobTypeAnalysis',
      'isLoading'
    ]),
    
    loading() {
      return this.isLoading
    },
    
    educationSalaryData() {
      return this.educationSalaryAnalysis
    },
    
    salaryData() {
      return this.salaryAnalysis
    },
    
    locationData() {
      return this.locationAnalysis
    },
    
    jobTypeData() {
      return this.jobTypeAnalysis
    },
    
    provinceOptions() {
      if (!this.locationData || !this.locationData.province) return []
      return this.locationData.province.categories.filter(p => p !== '其他')
    },
    
    cityData() {
      if (!this.locationData || !this.locationData.city || !this.selectedProvince) return null
      return this.locationData.city[this.selectedProvince]
    }
  },
  
  watch: {
    educationSalaryData() {
      this.$nextTick(() => {
        this.renderEducationSalaryChart()
      })
    },
    
    salaryData() {
      this.$nextTick(() => {
        this.renderSalaryChart()
      })
    },
    
    locationData() {
      this.$nextTick(() => {
        this.renderProvinceChart()
      })
    },
    
    jobTypeData() {
      this.$nextTick(() => {
        this.renderJobTypeChart()
      })
    },
    
    educationSalaryChartType() {
      this.$nextTick(() => {
        this.renderEducationSalaryChart()
      })
    },
    
    selectedProvince() {
      this.$nextTick(() => {
        if (this.selectedProvince && this.cityData) {
          this.renderCityChart()
        }
      })
    }
  },
  
  created() {
    this.fetchAnalysisData()
  },
  
  mounted() {
    // 窗口大小变化时重绘图表
    window.addEventListener('resize', this.resizeCharts)
  },
  
  beforeDestroy() {
    // 销毁事件监听和图表实例
    window.removeEventListener('resize', this.resizeCharts)
    Object.values(this.charts).forEach(chart => {
      if (chart) chart.dispose()
    })
  },
  
  methods: {
    fetchAnalysisData() {
      this.$store.dispatch('fetchAllAnalysisData')
    },
    
    resizeCharts() {
      Object.values(this.charts).forEach(chart => {
        if (chart) chart.resize()
      })
    },
    
    renderEducationSalaryChart() {
      if (!this.educationSalaryData || !this.$refs.educationSalaryChart) return
      
      if (this.charts.educationSalary) {
        this.charts.educationSalary.dispose()
      }
      
      this.charts.educationSalary = echarts.init(this.$refs.educationSalaryChart)
      
      let option = {}
      
      if (this.educationSalaryChartType === 'bar') {
        option = {
          title: {
            text: '不同学历要求的平均薪资(元/月)',
            left: 'center'
          },
          tooltip: {
            trigger: 'axis',
            axisPointer: {
              type: 'shadow'
            },
            formatter: function(params) {
              // 展示薪资和职位数量
              const data = params[0];
              return `${data.name}<br/>平均薪资: ${data.value}元/月<br/>职位数量: ${data.data.count}个`;
            }
          },
          grid: {
            left: '5%',
            right: '5%',
            bottom: '10%',
            containLabel: true
          },
          xAxis: {
            type: 'category',
            data: this.educationSalaryData.categories,
            axisLabel: {
              interval: 0,
              rotate: 30,
              fontSize: 12
            }
          },
          yAxis: {
            type: 'value',
            name: '平均薪资(元/月)'
          },
          series: [
            {
              name: '平均薪资',
              type: 'bar',
              data: this.educationSalaryData.categories.map((category, index) => ({
                value: this.educationSalaryData.data[index],
                count: this.educationSalaryData.counts ? this.educationSalaryData.counts[index] : 0
              })),
              itemStyle: {
                color: function(params) {
                  // 根据薪资高低设置不同颜色
                  const colorList = [
                    '#FF4500', '#FF6347', '#FF7F50', '#FF8C00', '#FFA500', 
                    '#FFB90F', '#FFC125', '#FFD700', '#FFEC8B', '#FFFACD'
                  ];
                  return colorList[params.dataIndex % colorList.length];
                }
              },
              label: {
                show: true,
                position: 'top',
                formatter: '{c}元'
              }
            }
          ]
        }
      } else {
        option = {
          title: {
            text: '不同学历要求的平均薪资(元/月)',
            left: 'center'
          },
          tooltip: {
            trigger: 'axis',
            formatter: function(params) {
              // 展示薪资和职位数量
              const data = params[0];
              return `${data.name}<br/>平均薪资: ${data.value}元/月<br/>职位数量: ${data.data.count}个`;
            }
          },
          grid: {
            left: '5%',
            right: '5%',
            bottom: '10%',
            containLabel: true
          },
          xAxis: {
            type: 'category',
            data: this.educationSalaryData.categories,
            axisLabel: {
              interval: 0,
              rotate: 30,
              fontSize: 12
            }
          },
          yAxis: {
            type: 'value',
            name: '平均薪资(元/月)'
          },
          series: [
            {
              name: '平均薪资',
              type: 'line',
              data: this.educationSalaryData.categories.map((category, index) => ({
                value: this.educationSalaryData.data[index],
                count: this.educationSalaryData.counts ? this.educationSalaryData.counts[index] : 0
              })),
              smooth: true,
              lineStyle: {
                width: 4,
                color: '#5470c6'
              },
              itemStyle: {
                borderWidth: 2
              },
              symbol: 'circle',
              symbolSize: 8,
              label: {
                show: true,
                position: 'top',
                formatter: '{c}元'
              }
            }
          ]
        }
      }
      
      this.charts.educationSalary.setOption(option)
    },
    
    renderSalaryChart() {
      if (!this.salaryData || !this.$refs.salaryChart) return
      
      if (this.charts.salary) {
        this.charts.salary.dispose()
      }
      
      this.charts.salary = echarts.init(this.$refs.salaryChart)
      
      const option = {
        title: {
          text: '薪资分布',
          left: 'center'
        },
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'shadow'
          }
        },
        xAxis: {
          type: 'category',
          data: this.salaryData.categories
        },
        yAxis: {
          type: 'value'
        },
        series: [
          {
            name: '职位数量',
            type: 'bar',
            data: this.salaryData.data,
            itemStyle: {
              color: '#67c23a'
            }
          }
        ]
      }
      
      this.charts.salary.setOption(option)
    },
    
    renderProvinceChart() {
      if (!this.locationData || !this.$refs.provinceChart) return
      
      if (this.charts.province) {
        this.charts.province.dispose()
      }
      
      this.charts.province = echarts.init(this.$refs.provinceChart)
      
      const option = {
        title: {
          text: '省份分布',
          left: 'center'
        },
        tooltip: {
          trigger: 'item',
          formatter: '{a} <br/>{b}: {c} ({d}%)'
        },
        legend: {
          orient: 'vertical',
          left: 'left',
          data: this.locationData.province.categories
        },
        series: [
          {
            name: '省份分布',
            type: 'pie',
            radius: '55%',
            center: ['50%', '60%'],
            data: this.locationData.province.categories.map((name, index) => ({
              value: this.locationData.province.data[index],
              name
            })),
            emphasis: {
              itemStyle: {
                shadowBlur: 10,
                shadowOffsetX: 0,
                shadowColor: 'rgba(0, 0, 0, 0.5)'
              }
            }
          }
        ]
      }
      
      this.charts.province.setOption(option)
      
      // 点击省份切换选中的省份
      this.charts.province.on('click', params => {
        if (params.name !== '其他') {
          this.selectedProvince = params.name
        }
      })
    },
    
    renderCityChart() {
      if (!this.cityData || !this.$refs.cityChart) return
      
      if (this.charts.city) {
        this.charts.city.dispose()
      }
      
      this.charts.city = echarts.init(this.$refs.cityChart)
      
      const option = {
        title: {
          text: `${this.selectedProvince}城市分布`,
          left: 'center'
        },
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'shadow'
          }
        },
        xAxis: {
          type: 'category',
          data: this.cityData.categories,
          axisLabel: {
            rotate: 45,
            interval: 0
          }
        },
        yAxis: {
          type: 'value'
        },
        series: [
          {
            name: '职位数量',
            type: 'bar',
            data: this.cityData.data,
            itemStyle: {
              color: '#409eff'
            }
          }
        ]
      }
      
      this.charts.city.setOption(option)
    },
    
    renderJobTypeChart() {
      if (!this.jobTypeData || !this.$refs.jobTypeChart) return
      
      if (this.charts.jobType) {
        this.charts.jobType.dispose()
      }
      
      this.charts.jobType = echarts.init(this.$refs.jobTypeChart)
      
      const option = {
        title: {
          text: '岗位类型分布',
          left: 'center'
        },
        tooltip: {
          trigger: 'item',
          formatter: '{a} <br/>{b}: {c} ({d}%)'
        },
        legend: {
          orient: 'vertical',
          left: 'left',
          data: this.jobTypeData.categories
        },
        series: [
          {
            name: '岗位类型',
            type: 'pie',
            radius: '55%',
            center: ['50%', '60%'],
            data: this.jobTypeData.categories.map((name, index) => ({
              value: this.jobTypeData.data[index],
              name
            })),
            emphasis: {
              itemStyle: {
                shadowBlur: 10,
                shadowOffsetX: 0,
                shadowColor: 'rgba(0, 0, 0, 0.5)'
              }
            }
          }
        ]
      }
      
      this.charts.jobType.setOption(option)
    }
  }
}
</script>

<style scoped>
.analysis-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.loading-container {
  padding: 20px;
}

.chart-card {
  margin-bottom: 20px;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chart-container {
  padding: 10px;
}

.chart {
  height: 400px;
}

.chart-row {
  display: flex;
  flex-wrap: wrap;
  margin: -10px;
}

.chart-row .chart {
  flex: 1;
  min-width: 300px;
  margin: 10px;
}

.empty-data {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 300px;
}
</style> 