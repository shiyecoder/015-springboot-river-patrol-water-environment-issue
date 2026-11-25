<template>
  <div class="page">
    <h1 class="page-title">整改跟踪</h1>
    <p class="page-sub">处置单位分阶段上报进度、处置人数、物资、费用与整改凭证</p>

    <div class="filter">
      <el-select v-model="q.status" placeholder="处置状态" clearable>
        <el-option label="处置中" value="处置中" />
        <el-option label="待复查" value="待复查" />
      </el-select>
      <el-input v-model="q.keyword" placeholder="问题编号或标题" clearable @keyup.enter="search" />
      <el-button type="primary" @click="search">查询</el-button>
      <el-button @click="reset">重置</el-button>
    </div>

    <div class="card" style="padding: 0">
      <el-table :data="rows" v-loading="loading">
        <el-table-column prop="code" label="问题编号" min-width="140" />
        <el-table-column prop="title" label="问题" min-width="230" show-overflow-tooltip />
        <el-table-column prop="sectionName" label="河段" min-width="170" />
        <el-table-column label="级别" width="80">
          <template #default="{ row }"><span :class="row.level === '重大' ? 'tag t-x' : 'tag t-5'">{{ row.level }}</span></template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }"><span class="tag" :class="statusClass(row.status)">{{ row.status }}</span></template>
        </el-table-column>
        <el-table-column prop="lastStage" label="当前阶段" min-width="170" />
        <el-table-column label="时限" min-width="170">
          <template #default="{ row }">
            <span :style="{ color: row.overdue ? '#b03035' : '#1f2d33' }">{{ fmt(row.deadline) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="open(row)">填报进度</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div style="display: flex; justify-content: flex-end; padding: 12px 16px">
        <el-pagination v-model:current-page="q.page" v-model:page-size="q.size" :total="total"
          :page-sizes="[10, 20, 50]" layout="total, sizes, prev, pager, next" @current-change="load" @size-change="search" />
      </div>
    </div>

    <el-drawer v-model="drawer" :title="'整改跟踪 · ' + cur.code" size="560px">
      <div v-if="cur.id">
        <div style="display: flex; gap: 8px; margin-bottom: 10px">
          <span class="tag" :class="statusClass(cur.status)">{{ cur.status }}</span>
          <span v-if="cur.supervise" class="tag t-x">督办</span>
          <span style="font-size: 12px; color: #8b9aa1">期限 {{ fmt(cur.deadline) }}</span>
        </div>
        <p style="font-size: 13px; margin: 0 0 12px">{{ cur.title }} · {{ cur.sectionName }}</p>

        <el-divider content-position="left">整改进度</el-divider>
        <el-timeline v-if="progress.length">
          <el-timeline-item v-for="p in progress" :key="p.id" :timestamp="fmt(p.progressTime)" color="#237A8B">
            <div style="font-size: 13px; font-weight: 500">{{ p.stage }}</div>
            <div style="font-size: 12px; color: #5f7078">{{ p.content }}</div>
            <div style="font-size: 12px; color: #8b9aa1">处置人数 {{ p.personCount }} · 费用 ¥{{ p.cost }} · {{ p.material }}</div>
            <div v-if="p.images" style="display: flex; gap: 6px; margin-top: 6px">
              <el-image v-for="(i, idx) in p.images.split(',')" :key="idx" :src="i" fit="cover"
                style="width: 84px; height: 64px; border-radius: 3px" :preview-src-list="p.images.split(',')" />
            </div>
          </el-timeline-item>
        </el-timeline>
        <div v-else class="empty-tip">尚未填报进度，请先接单并录入第一阶段</div>

        <template v-if="cur.status === '处置中'">
          <el-divider content-position="left">上报整改进度</el-divider>
          <el-form :model="form" label-width="100px">
            <el-form-item label="阶段" required>
              <el-select v-model="form.stage" style="width: 100%">
                <el-option v-for="s in stages" :key="s" :label="s" :value="s" />
              </el-select>
            </el-form-item>
            <el-form-item label="处置内容" required>
              <el-input v-model="form.content" type="textarea" :rows="3" placeholder="不少于 5 个字" />
            </el-form-item>
            <el-form-item label="处置人数"><el-input v-model="form.personCount" style="width: 160px" /></el-form-item>
            <el-form-item label="费用（元）"><el-input v-model="form.cost" style="width: 160px" /></el-form-item>
            <el-form-item label="物资使用"><el-input v-model="form.material" /></el-form-item>
            <el-form-item label="整改凭证">
              <el-upload :show-file-list="false" :http-request="upload" accept="image/*" multiple>
                <div style="display: flex; gap: 8px">
                  <img v-for="i in images" :key="i" :src="i" style="width: 90px; height: 68px; object-fit: cover; border-radius: 3px" />
                  <div style="width: 90px; height: 68px; border: 1px dashed #dce5e8; border-radius: 4px; display: flex; align-items: center; justify-content: center; color: #8b9aa1; font-size: 12px">＋ 上传</div>
                </div>
              </el-upload>
            </el-form-item>
          </el-form>
          <div style="display: flex; gap: 8px">
            <el-button type="primary" @click="save">提交进度</el-button>
            <el-button type="success" @click="submitResult">提交处置结果</el-button>
          </div>
        </template>
      </div>
    </el-drawer>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '../api'
import { fmt, statusClass } from '../utils'

const loading = ref(false)
const rows = ref([])
const total = ref(0)
const drawer = ref(false)
const cur = ref({})
const progress = ref([])
const images = ref([])
const stages = ['接单确认', '第一阶段：临时措施', '第二阶段：溯源排查', '第三阶段：整改实施', '第四阶段：提交结果']
const form = reactive({ stage: '第三阶段：整改实施', content: '', personCount: '8', cost: '0', material: '' })
const q = reactive({ page: 1, size: 10, status: '', keyword: '' })

async function load() {
  loading.value = true
  try {
    const d = await api.disposals(q)
    rows.value = d.records
    total.value = d.total
  } finally { loading.value = false }
}
function search() { q.page = 1; load() }
function reset() { Object.assign(q, { page: 1, status: '', keyword: '' }); load() }

async function open(row) {
  cur.value = row
  images.value = []
  Object.assign(form, { stage: '第三阶段：整改实施', content: '', personCount: '8', cost: '0', material: '' })
  progress.value = await api.progress(row.id)
  drawer.value = true
}

async function upload({ file }) {
  const d = await api.upload(file, 'disposal')
  images.value.push(d.path)
}

async function save() {
  if (form.content.trim().length < 5) return ElMessage.warning('处置内容不少于 5 个字')
  await api.addProgress({ ...form, issueId: cur.value.id, images: images.value.join(',') })
  ElMessage.success('进度已提交')
  progress.value = await api.progress(cur.value.id)
  images.value = []
  form.content = ''
  load()
}

async function submitResult() {
  await ElMessageBox.confirm('提交后进入待复查，是否确认？', '提交处置结果', { type: 'warning' })
  await api.transition(cur.value.id, { action: 'submitResult' })
  ElMessage.success('已提交，等待复查')
  drawer.value = false
  load()
}

onMounted(load)
</script>
