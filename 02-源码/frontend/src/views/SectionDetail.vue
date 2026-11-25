<template>
  <div class="page" v-loading="loading">
    <h1 class="page-title">{{ s.code }} {{ s.name }}</h1>
    <p class="page-sub">
      <span class="tag t-1">河道断面主档</span>
      {{ s.area }} · 责任河长 {{ s.manager }} · 更新于 {{ fmt(s.updateTime) }}
    </p>

    <div class="detail-grid">
      <div>
        <div class="card">
          <div class="card-hd"><h3>基础信息</h3><span class="hint">断面长度 {{ s.lengthKm }} km</span></div>
          <dl class="kv">
            <dt>断面编号</dt><dd>{{ s.code }}</dd>
            <dt>所属河流</dt><dd>{{ river.name }}（全长 {{ river.lengthKm }} km）</dd>
            <dt>起止位置</dt><dd>{{ s.startPoint }} 至 {{ s.endPoint }}</dd>
            <dt>所属区域</dt><dd>{{ s.area }}</dd>
            <dt>巡查路线</dt><dd>{{ s.patrolRoute }}</dd>
            <dt>巡查频次</dt><dd>{{ s.patrolFreq }}</dd>
            <dt>水质等级</dt><dd>{{ s.waterQualityLevel }}</dd>
            <dt>断面状态</dt><dd><span class="tag" :class="statusClass(s.status)">{{ s.status }}</span></dd>
            <dt>现场图片</dt>
            <dd><img :src="s.coverImage" alt="断面现场" style="width: 240px; border-radius: 4px; border: 1px solid #dce5e8" /></dd>
          </dl>
        </div>

        <div class="card">
          <div class="card-hd"><h3>巡查点与排口</h3><span class="hint">共 {{ points.length }} 个点位，按巡查顺序</span></div>
          <el-table :data="points" size="small">
            <el-table-column prop="sort" label="序号" width="60" />
            <el-table-column prop="name" label="点位名称" min-width="150" />
            <el-table-column prop="type" label="类型" width="110" />
            <el-table-column label="坐标" min-width="180">
              <template #default="{ row }">{{ row.longitude }}, {{ row.latitude }}</template>
            </el-table-column>
            <el-table-column prop="facility" label="关键设施" min-width="130" />
            <el-table-column label="状态" width="90">
              <template #default="{ row }"><span class="tag" :class="statusClass(row.status)">{{ row.status }}</span></template>
            </el-table-column>
          </el-table>
        </div>

        <div class="card">
          <div class="card-hd"><h3>历史水质记录</h3><span class="hint">最近 6 次</span></div>
          <el-table :data="waterRecords" size="small">
            <el-table-column prop="recordTime" label="检测时间" min-width="170" />
            <el-table-column prop="ph" label="pH" width="80" />
            <el-table-column prop="turbidity" label="浊度 NTU" width="110" />
            <el-table-column prop="dissolvedOxygen" label="溶解氧" width="100" />
            <el-table-column prop="level" label="判定等级" width="100" />
            <el-table-column prop="remark" label="备注" min-width="140" />
          </el-table>
        </div>
      </div>

      <div>
        <div class="card">
          <div class="card-hd"><h3>关联问题单</h3><span class="hint">最近 8 条</span></div>
          <el-table :data="issues" size="small">
            <el-table-column prop="code" label="编号" min-width="130" />
            <el-table-column label="状态" width="90">
              <template #default="{ row }"><span class="tag" :class="statusClass(row.status)">{{ row.status }}</span></template>
            </el-table-column>
            <el-table-column prop="issueType" label="类型" width="110" />
          </el-table>
        </div>

        <div class="card">
          <div class="card-hd"><h3>操作记录</h3></div>
          <el-timeline v-if="logs.length">
            <el-timeline-item v-for="l in logs" :key="l.id" :timestamp="fmt(l.createTime)" color="#237A8B">
              <div style="font-size: 13px">{{ l.action }}<span v-if="l.beforeStatus">（{{ l.beforeStatus }} → {{ l.afterStatus }}）</span></div>
              <div style="font-size: 12px; color: #8b9aa1">{{ l.username }}<span v-if="l.reason"> · {{ l.reason }}</span></div>
            </el-timeline-item>
          </el-timeline>
          <div v-else class="empty-tip">暂无操作记录</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import api from '../api'
import { fmt, statusClass } from '../utils'

const route = useRoute()
const loading = ref(true)
const s = ref({})
const river = ref({})
const points = ref([])
const issues = ref([])
const waterRecords = ref([])
const logs = ref([])

onMounted(async () => {
  try {
    const d = await api.section(route.params.id)
    s.value = d.section
    river.value = d.river || {}
    points.value = d.points || []
    issues.value = d.issues || []
    waterRecords.value = d.waterRecords || []
    logs.value = d.logs || []
  } finally { loading.value = false }
})
</script>
