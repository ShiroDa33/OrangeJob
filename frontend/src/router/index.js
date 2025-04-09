import Vue from 'vue'
import VueRouter from 'vue-router'

Vue.use(VueRouter)

// 路由懒加载
const Home = () => import('../views/Home.vue')
const JobList = () => import('../views/JobList.vue')
const JobDetail = () => import('../views/JobDetail.vue')
const Analysis = () => import('../views/Analysis.vue')
const NotFound = () => import('../views/NotFound.vue')

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home,
    meta: { title: '首页 - 橙子就业' }
  },
  {
    path: '/jobs',
    name: 'JobList',
    component: JobList,
    meta: { title: '职位列表 - 橙子就业' }
  },
  {
    path: '/jobs/:id',
    name: 'JobDetail',
    component: JobDetail,
    meta: { title: '职位详情 - 橙子就业' }
  },
  {
    path: '/analysis',
    name: 'Analysis',
    component: Analysis,
    meta: { title: '数据分析 - 橙子就业' }
  },
  {
    path: '*',
    name: 'NotFound',
    component: NotFound,
    meta: { title: '页面未找到 - 橙子就业' }
  }
]

const router = new VueRouter({
  mode: 'history',
  base: process.env.BASE_URL,
  routes
})

// 全局前置守卫，修改页面标题
router.beforeEach((to, from, next) => {
  if (to.meta.title) {
    document.title = to.meta.title
  }
  next()
})

export default router 