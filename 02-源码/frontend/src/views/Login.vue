<template>
  <div class="login-wrap">
    <div class="left">
      <div class="brand"><i></i>河长制信息化 · 水环境巡查处置平台</div>
      <div class="slogan">
        <h1>巡河有痕<br />问题有单 处置有据</h1>
        <p>覆盖河道断面档案、周期与临时巡查、快速水质录入、问题派单督办、整改跟踪与复查销号全流程，并以问题复发热点识别辅助专项治理决策。</p>
        <div class="roles">
          <span v-for="r in roles" :key="r">{{ r }}</span>
        </div>
      </div>
      <div class="meta"><span>数据由巡查员现场录入</span><span>不接入实时水质设备</span></div>
    </div>

    <div class="right">
      <div class="card-login">
        <h2>登录</h2>
        <p class="sub">请使用河长办分配的账号登录</p>
        <el-form :model="form" label-position="top" @submit.prevent>
          <el-form-item label="账号">
            <el-input v-model="form.username" size="large" placeholder="请输入账号" />
          </el-form-item>
          <el-form-item label="密码">
            <el-input v-model="form.password" size="large" type="password" show-password placeholder="请输入密码" @keyup.enter="submit" />
          </el-form-item>
          <div class="row">
            <el-checkbox v-model="remember">记住账号</el-checkbox>
            <span class="link" @click="$message.info('请联系河长办管理员重置密码')">忘记密码？</span>
          </div>
          <el-button type="primary" size="large" style="width: 100%" :loading="loading" @click="submit">登 录</el-button>
        </el-form>
        <div class="tip">
          默认管理员：admin / admin123<br />
          连续 5 次密码错误将锁定 10 分钟，密码以 BCrypt 存储。
        </div>
        <div class="quick">
          <span v-for="a in accounts" :key="a.u" @click="fill(a)">{{ a.n }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api'

const router = useRouter()
const loading = ref(false)
const remember = ref(true)
const form = ref({ username: 'admin', password: 'admin123' })
const roles = ['河道巡查员', '河长办调度员', '处置单位', '复查人员', '管理员']
const accounts = [
  { u: 'admin', p: 'admin123', n: '管理员' },
  { u: 'zhangqm', p: 'admin123', n: '调度员' },
  { u: 'zhouzy', p: 'admin123', n: '巡查员' },
  { u: 'liuhb', p: 'admin123', n: '处置单位' },
  { u: 'zhaomin', p: 'admin123', n: '复查人员' }
]

onMounted(() => {
  const saved = localStorage.getItem('rememberUser')
  if (saved) form.value.username = saved
})

function fill(a) {
  form.value = { username: a.u, password: a.p }
}

async function submit() {
  if (!form.value.username || !form.value.password) return
  loading.value = true
  try {
    const data = await api.login(form.value)
    localStorage.setItem('token', data.token)
    localStorage.setItem('user', JSON.stringify(data.user))
    localStorage.setItem('menus', JSON.stringify(data.menus))
    if (remember.value) localStorage.setItem('rememberUser', form.value.username)
    router.replace('/dashboard')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-wrap { display: flex; min-height: 100vh; background: #0f2a3a; }
.left {
  flex: 1.15; position: relative; padding: 64px 72px; color: #fff;
  background: linear-gradient(160deg, rgba(21,52,74,.94) 0%, rgba(29,74,94,.9) 55%, rgba(35,122,139,.86) 100%),
    url('/login-bg.jpg') center/cover no-repeat;
  display: flex; flex-direction: column; justify-content: space-between; overflow: hidden;
}
.brand { display: flex; align-items: center; gap: 10px; font-size: 15px; font-weight: 600; letter-spacing: .5px; }
.brand i { width: 10px; height: 10px; border-radius: 50%; background: #57c4c9; display: block; }
.slogan h1 { font-size: 34px; line-height: 1.45; margin: 0 0 16px; font-weight: 600; letter-spacing: .5px; }
.slogan p { font-size: 14px; line-height: 1.9; color: rgba(255,255,255,.72); max-width: 460px; margin: 0 0 18px; }
.roles { display: flex; flex-wrap: wrap; gap: 6px; }
.roles span { font-size: 11px; padding: 4px 8px; border-radius: 3px; background: rgba(87,196,201,.16); color: #cfeff0; }
.meta { display: flex; gap: 24px; font-size: 12px; color: rgba(255,255,255,.5); }
.right { width: 520px; background: #f3f7f8; display: flex; align-items: center; justify-content: center; padding: 40px; }
.card-login { width: 100%; max-width: 380px; }
.card-login h2 { font-size: 22px; color: #15344a; margin: 0 0 6px; }
.card-login .sub { font-size: 13px; color: #5f7078; margin: 0 0 24px; }
.row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.link { font-size: 13px; color: #2d5b6b; cursor: pointer; }
.tip { margin-top: 18px; font-size: 12px; line-height: 1.8; color: #8b9aa1; }
.quick { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 12px; }
.quick span { font-size: 11px; color: #2d5b6b; background: #e8f1f3; padding: 4px 8px; border-radius: 3px; cursor: pointer; }
.quick span:hover { background: #d5e6e9; }
@media (max-width: 900px) {
  .left { display: none; }
  .right { width: 100%; }
}
</style>
