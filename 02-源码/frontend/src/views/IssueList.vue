<template>
  <div class="page">
    <h1 class="page-title">{{ isDispatch ? '调度派单台' : '巡查问题单' }}</h1>
    <p class="page-sub">
      {{ isDispatch ? '研判问题级别、指定责任单位与协办单位，重大问题自动建立督办' : '巡查员现场上报，状态流转全部由后端校验并留痕' }}
    </p>

    <el-tabs v-model="q.tab" @tab-change="search">
      <el-tab-pane label="全部" name="" />
      <el-tab-pane label="待办" name="todo" />
      <el-tab-pane label="处理中" name="doing" />
      <el-tab-pane label="已完成" name="done" />
      <el-tab-pane label="异常" name="abnormal" />
    </el-tabs>

    <div class="filter">
      <el-select v-model="q.status" placeholder="处置状态" clearable>
        <el-option v-for="s in ['待确认', '待派单', '处置中', '待复查', '已关闭', '无效上报']" :key="s" :label="s" :value="s" />
      </el-select>
      <el-select v-model="q.type" placeholder="问题类型" clearable>
        <el-option v-for="t in types" :key="t" :label="t" :value="t" />
      </el-select>
      <el-select v-model="q.level" placeholder="问题级别" clearable>
        <el-option label="重大" value="重大" />
        <el-option label="一般" value="一般" />
      </el-select>
      <el-input v-model="q.keyword" placeholder="编号或标题" clearable @keyup.enter="search" />
      <el-button type="primary" @click="search">查询</el-button>
      <el-button @click="reset">重置</el-button>
      <el-button v-if="canReport" style="margin-left: auto" @click="openReport">问题上报</el-button>
    </div>

    <div class="card" style="padding: 0">
      <el-table :data="rows" v-loading="loading">
        <el-table-column prop="code" label="编号" min-width="140" />
        <el-table-column label="证据" width="90">
          <template #default="{ row }">
            <el-image :src="(row.image || '').split(',')[0]" fit="cover"
              style="width: 60px; height: 45px; border-radius: 3px" :preview-src-list="[row.image]" />
          </template>
        </el-table-column>
        <el-table-column prop="title" label="问题标题" min-width="230" show-overflow-tooltip />
        <el-table-column prop="sectionName" label="河段" min-width="170" show-overflow-tooltip />
        <el-table-column prop="issueType" label="类型" width="110" />
        <el-table-column label="级别" width="80">
          <template #default="{ row }">
            <span :class="row.level === '重大' ? 'tag t-x' : 'tag t-5'">{{ row.level }}</span>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }"><span class="tag" :class="statusClass(row.status)">{{ row.status }}</span></template>
        </el-table-column>
        <el-table-column label="上报时间" min-width="170">
          <template #default="{ row }">{{ row.reportTime }}</template>
        </el-table-column>
        <el-table-column label="时限" width="100">
          <template #default="{ row }">
            <span v-if="row.overdue" class="tag t-x">已逾期</span>
            <span v-else style="font-size: 12px; color: #5f7078">正常</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="130" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="openDetail(row)">查看</el-button>
            <el-button v-if="isDispatch && row.status === '待派单' && canDispatch" link type="primary" @click="openDispatch(row)">派单</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div style="display: flex; justify-content: flex-end; padding: 12px 16px">
        <el-pagination v-model:current-page="q.page" v-model:page-size="q.size" :total="total"
          :page-sizes="[10, 20, 50]" layout="total, sizes, prev, pager, next" @current-change="load" @size-change="search" />
      </div>
    </div>

    <!-- 上报 -->
    <el-drawer v-model="reportDrawer" title="问题上报" size="560px" :before-close="checkDirty">
      <el-form :model="report" label-width="100px">
        <el-form-item label="所属河段" required>
          <el-select v-model="report.sectionId" filterable style="width: 100%" @change="checkDuplicate">
            <el-option v-for="s in sections" :key="s.id" :label="`${s.code} ${s.name}`" :value="s.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="问题类型" required>
          <el-select v-model="report.issueType" style="width: 100%" @change="checkDuplicate">
            <el-option v-for="t in types" :key="t" :label="t" :value="t" />
          </el-select>
        </el-form-item>
        <el-form-item label="问题级别" required>
          <el-radio-group v-model="report.level">
            <el-radio label="一般">一般</el-radio>
            <el-radio label="重大">重大</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="问题标题" required><el-input v-model="report.title" maxlength="80" /></el-form-item>
        <el-form-item label="问题描述" required>
          <el-input v-model="report.description" type="textarea" :rows="3" placeholder="不少于 5 个字，描述现象、程度与初步判断" />
        </el-form-item>
        <el-form-item label="影响范围" required>
          <el-input v-model="report.impactScope" type="textarea" :rows="2" />
        </el-form-item>
        <el-form-item label="证据图片">
          <el-upload :show-file-list="false" :http-request="uploadEvidence" accept="image/*">
            <div style="display: flex; gap: 8px">
              <img v-for="i in evidence" :key="i" :src="i" style="width: 96px; height: 72px; object-fit: cover; border-radius: 3px" />
              <div style="width: 96px; height: 72px; border: 1px dashed #dce5e8; border-radius: 4px; display: flex; align-items: center; justify-content: center; color: #8b9aa1; font-size: 12px">＋ 上传</div>
            </div>
          </el-upload>
        </el-form-item>
      </el-form>

      <el-alert v-if="dups.length" type="warning" :closable="false" style="margin-bottom: 12px">
        <template #title>重复上报提醒：该河段近 30 天有 {{ dups.length }} 条同类未关闭问题</template>
        <div v-for="d in dups" :key="d.id" style="font-size: 12px">{{ d.code }} · {{ d.issueType }} · {{ d.status }} · {{ d.title }}</div>
      </el-alert>

      <template #footer>
        <el-button @click="reportDrawer = false">取消</el-button>
        <el-button type="primary" @click="submitReport">提交上报</el-button>
      </template>
    </el-drawer>

    <!-- 详情 -->
    <el-drawer v-model="detailDrawer" :title="cur.code + ' ' + (cur.title || '')" size="620px">
      <div v-if="detail.issue">
        <div style="display: flex; gap: 8px; margin-bottom: 12px">
          <span class="tag" :class="statusClass(detail.issue.status)">{{ detail.issue.status }}</span>
          <span class="tag" :class="detail.issue.level === '重大' ? 't-x' : 't-5'">{{ detail.issue.level }}</span>
          <span v-if="detail.issue.supervise" class="tag t-x">督办</span>
          <span style="font-size: 12px; color: #8b9aa1">要求完成 {{ fmt(detail.issue.deadline) }}</span>
        </div>
        <dl class="kv" style="margin-bottom: 12px">
          <dt>所属河段</dt><dd>{{ detail.section?.code }} {{ detail.section?.name }}</dd>
          <dt>问题类型</dt><dd>{{ detail.issue.issueType }}</dd>
          <dt>上报人</dt><dd>{{ detail.reporter?.realName }} · {{ fmt(detail.issue.reportTime) }}</dd>
          <dt>问题描述</dt><dd>{{ detail.issue.description }}</dd>
          <dt>影响范围</dt><dd>{{ detail.issue.impactScope }}</dd>
          <dt>临时措施</dt><dd>{{ detail.issue.tempMeasure || '—' }}</dd>
        </dl>
        <div v-if="detail.issue.image" style="display: flex; gap: 8px; margin-bottom: 12px">
          <el-image v-for="(i, idx) in detail.issue.image.split(',')" :key="idx" :src="i" fit="cover"
            style="width: 120px; height: 90px; border-radius: 4px" :preview-src-list="detail.issue.image.split(',')" />
        </div>

        <el-divider content-position="left">处置进度</el-divider>
        <el-timeline v-if="detail.progress?.length">
          <el-timeline-item v-for="p in detail.progress" :key="p.id" :timestamp="fmt(p.progressTime)" color="#237A8B">
            <div style="font-size: 13px; font-weight: 500">{{ p.stage }}</div>
            <div style="font-size: 12px; color: #5f7078">{{ p.content }}</div>
            <div style="font-size: 12px; color: #8b9aa1">人数 {{ p.personCount }} · 费用 ¥{{ p.cost }}</div>
          </el-timeline-item>
        </el-timeline>
        <div v-else class="empty-tip">暂无处置进度</div>

        <el-divider content-position="left">操作记录</el-divider>
        <el-timeline>
          <el-timeline-item v-for="l in detail.logs || []" :key="l.id" :timestamp="fmt(l.createTime)" size="normal">
            <div style="font-size: 13px">{{ l.action }} <span v-if="l.afterStatus">→ {{ l.afterStatus }}</span></div>
            <div style="font-size: 12px; color: #8b9aa1">{{ l.username }}<span v-if="l.reason"> · {{ l.reason }}</span></div>
          </el-timeline-item>
        </el-timeline>

        <div v-if="actions.length" class="card" style="margin-top: 12px">
          <div class="card-hd"><h3>可执行操作</h3><span class="hint">后端校验角色与状态</span></div>
          <div style="display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 10px">
            <el-button v-for="a in actions" :key="a.key" size="small" :type="a.type || 'default'" @click="doAction(a)">{{ a.label }}</el-button>
          </div>
          <div v-if="pendingAction">
            <el-alert :title="pendingAction.tip" type="info" :closable="false" style="margin-bottom: 10px" />
            <el-input v-model="actionForm.reason" type="textarea" :rows="2" placeholder="原因（驳回/无效上报不少于 5 个字）" />
            <div v-if="pendingAction.key === 'dispatch'" style="margin-top: 10px">
              <el-select v-model="actionForm.deptId" placeholder="责任单位" style="width: 100%; margin-bottom: 8px">
                <el-option v-for="d in depts" :key="d.id" :label="d.name" :value="d.id" />
              </el-select>
              <el-input v-model="actionForm.days" placeholder="处置期限（天）" style="margin-bottom: 8px" />
              <el-input v-model="actionForm.tempMeasure" type="textarea" :rows="2" placeholder="临时措施（重大问题必填）" />
            </div>
            <div style="margin-top: 10px; text-align: right">
              <el-button size="small" @click="pendingAction = null">取消</el-button>
              <el-button size="small" type="primary" @click="confirmAction">确认提交</el-button>
            </div>
          </div>
        </div>
      </div>
    </el-drawer>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '../api'
import { fmt, statusClass } from '../utils'

const props = defineProps({ mode: { type: String, default: '' } })
const isDispatch = computed(() => props.mode === 'dispatch')
const user = JSON.parse(localStorage.getItem('user') || '{}')
const role = user.roleCode
const canReport = ['patroller', 'dispatcher', 'admin'].includes(role)
const canDispatch = ['dispatcher', 'admin'].includes(role)

const types = ['水面漂浮物', '岸线垃圾', '非法排放', '设施损坏', '水色异常']
const loading = ref(false)
const rows = ref([])
const total = ref(0)
const sections = ref([])
const depts = ref([])
const dups = ref([])
const evidence = ref([])
const q = reactive({ page: 1, size: 10, tab: '', status: isDispatch.value ? '待派单' : '', type: '', level: '', keyword: '' })

const reportDrawer = ref(false)
const report = ref({ level: '一般' })
const detailDrawer = ref(false)
const cur = ref({})
const detail = ref({})
const actions = ref([])
const pendingAction = ref(null)
const actionForm = reactive({ reason: '', deptId: '', days: '3', tempMeasure: '' })

async function load() {
  loading.value = true
  try {
    const d = await api.issues(q)
    rows.value = d.records
    total.value = d.total
  } finally { loading.value = false }
}
function search() { q.page = 1; load() }
function reset() {
  Object.assign(q, { page: 1, tab: '', status: '', type: '', level: '', keyword: '' })
  load()
}

async function openReport() {
  report.value = { level: '一般', issueType: '岸线垃圾', title: '', description: '', impactScope: '' }
  evidence.value = []
  dups.value = []
  reportDrawer.value = true
  if (!sections.value.length) sections.value = await api.sectionOptions()
}
function checkDirty(done) { done() }

async function checkDuplicate() {
  if (!report.value.sectionId || !report.value.issueType) return
  dups.value = await api.duplicates({ sectionId: report.value.sectionId, type: report.value.issueType })
}

async function uploadEvidence({ file }) {
  const d = await api.upload(file, 'issue')
  evidence.value.push(d.path)
}

async function submitReport() {
  if (!report.value.sectionId || !report.value.title) return ElMessage.warning('请填写河段与标题')
  if ((report.value.description || '').length < 5) return ElMessage.warning('问题描述不少于 5 个字')
  if (!report.value.impactScope) return ElMessage.warning('请填写影响范围')
  await api.createIssue({ ...report.value, image: evidence.value.join(',') })
  ElMessage.success('问题已提交，进入待确认')
  reportDrawer.value = false
  load()
}

function computeActions(issue) {
  const s = issue.status
  const list = []
  if (s === '待确认' && canDispatch) {
    list.push({ key: 'submit', label: '提交研判', tip: '提交后进入待派单' })
    list.push({ key: 'invalid', label: '标记无效上报', tip: '需填写不少于 5 个字的原因' })
  }
  if (s === '待派单' && canDispatch) {
    list.push({ key: 'dispatch', label: '派发处置', tip: '派单后责任单位可填报整改进度；重大问题必须填写临时措施' })
  }
  if (s === '处置中' && ['handler', 'admin'].includes(role)) {
    list.push({ key: 'submitResult', label: '提交处置结果', tip: '需先填报整改进度，提交后进入待复查' })
  }
  if (s === '待复查' && ['reviewer', 'admin'].includes(role)) {
    list.push({ key: 'pass', label: '复查通过并关闭', tip: '关闭后如需复发处置请关联新单，不改历史', type: 'success' })
    list.push({ key: 'reject', label: '驳回继续整改', tip: '驳回需填写不少于 5 个字的原因', type: 'danger' })
  }
  return list
}

async function openDetail(row) {
  cur.value = row
  detail.value = await api.issue(row.id)
  actions.value = computeActions(detail.value.issue)
  pendingAction.value = null
  Object.assign(actionForm, { reason: '', deptId: '', days: '3', tempMeasure: '' })
  detailDrawer.value = true
  if (!depts.value.length) depts.value = await api.depts()
}

function openDispatch(row) { openDetail(row).then(() => doAction({ key: 'dispatch', tip: '指派责任单位与完成期限' })) }

function doAction(a) {
  pendingAction.value = a
  if (a.key === 'pass') actionForm.reason = ''
}

async function confirmAction() {
  const a = pendingAction.value
  if (['reject', 'invalid'].includes(a.key) && actionForm.reason.trim().length < 5) {
    return ElMessage.warning('原因不少于 5 个字')
  }
  if (a.key === 'dispatch' && !actionForm.deptId) return ElMessage.warning('请选择责任单位')
  await ElMessageBox.confirm(`确认执行「${a.label}」？`, '操作确认', { type: 'warning' })
  await api.transition(cur.value.id, { action: a.key, ...actionForm })
  ElMessage.success('操作成功')
  pendingAction.value = null
  detail.value = await api.issue(cur.value.id)
  actions.value = computeActions(detail.value.issue)
  load()
}

onMounted(load)
</script>
