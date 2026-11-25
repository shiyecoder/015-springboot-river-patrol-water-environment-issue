<template>
  <div class="page">
    <h1 class="page-title">河道断面档案</h1>
    <p class="page-sub">维护河流、河段、起止位置、巡查点与排口信息，共 {{ total }} 个断面</p>

    <div class="filter">
      <el-select v-model="q.area" placeholder="所属区域" clearable>
        <el-option v-for="a in areas" :key="a" :label="a" :value="a" />
      </el-select>
      <el-select v-model="q.level" placeholder="水质等级" clearable>
        <el-option v-for="l in ['Ⅱ类', 'Ⅲ类', 'Ⅳ类', 'Ⅴ类', '劣Ⅴ类']" :key="l" :label="l" :value="l" />
      </el-select>
      <el-select v-model="q.status" placeholder="断面状态" clearable>
        <el-option v-for="s in ['正常', '预警', '整治中', '重点监管']" :key="s" :label="s" :value="s" />
      </el-select>
      <el-input v-model="q.keyword" placeholder="断面编号或名称" clearable @keyup.enter="search" />
      <el-button type="primary" @click="search">查询</el-button>
      <el-button @click="reset">重置</el-button>
      <el-button style="margin-left: auto" v-if="canEdit" @click="openForm()">新增断面</el-button>
    </div>

    <div class="card" style="padding: 0">
      <el-table :data="rows" v-loading="loading" style="width: 100%">
        <el-table-column prop="code" label="断面编号" min-width="120" />
        <el-table-column label="现场" width="100">
          <template #default="{ row }">
            <img :src="row.coverImage" alt="断面现场" style="width: 64px; height: 48px; object-fit: cover; border-radius: 3px" />
          </template>
        </el-table-column>
        <el-table-column prop="name" label="断面名称" min-width="180" />
        <el-table-column prop="riverName" label="所属河流" min-width="110" />
        <el-table-column prop="area" label="所属区域" min-width="110" />
        <el-table-column prop="waterQualityLevel" label="水质等级" width="100" />
        <el-table-column prop="manager" label="责任人" width="100" />
        <el-table-column prop="patrolFreq" label="巡查频次" min-width="120" />
        <el-table-column label="状态" width="100">
          <template #default="{ row }"><span class="tag" :class="statusClass(row.status)">{{ row.status }}</span></template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="$router.push(`/section/${row.id}`)">查看</el-button>
            <el-button v-if="canEdit" link type="primary" @click="openForm(row)">编辑</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div style="display: flex; justify-content: flex-end; padding: 12px 16px">
        <el-pagination v-model:current-page="q.page" v-model:page-size="q.size" :total="total"
          :page-sizes="[10, 20, 50]" layout="total, sizes, prev, pager, next" @current-change="load" @size-change="search" />
      </div>
    </div>

    <el-drawer v-model="drawer" :title="form.id ? '编辑断面' : '新增断面'" size="520px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="断面编号"><el-input v-model="form.code" placeholder="留空由后端生成" /></el-form-item>
        <el-form-item label="断面名称" required><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="所属河流" required>
          <el-select v-model="form.riverId" style="width: 100%">
            <el-option v-for="r in rivers" :key="r.id" :label="r.name" :value="r.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="所属区域" required><el-input v-model="form.area" /></el-form-item>
        <el-form-item label="起点"><el-input v-model="form.startPoint" /></el-form-item>
        <el-form-item label="终点"><el-input v-model="form.endPoint" /></el-form-item>
        <el-form-item label="断面长度"><el-input v-model="form.lengthKm" placeholder="km" /></el-form-item>
        <el-form-item label="水质等级">
          <el-select v-model="form.waterQualityLevel" style="width: 100%">
            <el-option v-for="l in ['Ⅱ类', 'Ⅲ类', 'Ⅳ类', 'Ⅴ类', '劣Ⅴ类']" :key="l" :label="l" :value="l" />
          </el-select>
        </el-form-item>
        <el-form-item label="巡查路线" required><el-input v-model="form.patrolRoute" type="textarea" :rows="2" /></el-form-item>
        <el-form-item label="责任人" required><el-input v-model="form.manager" /></el-form-item>
        <el-form-item label="巡查频次"><el-input v-model="form.patrolFreq" maxlength="100" show-word-limit /></el-form-item>
        <el-form-item label="断面状态">
          <el-select v-model="form.status" style="width: 100%">
            <el-option v-for="s in ['正常', '预警', '整治中', '重点监管']" :key="s" :label="s" :value="s" />
          </el-select>
        </el-form-item>
        <el-form-item label="现场图片">
          <el-upload :show-file-list="false" :http-request="doUpload" accept="image/*">
            <img v-if="form.coverImage" :src="form.coverImage" style="width: 140px; height: 100px; object-fit: cover; border-radius: 4px" />
            <el-button v-else>上传图片</el-button>
          </el-upload>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="drawer = false">取消</el-button>
        <el-button type="primary" @click="save">保存</el-button>
      </template>
    </el-drawer>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import api from '../api'
import { statusClass } from '../utils'

const loading = ref(false)
const rows = ref([])
const total = ref(0)
const drawer = ref(false)
const rivers = ref([])
const form = ref({})
const user = JSON.parse(localStorage.getItem('user') || '{}')
const canEdit = computed(() => ['admin', 'dispatcher'].includes(user.roleCode))
const areas = ['城东片区', '城南片区', '城西片区', '城北片区', '城中心']

const q = reactive({ page: 1, size: 10, keyword: '', area: '', level: '', status: '' })

async function load() {
  loading.value = true
  try {
    const d = await api.sections(q)
    rows.value = d.records
    total.value = d.total
  } finally { loading.value = false }
}
function search() { q.page = 1; load() }
function reset() { Object.assign(q, { page: 1, keyword: '', area: '', level: '', status: '' }); load() }

function openForm(row) {
  form.value = row
    ? { ...row, riverId: row.riverId }
    : { status: '正常', waterQualityLevel: 'Ⅳ类', coverImage: '' }
  drawer.value = true
}

async function doUpload({ file }) {
  const d = await api.upload(file, 'section')
  form.value.coverImage = d.path
  ElMessage.success('图片已上传')
}

async function save() {
  if (!form.value.name) return ElMessage.warning('请填写断面名称')
  await api.saveSection(form.value)
  ElMessage.success('已保存')
  drawer.value = false
  load()
}

onMounted(async () => {
  load()
  rivers.value = await api.rivers()
})
</script>
