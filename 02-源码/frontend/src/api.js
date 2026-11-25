import axios from 'axios'
import { ElMessage } from 'element-plus'

// 统一 axios 封装：自动带 token，统一错误提示，401 回登录页
const http = axios.create({ baseURL: '/api', timeout: 20000 })

http.interceptors.request.use(cfg => {
  const token = localStorage.getItem('token')
  if (token) cfg.headers.Authorization = 'Bearer ' + token
  return cfg
})

http.interceptors.response.use(
  res => {
    const body = res.data
    if (body && typeof body.code !== 'undefined' && body.code !== 200) {
      ElMessage.error(body.msg || '请求失败')
      if (body.code === 401) {
        localStorage.clear()
        location.href = '/login'
      }
      return Promise.reject(new Error(body.msg))
    }
    return body.data
  },
  err => {
    const msg = err.response?.data?.msg || err.message || '网络异常'
    ElMessage.error(msg)
    return Promise.reject(err)
  }
)

export const api = {
  login: data => http.post('/auth/login', data),
  info: () => http.get('/auth/info'),
  dashboard: () => http.get('/dashboard/overview'),
  sections: params => http.get('/section/page', { params }),
  sectionOptions: () => http.get('/section/options'),
  rivers: () => http.get('/section/rivers'),
  section: id => http.get(`/section/${id}`),
  saveSection: data => (data.id ? http.put(`/section/${data.id}`, data) : http.post('/section', data)),
  tasks: params => http.get('/task/page', { params }),
  task: id => http.get(`/task/${id}`),
  createTask: data => http.post('/task', data),
  recordTask: (id, data) => http.post(`/task/${id}/record`, data),
  finishTask: id => http.post(`/task/${id}/finish`),
  issues: params => http.get('/issue/page', { params }),
  issue: id => http.get(`/issue/${id}`),
  createIssue: data => http.post('/issue', data),
  duplicates: params => http.get('/issue/duplicate', { params }),
  transition: (id, data) => http.post(`/issue/${id}/transition`, data),
  issueCounts: () => http.get('/issue/counts'),
  depts: () => http.get('/issue/depts'),
  disposals: params => http.get('/disposal/page', { params }),
  progress: issueId => http.get(`/disposal/${issueId}`),
  addProgress: data => http.post('/disposal', data),
  reviews: params => http.get('/review/page', { params }),
  submitReview: data => http.post('/review', data),
  hotspotList: params => http.get('/hotspot/list', { params }),
  hotspotStats: () => http.get('/hotspot/stats'),
  evaluate: id => http.post(`/hotspot/evaluate/${id}`),
  adjustScore: (id, data) => http.post(`/hotspot/${id}/adjust`, data),
  rules: () => http.get('/hotspot/rules'),
  saveRule: data => http.post('/hotspot/rules', data),
  users: params => http.get('/sys/user/page', { params }),
  saveUser: data => http.post('/sys/user', data),
  toggleUser: id => http.post(`/sys/user/${id}/status`),
  resetUser: id => http.post(`/sys/user/${id}/reset`),
  roles: () => http.get('/sys/role/list'),
  roleMenus: id => http.get(`/sys/role/${id}/menus`),
  assignMenus: (id, ids) => http.put(`/sys/role/${id}/menus`, ids),
  menus: () => http.get('/sys/menu/list'),
  sysDepts: () => http.get('/sys/dept/list'),
  logs: params => http.get('/sys/log/page', { params }),
  messages: params => http.get('/message/list', { params }),
  readMessage: id => http.post(`/message/${id}/read`),
  profile: () => http.get('/profile'),
  updateProfile: data => http.put('/profile', data),
  changePassword: data => http.put('/profile/password', data),
  upload: (file, biz = 'common') => {
    const fd = new FormData()
    fd.append('file', file)
    return http.post(`/upload?biz=${biz}`, fd, { headers: { 'Content-Type': 'multipart/form-data' } })
  }
}

export default api
