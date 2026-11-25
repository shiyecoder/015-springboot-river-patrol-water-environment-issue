<template>
  <div class="app">
    <aside class="side">
      <div class="brand"><span class="dot"></span>水环境巡查处置平台</div>
      <nav>
        <template v-for="g in groups" :key="g.name">
          <div v-if="g.showTitle" class="grp">{{ g.name }}</div>
          <router-link v-for="m in g.items" :key="m.path" :to="m.path" class="item"
                       :class="{ on: isActive(m.path) }">
            <el-icon><component :is="iconOf(m.icon)" /></el-icon>{{ m.name }}
          </router-link>
        </template>
      </nav>
    </aside>

    <div class="main">
      <header class="top">
        <div class="crumb">河道巡查 / <b>{{ currentTitle }}</b></div>
        <div class="right">
          <span class="role">{{ roleName }}</span>
          <el-popover placement="bottom-end" :width="340" trigger="click">
            <template #reference>
              <span class="msg">消息 <i v-if="unread" class="badge">{{ unread }}</i></span>
            </template>
            <div class="msg-list">
              <div v-if="!messages.length" class="empty-tip">暂无未读消息</div>
              <div v-for="m in messages" :key="m.id" class="msg-item" @click="openMsg(m)">
                <div class="mt">{{ m.title }}</div>
                <div class="mc">{{ m.content }}</div>
                <div class="md">{{ m.createTime }}</div>
              </div>
            </div>
          </el-popover>
          <el-dropdown @command="onCommand">
            <span class="user">
              <img v-if="user.avatar" class="avatar-img" :src="user.avatar" alt="头像" />
              <span v-else class="avatar">{{ (user.realName || 'U').slice(0, 1) }}</span>
              {{ user.realName }}
              <el-icon><ArrowDown /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">个人中心</el-dropdown-item>
                <el-dropdown-item command="logout" divided>退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </header>
      <main class="content"><router-view :key="$route.fullPath" /></main>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '../api'
import { ROLE_NAME } from '../utils'
import {
  DataBoard, Compass, Tickets, Warning, Promotion, EditPen, Search, DataAnalysis,
  Setting, User, Bell, ArrowDown
} from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const user = ref(JSON.parse(localStorage.getItem('user') || '{}'))
const rawMenus = ref(JSON.parse(localStorage.getItem('menus') || '[]'))
const messages = ref([])
const unread = ref(0)

// 主菜单按业务分组，子页面（隐藏菜单）不进入导航
const GROUP_MAP = {
  水环境热点看板: '工作台', 河道档案: '河道档案', 巡查管理: '巡查管理', 问题上报: '问题处置',
  调度派单: '问题处置', 整改跟踪: '问题处置', 复核销号: '问题处置', 热点分析: '统计分析', 系统管理: '系统管理'
}

const groups = computed(() => {
  const list = []
  for (const m of rawMenus.value) {
    if (!m.path || m.visible === 0) continue
    const name = GROUP_MAP[m.name] || '其他'
    let g = list.find(x => x.name === name)
    if (!g) { g = { name, items: [] }; list.push(g) }
    // /sys 是目录节点（无对应页面），只呈现其子菜单
    if (m.path !== '/sys') g.items.push({ path: m.path, name: m.name, icon: m.icon })
    for (const c of m.children || []) {
      if (c.visible === 0 || !c.path) continue
      g.items.push({ path: c.path, name: c.name, icon: c.icon })
    }
  }
  // 分组标题与唯一菜单同名时不重复展示标题
  return list.filter(g => g.items.length).map(g => ({
    ...g, showTitle: !(g.items.length === 1 && g.items[0].name === g.name)
  }))
})

const roleName = computed(() => ROLE_NAME[user.value.roleCode] || '用户')
const currentTitle = computed(() => route.meta.title || '工作台')
const isActive = p => route.path === p || route.path.startsWith(p + '/')

const ICONS = {
  dashboard: DataBoard, river: Compass, point: Compass, task: Tickets, water: Tickets,
  issue: Warning, dispatch: Promotion, disposal: EditPen, review: Search,
  chart: DataAnalysis, rule: Setting, user: User, role: Setting, menu: Setting, msg: Bell
}
const iconOf = k => ICONS[k] || Tickets

async function loadMessages() {
  messages.value = await api.messages({ onlyUnread: 1 })
  unread.value = messages.value.length
}

function openMsg(m) {
  api.readMessage(m.id).then(() => {
    if (m.bizNo && m.bizNo.startsWith('WT')) router.push('/issue')
    loadMessages()
  })
}

async function onCommand(cmd) {
  if (cmd === 'profile') return router.push('/profile')
  if (cmd === 'logout') {
    localStorage.clear()
    router.replace('/login')
  }
}

onMounted(async () => {
  loadMessages()
  try {
    const data = await api.info()
    user.value = data.user
    localStorage.setItem('user', JSON.stringify(data.user))
    localStorage.setItem('menus', JSON.stringify(data.menus))
    rawMenus.value = data.menus
  } catch (e) { /* 拦截器已提示 */ }
})
</script>

<style scoped>
.app { display: flex; min-height: 100vh; }
.side { width: 220px; background: #15344a; flex-shrink: 0; display: flex; flex-direction: column; }
.brand { height: 56px; display: flex; align-items: center; gap: 8px; padding: 0 16px; color: #fff; font-size: 14px; font-weight: 600; border-bottom: 1px solid rgba(255,255,255,.1); }
.dot { width: 8px; height: 8px; border-radius: 50%; background: #57c4c9; }
.side nav { padding: 10px 8px; overflow: auto; }
.grp { font-size: 11px; color: rgba(255,255,255,.45); padding: 12px 10px 6px; letter-spacing: 1px; }
.item { display: flex; align-items: center; gap: 10px; height: 38px; padding: 0 10px; border-radius: 4px; color: rgba(255,255,255,.82); font-size: 13px; margin-bottom: 2px; }
.item:hover { background: rgba(255,255,255,.08); color: #fff; }
.item.on { background: rgba(255,255,255,.14); color: #fff; font-weight: 500; box-shadow: inset 2px 0 0 #57c4c9; }
.main { flex: 1; min-width: 0; display: flex; flex-direction: column; }
.top { height: 56px; background: #fff; border-bottom: 1px solid var(--r-border); display: flex; align-items: center; justify-content: space-between; padding: 0 24px; flex-shrink: 0; }
.crumb { font-size: 13px; color: var(--r-sub); }
.crumb b { color: var(--r-text); font-weight: 500; }
.right { display: flex; align-items: center; gap: 18px; font-size: 13px; color: var(--r-sub); }
.role { background: #e8f1f3; color: #15344a; padding: 3px 8px; border-radius: 3px; font-size: 12px; }
.msg { cursor: pointer; position: relative; }
.badge { position: absolute; top: -6px; right: -12px; background: #b03035; color: #fff; font-size: 10px; border-radius: 8px; padding: 0 4px; font-style: normal; }
.user { display: flex; align-items: center; gap: 6px; cursor: pointer; color: var(--r-text); }
.avatar { width: 30px; height: 30px; border-radius: 50%; background: #dde8ea; color: #15344a; display: flex; align-items: center; justify-content: center; font-weight: 600; font-size: 12px; }
.msg-list { max-height: 360px; overflow: auto; }
.msg-item { padding: 8px 4px; border-bottom: 1px solid #eef3f4; cursor: pointer; }
.msg-item .mt { font-size: 13px; font-weight: 500; }
.msg-item .mc { font-size: 12px; color: var(--r-sub); margin: 2px 0; }
.msg-item .md { font-size: 11px; color: var(--r-muted); }
.content { flex: 1; overflow: auto; }
</style>
