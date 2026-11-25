<template>
  <div class="page">
    <h1 class="page-title">个人中心</h1>
    <p class="page-sub">修改资料、联系方式与密码；头像上传后右上角立即同步</p>

    <div class="detail-grid" style="grid-template-columns: 380px 1fr">
      <div class="card">
        <div class="card-hd"><h3>头像</h3></div>
        <div style="display: flex; align-items: center; gap: 16px">
          <img v-if="form.avatar" :src="form.avatar" style="width: 88px; height: 88px; border-radius: 50%; object-fit: cover; border: 1px solid #dce5e8" alt="头像" />
          <div v-else style="width: 88px; height: 88px; border-radius: 50%; background: #dde8ea; display: flex; align-items: center; justify-content: center; color: #15344a; font-size: 28px">
            {{ form.realName?.slice(0, 1) }}
          </div>
          <div>
            <el-upload :show-file-list="false" :http-request="uploadAvatar" accept="image/*">
              <el-button>上传新头像</el-button>
            </el-upload>
            <div style="font-size: 12px; color: #8b9aa1; margin-top: 6px">支持 jpg/png，≤10MB</div>
          </div>
        </div>
        <el-divider />
        <dl class="kv">
          <dt>账号</dt><dd>{{ form.username }}</dd>
          <dt>角色</dt><dd>{{ roleName }}</dd>
          <dt>最近登录</dt><dd>{{ fmt(form.lastLogin) }}</dd>
        </dl>
      </div>

      <div>
        <div class="card">
          <div class="card-hd"><h3>基本资料</h3></div>
          <el-form :model="form" label-width="100px" style="max-width: 460px">
            <el-form-item label="姓名"><el-input v-model="form.realName" /></el-form-item>
            <el-form-item label="联系方式"><el-input v-model="form.phone" /></el-form-item>
          </el-form>
          <el-button type="primary" @click="save">保存资料</el-button>
        </div>

        <div class="card">
          <div class="card-hd"><h3>修改密码</h3></div>
          <el-form :model="pwd" label-width="100px" style="max-width: 460px">
            <el-form-item label="原密码"><el-input v-model="pwd.oldPassword" type="password" show-password /></el-form-item>
            <el-form-item label="新密码"><el-input v-model="pwd.newPassword" type="password" show-password /></el-form-item>
            <el-form-item label="确认新密码"><el-input v-model="pwd.confirm" type="password" show-password /></el-form-item>
          </el-form>
          <el-button type="primary" @click="changePwd">修改密码</el-button>
          <span style="font-size: 12px; color: #8b9aa1; margin-left: 8px">密码以 BCrypt 存储，任何接口不返回密码字段</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import api from '../api'
import { fmt, ROLE_NAME } from '../utils'

const form = reactive({})
const pwd = reactive({ oldPassword: '', newPassword: '', confirm: '' })
const roleName = computed(() => ROLE_NAME[form.roleCode] || '—')

async function load() {
  const d = await api.profile()
  Object.assign(form, d)
}

async function uploadAvatar({ file }) {
  const d = await api.upload(file, 'avatar')
  form.avatar = d.path
  await api.updateProfile({ avatar: d.path })
  const u = JSON.parse(localStorage.getItem('user') || '{}')
  u.avatar = d.path
  localStorage.setItem('user', JSON.stringify(u))
  ElMessage.success('头像已更新，右上角已同步')
}

async function save() {
  await api.updateProfile({ realName: form.realName, phone: form.phone })
  const u = JSON.parse(localStorage.getItem('user') || '{}')
  u.realName = form.realName
  u.phone = form.phone
  localStorage.setItem('user', JSON.stringify(u))
  ElMessage.success('资料已保存')
}

async function changePwd() {
  if (!pwd.oldPassword) return ElMessage.warning('请输入原密码')
  if (pwd.newPassword.length < 6) return ElMessage.warning('新密码不少于 6 位')
  if (pwd.newPassword !== pwd.confirm) return ElMessage.warning('两次输入的新密码不一致')
  await api.changePassword({ oldPassword: pwd.oldPassword, newPassword: pwd.newPassword })
  ElMessage.success('密码已修改，请重新登录')
  setTimeout(() => { localStorage.clear(); location.href = '/login' }, 800)
}

onMounted(load)
</script>
