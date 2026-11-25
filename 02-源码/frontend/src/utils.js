// 全局时间格式化：全系统统一调用，格式 yyyy-MM-dd HH:mm:ss
export function fmt(v) {
  if (!v) return '—'
  const d = new Date(String(v).replace(' ', 'T'))
  if (isNaN(d.getTime())) return String(v)
  const p = n => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())} ${p(d.getHours())}:${p(d.getMinutes())}:${p(d.getSeconds())}`
}

export function fmtDate(v) {
  return fmt(v).slice(0, 10)
}

// 状态 → 标签样式（不只用颜色，必须同时展示中文）
export const STATUS_CLASS = {
  待确认: 't-0', 待派单: 't-1', 处置中: 't-2', 待复查: 't-3', 已关闭: 't-4',
  无效上报: 't-5', 逾期: 't-x', 正常: 't-4', 预警: 't-3', 整治中: 't-2', 重点监管: 't-x',
  待执行: 't-1', 执行中: 't-0', 已完成: 't-4', 已逾期: 't-x', 启用: 't-4', 停用: 't-5'
}
export const statusClass = s => STATUS_CLASS[s] || 't-5'

export const ROLE_NAME = {
  admin: '管理员', dispatcher: '河长办调度员', patroller: '河道巡查员',
  handler: '处置单位人员', reviewer: '复查人员'
}

export const LEVEL_CLASS = { 高: 't-x', 中: 't-3', 低: 't-4' }

export function can(role, ...roles) {
  return roles.includes(role)
}
