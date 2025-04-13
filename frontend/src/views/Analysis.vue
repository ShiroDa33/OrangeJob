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
        <div slot="header" class="chart-header">
          <span>岗位类型分析</span>
          <el-tooltip content="点击岗位类型可查看薪资趋势" placement="top">
            <el-button size="small" type="text" icon="el-icon-info">提示</el-button>
          </el-tooltip>
        </div>
        <div class="chart-container">
          <div v-if="!jobTypeData" class="empty-data">
            <el-empty description="暂无岗位类型数据"></el-empty>
          </div>
          <div v-else ref="jobTypeChart" class="chart"></div>
        </div>
      </el-card>
      
      <!-- 岗位类型薪资趋势分析（新增） -->
      <el-card v-if="jobTypeSalaryTrend" class="chart-card">
        <div slot="header" class="chart-header">
          <span>{{ jobTypeSalaryTrend.job_type }} 薪资趋势分析</span>
          <el-button size="small" type="text" @click="clearJobTypeSalaryTrend">关闭</el-button>
        </div>
        <div class="chart-container">
          <div v-if="!jobTypeSalaryTrend.salary_trend || jobTypeSalaryTrend.salary_trend.length === 0" class="empty-data">
            <el-empty description="暂无薪资趋势数据"></el-empty>
          </div>
          <div v-else ref="salaryTrendChart" class="chart" style="height: 400px;"></div>
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
        jobType: null,
        salaryTrend: null
      }
    }
  },
  
  computed: {
    ...mapGetters([
      'educationSalaryAnalysis',
      'salaryAnalysis',
      'locationAnalysis',
      'jobTypeAnalysis',
      'isLoading',
      'jobTypeSalaryTrend',
      'selectedJobType'
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
    },
    
    jobTypeSalaryTrend() {
      this.$nextTick(() => {
        // 先确保其他图表重新渲染
        this.renderEducationSalaryChart()
        this.renderSalaryChart()
        this.renderProvinceChart()
        this.renderJobTypeChart()
        
        // 如果有城市数据，重新渲染城市图表
        if (this.selectedProvince && this.cityData) {
          this.renderCityChart()
        }
        
        // 最后渲染薪资趋势图表
        if (this.jobTypeSalaryTrend && this.jobTypeSalaryTrend.salary_trend && this.jobTypeSalaryTrend.salary_trend.length > 0) {
          this.renderSalaryTrendChart()
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
    
    // 确保所有DOM已渲染后初始化图表
    this.$nextTick(() => {
      // 等待数据加载完成后渲染图表
      if (!this.loading) {
        this.renderAllCharts()
      }
    })
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
        .then(() => {
          // 数据加载完成后渲染所有图表
          this.renderAllCharts()
        })
    },
    
    // 新增：渲染所有图表的方法
    renderAllCharts() {
      this.renderEducationSalaryChart()
      this.renderSalaryChart()
      this.renderProvinceChart() 
      this.renderJobTypeChart()
      
      if (this.selectedProvince && this.cityData) {
        this.renderCityChart()
      }
      
      if (this.jobTypeSalaryTrend && this.jobTypeSalaryTrend.salary_trend && this.jobTypeSalaryTrend.salary_trend.length > 0) {
        this.renderSalaryTrendChart()
      }
    },
    
    resizeCharts() {
      Object.values(this.charts).forEach(chart => {
        if (chart) chart.resize()
      })
    },
    
    renderEducationSalaryChart() {
      // 确保数据和DOM元素都存在
      if (!this.educationSalaryData || !this.$refs.educationSalaryChart || !this.$refs.educationSalaryChart.offsetHeight) {
        return
      }
      
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
      // 确保数据和DOM元素都存在
      if (!this.salaryData || !this.$refs.salaryChart || !this.$refs.salaryChart.offsetHeight) {
        return
      }
      
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
      // 确保数据和DOM元素都存在
      if (!this.locationData || !this.$refs.provinceChart || !this.$refs.provinceChart.offsetHeight) {
        return
      }
      
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
      // 确保数据和DOM元素都存在
      if (!this.cityData || !this.$refs.cityChart || !this.$refs.cityChart.offsetHeight) {
        return
      }
      
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
      // 确保数据和DOM元素都存在
      if (!this.jobTypeData || !this.$refs.jobTypeChart || !this.$refs.jobTypeChart.offsetHeight) {
        return
      }
      
      const { categories, data } = this.jobTypeData
      
      // 清理旧图表
      if (this.charts.jobType) {
        this.charts.jobType.dispose()
      }
      
      // 创建新图表
      this.charts.jobType = echarts.init(this.$refs.jobTypeChart)
      
      // 图表配置
      const option = {
        title: {
          text: '岗位类型分布',
          left: 'center'
        },
        tooltip: {
          trigger: 'item',
          formatter: '{a} <br/>{b} : {c} ({d}%)'
        },
        legend: {
          orient: 'vertical',
          left: 'left',
          data: categories
        },
        series: [
          {
            name: '岗位数量',
            type: 'pie',
            radius: '55%',
            center: ['50%', '60%'],
            data: categories.map((name, index) => ({
              name,
              value: data[index]
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
      
      // 设置图表选项
      this.charts.jobType.setOption(option)
      
      // 添加点击事件处理
      this.charts.jobType.on('click', (params) => {
        this.handleJobTypeClick(params.name)
      })
    },
    
    // 处理岗位类型点击
    handleJobTypeClick(jobType) {
      this.$store.dispatch('fetchJobTypeSalaryTrend', jobType)
    },
    
    // 清除岗位类型薪资趋势数据
    clearJobTypeSalaryTrend() {
      // 先清除状态
      this.$store.commit('SET_JOB_TYPE_SALARY_TREND', null)
      this.$store.commit('SET_SELECTED_JOB_TYPE', null)
      
      // 清除薪资趋势图表
      if (this.charts.salaryTrend) {
        this.charts.salaryTrend.dispose()
        this.charts.salaryTrend = null
      }
      
      // 确保其他图表仍然显示
      this.$nextTick(() => {
        this.renderEducationSalaryChart()
        this.renderSalaryChart()
        this.renderProvinceChart()
        this.renderJobTypeChart()
        
        if (this.selectedProvince && this.cityData) {
          this.renderCityChart()
        }
      })
    },
    
    // 渲染薪资趋势图表（新增）
    renderSalaryTrendChart() {
      // 确保数据和DOM元素都存在
      if (!this.jobTypeSalaryTrend || !this.$refs.salaryTrendChart || !this.$refs.salaryTrendChart.offsetHeight) {
        return
      }
      
      // 准备数据
      const { salary_trend, predictions } = this.jobTypeSalaryTrend
      
      // 分离真实数据和模拟数据
      const realData = salary_trend.filter(item => item.is_real)
      
      // 所有历史数据（包括真实和模拟）
      const dates = salary_trend.map(item => item.date)
      const salaries = salary_trend.map(item => item.average_salary)
      const counts = salary_trend.map(item => item.count)
      
      // 真实数据点
      const realDates = realData.map(item => item.date)
      const realSalaries = realData.map(item => item.average_salary)
      
      // 预测数据
      const predictionDates = predictions.map(item => item.date)
      const predictionSalaries = predictions.map(item => item.predicted_salary)
      
      // 合并日期轴（历史+预测）
      const allDates = [...dates, ...predictionDates]
      
      // 清理旧图表
      if (this.charts.salaryTrend) {
        this.charts.salaryTrend.dispose()
      }
      
      // 创建新图表
      this.charts.salaryTrend = echarts.init(this.$refs.salaryTrendChart)
      
      // 图表配置
      const option = {
        title: {
          text: `${this.jobTypeSalaryTrend.job_type} 薪资趋势及预测`,
          subtext: '注意：历史数据部分基于当前薪资模拟生成',
          left: 'center'
        },
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'cross',
            label: {
              backgroundColor: '#6a7985'
            }
          },
          formatter: function(params) {
            let result = params[0].name + '<br/>';
            
            // 添加所有系列数据
            params.forEach(param => {
              // 添加标记如果是模拟数据
              let isMock = param.seriesName === '历史薪资' && 
                           !realDates.includes(param.name);
              
              let value = param.value;
              if (value !== '-') {
                result += param.marker + param.seriesName + ': ' + value;
                if (isMock) {
                  result += ' (模拟数据)';
                }
                result += '<br/>';
              }
            });
            
            return result;
          }
        },
        legend: {
          data: ['历史薪资', '职位数量', '薪资预测', '真实数据点'],
          bottom: 10
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '15%',
          top: '15%',
          containLabel: true
        },
        xAxis: [
          {
            type: 'category',
            boundaryGap: false,
            data: allDates,
            axisLabel: {
              rotate: 45
            }
          }
        ],
        yAxis: [
          {
            type: 'value',
            name: '薪资（元/月）',
            position: 'left'
          },
          {
            type: 'value',
            name: '职位数量',
            position: 'right'
          }
        ],
        series: [
          {
            name: '历史薪资',
            type: 'line',
            // 不设置stack属性以避免堆叠
            areaStyle: {
              opacity: 0.3
            },
            emphasis: {
              focus: 'series'
            },
            lineStyle: {
              width: 2
            },
            data: salaries,
            z: 1
          },
          {
            name: '职位数量',
            type: 'bar',
            yAxisIndex: 1,
            emphasis: {
              focus: 'series'
            },
            data: counts,
            itemStyle: {
              color: '#91cc75',
              opacity: 0.6
            },
            z: 0
          },
          {
            name: '薪资预测',
            type: 'line',
            // 不设置stack以避免堆叠
            areaStyle: {
              opacity: 0.3,
              color: '#fac858'
            },
            emphasis: {
              focus: 'series'
            },
            lineStyle: {
              type: 'dashed',
              width: 2,
              color: '#ff9900'
            },
            itemStyle: {
              color: '#ff9900'
            },
            data: Array(dates.length).fill('-').concat(predictionSalaries),
            z: 2
          },
          {
            name: '真实数据点',
            type: 'scatter',
            symbolSize: 10,
            itemStyle: {
              color: '#ee6666'
            },
            data: realDates.map((date, index) => {
              return [date, realSalaries[index]];
            }),
            z: 3
          }
        ]
      }
      
      // 设置图表选项
      this.charts.salaryTrend.setOption(option)
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
  gap: 20px;
}

.chart-row .chart {
  flex: 1;
  min-width: 300px;
}

.empty-data {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 300px;
}
</style> 