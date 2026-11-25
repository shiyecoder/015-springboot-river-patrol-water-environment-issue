import { createRouter, createWebHistory } from 'vue-router'

// 路由与后端菜单 path 对齐；hidden 路由不在菜单显示
const routes = [
  { path: '/login', component: () => import('./views/Login.vue'), meta: { public: true } },
  {
    path: '/',
    component: () => import('./views/Layout.vue'),
    redirect: '/dashboard',
    children: [
      { path: 'dashboard', component: () => import('./views/Dashboard.vue'), meta: { title: '水环境热点看板' } },
      { path: 'section', component: () => import('./views/SectionList.vue'), meta: { title: '河道断面' } },
      { path: 'section/:id', component: () => import('./views/SectionDetail.vue'), meta: { title: '断面详情', hidden: true } },
      { path: 'task', component: () => import('./views/TaskList.vue'), meta: { title: '计划任务' } },
      { path: 'task/:id/execute', component: () => import('./views/TaskExecute.vue'), meta: { title: '巡查记录录入', hidden: true } },
      { path: 'issue', component: () => import('./views/IssueList.vue'), meta: { title: '问题上报' } },
      { path: 'dispatch', component: () => import('./views/IssueList.vue'), meta: { title: '调度派单', props: { mode: 'dispatch' } } },
      { path: 'disposal', component: () => import('./views/Disposal.vue'), meta: { title: '整改跟踪' } },
      { path: 'review', component: () => import('./views/Review.vue'), meta: { title: '复核销号' } },
      { path: 'hotspot', component: () => import('./views/Hotspot.vue'), meta: { title: '热点分析' } },
      { path: 'rule', component: () => import('./views/Hotspot.vue'), meta: { title: '规则配置', props: { tab: 'rule' } } },
      { path: 'sys/user', component: () => import('./views/SysUser.vue'), meta: { title: '用户管理' } },
      { path: 'sys/role', component: () => import('./views/SysUser.vue'), meta: { title: '角色管理', props: { tab: 'role' } } },
      { path: 'sys/menu', component: () => import('./views/SysUser.vue'), meta: { title: '菜单管理', props: { tab: 'menu' } } },
      { path: 'sys/dept', component: () => import('./views/SysUser.vue'), meta: { title: '部门管理', props: { tab: 'dept' } } },
      { path: 'profile', component: () => import('./views/Profile.vue'), meta: { title: '个人中心', hidden: true } }
    ]
  }
]

const router = createRouter({ history: createWebHistory(), routes })

router.beforeEach((to) => {
  if (to.meta.public) return true
  if (!localStorage.getItem('token')) return '/login'
  return true
})

export default router
