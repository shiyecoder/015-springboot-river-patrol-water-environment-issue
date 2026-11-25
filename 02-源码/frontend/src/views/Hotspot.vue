<template>
  <div class="page">
    <h1 class="page-title">水环境热点分析</h1>
    <p class="page-sub">按河段、问题类型与时间窗口统计复发次数，输出需要专项治理的河段清单；权重可配置、计算可追溯</p>

    <el-tabs v-model="tab">
      <el-tab-pane label="热点河段清单" name="list">
        <div class="metrics" style="grid-template-columns: repeat(4, 1fr)">
          <div class="metric"><div class="lb">参与计算断面</div><div class="vl num">{{ stats.total || 0 }}<small>个</small></div><div class="df">规则 {{ activeRule.version }}</div></div>
          <div class="metric"><div class="lb">高风险河段</div><div class="vl num" style="color: #b03035">{{ stats.distribution?.高 || 0 }}<small>个</small></div><div class="df">建议专项治理</div></div>
          <div class="metric"><div class="lb">推荐采纳率</div><div class="vl num">{{ stats.adoptRate || 0 }}<small>%</small></div><div class="df">未人工调整占比</div></div>
          <div class="metric"><div class="lb">人工调整率</div><div class="vl num">{{ stats.adjustRate || 0 }}<small>%</small></div><div class="df">均已填写原因</div></div>
        </div>

        <div class="filter">
          <el-select v-model="level" placeholder="结果等级" clearable @change="load">
            <el-option label="高" value="高" /><el-option label="中" value="中" /><el-option label="低" value="低" />
          </el-select>
          <el-select v-model="evalSection" placeholder="选择断面执行计算" filterable clearable style="width: 260px">
            <el-option v-for="s in sections" :key="s.id" :label="`${s.code} ${s.name}`" :value="s.id" />
          </el-select>
          <el-button type="primary" :disabled="!evalSection" @click="evaluate">执行热点识别</el-button>
          <el-button style="margin-left: auto" @click="load">刷新</el-button>
        </div>

        <div class="card" style="padding: 0">
          <el-table :data="rows" v-loading="loading">
            <el-table-column type="index" label="排名" width="70" />
            <el-table-column prop="sectionName" label="河段" min-width="220" />
            <el-table-column prop="waterQuality" label="水质" width="90" />
            <el-table-column prop="totalScore" label="总分" width="90">
              <template #default="{ row }"><span class="num" style="font-weight: 600">{{ row.totalScore }}</span></template>
            </el-table-column>
            <el-table-column label="系统等级" width="100">
              <template #default="{ row }"><span class="tag" :class="levelClass(row.level)">{{ row.level }}</span></template>
            </el-table-column>
            <el-table-column label="生效等级" width="100">
              <template #default="{ row }">
                <span class="tag" :class="levelClass(row.effectiveLevel)">{{ row.effectiveLevel }}</span>
                <span v-if="row.manualLevel" style="font-size: 11px; color: #8a6d3b">已调整</span>
              </template>
            </el-table-column>
            <el-table-column prop="recommend" label="推荐措施" width="130" />
            <el-table-column label="计算时间" min-width="170">
              <template #default="{ row }">{{ fmt(row.calcTime) }}</template>
            </el-table-column>
            <el-table-column label="操作" width="120" fixed="right">
              <template #default="{ row }">
                <el-button link type="primary" @click="showDetail(row)">明细</el-button>
              </template>
            </el-table-column>
          </el-table>
          <div v-if="!rows.length && !loading" class="empty-tip">暂无计算结果，请选择断面执行热议识别</div>
        </div>
      </el-tab-pane>

      <el-tab-pane label="规则配置" name="rule">
        <div class="detail-grid">
          <div class="card">
            <div class="card-hd"><h3>当前规则 {{ activeRule.version }}</h3><span class="hint">生效 {{ fmt(activeRule.effectiveTime) }}</span></div>
            <el-form :model="rule" label-width="130px">
              <el-form-item label="河段位置权重"><el-input v-model="rule.weightPosition" style="width: 120px" /><span class="unit">%</span></el-form-item>
              <el-form-item label="问题类型权重"><el-input v-model="rule.weightType" style="width: 120px" /><span class="unit">%</span></el-form-item>
              <el-form-item label="近90天次数权重"><el-input v-model="rule.weightCount" style="width: 120px" /><span class="unit">%</span></el-form-item>
              <el-form-item label="处置时长权重"><el-input v-model="rule.weightDuration" style="width: 120px" /><span class="unit">%</span></el-form-item>
              <el-form-item label="复核结果权重"><el-input v-model="rule.weightReview" style="width: 120px" /><span class="unit">%</span></el-form-item>
              <el-form-item label="水质变化权重"><el-input v-model="rule.weightQuality" style="width: 120px" /><span class="unit">%</span></el-form-item>
              <el-form-item label="权重合计">
                <b class="num" :style="{ color: weightSum === 100 ? '#2d7a58' : '#b03035' }">{{ weightSum }}%</b>
                <span style="font-size: 12px; color: #8b9aa1; margin-left: 8px">必须等于 100%</span>
              </el-form-item>
              <el-form-item label="高风险阈值"><el-input v-model="rule.thresholdHigh" style="width: 120px" /></el-form-item>
              <el-form-item label="中风险阈值"><el-input v-model="rule.thresholdMid" style="width: 120px" /></el-form-item>
              <el-form-item label="统计窗口（天）"><el-input v-model="rule.windowDays" style="width: 120px" /></el-form-item>
              <el-form-item label="次数满分线"><el-input v-model="rule.countFull" style="width: 120px" /></el-form-item>
            </el-form>
            <el-button type="primary" :disabled="weightSum !== 100" @click="saveRule">保存为新版本</el-button>
            <div style="font-size: 12px; color: #8b9aa1; margin-top: 8px">修改后生成新版本，历史计算结果保留原规则快照，不可覆盖</div>
          </div>

          <div>
            <div class="card">
              <div class="card-hd"><h3>版本记录</h3></div>
              <el-table :data="rules" size="small">
                <el-table-column prop="version" label="版本" width="70" />
                <el-table-column label="生效时间" min-width="160">
                  <template #default="{ row }">{{ fmt(row.effectiveTime) }}</template>
                </el-table-column>
                <el-table-column prop="createBy" label="修改人" width="90" />
                <el-table-column label="状态" width="80">
                  <template #default="{ row }"><span class="tag" :class="row.status === '启用' ? 't-4' : 't-5'">{{ row.status }}</span></template>
                </el-table-column>
              </el-table>
            </div>
            <div class="card">
              <div class="card-hd"><h3>计算说明</h3></div>
              <pre style="font-family: ui-monospace, Menlo, monospace; font-size: 12px; background: #f3f7f8; padding: 12px; border-radius: 4px; overflow: auto; line-height: 1.9">总分 = Σ(因素归一化得分 × 权重)
  position = 重点监管/整治中 ? 1.0 : 0.6
  type     = 非法排放 1.0 / 水色异常 0.8 / 岸线垃圾 0.6 ...
  count    = min(近90天次数 / 5, 1)
  duration = min(平均处置时长 / 60h, 1)
  review   = 1 - 复查通过率
  quality  = 水质恶化程度(0~1)
等级：总分 ≥ 75 高；≥ 50 中；否则低</pre>
              <div style="font-size: 12px; color: #8b9aa1; margin-top: 8px">每次计算保存输入快照、规则版本、各项得分与生成时间，可逐项追溯</div>
            </div>
          </div>
        </div>
      </el-tab-pane>
    </el-tabs>

    <el-dialog v-model="dialog" title="计算明细与结果解释" width="720px">
      <template v-if="cur.id">
        <div style="display: flex; align-items: baseline; gap: 10px; margin-bottom: 8px">
          <span class="num" style="font-size: 28px; font-weight: 600; color: #15344a">{{ cur.totalScore }}</span>
          <span class="tag" :class="levelClass(cur.effectiveLevel)">{{ cur.effectiveLevel }}</span>
          <span style="font-size: 12px; color: #8b9aa1">规则 {{ cur.ruleVersion }} · {{ fmt(cur.calcTime) }}</span>
        </div>
        <el-table :data="detailRows" size="small">
          <el-table-column prop="name" label="输入因素" min-width="120" />
          <el-table-column prop="weight" label="权重" width="80" />
          <el-table-column prop="score" label="得分" width="90" />
          <el-table-column prop="note" label="说明" min-width="220" />
        </el-table>
        <div class="card" style="margin-top: 12px; margin-bottom: 0">
          <div class="card-hd"><h3>结果解释</h3></div>
          <div style="font-size: 13px; line-height: 1.9">主要影响因素：{{ cur.factors }}</div>
          <div style="font-size: 13px; line-height: 1.9">未满足条件：{{ cur.unmet || '无' }}</div>
          <div style="font-size: 13px; line-height: 1.9">可改进项：{{ cur.suggestions }}</div>
          <div v-if="cur.manualLevel" style="font-size: 13px; color: #8a6d3b; margin-top: 6px">
            人工调整为「{{ cur.manualLevel }}」，原因：{{ cur.manualReason }}
          </div>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import api from '../api'
import { fmt, LEVEL_CLASS } from '../utils'

const tab = ref('list')
const rows = ref([])
const rules = ref([])
const stats = ref({})
const sections = ref([])
const level = ref('')
const evalSection = ref('')
const loading = ref(false)
const dialog = ref(false)
const cur = ref({})
const levelClass = lv => LEVEL_CLASS[lv] || 't-5'

const activeRule = computed(() => rules.value.find(r => r.status === '启用') || {})
const rule = ref({})
const weightSum = computed(() => ['weightPosition', 'weightType', 'weightCount', 'weightDuration', 'weightReview', 'weightQuality']
  .reduce((s, k) => s + Number(rule.value[k] || 0), 0))

const detailRows = computed(() => {
  const c = cur.value
  if (!c.id) return []
  return [
    { name: '河段位置', weight: '15%', score: c.scorePosition ?? '—', note: '敏感区/重点监管断面权重更高' },
    { name: '问题类型', weight: '20%', score: c.scoreType ?? '—', note: '非法排放 > 水色异常 > 岸线垃圾' },
    { name: '近90天次数', weight: '25%', score: c.scoreCount ?? '—', note: '达到满分线即得满分' },
    { name: '处置时长', weight: '15%', score: c.scoreDuration ?? '—', note: '超过 60 小时得满分' },
    { name: '复核结果', weight: '15%', score: c.scoreReview ?? '—', note: '按驳回比例计' },
    { name: '水质变化', weight: '10%', score: c.scoreQuality ?? '—', note: '水质等级越差得分越高' }
  ]
})

async function load() {
  loading.value = true
  try {
    rows.value = await api.hotspotList({ level: level.value })
    stats.value = await api.hotspotStats()
  } finally { loading.value = false }
}

async function loadRules() {
  rules.value = await api.rules()
  const a = rules.value.find(r => r.status === '启用')
  if (a) rule.value = { ...a }
}

async function evaluate() {
  await api.evaluate(evalSection.value)
  ElMessage.success('计算完成，已保存计算留痕')
  load()
}

function showDetail(row) {
  cur.value = row
  dialog.value = true
}

async function saveRule() {
  const payload = { ...rule.value, id: null }
  await api.saveRule(payload)
  ElMessage.success('新规则版本已生效')
  loadRules()
}

onMounted(async () => {
  load()
  loadRules()
  sections.value = await api.sectionOptions()
})
</script>

<style scoped>
.unit { margin-left: 6px; color: #8b9aa1; font-size: 12px; }
</style>
