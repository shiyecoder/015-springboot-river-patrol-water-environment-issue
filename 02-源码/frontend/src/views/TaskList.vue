<template>
  <div class="page">
    <h1 class="page-title">巡查计划任务</h1>
    <p class="page-sub">按河段、周期、人员自动生成，支持特殊天气后的临时任务；逾期自动标记</p>

    <div class="filter">
      <el-select v-model="q.taskType" placeholder="任务类型" clearable>
        <el-option label="周期任务" value="周期任务" />
        <el-option label="临时任务" value="临时任务" />
      </el-select>
      <el-select v-model="q.status" placeholder="任务状态" clearable>
        <el-option v-for="s in ['待执行', '执行中', '已完成', '已逾期']" :key="s" :label="s" :value="s" />
      </el-select>
      <el-input v-model="q.keyword" placeholder="任务编号或名称" clearable @keyup.enter="search" />
      <el-button type="primary" @click="search">查询</el-button>
      <el-button @click="reset">重置</el-button>
      <el-button v-if="canCreate" style="margin-left: auto" @click="openCreate">新建临时任务</el-button>
    </div>

    <div class="card" style="padding: 0">
      <el-table :data="rows" v-loading="loading">
        <el-table-column prop="code" label="任务编号" min-width="140" />
        <el-table-column prop="title" label="任务名称" min-width="220" />
        <el-table-column prop="sectionName" label="河段" min-width="170" />
        <el-table-column prop="taskType" label="类型" width="100" />
        <el-table-column prop="cycleType" label="周期" min-width="110" />
        <el-table-column prop="assigneeName" label="巡查员" width="100" />
        <el-table-column label="完成时限" min-width="170">
          <template #default="{ row }">{{ fmt(row.deadline) }}</template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <span class="tag" :class="statusClass(row.overdue && row.status !== '已完成' ? '已逾期' : row.status)">
              {{ row.overdue && row.status !== '已完成' ? '已逾期' : row.status }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button v-if="row.status !== '已完成'" link type="primary" @click="$router.push(`/task/${row.id}/execute`)">
              {{ row.status === '待执行' ? '去巡查' : '录入' }}
            </el-button>
            <el-button v-else link type="primary" @click="$router.push(`/task/${row.id}/execute`)">查看</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div style="display: flex; justify-content: flex-end; padding: 12px 16px">
        <el-pagination v-model:current-page="q.page" v-model:page-size="q.size" :total="total"
          :page-sizes="[10, 20, 50]" layout="total, sizes, prev, pager, next" @current-change="load" @size-change="search" />
      </div>
    </div>

    <el-drawer v-model="drawer" title="新建临时任务" size="480px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="任务名称" required><el-input v-model="form.title" /></el-form-item>
        <el-form-item label="所属河段" required>
          <el-select v-model="form.sectionId" filterable style="width: 100%">
            <el-option v-for="s in sections" :key="s.id" :label="`${s.code} ${s.name}`" :value="s.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="巡查员" required>
          <el-select v-model="form.assigneeId" style="width: 100%">
            <el-option v-for="u in patrollers" :key="u.id" :label="u.realName" :value="u.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="完成时限">
          <el-date-picker v-model="form.deadline" type="datetime" style="width: 100%" value-format="YYYY-MM-DD HH:mm:ss" />
        </el-form-item>
        <el-form-item label="备注"><el-input v-model="form.remark" type="textarea" :rows="2" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="drawer = false">取消</el-button>
        <el-button type="primary" @click="save">创建</el-button>
      </template>
    </el-drawer>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import api from '../api'
import { fmt, statusClass } from '../utils'

const loading = ref(false)
const rows = ref([])
const total = ref(0)
const drawer = ref(false)
const sections = ref([])
const patrollers = ref([])
const form = ref({ taskType: '临时任务', remark: '特殊天气后加密巡查' })
const user = JSON.parse(localStorage.getItem('user') || '{}')
const canCreate = computed(() => ['admin', 'dispatcher'].includes(user.roleCode))

const q = reactive({ page: 1, size: 10, status: '', taskType: '', keyword: '' })

async function load() {
  loading.value = true
  try {
    const d = await api.tasks(q)
    rows.value = d.records
    total.value = d.total
  } finally { loading.value = false }
}
function search() { q.page = 1; load() }
function reset() { Object.assign(q, { page: 1, status: '', taskType: '', keyword: '' }); load() }

async function openCreate() {
  form.value = { taskType: '临时任务', remark: '特殊天气后加密巡查', deadline: '' }
  drawer.value = true
  if (!sections.value.length) sections.value = await api.sectionOptions()
  if (!patrollers.value.length) {
    const d = await api.users({ page: 1, size: 50, roleCode: 'patroller' })
    patrollers.value = d.records
  }
}

async function save() {
  if (!form.value.title || !form.value.sectionId || !form.value.assigneeId) return ElMessage.warning('请填写必填项')
  await api.createTask(form.value)
  ElMessage.success('临时任务已创建')
  drawer.value = false
  load()
}

onMounted(load)
</script>
