<template>
  <div class="page">
    <h1 class="page-title">水环境热点看板</h1>
    <p class="page-sub">统计口径：最近 30 天 · 数据由巡查记录与问题单实时汇总 · {{ today }}</p>

    <div class="metrics">
      <div class="metric"><div class="lb">巡查完成率</div><div class="vl num">{{ m.patrolRate || 0 }}<small>%</small></div><div class="df">本周期任务完成情况</div></div>
      <div class="metric"><div class="lb">本月问题数</div><div class="vl num">{{ m.issueCount || 0 }}<small>件</small></div><div class="df">重大 {{ m.majorCount || 0 }} 件</div></div>
      <div class="metric"><div class="lb">按期处置率</div><div class="vl num">{{ m.onTimeRate || 0 }}<small>%</small></div><div class="df">已关闭单按期占比</div></div>
      <div class="metric"><div class="lb">问题复发率</div><div class="vl num">{{ m.recurRate || 0 }}<small>%</small></div><div class="df">同断面同类 ≥2 次</div></div>
      <div class="metric"><div class="lb">复查通过率</div><div class="vl num">{{ m.reviewPassRate || 0 }}<small>%</small></div><div class="df">驳回后需继续整改</div></div>
      <div class="metric"><div class="lb">逾期未处置</div><div class="vl num" style="color: #b03035">{{ m.overdue || 0 }}<small>件</small></div><div class="df" style="color: #b03035">需督办</div></div>
    </div>

    <div class="charts">
      <div class="chart-box"><h3>问题上报与关闭趋势（近 6 个月）</h3><div ref="c1" class="echart"></div></div>
      <div class="chart-box"><h3>问题状态分布</h3><div ref="c2" class="echart"></div></div>
      <div class="chart-box"><h3>问题类型构成</h3><div ref="c3" class="echart"></div></div>
      <div class="chart-box"><h3>责任单位处置量排行</h3><div ref="c4" class="echart"></div></div>
      <div class="chart-box"><h3>断面水质等级分布</h3><div ref="c5" class="echart"></div></div>
      <div class="chart-box"><h3>复发热点识别结果</h3><div ref="c6" class="echart"></div></div>
    </div>
  </div>
</template>

<script setup>
import { onBeforeUnmount, onMounted, reactive, ref } from 'vue'
import * as echarts from 'echarts'
import api from '../api'

const m = reactive({})
const today = new Date().toLocaleDateString('zh-CN')
const c1 = ref(); const c2 = ref(); const c3 = ref(); const c4 = ref(); const c5 = ref(); const c6 = ref()
let charts = []

const PALETTE = ['#15344A', '#237A8B', '#2D5B6B', '#6FA9B4', '#2D7A58', '#8A6D3B', '#8B9AA1', '#B03035']
const axis = { axisLabel: { fontSize: 10, color: '#5F7078' }, axisLine: { lineStyle: { color: '#DCE5E8' } }, axisTick: { show: false } }

function draw(el, option) {
  const chart = echarts.init(el)
  chart.setOption(option)
  charts.push(chart)
}

async function load() {
  const d = await api.dashboard()
  Object.assign(m, d.metrics)

  draw(c1.value, {
    color: ['#15344A', '#237A8B'],
    tooltip: { trigger: 'axis' },
    legend: { data: ['上报', '关闭'], bottom: 0, itemWidth: 8, itemHeight: 8, textStyle: { fontSize: 10 } },
    grid: { left: 34, right: 14, top: 14, bottom: 34 },
    xAxis: { type: 'category', data: d.trend.months, ...axis, axisLabel: { ...axis.axisLabel, formatter: v => v.slice(5) } },
    yAxis: { type: 'value', splitLine: { lineStyle: { color: '#EDF2F3' } }, axisLabel: axis.axisLabel },
    series: [
      { name: '上报', type: 'line', smooth: true, data: d.trend.report, symbolSize: 4 },
      { name: '关闭', type: 'line', smooth: true, data: d.trend.close, symbolSize: 4, lineStyle: { type: 'dashed' } }
    ]
  })

  draw(c2.value, {
    color: PALETTE,
    tooltip: { trigger: 'item' },
    legend: { bottom: 0, itemWidth: 8, itemHeight: 8, textStyle: { fontSize: 10 } },
    series: [{
      type: 'pie', radius: ['42%', '65%'], center: ['50%', '44%'], label: { show: false },
      data: Object.entries(d.statusDist).map(([k, v]) => ({ name: k, value: v }))
    }]
  })

  draw(c3.value, {
    color: ['#237A8B'],
    tooltip: { trigger: 'axis' },
    grid: { left: 34, right: 14, top: 14, bottom: 44 },
    xAxis: { type: 'category', data: Object.keys(d.typeDist), ...axis, axisLabel: { ...axis.axisLabel, interval: 0, rotate: 28, fontSize: 9 } },
    yAxis: { type: 'value', splitLine: { lineStyle: { color: '#EDF2F3' } }, axisLabel: axis.axisLabel },
    series: [{ type: 'bar', barWidth: 18, data: Object.values(d.typeDist), itemStyle: { borderRadius: [2, 2, 0, 0] } }]
  })

  draw(c4.value, {
    color: ['#2D5B6B'],
    tooltip: { trigger: 'axis' },
    grid: { left: 70, right: 16, top: 12, bottom: 12 },
    xAxis: { type: 'value', splitLine: { lineStyle: { color: '#EDF2F3' } }, axisLabel: axis.axisLabel },
    yAxis: { type: 'category', data: Object.keys(d.deptRank).reverse(), ...axis },
    series: [{ type: 'bar', barWidth: 14, data: Object.values(d.deptRank).reverse(), itemStyle: { borderRadius: [0, 2, 2, 0] } }]
  })

  draw(c5.value, {
    color: PALETTE,
    tooltip: { trigger: 'item' },
    legend: { bottom: 0, itemWidth: 8, itemHeight: 8, textStyle: { fontSize: 10 } },
    series: [{
      type: 'pie', roseType: 'radius', radius: ['30%', '62%'], center: ['50%', '44%'], label: { show: false },
      data: Object.entries(d.qualityDist).map(([k, v]) => ({ name: k, value: v }))
    }]
  })

  draw(c6.value, {
    color: ['#B03035', '#8A6D3B', '#2D7A58'],
    tooltip: { trigger: 'axis' },
    grid: { left: 32, right: 12, top: 12, bottom: 28 },
    xAxis: { type: 'category', data: Object.keys(d.hotspotDist), ...axis },
    yAxis: { type: 'value', splitLine: { lineStyle: { color: '#EDF2F3' } }, axisLabel: axis.axisLabel },
    series: [{ type: 'bar', barWidth: 26, data: Object.entries(d.hotspotDist).map(([k, v], i) => ({ value: v, itemStyle: { color: PALETTE[i === 0 ? 7 : (i === 1 ? 5 : 4)] } })) }]
  })
}

const resize = () => charts.forEach(c => c.resize())
onMounted(() => { load(); window.addEventListener('resize', resize) })
onBeforeUnmount(() => { window.removeEventListener('resize', resize); charts.forEach(c => c.dispose()); charts = [] })
</script>
