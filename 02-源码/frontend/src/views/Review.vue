<template>
  <div class="page">
    <h1 class="page-title">复核销号</h1>
    <p class="page-sub">复查人员现场重新记录水色、气味与水质指标，合格关闭，不合格驳回继续整改</p>

    <div class="filter">
      <el-select v-model="q.status" placeholder="复核状态" clearable>
        <el-option label="待复查" value="待复查" />
        <el-option label="已关闭" value="已关闭" />
      </el-select>
      <el-button type="primary" @click="search">查询</el-button>
      <el-button @click="reset">重置</el-button>
    </div>

    <div class="card" style="padding: 0">
      <el-table :data="rows" v-loading="loading">
        <el-table-column prop="code" label="问题编号" min-width="140" />
        <el-table-column prop="title" label="问题" min-width="240" show-overflow-tooltip />
        <el-table-column prop="sectionName" label="河段" min-width="170" />
        <el-table-column label="级别" width="80">
          <template #default="{ row }"><span :class="row.level === '重大' ? 'tag t-x' : 'tag t-5'">{{ row.level }}</span></template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }"><span class="tag" :class="statusClass(row.status)">{{ row.status }}</span></template>
        </el-table-column>
        <el-table-column label="处置完成时间" min-width="170">
          <template #default="{ row }">{{ fmt(row.disposeTime) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="open(row)">{{ row.status === '待复查' ? '复核' : '查看' }}</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div style="display: flex; justify-content: flex-end; padding: 12px 16px">
        <el-pagination v-model:current-page="q.page" v-model:page-size="q.size" :total="total"
          :page-sizes="[10, 20, 50]" layout="total, sizes, prev, pager, next" @current-change="load" @size-change="search" />
      </div>
    </div>

    <el-drawer v-model="drawer" :title="'复核销号 · ' + cur.code" size="680px">
      <div v-if="cur.id" class="detail-grid" style="grid-template-columns: 1fr 1fr">
        <div>
          <div class="card">
            <div class="card-hd"><h3>处置结果对照</h3><span class="hint">派单要求与实际上报</span></div>
            <el-table :data="cur.progress" size="small">
              <el-table-column prop="stage" label="阶段" min-width="130" />
              <el-table-column prop="content" label="内容" min-width="200" show-overflow-tooltip />
              <el-table-column prop="personCount" label="人数" width="70" />
            </el-table>
          </div>

          <div class="card" v-if="cur.status === '待复查'">
            <div class="card-hd"><h3>现场复核记录</h3><span class="hint">复查人不可为原处置人</span></div>
            <el-form :model="form" label-width="90px">
              <el-form-item label="现场水色">
                <el-select v-model="form.waterColor" style="width: 160px">
                  <el-option label="正常" value="正常" /><el-option label="轻微异常" value="轻微异常" />
                </el-select>
              </el-form-item>
              <el-form-item label="气味">
                <el-select v-model="form.smell" style="width: 160px">
                  <el-option label="无" value="无" /><el-option label="轻微" value="轻微" />
                </el-select>
              </el-form-item>
              <el-form-item label="pH"><el-input v-model="form.ph" style="width: 120px" /></el-form-item>
              <el-form-item label="浊度"><el-input v-model="form.turbidity" style="width: 120px" /></el-form-item>
              <el-form-item label="溶解氧"><el-input v-model="form.dissolvedOxygen" style="width: 120px" /></el-form-item>
              <el-form-item label="复核结论" required>
                <el-input v-model="form.conclusion" type="textarea" :rows="2" placeholder="不少于 5 个字" />
              </el-form-item>
              <el-form-item label="现场照片">
                <el-upload :show-file-list="false" :http-request="upload" accept="image/*">
                  <div style="display: flex; gap: 6px">
                    <img v-for="i in images" :key="i" :src="i" style="width: 84px; height: 62px; object-fit: cover; border-radius: 3px" />
                    <div style="width: 84px; height: 62px; border: 1px dashed #dce5e8; border-radius: 4px; display: flex; align-items: center; justify-content: center; color: #8b9aa1; font-size: 12px">＋</div>
                  </div>
                </el-upload>
              </el-form-item>
            </el-form>
            <div style="display: flex; gap: 8px">
              <el-button type="primary" @click="submit(true)">通过并关闭</el-button>
              <el-button type="danger" plain @click="submit(false)">驳回继续整改</el-button>
            </div>
            <div style="font-size: 12px; color: #8b9aa1; margin-top: 8px">驳回需填写不少于 5 个字的原因，原因填在复核结论中即可</div>
          </div>
        </div>

        <div>
          <div class="card" style="border-color: #b9cbd2">
            <div class="card-hd"><h3>问题复发热点识别</h3><span class="hint">{{ cur.score?.ruleVersion || '—' }}</span></div>
            <template v-if="cur.score">
              <div style="display: flex; align-items: baseline; gap: 10px; margin-bottom: 8px">
                <span class="num" style="font-size: 30px; font-weight: 600; color: #15344a">{{ cur.score.totalScore }}</span>
                <span class="tag" :class="levelClass(cur.score.manualLevel || cur.score.level)">{{ cur.score.manualLevel || cur.score.level }}</span>
                <span style="font-size: 11px; color: #8b9aa1">阈值 高≥75 / 中≥50</span>
              </div>
              <div style="font-size: 12px; color: #5f7078; margin-bottom: 8px">{{ cur.score.factors }}</div>
              <el-table :data="scoreDetail" size="small">
                <el-table-column prop="name" label="因素" min-width="100" />
                <el-table-column prop="weight" label="权重" width="70" />
                <el-table-column prop="score" label="得分" width="70" />
              </el-table>
              <div style="font-size: 12px; color: #8b9aa1; margin-top: 8px">推荐：{{ cur.score.recommend }}</div>
              <div style="font-size: 12px; color: #8b9aa1">未满足：{{ cur.score.unmet || '无' }}</div>
              <div style="font-size: 12px; color: #8b9aa1">改进项：{{ cur.score.suggestions }}</div>

              <el-divider />
              <el-form label-width="80px">
                <el-form-item label="人工调整">
                  <el-select v-model="adjust.level" style="width: 160px">
                    <el-option label="维持系统结果" :value="cur.score.level" />
                    <el-option label="调整为高" value="高" />
                    <el-option label="调整为中" value="中" />
                    <el-option label="调整为低" value="低" />
                  </el-select>
                </el-form-item>
                <el-form-item label="原因">
                  <el-input v-model="adjust.reason" placeholder="不少于 5 个字" />
                </el-form-item>
              </el-form>
              <el-button size="small" type="primary" @click="saveAdjust">保存调整</el-button>
              <span style="font-size: 11px; color: #8b9aa1; margin-left: 8px">原始计算结果不会被覆盖</span>
            </template>
            <div v-else class="empty-tip">该断面暂无计算结果，可在热点分析页发起计算</div>
          </div>

          <div class="card">
            <div class="card-hd"><h3>历史复查</h3></div>
            <el-timeline v-if="cur.reviews?.length">
              <el-timeline-item v-for="r in cur.reviews" :key="r.id" :timestamp="fmt(r.reviewTime)"
                :color="r.pass ? '#2d7a58' : '#b03035'">
                <div style="font-size: 13px">{{ r.pass ? '复查通过' : '复查驳回' }}</div>
                <div style="font-size: 12px; color: #5f7078">{{ r.conclusion }}</div>
              </el-timeline-item>
            </el-timeline>
            <div v-else class="empty-tip">暂无复查记录</div>
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
import { fmt, statusClass, LEVEL_CLASS } from '../utils'

const loading = ref(false)
const rows = ref([])
const total = ref(0)
const drawer = ref(false)
const cur = ref({})
const images = ref([])
const form = reactive({ waterColor: '正常', smell: '无', ph: '7.2', turbidity: '18.0', dissolvedOxygen: '5.6', conclusion: '' })
const adjust = reactive({ level: '', reason: '' })
const q = reactive({ page: 1, size: 10, status: '' })
const levelClass = lv => LEVEL_CLASS[lv] || 't-5'

const scoreDetail = computed(() => {
  const s = cur.value.score
  if (!s) return []
  return [
    { name: '河段位置', weight: '15%', score: s.scorePosition },
    { name: '问题类型', weight: '20%', score: s.scoreType },
    { name: '近90天次数', weight: '25%', score: s.scoreCount },
    { name: '处置时长', weight: '15%', score: s.scoreDuration },
    { name: '复核结果', weight: '15%', score: s.scoreReview },
    { name: '水质变化', weight: '10%', score: s.scoreQuality }
  ]
})

async function load() {
  loading.value = true
  try {
    const d = await api.reviews(q)
    rows.value = d.records
    total.value = d.total
  } finally { loading.value = false }
}
function search() { q.page = 1; load() }
function reset() { q.status = ''; q.page = 1; load() }

async function open(row) {
  cur.value = row
  images.value = []
  adjust.level = row.score?.level || ''
  adjust.reason = ''
  Object.assign(form, { waterColor: '正常', smell: '无', ph: '7.2', turbidity: '18.0', dissolvedOxygen: '5.6', conclusion: '' })
  drawer.value = true
}

async function upload({ file }) {
  const d = await api.upload(file, 'review')
  images.value.push(d.path)
}

async function submit(pass) {
  if (form.conclusion.trim().length < 5) return ElMessage.warning('复核结论不少于 5 个字')
  await ElMessageBox.confirm(pass ? '确认复查通过并关闭该问题？' : '确认驳回，退回处置单位继续整改？', '复核确认',
    { type: pass ? 'success' : 'warning' })
  await api.submitReview({ ...form, issueId: cur.value.id, pass, reason: pass ? '' : form.conclusion, images: images.value.join(',') })
  ElMessage.success(pass ? '已关闭' : '已驳回')
  drawer.value = false
  load()
}

async function saveAdjust() {
  if (!cur.value.score) return
  if (adjust.reason.trim().length < 5) return ElMessage.warning('调整原因不少于 5 个字')
  await api.adjustScore(cur.value.score.id, { level: adjust.level, reason: adjust.reason })
  ElMessage.success('已保存人工调整')
  load()
}

onMounted(load)
</script>
