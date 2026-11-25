<template>
  <div class="page" v-loading="loading">
    <h1 class="page-title">巡查记录录入 · {{ task.code }}</h1>
    <p class="page-sub">{{ section.name }} · 巡查员 {{ assigneeName }} · 完成时限 {{ fmt(task.deadline) }} · 状态 {{ task.status }}</p>

    <div class="detail-grid">
      <div>
        <div class="card">
          <div class="card-hd">
            <h3>逐点现场情况</h3>
            <span class="hint">已录入 {{ records.length }} / {{ points.length }} 个点位</span>
          </div>
          <el-table :data="points" size="small">
            <el-table-column prop="sort" label="序号" width="60" />
            <el-table-column prop="name" label="点位" min-width="160" />
            <el-table-column prop="type" label="类型" width="110" />
            <el-table-column label="现场记录" min-width="140">
              <template #default="{ row }">
                <span v-if="recordOf(row.id)" class="tag t-4">已录入</span>
                <span v-else class="tag t-3">待录入</span>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="90">
              <template #default="{ row }">
                <el-button link type="primary" @click="pick(row)">录入</el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>

        <div class="card">
          <div class="card-hd"><h3>快速水质数据 · {{ currentPoint.name || '请选择点位' }}</h3><span class="hint">便携式检测仪读数</span></div>
          <el-form :model="form" label-width="110px" :disabled="task.status === '已完成'">
            <el-form-item label="pH">
              <el-input v-model="form.ph" style="width: 160px" placeholder="7.4" />
            </el-form-item>
            <el-form-item label="浊度 NTU">
              <el-input v-model="form.turbidity" style="width: 160px" placeholder="26.0" />
            </el-form-item>
            <el-form-item label="溶解氧 mg/L">
              <el-input v-model="form.dissolvedOxygen" style="width: 160px" placeholder="4.8" />
            </el-form-item>
            <el-form-item label="水质等级">
              <el-select v-model="form.level" style="width: 160px">
                <el-option v-for="l in ['Ⅱ类', 'Ⅲ类', 'Ⅳ类', 'Ⅴ类', '劣Ⅴ类']" :key="l" :label="l" :value="l" />
              </el-select>
            </el-form-item>
            <el-form-item label="现场照片">
              <el-upload :show-file-list="false" :http-request="doUpload" accept="image/*">
                <img v-if="form.image" :src="form.image" style="width: 120px; height: 90px; object-fit: cover; border-radius: 4px" />
                <el-button v-else size="small">上传照片</el-button>
              </el-upload>
            </el-form-item>
            <el-form-item label="备注">
              <el-input v-model="form.remark" type="textarea" :rows="2" style="width: 420px" />
            </el-form-item>
          </el-form>
          <div v-if="task.status !== '已完成'" style="display: flex; gap: 8px">
            <el-button type="primary" @click="saveRecord" :disabled="!currentPoint.id">保存该点位记录</el-button>
            <el-button type="success" @click="finish">提交并完成任务</el-button>
            <el-button @click="$router.push('/task')">返回列表</el-button>
          </div>
          <div v-else class="empty-tip">任务已完成，记录只读</div>
        </div>
      </div>

      <div>
        <div class="card">
          <div class="card-hd"><h3>任务摘要</h3></div>
          <dl class="kv">
            <dt>任务编号</dt><dd>{{ task.code }}</dd>
            <dt>河段</dt><dd>{{ section.code }} {{ section.name }}</dd>
            <dt>巡查路线</dt><dd>{{ section.patrolRoute }}</dd>
            <dt>点位数量</dt><dd>{{ points.length }} 个</dd>
            <dt>完成时限</dt><dd>{{ fmt(task.deadline) }}</dd>
            <dt>完成时间</dt><dd>{{ fmt(task.finishTime) }}</dd>
          </dl>
        </div>
        <div class="card">
          <div class="card-hd"><h3>已录入记录</h3><span class="hint">{{ records.length }} 条</span></div>
          <div v-if="!records.length" class="empty-tip">还没有录入记录</div>
          <el-timeline v-else>
            <el-timeline-item v-for="r in records" :key="r.id" :timestamp="fmt(r.recordTime)" color="#237A8B">
              <div style="font-size: 13px">pH {{ r.ph }} / 浊度 {{ r.turbidity }} / DO {{ r.dissolvedOxygen }}</div>
              <div style="font-size: 12px; color: #8b9aa1">{{ r.level }} · {{ r.remark }}</div>
            </el-timeline-item>
          </el-timeline>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import api from '../api'
import { fmt } from '../utils'

const route = useRoute()
const loading = ref(true)
const task = ref({})
const section = ref({})
const points = ref([])
const records = ref([])
const currentPoint = ref({})
const form = reactive({ pointId: '', ph: '7.4', turbidity: '26.0', dissolvedOxygen: '4.8', level: 'Ⅳ类', image: '', remark: '现场快速检测' })
const assigneeName = ref('')

const recordOf = id => records.value.find(r => r.pointId === id)

async function load() {
  loading.value = true
  try {
    const d = await api.task(route.params.id)
    task.value = d.task
    section.value = d.section || {}
    points.value = d.points || []
    records.value = d.records || []
    if (points.value.length) pick(points.value[0])
  } finally { loading.value = false }
}

function pick(p) {
  currentPoint.value = p
  form.pointId = p.id
  const rec = recordOf(p.id)
  if (rec) Object.assign(form, { ph: rec.ph, turbidity: rec.turbidity, dissolvedOxygen: rec.dissolvedOxygen, level: rec.level, image: rec.image, remark: rec.remark })
}

async function doUpload({ file }) {
  const d = await api.upload(file, 'water')
  form.image = d.path
}

async function saveRecord() {
  await api.recordTask(task.value.id, form)
  ElMessage.success('记录已保存')
  load()
}

async function finish() {
  if (!records.value.length) return ElMessage.warning('请先录入至少一个点位')
  await api.finishTask(task.value.id)
  ElMessage.success('任务已完成')
  load()
}

onMounted(load)
</script>
