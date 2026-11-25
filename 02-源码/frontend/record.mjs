// 演示视频录制：CDP Page.startScreencast 抓帧（按真实时间轴）+ ffmpeg 合成 mp4
// 用法：cd frontend && node record.mjs（需先启动后端 8084 与前端 5174）
import puppeteer from 'puppeteer-core'
import fs from 'node:fs'
import path from 'node:path'

const CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
const BASE = 'http://127.0.0.1:5174'
const DIR = path.resolve('../demo/frames')
fs.rmSync(DIR, { recursive: true, force: true })
fs.mkdirSync(DIR, { recursive: true })

const sleep = ms => new Promise(r => setTimeout(r, ms))
const frames = []
let recording = false

const browser = await puppeteer.launch({
  executablePath: CHROME,
  headless: 'new',
  args: ['--headless=new', '--disable-gpu', '--no-sandbox', '--hide-scrollbars']
})
const page = await browser.newPage()
await page.setViewport({ width: 1920, height: 1080 })
const cdp = await page.createCDPSession()

cdp.on('Page.screencastFrame', async f => {
  if (!recording) return
  const name = 'f-' + String(frames.length + 1).padStart(5, '0') + '.jpg'
  fs.writeFileSync(path.join(DIR, name), Buffer.from(f.data, 'base64'))
  frames.push({ file: name, ts: f.metadata.timestamp })
  try { await cdp.send('Page.screencastFrameAck', { sessionId: f.sessionId }) } catch (e) { /* ignore */ }
})

async function go(url, wait = 4200) {
  await page.goto(BASE + url, { waitUntil: 'networkidle2', timeout: 30000 })
  await sleep(wait)
}

async function login(username) {
  await page.goto(BASE + '/login', { waitUntil: 'networkidle2' })
  await sleep(1600)
  await page.click('input[placeholder="请输入账号"]', { clickCount: 3 })
  await page.type('input[placeholder="请输入账号"]', username, { delay: 55 })
  await page.click('input[placeholder="请输入密码"]', { clickCount: 3 })
  await page.type('input[placeholder="请输入密码"]', 'admin123', { delay: 55 })
  await sleep(900)
  await page.click('button.el-button--primary')
  await sleep(4200)
}

async function clickRowButton(text) {
  const ok = await page.evaluate(t => {
    for (const r of document.querySelectorAll('.el-table__body tr')) {
      for (const b of r.querySelectorAll('button')) {
        if (b.innerText.trim() === t) { b.click(); return true }
      }
    }
    return false
  }, text)
  await sleep(3400)
  return ok
}

async function clickText(text) {
  await page.evaluate(t => {
    const els = [...document.querySelectorAll('button, .el-button, .el-tabs__item')]
    const el = els.find(e => e.innerText.trim() === t)
    if (el) el.click()
  }, text)
  await sleep(3000)
}

const t0 = Date.now()
try {
  await page.goto(BASE + '/login', { waitUntil: 'networkidle2' })
  await sleep(1200)
  await cdp.send('Page.startScreencast', { format: 'jpeg', quality: 80, maxWidth: 1920, maxHeight: 1080, everyNthFrame: 1 })
  recording = true
  await sleep(1500)

  // 1) 管理员：看板 → 河道档案 → 问题单 → 派单 → 热点 → 规则 → 角色
  await login('admin')
  await sleep(4000)
  await page.evaluate(() => window.scrollTo(0, 300)); await sleep(3000)
  await page.evaluate(() => window.scrollTo(0, 0)); await sleep(2000)

  await go('/section', 4500)
  await clickRowButton('查看')
  await page.evaluate(() => window.scrollTo(0, 320)); await sleep(3200)
  await page.evaluate(() => window.scrollTo(0, 0)); await sleep(1500)

  await go('/issue', 4200)
  await clickRowButton('查看')
  await sleep(3500)
  await page.keyboard.press('Escape'); await sleep(1500)

  await go('/dispatch', 3800)
  await clickRowButton('派单')
  await sleep(3000)
  await page.keyboard.press('Escape'); await sleep(1500)

  await go('/hotspot', 4000)
  await clickRowButton('明细')
  await sleep(3600)
  await page.keyboard.press('Escape'); await sleep(1400)

  await go('/rule', 3500)
  await go('/sys/role', 3500)

  // 2) 巡查员：任务 → 逐点录入 → 问题上报
  await login('zhouzy')
  await go('/task', 4000)
  await clickRowButton('录入')
  await sleep(3200)
  await clickText('保存该点位记录')
  await sleep(2400)

  await go('/issue', 3800)
  await clickText('问题上报')
  await sleep(3600)
  await page.keyboard.press('Escape'); await sleep(1400)

  // 3) 处置单位：整改跟踪填报
  await login('liuhb')
  await go('/disposal', 3800)
  await clickRowButton('填报进度')
  await sleep(3400)
  await page.keyboard.press('Escape'); await sleep(1400)

  // 4) 复查人员：复核销号 + 热点识别结果面板
  await login('zhaomin')
  await go('/review', 4000)
  await clickRowButton('复核')
  await sleep(3800)
  await page.evaluate(() => { const d = document.querySelector('.el-drawer__body'); if (d) d.scrollTop = 340 })
  await sleep(3400)

  // 5) 回到登录页收尾
  await page.evaluate(() => localStorage.clear())
  await go('/login', 3600)
} catch (e) {
  console.error('RECORD_ERROR', e)
  fs.writeFileSync('../demo/error.log', String(e))
} finally {
  const seconds = (Date.now() - t0) / 1000
  recording = false
  try { await cdp.send('Page.stopScreencast') } catch (e) { /* ignore */ }
  await browser.close()

  // 按抓帧时间戳生成 concat 清单，保持真实节奏
  const list = ['ffconcat version 1.0']
  for (let i = 0; i < frames.length; i++) {
    const next = frames[i + 1]
    const dur = next ? Math.max(0.05, next.ts - frames[i].ts) : 1.2
    list.push(`file '${frames[i].file}'`)
    list.push(`duration ${dur.toFixed(3)}`)
  }
  if (frames.length) {
    list.push(`file '${frames[frames.length - 1].file}'`)
    list.push('duration 1.2')
  }
  fs.writeFileSync('../demo/frames.txt', list.join('\n'))
  fs.writeFileSync('../demo/meta.json', JSON.stringify({
    frames: frames.length, seconds: Math.round(seconds),
    firstTs: frames[0]?.ts, lastTs: frames[frames.length - 1]?.ts
  }, null, 2))
  console.log('frames', frames.length, 'seconds', Math.round(seconds))
}
