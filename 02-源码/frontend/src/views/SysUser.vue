<template>
  <div class="page">
    <h1 class="page-title">用户与权限</h1>
    <p class="page-sub">菜单、按钮、数据范围三层权限；管理员可为角色分配菜单</p>

    <el-tabs v-model="tab">
      <el-tab-pane label="用户管理" name="user">
        <div class="filter">
          <el-input v-model="q.keyword" placeholder="姓名或账号" clearable @keyup.enter="loadUsers" />
          <el-select v-model="q.roleCode" placeholder="角色" clearable @change="loadUsers">
            <el-option v-for="r in roles" :key="r.code" :label="r.name" :value="r.code" />
          </el-select>
          <el-button type="primary" @click="loadUsers">查询</el-button>
          <el-button v-if="isAdmin" style="margin-left: auto" @click="openUser()">新增用户</el-button>
        </div>
        <div class="card" style="padding: 0">
          <el-table :data="users" v-loading="loading">
            <el-table-column prop="username" label="账号" min-width="120" />
            <el-table-column label="头像" width="80">
              <template #default="{ row }">
                <img v-if="row.avatar" :src="row.avatar" class="avatar-img" alt="头像" />
                <span v-else class="avatar-img" style="display: inline-flex; align-items: center; justify-content: center">{{ row.realName?.slice(0, 1) }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="realName" label="姓名" width="110" />
            <el-table-column prop="roleName" label="角色" min-width="140" />
            <el-table-column prop="deptName" label="部门" min-width="140" />
            <el-table-column prop="phone" label="联系方式" min-width="130" />
            <el-table-column label="状态" width="90">
              <template #default="{ row }"><span class="tag" :class="row.status === 1 ? 't-4' : 't-5'">{{ row.status === 1 ? '启用' : '停用' }}</span></template>
            </el-table-column>
            <el-table-column label="最近登录" min-width="170">
              <template #default="{ row }">{{ fmt(row.lastLogin) }}</template>
            </el-table-column>
            <el-table-column v-if="isAdmin" label="操作" width="190" fixed="right">
              <template #default="{ row }">
                <el-button link type="primary" @click="openUser(row)">编辑</el-button>
                <el-button link type="primary" @click="toggle(row)">{{ row.status === 1 ? '停用' : '启用' }}</el-button>
                <el-button link type="primary" @click="reset(row)">重置密码</el-button>
              </template>
            </el-table-column>
          </el-table>
          <div style="display: flex; justify-content: flex-end; padding: 12px 16px">
            <el-pagination v-model:current-page="q.page" v-model:page-size="q.size" :total="total"
              :page-sizes="[10, 20, 50]" layout="total, sizes, prev, pager, next" @current-change="loadUsers" />
          </div>
        </div>
      </el-tab-pane>

      <el-tab-pane label="角色管理" name="role">
        <div class="detail-grid">
          <div class="card" style="padding: 0">
            <el-table :data="roles" @row-click="pickRole" highlight-current-row>
              <el-table-column prop="name" label="角色名称" min-width="150" />
              <el-table-column prop="code" label="编码" min-width="120" />
              <el-table-column prop="dataScope" label="数据范围" width="110" />
              <el-table-column prop="remark" label="说明" min-width="200" />
            </el-table>
          </div>
          <div class="card">
            <div class="card-hd"><h3>为角色分配菜单 · {{ curRole.name || '请选择角色' }}</h3></div>
            <el-tree ref="treeRef" :data="menuTree" show-checkbox node-key="id" :props="{ label: 'name', children: 'children' }" default-expand-all />
            <div style="margin-top: 12px; text-align: right">
              <el-button @click="loadRoleMenus">重置</el-button>
              <el-button type="primary" :disabled="!isAdmin || !curRole.id" @click="saveRoleMenus">保存授权</el-button>
            </div>
          </div>
        </div>
      </el-tab-pane>

      <el-tab-pane label="菜单管理" name="menu">
        <div class="card" style="padding: 0">
          <el-table :data="menus">
            <el-table-column prop="id" label="ID" width="70" />
            <el-table-column prop="name" label="菜单名称" min-width="180" />
            <el-table-column prop="path" label="路由地址" min-width="180" />
            <el-table-column prop="perm" label="权限标识" min-width="160" />
            <el-table-column label="类型" width="80">
              <template #default="{ row }">{{ row.type === 'M' ? '菜单' : '按钮' }}</template>
            </el-table-column>
            <el-table-column label="可见" width="80">
              <template #default="{ row }">{{ row.visible === 1 ? '显示' : '隐藏' }}</template>
            </el-table-column>
            <el-table-column prop="sort" label="排序" width="80" />
          </el-table>
        </div>
      </el-tab-pane>

      <el-tab-pane label="部门管理" name="dept">
        <div class="card" style="padding: 0">
          <el-table :data="depts">
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column prop="name" label="部门名称" min-width="220" />
            <el-table-column prop="parentId" label="上级部门" width="120" />
            <el-table-column prop="sort" label="排序" width="100" />
          </el-table>
        </div>
      </el-tab-pane>

      <el-tab-pane label="操作日志" name="log">
        <div class="filter">
          <el-input v-model="logQuery.bizNo" placeholder="业务编号" clearable @keyup.enter="loadLogs" />
          <el-button type="primary" @click="loadLogs">查询</el-button>
        </div>
        <div class="card" style="padding: 0">
          <el-table :data="logs" v-loading="loading">
            <el-table-column prop="createTime" label="时间" min-width="170" />
            <el-table-column prop="username" label="操作人" width="110" />
            <el-table-column prop="module" label="模块" width="110" />
            <el-table-column prop="action" label="操作" min-width="130" />
            <el-table-column prop="bizNo" label="业务编号" min-width="140" />
            <el-table-column label="状态变化" min-width="160">
              <template #default="{ row }">{{ row.beforeStatus || '—' }} → {{ row.afterStatus || '—' }}</template>
            </el-table-column>
            <el-table-column prop="reason" label="原因" min-width="200" show-overflow-tooltip />
          </el-table>
          <div style="display: flex; justify-content: flex-end; padding: 12px 16px">
            <el-pagination v-model:current-page="logQuery.page" :page-size="10" :total="logTotal"
              layout="total, prev, pager, next" @current-change="loadLogs" />
          </div>
        </div>
      </el-tab-pane>
    </el-tabs>

    <el-dialog v-model="userDialog" :title="userForm.id ? '编辑用户' : '新增用户'" width="480px">
      <el-form :model="userForm" label-width="90px">
        <el-form-item label="账号" required><el-input v-model="userForm.username" :disabled="!!userForm.id" /></el-form-item>
        <el-form-item label="姓名" required><el-input v-model="userForm.realName" /></el-form-item>
        <el-form-item label="角色" required>
          <el-select v-model="userForm.roleCode" style="width: 100%">
            <el-option v-for="r in roles" :key="r.code" :label="r.name" :value="r.code" />
          </el-select>
        </el-form-item>
        <el-form-item label="部门">
          <el-select v-model="userForm.deptId" style="width: 100%">
            <el-option v-for="d in depts" :key="d.id" :label="d.name" :value="d.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="联系方式"><el-input v-model="userForm.phone" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="userDialog = false">取消</el-button>
        <el-button type="primary" @click="saveUser">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '../api'
import { fmt } from '../utils'

const props = defineProps({ tab: { type: String, default: 'user' } })
const tab = ref(props.tab)
const user = JSON.parse(localStorage.getItem('user') || '{}')
const isAdmin = user.roleCode === 'admin'
const loading = ref(false)
const users = ref([])
const total = ref(0)
const roles = ref([])
const menus = ref([])
const depts = ref([])
const logs = ref([])
const logTotal = ref(0)
const menuTree = ref([])
const curRole = ref({})
const treeRef = ref(null)
const userDialog = ref(false)
const userForm = ref({})
const q = reactive({ page: 1, size: 10, keyword: '', roleCode: '' })
const logQuery = reactive({ page: 1, bizNo: '' })

async function loadUsers() {
  loading.value = true
  try {
    const d = await api.users(q)
    users.value = d.records
    total.value = d.total
  } finally { loading.value = false }
}

async function loadLogs() {
  const d = await api.logs(logQuery)
  logs.value = d.records
  logTotal.value = d.total
}

function openUser(row) {
  userForm.value = row ? { ...row } : { roleCode: 'patroller' }
  userDialog.value = true
}

async function saveUser() {
  if (!userForm.value.username || !userForm.value.realName) return ElMessage.warning('请填写账号与姓名')
  await api.saveUser(userForm.value)
  ElMessage.success('已保存')
  userDialog.value = false
  loadUsers()
}

async function toggle(row) {
  await api.toggleUser(row.id)
  ElMessage.success('状态已更新')
  loadUsers()
}

async function reset(row) {
  await ElMessageBox.confirm(`确认重置 ${row.realName} 的密码为 admin123？`, '重置密码', { type: 'warning' })
  await api.resetUser(row.id)
  ElMessage.success('密码已重置')
}

async function pickRole(row) {
  curRole.value = row
  await loadRoleMenus()
}

async function loadRoleMenus() {
  if (!curRole.value.id) return
  const ids = await api.roleMenus(curRole.value.id)
  treeRef.value?.setCheckedKeys(ids)
}

async function saveRoleMenus() {
  const ids = treeRef.value.getCheckedKeys().concat(treeRef.value.getHalfCheckedKeys())
  await api.assignMenus(curRole.value.id, ids)
  ElMessage.success('授权已保存，重新登录后生效')
}

function buildTree(list, parent = 0) {
  return list.filter(m => m.parentId === parent).map(m => ({
    id: m.id, name: m.name, children: buildTree(list, m.id)
  }))
}

onMounted(async () => {
  loadUsers()
  roles.value = await api.roles()
  menus.value = await api.menus()
  menuTree.value = buildTree(menus.value)
  depts.value = await api.sysDepts()
  loadLogs()
  if (tab.value === 'role' && roles.value.length) pickRole(roles.value[0])
})
</script>
