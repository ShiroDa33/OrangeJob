<template>
  <div id="app">
    <el-container>
      <el-header>
        <div class="header-container">
          <div class="logo">
            <span class="orange-color">橙子就业</span>
            <span class="subtitle">就业信息分析平台</span>
          </div>
          <el-menu
            :default-active="activeIndex"
            class="main-menu"
            mode="horizontal"
            router
            background-color="#ffffff"
            text-color="#303133"
            active-text-color="#ff9900"
          >
            <el-menu-item index="/">首页</el-menu-item>
            <el-menu-item index="/jobs">职位列表</el-menu-item>
            <el-menu-item index="/analysis">数据分析</el-menu-item>
          </el-menu>
        </div>
      </el-header>
      
      <el-main>
        <router-view/>
      </el-main>
      
      <el-footer>
        <div class="footer-content">
          <p>© 2025 橙子就业 - 就业信息分析平台</p>
        </div>
      </el-footer>
    </el-container>
  </div>
</template>

<script>
export default {
  name: 'App',
  data() {
    return {
      activeIndex: '/'
    }
  },
  watch: {
    $route: {
      immediate: true,
      handler(to) {
        this.activeIndex = to.path;
      }
    }
  }
}
</script>

<style>
.el-header {
  background-color: #ffffff;
  color: #333;
  line-height: 60px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
}

.header-container {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logo {
  font-size: 24px;
  font-weight: bold;
  display: flex;
  align-items: center;
}

.subtitle {
  font-size: 16px;
  font-weight: normal;
  margin-left: 10px;
  color: #909399;
}

.main-menu {
  border-bottom: none;
}

.el-main {
  background-color: #f0f2f5;
  min-height: calc(100vh - 120px);
}

.el-footer {
  background-color: #ffffff;
  padding: 20px;
  box-shadow: 0 -1px 4px rgba(0, 0, 0, 0.08);
}

.footer-content {
  text-align: center;
  color: #909399;
}
</style> 