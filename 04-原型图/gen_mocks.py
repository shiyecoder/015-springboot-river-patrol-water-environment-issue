#!/usr/bin/env python3
# 生成 design/pages 下的可点击 HTML 原型（共享 ../mock.css 与 ../icons.svg）
import pathlib

ROOT = pathlib.Path(__file__).parent
PAGES = ROOT / "pages"
PAGES.mkdir(exist_ok=True)

NAV = [
    ("工作台", [("dashboard.html", "i-dashboard", "水环境热点看板")]),
    ("河道档案", [("section-list.html", "i-river", "河道断面"), ("section-detail.html", "i-point", "断面详情")]),
    ("巡查管理", [("task-list.html", "i-task", "计划任务"), ("task-execute.html", "i-water", "巡查记录")]),
    ("问题处置", [("issue-report.html", "i-issue", "问题上报"), ("dispatch.html", "i-dispatch", "调度派单"),
                ("disposal.html", "i-disposal", "整改跟踪"), ("review.html", "i-review", "复核销号")]),
    ("统计分析", [("hotspot.html", "i-chart", "热点看板"), ("rule-config.html", "i-rule", "规则配置")]),
    ("系统管理", [("sys.html", "i-user", "用户与权限")]),
]


def shell(title, crumb, active, content, role="河长办调度员"):
    nav = ""
    for grp, items in NAV:
        nav += '<div class="grp">%s</div>' % grp
        for href, icon, label in items:
            cls = "item on" if href == active else "item"
            nav += '<a class="%s" href="%s"><svg><use href="../icons.svg#%s"/></svg>%s</a>' % (cls, href, icon, label)
    return """<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8"><title>%s · 河道巡查与水环境问题处置系统</title>
<link rel="stylesheet" href="../mock.css"></head>
<body><div class="app">
<aside class="side"><div class="brand"><span class="dot"></span>水环境巡查处置平台</div><nav>%s</nav></aside>
<div class="main"><header class="top"><div class="crumb">河道巡查 / <b>%s</b></div>
<div class="right"><span>%s</span><span>消息 3</span><div class="avatar">张</div></div></header>
<main class="content">%s</main></div></div></body></html>""" % (title, nav, crumb, role, content)


def tag(t, text):
    return '<span class="tag t-%s">%s</span>' % (t, text)


def pager(total=48, cur=1, size=10):
    return ('<div class="pager"><span>共 %d 条</span><select class="sel" style="width:96px;height:26px">'
            '<option>10 条/页</option><option>20 条/页</option><option>50 条/页</option></select>'
            '<span class="pg">‹</span><span class="pg on">1</span><span class="pg">2</span>'
            '<span class="pg">3</span><span class="pg">4</span><span class="pg">5</span><span class="pg">›</span></div>') % total


def table(head, rows, widths=None):
    th = "".join('<th%s>%s</th>' % ((' class="%s"' % widths[i]) if widths and widths[i] else "", h) for i, h in enumerate(head))
    body = "".join("<tr>" + "".join('<td%s>%s</td>' % ((' class="%s"' % widths[i]) if widths and widths[i] else "", c) for i, c in enumerate(r)) + "</tr>" for r in rows)
    return '<div class="tbl-wrap"><table><thead><tr>%s</tr></thead><tbody>%s</tbody></table></div>' % (th, body)


SECTIONS = [
    ("HD-0012", "白鹭溪·工业园段", "城东片区", "Ⅲ类", "周志远", "每周 2 次", "正常", "0"),
    ("HD-0013", "白鹭溪·老桥段", "城东片区", "Ⅳ类", "周志远", "每周 2 次", "预警", "2"),
    ("HD-0021", "青枫河·湿地公园段", "城南片区", "Ⅱ类", "李慧", "每周 1 次", "正常", "0"),
    ("HD-0022", "青枫河·南闸口段", "城南片区", "Ⅴ类", "李慧", "每日 1 次", "整治中", "2"),
    ("HD-0031", "石鼓渠·农灌段", "城西片区", "Ⅳ类", "陈立", "每两周 1 次", "正常", "0"),
    ("HD-0032", "石鼓渠·集镇段", "城西片区", "劣Ⅴ类", "陈立", "每日 1 次", "重点监管", "2"),
    ("HD-0041", "东湖连通渠·北段", "城北片区", "Ⅲ类", "王倩", "每周 1 次", "正常", "0"),
    ("HD-0042", "东湖连通渠·南段", "城北片区", "Ⅳ类", "王倩", "每周 1 次", "预警", "1"),
]


def section_rows():
    rows = []
    for code, name, area, lvl, mgr, freq, st, sup in SECTIONS:
        st_tag = {"正常": tag(4, "正常"), "预警": tag(3, "预警"), "整治中": tag(2, "整治中"), "重点监管": tag("x", "重点监管")}[st]
        rows.append([code, name, area, lvl, mgr, freq, st_tag, ("<span class='badge'>督办</span>" if sup == "1" else "—"),
                     '<a href="section-detail.html">查看</a> <a href="task-list.html">任务</a> <a href="#">更多</a>'])
    return rows


ISSUES = [
    ("WT-2026-0131", "工业园排口持续性泡沫排放", "白鹭溪·工业园段", "非法排放", "重大", "待派单", "1"),
    ("WT-2026-0130", "老桥下岸线垃圾堆积约 30㎡", "白鹭溪·老桥段", "岸线垃圾", "一般", "处置中", "2"),
    ("WT-2026-0129", "湿地公园段水面漂浮物聚集", "青枫河·湿地公园段", "水面漂浮物", "一般", "待复查", "3"),
    ("WT-2026-0128", "南闸口氨氮异常，水色发黑", "青枫河·南闸口段", "水色异常", "重大", "处置中", "2"),
    ("WT-2026-0127", "农灌段护栏缺失 12 米", "石鼓渠·农灌段", "设施损坏", "一般", "已关闭", "4"),
    ("WT-2026-0126", "集镇段生活污水直排", "石鼓渠·集镇段", "非法排放", "重大", "待复查", "3"),
    ("WT-2026-0125", "北段水面油膜", "东湖连通渠·北段", "水色异常", "一般", "待确认", "0"),
    ("WT-2026-0124", "南段疑似偷倒建筑渣土", "东湖连通渠·南段", "岸线垃圾", "一般", "无效上报", "5"),
]
ST = {"待确认": "待确认", "待派单": "待派单", "处置中": "处置中", "待复查": "待复查", "已关闭": "已关闭", "无效上报": "无效上报"}


def issue_rows(limit=8, show_ops=True):
    rows = []
    for code, title, sec, typ, lvl, st, ti in ISSUES[:limit]:
        lv = '<span class="badge">重大</span>' if lvl == "重大" else lvl
        ops = ('<a href="dispatch.html">派单</a> <a href="disposal.html">跟踪</a> <a href="review.html">复核</a> '
               '<a href="#">更多</a>') if show_ops else '<a href="#">查看</a>'
        rows.append([code, title, sec, typ, lv, tag(ti, ST[st]), "2026-10-30 09:12", ops])
    return rows


PAGES_CONTENT = {}

PAGES_CONTENT["dashboard.html"] = """
<h1 class="page">水环境热点看板</h1>
<p class="subtitle">统计口径：2026-10-01 至 2026-10-31 · 数据由巡查记录与问题单实时汇总</p>
<div class="metrics">
  <div class="metric"><div class="lb">巡查完成率</div><div class="vl num">92.6<small>%</small></div><div class="df">较上月 +3.2%</div></div>
  <div class="metric"><div class="lb">本月问题数</div><div class="vl num">38<small>件</small></div><div class="df">重大 7 件</div></div>
  <div class="metric"><div class="lb">按期处置率</div><div class="vl num">85.4<small>%</small></div><div class="df">较上月 +1.8%</div></div>
  <div class="metric"><div class="lb">问题复发率</div><div class="vl num">11.2<small>%</small></div><div class="df">较上月 -2.4%</div></div>
  <div class="metric"><div class="lb">复查通过率</div><div class="vl num">88.0<small>%</small></div><div class="df">驳回 6 次</div></div>
  <div class="metric"><div class="lb">逾期未处置</div><div class="vl num" style="color:#B03035">4<small>件</small></div><div class="df" style="color:#B03035">需督办</div></div>
</div>
<div class="charts">
  <div class="chart"><h3>问题上报与关闭趋势 <span>近 6 个月</span></h3>
    <div class="line"><svg viewBox="0 0 300 110" preserveAspectRatio="none">
      <polyline points="0,80 50,68 100,72 150,50 200,44 250,30 300,26" fill="none" stroke="#15344A" stroke-width="2"/>
      <polyline points="0,96 50,88 100,84 150,74 200,66 250,58 300,52" fill="none" stroke="#237A8B" stroke-width="2" stroke-dasharray="4 3"/>
      <line x1="0" y1="108" x2="300" y2="108" stroke="#DCE5E8"/></svg></div>
    <div class="legend"><span><i style="background:#15344A"></i>上报</span><span><i style="background:#237A8B"></i>关闭</span></div></div>
  <div class="chart"><h3>问题状态分布 <span>共 38 件</span></h3>
    <div class="bars"><i style="height:60%"></i><i style="height:82%"></i><i style="height:100%"></i><i style="height:48%"></i><i style="height:70%"></i><i style="height:26%"></i></div>
    <div class="legend"><span>待确认</span><span>待派单</span><span>处置中</span><span>待复查</span><span>已关闭</span><span>无效</span></div></div>
  <div class="chart"><h3>问题类型构成 <span>近 30 天</span></h3>
    <div class="bars"><i style="height:92%"></i><i style="height:74%"></i><i style="height:56%"></i><i style="height:40%"></i><i style="height:28%"></i></div>
    <div class="legend"><span>非法排放</span><span>岸线垃圾</span><span>漂浮物</span><span>设施损坏</span><span>水色异常</span></div></div>
  <div class="chart"><h3>责任单位处置时效 <span>小时</span></h3>
    <div class="bars"><i style="height:44%"></i><i style="height:66%"></i><i style="height:88%"></i><i style="height:54%"></i><i style="height:76%"></i></div>
    <div class="legend"><span>水务集团</span><span>街道办</span><span>环卫中心</span><span>城管中队</span><span>园区管委</span></div></div>
  <div class="chart"><h3>水质等级分布 <span>断面 24 个</span></h3>
    <div class="bars"><i style="height:36%"></i><i style="height:66%"></i><i style="height:92%"></i><i style="height:52%"></i><i style="height:22%"></i></div>
    <div class="legend"><span>Ⅱ类</span><span>Ⅲ类</span><span>Ⅳ类</span><span>Ⅴ类</span><span>劣Ⅴ类</span></div></div>
  <div class="chart"><h3>复发热点识别结果 <span>规则 v3</span></h3>
    <div class="bars"><i style="height:100%"></i><i style="height:78%"></i><i style="height:62%"></i><i style="height:44%"></i><i style="height:30%"></i></div>
    <div class="legend"><span>石鼓渠集镇段</span><span>青枫河南闸口</span><span>白鹭溪老桥</span><span>东湖南段</span><span>其他</span></div></div>
</div>"""

PAGES_CONTENT["section-list.html"] = """
<h1 class="page">河道断面档案</h1><p class="subtitle">维护河流、河段、起止位置、巡查点与排口信息，共 24 个断面</p>
<div class="filter">
  <div class="f"><label>河道名称</label><select class="sel"><option>全部河道</option><option>白鹭溪</option><option>青枫河</option></select></div>
  <div class="f"><label>所属区域</label><select class="sel"><option>全部区域</option><option>城东片区</option></select></div>
  <div class="f"><label>水质等级</label><select class="sel"><option>全部等级</option><option>Ⅱ类</option><option>Ⅲ类</option></select></div>
  <div class="f"><label>断面状态</label><select class="sel"><option>全部状态</option><option>正常</option><option>预警</option></select></div>
  <div class="f"><label>断面编号/名称</label><input class="inp wide" placeholder="输入编号或名称搜索"></div>
  <button class="btn primary"><svg><use href="../icons.svg#i-search"/></svg>查询</button>
  <button class="btn">重置</button><button class="btn">导出当前结果</button>
  <button class="btn primary" style="margin-left:auto"><svg><use href="../icons.svg#i-plus"/></svg>新增断面</button>
</div>
<div class="card" style="padding:0"><div class="tbl-wrap" style="border:none">
""" + table(["断面编号", "断面名称", "所属区域", "水质等级", "责任人", "巡查频次", "状态", "督办", "操作"], section_rows(),
             ["nowrap", "", "", "nowrap", "nowrap", "nowrap", "nowrap", "nowrap", "nowrap"]) + """
</div></div>
""" + pager(24)

PAGES_CONTENT["section-detail.html"] = """
<h1 class="page">HD-0013 白鹭溪·老桥段</h1>
<p class="subtitle"><span class="rolebar">河道断面主档</span> 城东片区 · 责任河长 周志远 · 更新于 2026-10-30 16:20:00</p>
<div class="grid2">
 <div>
  <div class="card"><div class="card-hd"><h2>基础信息</h2><button class="btn sm">编辑</button></div>
   <dl class="kv">
    <dt>断面编号</dt><dd>HD-0013</dd><dt>所属河流</dt><dd>白鹭溪（全长 8.6 km）</dd>
    <dt>起止位置</dt><dd>老桥东 50m 至橡胶坝上游 200m，全长 1.8 km</dd>
    <dt>所属区域</dt><dd>城东片区 · 河长办第二工作组</dd>
    <dt>巡查路线</dt><dd>老桥桥头 → 西岸步道 → 排口 P-07 → 橡胶坝（约 2.4 km 步行）</dd>
    <dt>巡查频次</dt><dd>每周 2 次（周二、周五）</dd>
    <dt>水质等级</dt><dd>Ⅳ类（最近一次 2026-10-28，pH 7.4，浊度 26 NTU，溶解氧 4.8 mg/L）</dd>
    <dt>断面状态</dt><dd>预警（近 90 天同类问题 3 次）</dd>
    <dt>现场图片</dt><dd><div class="thumbs"><div class="thumb"><img src="../assets/section-01.jpg" alt="断面现场"></div><div class="thumb"><img src="../assets/section-02.jpg" alt="断面现场"></div><div class="thumb"><div class="upl">上传图片</div></div></div></dd>
   </dl></div>
  <div class="card"><div class="card-hd"><h2>巡查点与排口</h2><span class="hint">共 6 个点位，按巡查顺序排列</span></div>
   """ + table(["序号", "点位名称", "类型", "坐标", "关键设施", "状态"],
               [["1", "老桥桥头", "巡查点", "121.4821, 31.2367", "护栏、救生圈", tag(4, "正常")],
                ["2", "西岸步道中段", "巡查点", "121.4835, 31.2361", "垃圾桶 2 个", tag(4, "正常")],
                ["3", "排口 P-07", "排口", "121.4849, 31.2354", "在线流量计", tag(3, "预警")],
                ["4", "橡胶坝", "关键设施", "121.4862, 31.2348", "闸门、警示牌", tag(4, "正常")]],
               ["nowrap", "", "nowrap", "nowrap", "", "nowrap"]) + """
  </div></div>
 <div>
  <div class="card"><div class="card-hd"><h2>关联问题单</h2><a href="issue-report.html">新建</a></div>
   """ + table(["编号", "状态", "类型"],
               [["WT-2026-0130", tag(2, "处置中"), "岸线垃圾"], ["WT-2026-0117", tag(4, "已关闭"), "漂浮物"],
                ["WT-2026-0098", tag(4, "已关闭"), "非法排放"]], ["nowrap", "nowrap", ""]) + """
  </div>
  <div class="card"><div class="card-hd"><h2>操作记录</h2></div>
   <div class="timeline">
    <div class="tl-item on"><b>问题单 WT-2026-0130 派发至环卫中心</b><p>2026-10-30 16:20 · 张启明 · 要求 10-31 前完成清理</p></div>
    <div class="tl-item"><b>断面状态由「正常」调整为「预警」</b><p>2026-10-29 09:05 · 系统规则 · 近 90 天同类问题 3 次</p></div>
    <div class="tl-item"><b>水质记录 20261028-03 录入</b><p>2026-10-28 10:12 · 周志远 · pH 7.4 / 浊度 26 / 溶解氧 4.8</p></div>
    <div class="tl-item"><b>断面档案创建</b><p>2026-04-12 14:30 · 李慧</p></div>
   </div></div>
 </div>
</div>"""

PAGES_CONTENT["task-list.html"] = """
<h1 class="page">巡查计划任务</h1><p class="subtitle">按河段、周期、人员自动生成，支持汛期与特殊天气后的临时任务</p>
<div class="filter">
 <div class="f"><label>任务类型</label><select class="sel"><option>全部</option><option>周期任务</option><option>临时任务</option></select></div>
 <div class="f"><label>河段</label><select class="sel"><option>全部河段</option></select></div>
 <div class="f"><label>巡查员</label><select class="sel"><option>全部人员</option></select></div>
 <div class="f"><label>完成时限</label><input class="inp" type="date" value="2026-10-31"></div>
 <div class="f"><label>任务状态</label><select class="sel"><option>全部状态</option><option>待执行</option><option>已完成</option></select></div>
 <button class="btn primary">查询</button><button class="btn">重置</button>
 <button class="btn primary" style="margin-left:auto"><svg><use href="../icons.svg#i-plus"/></svg>新建临时任务</button>
</div>
<div class="card" style="padding:0"><div class="tbl-wrap" style="border:none">
""" + table(["任务编号", "任务名称", "河段", "类型", "巡查员", "完成时限", "状态", "操作"],
            [["RW-2026-1041", "白鹭溪老桥段第 44 周常规巡查", "HD-0013", "周期", "周志远", "2026-11-01 18:00", tag(1, "待执行"), '<a href="task-execute.html">去巡查</a> <a href="#">改派</a>'],
             ["RW-2026-1040", "石鼓渠集镇段雨后加密巡查", "HD-0032", "临时", "陈立", "2026-10-31 20:00", tag(0, "执行中"), '<a href="task-execute.html">录入</a>'],
             ["RW-2026-1039", "青枫河南闸口段每日巡查", "HD-0022", "周期", "李慧", "2026-10-31 18:00", tag(0, "执行中"), '<a href="task-execute.html">录入</a>'],
             ["RW-2026-1038", "东湖连通渠北段第 44 周巡查", "HD-0041", "周期", "王倩", "2026-10-30 18:00", tag(4, "已完成"), '<a href="#">查看</a>'],
             ["RW-2026-1037", "湿地公园段漂浮物专项复查", "HD-0021", "临时", "李慧", "2026-10-29 18:00", tag("x", "已逾期"), '<a href="#">查看</a> <a href="#">催办</a>']],
            ["nowrap", "", "nowrap", "nowrap", "nowrap", "nowrap", "nowrap", "nowrap"]) + """
</div></div>""" + pager(56) + """
<div class="note">逾期规则：超过完成时限 2 小时未提交记录的周期任务自动标记为「已逾期」，并向巡查员与河长办同时推送站内消息。</div>"""

PAGES_CONTENT["task-execute.html"] = """
<h1 class="page">巡查记录录入 · RW-2026-1041</h1><p class="subtitle">白鹭溪·老桥段 · 周志远 · 完成时限 2026-11-01 18:00</p>
<div class="grid2"><div>
<div class="card"><div class="card-hd"><h2>逐点现场情况</h2><span class="hint">已录入 2 / 4 个点位</span></div>
""" + table(["点位", "现场情况", "快速水质", "照片", "操作"],
            [["老桥桥头", tag(4, "正常"), "—", "1 张", '<a href="#">重录</a>'],
             ["西岸步道中段", tag(3, "有少量垃圾"), "—", "2 张", '<a href="#">重录</a>'],
             ["排口 P-07", '<span class="badge">待录入</span>', '<span class="badge">待录入</span>', "—", '<a href="#">录入</a>'],
             ["橡胶坝", "待录入", "待录入", "—", '<a href="#">录入</a>']], ["nowrap", "", "nowrap", "nowrap", "nowrap"]) + """
</div>
<div class="card"><div class="card-hd"><h2>快速水质数据 · 排口 P-07</h2><span class="hint">便携式检测仪读数，保留 1 位小数</span></div>
<div class="filter">
 <div class="f"><label>pH</label><input class="inp" value="7.4" style="width:120px"></div>
 <div class="f"><label>浊度 NTU</label><input class="inp" value="26.0" style="width:120px"></div>
 <div class="f"><label>溶解氧 mg/L</label><input class="inp" value="4.8" style="width:120px"></div>
 <div class="f"><label>水质等级</label><select class="sel"><option>Ⅳ类</option><option>Ⅲ类</option><option>Ⅴ类</option></select></div>
 <div class="f"><label>检测时间</label><input class="inp" value="2026-10-31 17:20"></div>
</div>
<div class="f" style="margin-top:4px"><label>现场照片（上传组件，支持 jpg/png，单张 ≤10MB）</label>
<div class="thumbs"><div class="thumb"><img src="../assets/section-02.jpg" alt="现场"></div><div class="thumb"><div class="upl">＋ 上传</div></div></div></div>
<div style="margin-top:14px;display:flex;gap:8px"><button class="btn primary">保存并继续下一点</button><button class="btn">暂存草稿</button>
<button class="btn danger">上报问题</button></div>
</div></div>
<div>
<div class="card"><div class="card-hd"><h2>任务摘要</h2></div>
<dl class="kv"><dt>任务编号</dt><dd>RW-2026-1041</dd><dt>河段</dt><dd>HD-0013 白鹭溪·老桥段</dd>
<dt>巡查路线</dt><dd>老桥桥头 → 西岸步道 → 排口 P-07 → 橡胶坝</dd><dt>点位数量</dt><dd>4 个</dd>
<dt>开始时间</dt><dd>2026-10-31 16:42</dd><dt>天气</dt><dd>阴，东南风 2 级，近 24h 降雨 6mm</dd></dl></div>
<div class="card"><div class="card-hd"><h2>历史水质趋势</h2><span class="hint">近 6 次</span></div>
<div class="line"><svg viewBox="0 0 300 110" preserveAspectRatio="none">
<polyline points="0,40 60,46 120,58 180,66 240,72 300,78" fill="none" stroke="#237A8B" stroke-width="2"/>
<polyline points="0,70 60,72 120,64 180,58 240,52 300,48" fill="none" stroke="#15344A" stroke-width="2"/>
<line x1="0" y1="108" x2="300" y2="108" stroke="#DCE5E8"/></svg></div>
<div class="legend"><span><i style="background:#237A8B"></i>浊度</span><span><i style="background:#15344A"></i>溶解氧</span></div>
<p class="hint" style="margin-top:8px;font-size:12px;color:#5F7078">浊度 6 次连续上升，溶解氧下降，建议列入重点关注。</p></div>
</div></div>"""

PAGES_CONTENT["issue-report.html"] = """
<h1 class="page">问题上报</h1><p class="subtitle">巡查员现场登记问题，提交后进入「待确认」，由河长办研判定级</p>
<div class="grid2"><div>
<div class="card"><div class="card-hd"><h2>问题信息</h2><span class="hint">编号由系统生成：WT-2026-0132</span></div>
<div class="filter">
 <div class="f"><label>所属河段 *</label><select class="sel"><option>HD-0013 白鹭溪·老桥段</option></select></div>
 <div class="f"><label>关联点位 *</label><select class="sel"><option>排口 P-07</option></select></div>
 <div class="f"><label>问题类型 *</label><select class="sel"><option>非法排放</option><option>水面漂浮物</option></select></div>
 <div class="f"><label>问题级别 *</label><select class="sel"><option>重大</option><option>一般</option></select></div>
 <div class="f"><label>发现时间 *</label><input class="inp" value="2026-10-31 17:05"></div>
 <div class="f"><label>坐标</label><input class="inp" value="121.4849, 31.2354" style="width:200px"></div>
</div>
<div class="f" style="margin-bottom:12px"><label>问题描述 *</label>
<textarea class="inp" style="height:88px;width:100%;padding:8px 10px;resize:vertical">排口 P-07 持续排出灰白色泡沫状废水，下游 30 米水面有明显泡沫带，伴有异味。</textarea></div>
<div class="f" style="margin-bottom:12px"><label>影响范围 *</label>
<textarea class="inp" style="height:64px;width:100%;padding:8px 10px;resize:vertical">下游约 120 米河段，涉及西岸步道亲水平台，暂无居民取水。</textarea></div>
<div class="f"><label>证据材料 *</label><div class="thumbs">
<div class="thumb"><img src="../assets/issue-01.jpg" alt="证据"></div><div class="thumb"><img src="../assets/issue-02.jpg" alt="证据"></div>
<div class="thumb"><div class="upl">＋ 上传</div></div></div></div>
<div class="note" style="margin-top:8px">上传组件限制：图片 jpg/png ≤10MB，视频 mp4 ≤100MB；系统仅保存相对路径，不接收外部 URL。</div>
<div style="margin-top:14px;display:flex;gap:8px"><button class="btn primary">提交上报</button><button class="btn">保存草稿</button><button class="btn">取消</button></div>
</div></div>
<div>
<div class="card" style="border-color:#E3BFC1"><div class="card-hd"><h2 style="color:#B03035">重复上报提醒</h2><span class="hint">系统比对结果</span></div>
<p style="font-size:13px;margin-bottom:10px">同一河段 500 米范围内近 30 天存在 <b>2 条</b> 同类问题，请确认是否为同一事件：</p>
""" + table(["编号", "类型", "状态", "上报时间"],
            [["WT-2026-0130", "岸线垃圾", tag(2, "处置中"), "2026-10-30"],
             ["WT-2026-0117", "漂浮物", tag(4, "已关闭"), "2026-10-12"]], ["nowrap", "nowrap", "nowrap", "nowrap"]) + """
<div style="margin-top:10px;display:flex;gap:8px"><button class="btn sm primary">关联到 WT-2026-0130</button><button class="btn sm">确认是新问题</button></div>
</div>
<div class="card"><div class="card-hd"><h2>相似历史问题处置结果</h2></div>
<div class="timeline">
 <div class="tl-item on"><b>WT-2026-0117 漂浮物 · 已关闭</b><p>环卫中心 3 天完成清理，复查通过</p></div>
 <div class="tl-item"><b>WT-2026-0098 非法排放 · 已关闭</b><p>园区管委约谈企业，责令整改，罚款并限期治理</p></div>
</div>
<div class="note">该断面近 90 天已出现 3 次同类问题，提交后若定级为重大，必须填写临时措施。</div></div>
</div></div>"""

PAGES_CONTENT["dispatch.html"] = """
<h1 class="page">调度派单台</h1><p class="subtitle">河长办研判问题级别、指定责任单位与协办单位，重大问题自动建立督办</p>
<div class="filter">
 <div class="f"><label>处置状态</label><select class="sel"><option>待派单</option><option>全部</option></select></div>
 <div class="f"><label>问题级别</label><select class="sel"><option>全部</option><option>重大</option></select></div>
 <div class="f"><label>问题类型</label><select class="sel"><option>全部类型</option></select></div>
 <div class="f"><label>上报时间</label><input class="inp" type="date" value="2026-10-31"></div>
 <button class="btn primary">查询</button><button class="btn">重置</button>
 <div style="margin-left:auto;display:flex;gap:8px"><button class="btn">批量派发</button><button class="btn">导出</button></div>
</div>
<div class="grid2"><div class="card" style="padding:0"><div class="tbl-wrap" style="border:none">
""" + table(["编号", "问题", "级别", "状态", "超时", "操作"],
            [["WT-2026-0131", "工业园排口持续性泡沫排放", '<span class="badge">重大</span>', tag(1, "待派单"), '<span class="badge">剩余 3h</span>', "选中"],
             ["WT-2026-0130", "老桥下岸线垃圾堆积", "一般", tag(2, "处置中"), "—", "查看"],
             ["WT-2026-0126", "集镇段生活污水直排", '<span class="badge">重大</span>', tag(3, "待复查"), "已超时 6h", "查看"],
             ["WT-2026-0125", "北段水面油膜", "一般", tag(0, "待确认"), "—", "研判"]],
            ["nowrap", "", "nowrap", "nowrap", "nowrap", "nowrap"]) + """
</div></div>
<div class="card" style="box-shadow:0 8px 24px rgba(21,52,74,.18)"><div class="card-hd"><h2>派单 · WT-2026-0131</h2><span class="hint">抽屉视图</span></div>
<dl class="kv" style="margin-bottom:12px"><dt>问题级别</dt><dd><span class="badge">重大</span> 非法排放 · 白鹭溪·工业园段</dd>
<dt>已耗时</dt><dd class="num">2 小时 14 分（重大问题时限 4 小时）</dd><dt>上报人</dt><dd>周志远 · 2026-10-31 17:05</dd></dl>
<div class="f" style="margin-bottom:10px"><label>责任单位 *</label><select class="sel" style="width:100%"><option>园区管委会（牵头）</option><option>水务集团</option></select></div>
<div class="f" style="margin-bottom:10px"><label>协办单位</label><select class="sel" style="width:100%"><option>生态环境分局</option><option>城管中队</option></select></div>
<div class="f" style="margin-bottom:10px"><label>处置要求 *</label><textarea class="inp" style="width:100%;height:70px;padding:8px 10px">立即封堵排口，24 小时内提交溯源结果，3 日内完成整改。</textarea></div>
<div class="f" style="margin-bottom:10px"><label>完成期限 *</label><input class="inp" value="2026-11-03 18:00" style="width:100%"></div>
<div class="f" style="margin-bottom:10px"><label>临时措施（重大问题必填）*</label><textarea class="inp" style="width:100%;height:60px;padding:8px 10px">下游设置围油栏与吸油毡，暂停亲水平台开放。</textarea></div>
<div class="f" style="margin-bottom:14px"><label>建立督办</label><select class="sel" style="width:100%"><option>是 · 每日督办</option><option>否</option></select></div>
<div style="display:flex;gap:8px;justify-content:flex-end"><button class="btn">取消</button><button class="btn primary">确认派单</button></div>
</div></div>"""

PAGES_CONTENT["disposal.html"] = """
<h1 class="page">整改跟踪 · WT-2026-0131</h1><p class="subtitle"><span class="tag t-2">处置中</span> 责任单位：园区管委会 · 期限 2026-11-03 18:00 · 剩余 2 天 6 小时</p>
<div class="grid2"><div>
<div class="card"><div class="card-hd"><h2>处置信息</h2><span class="hint">步骤 3 / 4</span></div>
<div class="timeline">
 <div class="tl-item on"><b>接单</b><p>2026-10-31 18:02 · 园区管委 值班员 · 已确认接收</p></div>
 <div class="tl-item on"><b>第一阶段：封堵与围拦</b><p>2026-11-01 09:30 · 处置人数 8 人 · 物资：围油栏 60m、吸油毡 40 张</p>
  <div class="thumbs" style="margin-top:6px"><div class="thumb"><img src="../assets/issue-03.jpg" alt="整改"></div><div class="thumb"><img src="../assets/issue-04.jpg" alt="整改"></div></div></div>
 <div class="tl-item on"><b>第二阶段：溯源排查</b><p>2026-11-01 16:10 · 查明为园区 A 厂区雨水管错接污水管</p></div>
 <div class="tl-item"><b>第三阶段：管网整改（进行中）</b><p>计划 2026-11-02 完成错接点封堵与新管接入</p></div>
 <div class="tl-item"><b>第四阶段：提交结果</b><p>待完成</p></div>
</div></div>
<div class="card"><div class="card-hd"><h2>上报整改进度</h2></div>
<div class="filter">
 <div class="f"><label>阶段 *</label><select class="sel"><option>第三阶段：管网整改</option></select></div>
 <div class="f"><label>处置人数</label><input class="inp" value="12" style="width:100px"></div>
 <div class="f"><label>费用（元）</label><input class="inp" value="46000" style="width:120px"></div>
</div>
<div class="f" style="margin-bottom:10px"><label>处置内容 *</label><textarea class="inp" style="width:100%;height:70px;padding:8px 10px">完成错接点混凝土封堵，新敷设 DN300 污水管 42 米接入园区污水主干管。</textarea></div>
<div class="f" style="margin-bottom:10px"><label>物资使用</label><input class="inp" style="width:100%" value="DN300 波纹管 42m、水泥 2t、砂石 4m³"></div>
<div class="f" style="margin-bottom:12px"><label>整改凭证 *</label><div class="thumbs"><div class="thumb"><img src="../assets/issue-05.jpg" alt="凭证"></div><div class="thumb"><div class="upl">＋ 上传</div></div></div></div>
<button class="btn primary">提交进度</button> <button class="btn">申请延期</button>
</div></div>
<div>
<div class="card"><div class="card-hd"><h2>督办记录</h2><span class="badge">重大</span></div>
<div class="timeline">
 <div class="tl-item on"><b>河长办督办（第 2 次）</b><p>2026-11-01 09:00 · 张启明 · 要求今日 18:00 前提交溯源结论</p></div>
 <div class="tl-item"><b>河长办督办（第 1 次）</b><p>2026-10-31 20:00 · 张启明 · 提醒按时接单</p></div>
</div></div>
<div class="card"><div class="card-hd"><h2>时限与预警</h2></div>
<dl class="kv"><dt>派单时间</dt><dd>2026-10-31 18:00</dd><dt>要求完成</dt><dd>2026-11-03 18:00</dd>
<dt>剩余时长</dt><dd class="num" style="color:#B03035">2 天 6 小时</dd><dt>预警阈值</dt><dd>剩余 24 小时转黄、6 小时转红</dd>
<dt>处置时长</dt><dd class="num">已用 23 小时 36 分</dd></dl></div>
<div class="card"><div class="card-hd"><h2>关联单据</h2></div>
""" + table(["编号", "关系", "状态"], [["WT-2026-0131", "本单", tag(2, "处置中")], ["RW-2026-1041", "发现任务", tag(0, "执行中")]], ["nowrap", "", "nowrap"]) + """
</div></div></div>"""

PAGES_CONTENT["review.html"] = """
<h1 class="page">复核销号 · WT-2026-0126</h1><p class="subtitle"><span class="tag t-3">待复查</span> 石鼓渠·集镇段 · 处置单位：街道办 · 复查人：赵敏</p>
<div class="grid2"><div>
<div class="card"><div class="card-hd"><h2>现场复核记录</h2><span class="hint">复查人不可为原处置人</span></div>
<div class="filter">
 <div class="f"><label>复查时间 *</label><input class="inp" value="2026-11-01 10:20"></div>
 <div class="f"><label>现场水色</label><select class="sel"><option>正常</option><option>轻微异常</option></select></div>
 <div class="f"><label>气味</label><select class="sel"><option>无</option><option>轻微</option></select></div>
 <div class="f"><label>pH</label><input class="inp" value="7.2" style="width:90px"></div>
 <div class="f"><label>浊度</label><input class="inp" value="18.0" style="width:90px"></div>
 <div class="f"><label>溶解氧</label><input class="inp" value="5.6" style="width:90px"></div>
</div>
<div class="f" style="margin-bottom:10px"><label>复核结论 *</label><textarea class="inp" style="width:100%;height:70px;padding:8px 10px">排口已封堵，水面无污水流入，水质指标恢复至Ⅳ类，整改到位。</textarea></div>
<div class="f" style="margin-bottom:12px"><label>现场照片 *</label><div class="thumbs"><div class="thumb"><img src="../assets/section-04.jpg" alt="复查"></div><div class="thumb"><img src="../assets/section-05.jpg" alt="复查"></div><div class="thumb"><div class="upl">＋ 上传</div></div></div></div>
<div style="display:flex;gap:8px"><button class="btn primary">通过并关闭</button><button class="btn danger">驳回继续整改</button><button class="btn">转他人复查</button></div>
</div>
<div class="card"><div class="card-hd"><h2>处置结果对照</h2></div>
""" + table(["项目", "派单要求", "处置上报"], [["封堵排口", "3 日内完成", "2026-10-31 已完成"],
   ["水质恢复", "达Ⅳ类以上", "pH 7.2 / 浊度 18 / DO 5.6"], ["凭证", "现场照片 ≥2 张", "已上传 3 张"]], ["", "", ""]) + """
</div></div>
<div>
<div class="card" style="border-color:#B9CBD2"><div class="card-hd"><h2>问题复发热点识别 · 计算结果</h2><span class="hint">规则 v3 · 2026-11-01 10:22</span></div>
<div style="display:flex;align-items:baseline;gap:10px;margin-bottom:6px">
 <span class="num" style="font-size:32px;font-weight:600;color:#15344A">78.4</span>
 <span class="tag t-x">高复发风险</span><span class="hint" style="font-size:12px;color:#8B9AA1">满分 100，阈值 高≥75 / 中≥50</span></div>
<div class="note" style="margin-bottom:12px">推荐结论：该河段应纳入下一季度专项治理清单。主要驱动因素为「近 90 天同类问题 7 次」与「处置时长 96 小时」。</div>
""" + table(["输入因素", "原始值", "权重", "得分", "说明"],
            [["河段位置", "集镇段（敏感区）", "15%", "12.0", "距取水口 800m"],
             ["问题类型", "生活污水直排", "20%", "18.0", "非法排放权重最高"],
             ["近 90 天次数", "7 次", "25%", "23.5", "超阈值 4 次"],
             ["平均处置时长", "96 小时", "15%", "8.4", "超时限 1.6 倍"],
             ["复核结果", "驳回 1 次", "15%", "10.5", "首轮不合格"],
             ["水质变化", "劣Ⅴ类→Ⅳ类", "10%", "6.0", "改善但未达标"]], ["", "nowrap", "nowrap", "nowrap", ""]) + """
<div style="display:flex;gap:8px;margin-top:10px"><button class="btn sm">查看完整计算留痕</button><button class="btn sm">重新计算</button></div>
<div style="margin-top:14px;border-top:1px solid #DCE5E8;padding-top:12px">
 <div class="f" style="margin-bottom:8px"><label>人工调整结果</label><select class="sel"><option>维持系统结果（高）</option><option>调整为中</option><option>调整为低</option></select></div>
 <div class="f" style="margin-bottom:8px"><label>调整原因（≥5 字）*</label><input class="inp" style="width:100%" value="该段已列入市级整治计划，风险可控"></div>
 <div style="display:flex;gap:8px"><button class="btn sm primary">保存调整</button><span class="hint" style="font-size:12px;color:#8B9AA1;align-self:center">原始计算结果不会被覆盖</span></div>
</div></div>
<div class="card"><div class="card-hd"><h2>未满足条件与改进项</h2></div>
<ul style="font-size:13px;padding-left:18px;color:#1F2D33;line-height:1.9">
<li>近 90 天同类问题重复 ≥5 次，未达到「低复发」条件</li>
<li>平均处置时长 96 小时，超过制度要求 60 小时</li>
<li>建议：增设 2 处截污井、每周 2 次加密巡查、纳入雨污分流改造</li></ul></div>
</div></div>"""

PAGES_CONTENT["hotspot.html"] = """
<h1 class="page">水环境热点看板</h1><p class="subtitle">按河段、问题类型与时间窗口统计复发次数，输出专项治理河段清单</p>
<div class="filter">
 <div class="f"><label>时间窗口</label><select class="sel"><option>近 90 天</option><option>近 180 天</option><option>本年度</option></select></div>
 <div class="f"><label>河段</label><select class="sel"><option>全部河段</option></select></div>
 <div class="f"><label>问题类型</label><select class="sel"><option>全部类型</option></select></div>
 <div class="f"><label>规则版本</label><select class="sel"><option>v3（2026-09-01 生效）</option><option>v2</option></select></div>
 <button class="btn primary">重新计算</button><button class="btn">导出清单</button>
</div>
<div class="metrics" style="grid-template-columns:repeat(4,1fr)">
 <div class="metric"><div class="lb">热点河段数</div><div class="vl num">5<small>个</small></div><div class="df">高 2 / 中 3</div></div>
 <div class="metric"><div class="lb">推荐采纳率</div><div class="vl num">72.0<small>%</small></div><div class="df">近 90 天</div></div>
 <div class="metric"><div class="lb">人工调整率</div><div class="vl num">16.0<small>%</small></div><div class="df">调整均填写原因</div></div>
 <div class="metric"><div class="lb">调整后复发下降</div><div class="vl num">-23.5<small>%</small></div><div class="df">专项治理河段</div></div>
</div>
<div class="card" style="padding:0"><div class="card-hd" style="padding:16px 16px 0"><h2>热点河段排行</h2><span class="hint">按总分倒序，点击查看计算明细</span></div>
""" + table(["排名", "河段", "主要问题类型", "近 90 天次数", "平均处置时长", "总分", "等级", "推荐", "操作"],
            [["1", "HD-0032 石鼓渠·集镇段", "非法排放", "7", "96 h", "78.4", '<span class="tag t-x">高</span>', "纳入专项治理", '<a href="review.html">明细</a>'],
             ["2", "HD-0022 青枫河·南闸口段", "水色异常", "6", "82 h", "76.1", '<span class="tag t-x">高</span>', "纳入专项治理", '<a href="#">明细</a>'],
             ["3", "HD-0013 白鹭溪·老桥段", "岸线垃圾", "5", "64 h", "62.8", '<span class="tag t-3">中</span>', "加密巡查", '<a href="#">明细</a>'],
             ["4", "HD-0042 东湖连通渠·南段", "岸线垃圾", "4", "70 h", "55.2", '<span class="tag t-3">中</span>', "加密巡查", '<a href="#">明细</a>'],
             ["5", "HD-0021 青枫河·湿地公园段", "漂浮物", "3", "48 h", "51.6", '<span class="tag t-3">中</span>', "观察", '<a href="#">明细</a>'],
             ["6", "HD-0041 东湖连通渠·北段", "水色异常", "2", "40 h", "38.9", '<span class="tag t-4">低</span>', "常规管理", '<a href="#">明细</a>']],
            ["nowrap", "", "", "nowrap right", "nowrap right", "nowrap right", "nowrap", "nowrap", "nowrap"]) + """
</div>
<div class="grid3" style="margin-top:16px">
 <div class="chart"><h3>复发次数按类型 <span>近 90 天</span></h3><div class="bars"><i style="height:95%"></i><i style="height:70%"></i><i style="height:52%"></i><i style="height:38%"></i><i style="height:24%"></i></div>
  <div class="legend"><span>非法排放</span><span>岸线垃圾</span><span>漂浮物</span><span>设施损坏</span><span>水色异常</span></div></div>
 <div class="chart"><h3>结果等级分布 <span>共 24 个断面</span></h3><div class="bars"><i style="height:20%"></i><i style="height:38%"></i><i style="height:88%"></i></div>
  <div class="legend"><span>高 2</span><span>中 3</span><span>低 19</span></div></div>
 <div class="chart"><h3>人工调整率趋势 <span>近 6 个月</span></h3><div class="line"><svg viewBox="0 0 300 110" preserveAspectRatio="none">
  <polyline points="0,30 50,42 100,50 150,58 200,64 250,70 300,72" fill="none" stroke="#2D5B6B" stroke-width="2"/><line x1="0" y1="108" x2="300" y2="108" stroke="#DCE5E8"/></svg></div>
  <div class="legend"><span><i style="background:#2D5B6B"></i>调整率</span></div></div>
</div>"""

PAGES_CONTENT["rule-config.html"] = """
<h1 class="page">热点识别规则配置</h1><p class="subtitle">权重合计必须等于 100%，每次修改生成新版本并记录生效时间</p>
<div class="grid2"><div>
<div class="card"><div class="card-hd"><h2>当前规则 v3</h2><span class="hint">生效 2026-09-01 00:00 · 创建人 张启明</span></div>
""" + table(["输入因素", "数据来源", "缺失处理", "权重"],
            [["河段位置", "river_section.area", "不参与计算并提示补录", "15%"],
             ["问题类型", "river_issue.issue_type", "不参与计算并提示补录", "20%"],
             ["近 90 天次数", "river_issue 聚合", "按 0 计并标注", "25%"],
             ["处置时长", "派单至关闭时长", "按平均时长估算", "15%"],
             ["复核结果", "review_record.pass", "按未通过计", "15%"],
             ["水质变化", "water_quality_record", "不参与计算并提示补录", "10%"]], ["", "", "", "nowrap right"]) + """
<div style="display:flex;justify-content:space-between;align-items:center;margin-top:12px">
 <span style="font-size:13px">权重合计：<b class="num" style="color:#2D7A58">100%</b></span>
 <div style="display:flex;gap:8px"><button class="btn">查看历史版本</button><button class="btn primary">保存为新版本</button></div></div>
</div>
<div class="card"><div class="card-hd"><h2>阈值设置</h2></div>
<div class="filter">
 <div class="f"><label>高风险阈值</label><input class="inp" value="75" style="width:110px"></div>
 <div class="f"><label>中风险阈值</label><input class="inp" value="50" style="width:110px"></div>
 <div class="f"><label>统计窗口（天）</label><input class="inp" value="90" style="width:110px"></div>
 <div class="f"><label>次数满分线</label><input class="inp" value="5" style="width:110px"></div>
</div>
<div class="note">修改权重后仅影响新计算或主动重新计算的数据；历史计算结果保留原规则版本快照，不可覆盖。</div></div>
</div>
<div>
<div class="card"><div class="card-hd"><h2>版本记录</h2></div>
""" + table(["版本", "生效时间", "修改人", "变更说明", "状态"],
            [["v3", "2026-09-01", "张启明", "提高次数权重 20%→25%", tag(4, "启用")],
             ["v2", "2026-06-15", "张启明", "新增水质变化因素", tag(5, "历史")],
             ["v1", "2026-03-01", "系统初始化", "初始规则", tag(5, "历史")]], ["nowrap", "nowrap", "nowrap", "", "nowrap"]) + """
</div>
<div class="card"><div class="card-hd"><h2>计算公式说明</h2></div>
<pre style="font-family:ui-monospace,Menlo,monospace;font-size:12px;background:#F3F7F8;padding:12px;border-radius:4px;overflow:auto;line-height:1.9">总分 = Σ(因素归一化得分 × 权重)
  position = 敏感区? 1.0 : 0.6
  type     = 非法排放 1.0 / 水色异常 0.8 / 岸线垃圾 0.6 ...
  count    = min(近90天次数 / 5, 1)
  duration = min(平均处置时长 / 60h, 1)
  review   = 1 - 通过率
  quality  = 水质恶化程度(0~1)
等级：总分 ≥ 75 高；≥ 50 中；否则低
推荐：高 → 纳入专项治理；中 → 加密巡查；低 → 常规管理</pre>
<div class="note">计算过程逐项落库（river_patrol_score），保存输入快照、规则版本、各项得分与生成时间，保证可追溯。</div></div>
</div></div>"""

PAGES_CONTENT["sys.html"] = """
<h1 class="page">用户与权限</h1><p class="subtitle">菜单、按钮、数据范围三层权限；角色按需分配菜单</p>
<div class="card" style="padding:0"><div style="display:flex;gap:4px;padding:12px 16px 0;border-bottom:1px solid #DCE5E8">
 <span style="padding:8px 14px;border-bottom:2px solid #15344A;color:#15344A;font-weight:500;font-size:13px">用户管理</span>
 <span style="padding:8px 14px;color:#5F7078;font-size:13px">角色管理</span>
 <span style="padding:8px 14px;color:#5F7078;font-size:13px">菜单管理</span>
 <span style="padding:8px 14px;color:#5F7078;font-size:13px">部门管理</span>
 <span style="padding:8px 14px;color:#5F7078;font-size:13px">操作日志</span></div>
<div style="padding:16px">
<div class="filter">
 <div class="f"><label>姓名/账号</label><input class="inp wide" placeholder="输入姓名或账号"></div>
 <div class="f"><label>角色</label><select class="sel"><option>全部角色</option><option>巡查员</option><option>调度员</option></select></div>
 <div class="f"><label>部门</label><select class="sel"><option>全部部门</option></select></div>
 <div class="f"><label>状态</label><select class="sel"><option>全部</option><option>启用</option></select></div>
 <button class="btn primary">查询</button>
 <button class="btn primary" style="margin-left:auto">新增用户</button>
</div>
""" + table(["账号", "姓名", "角色", "部门", "数据范围", "状态", "最近登录", "操作"],
            [["admin", "系统管理员", "管理员", "河长办", "全部", tag(4, "启用"), "2026-10-31 17:02", "编辑 重置密码"],
             ["zhouzy", "周志远", "河道巡查员", "城东片区", "本人", tag(4, "启用"), "2026-10-31 16:40", "编辑 停用"],
             ["zhangqm", "张启明", "河长办调度员", "河长办", "本部门", tag(4, "启用"), "2026-10-31 15:20", "编辑 停用"],
             ["liuhb", "刘宏伟", "处置单位人员", "园区管委会", "本部门", tag(4, "启用"), "2026-10-31 09:12", "编辑 停用"],
             ["zhaomin", "赵敏", "复查人员", "河长办", "本部门", tag(4, "启用"), "2026-10-30 18:05", "编辑 停用"],
             ["chenli", "陈立", "河道巡查员", "城西片区", "本人", tag(5, "停用"), "2026-09-28 11:30", "编辑 启用"]],
            ["nowrap", "nowrap", "nowrap", "nowrap", "nowrap", "nowrap", "nowrap", "nowrap"]) + pager(18) + """
</div></div>
<div class="grid2" style="margin-top:16px">
<div class="card"><div class="card-hd"><h2>为角色分配菜单 · 河道巡查员</h2><span class="hint">勾选即授权，未授权菜单不出现在导航</span></div>
""" + table(["菜单", "类型", "权限标识", "已授权"],
            [["水环境热点看板", "菜单", "dashboard:view", "✓"], ["河道断面", "菜单", "section:list", "✓"],
             ["计划任务", "菜单", "task:list", "✓"], ["巡查记录录入", "按钮", "task:record", "✓"],
             ["问题上报", "菜单", "issue:report", "✓"], ["调度派单", "菜单", "dispatch:list", "—"],
             ["规则配置", "菜单", "rule:config", "—"]], ["", "nowrap", "nowrap", "nowrap"]) + """
<div style="margin-top:10px;display:flex;gap:8px;justify-content:flex-end"><button class="btn">重置</button><button class="btn primary">保存授权</button></div></div>
<div class="card"><div class="card-hd"><h2>数据范围规则</h2></div>
<ul style="font-size:13px;line-height:2;padding-left:18px">
<li>巡查员：仅本人创建、本人负责的巡查任务与问题单</li>
<li>调度员：本部门（河长办）全部单据，可跨部门派单</li>
<li>处置单位人员：本单位被派发的处置任务</li>
<li>复查人员：本部门待复查问题单，不可复核本人处置的单据</li>
<li>管理员：按授权组织范围查看全部数据</li></ul>
<div class="note">只有菜单权限不能直接调用写接口，后端对每个写操作单独校验按钮权限与数据范围。</div></div>
</div>"""


def login_page():
    return """<!DOCTYPE html><html lang="zh-CN"><head><meta charset="utf-8"><title>登录 · 河道巡查与水环境问题处置系统</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:-apple-system,"PingFang SC","Microsoft YaHei",sans-serif;background:#0F2A3A;min-height:100vh;display:flex;color:#1F2D33}
.left{flex:1.15;position:relative;background:linear-gradient(160deg,#15344A 0%,#1D4A5E 55%,#237A8B 100%);color:#fff;padding:64px 72px;display:flex;flex-direction:column;justify-content:space-between;overflow:hidden}
.left .brand{display:flex;align-items:center;gap:10px;font-size:15px;font-weight:600;letter-spacing:.5px}
.left .brand i{width:10px;height:10px;background:#57C4C9;border-radius:50%;display:block}
.left h1{font-size:34px;line-height:1.45;font-weight:600;margin-bottom:16px;letter-spacing:.5px}
.left p{font-size:14px;color:rgba(255,255,255,.72);line-height:1.9;max-width:460px}
.left .meta{font-size:12px;color:rgba(255,255,255,.5);display:flex;gap:24px}
.wave{position:absolute;left:0;right:0;bottom:0;opacity:.5}
.right{width:520px;background:#F3F7F8;display:flex;align-items:center;justify-content:center;padding:40px}
.card{width:100%;max-width:380px}
.card h2{font-size:22px;margin-bottom:6px;color:#15344A}
.card .sub{font-size:13px;color:#5F7078;margin-bottom:28px}
.f{margin-bottom:16px}
.f label{display:block;font-size:13px;color:#5F7078;margin-bottom:6px}
.f input{width:100%;height:42px;border:1px solid #DCE5E8;border-radius:4px;padding:0 12px;font-size:14px;background:#fff;font-family:inherit}
.f input:focus{outline:none;border-color:#237A8B;box-shadow:0 0 0 3px rgba(35,122,139,.12)}
.row{display:flex;justify-content:space-between;align-items:center;font-size:13px;color:#5F7078;margin-bottom:22px}
.row a{color:#2D5B6B;text-decoration:none}
.btn{width:100%;height:44px;background:#15344A;color:#fff;border:none;border-radius:4px;font-size:15px;cursor:pointer;font-family:inherit}
.btn:hover{background:#1C425C}
.tip{margin-top:18px;font-size:12px;color:#8B9AA1;line-height:1.8}
.roles{display:flex;flex-wrap:wrap;gap:6px;margin-top:14px}
.roles span{font-size:11px;color:#2D5B6B;background:#E8F1F3;padding:4px 8px;border-radius:3px}
</style></head><body>
<div class="left">
  <div class="brand"><i></i>河长制信息化 · 水环境巡查处置平台</div>
  <div>
    <h1>巡河有痕<br>问题有单 处置有据</h1>
    <p>覆盖河道断面档案、周期与临时巡查、快速水质录入、问题派单督办、整改跟踪与复查销号全流程，并以问题复发热点识别辅助专项治理决策。</p>
    <div class="roles"><span>河道巡查员</span><span>河长办调度员</span><span>处置单位</span><span>复查人员</span><span>管理员</span></div>
  </div>
  <svg class="wave" viewBox="0 0 600 120" preserveAspectRatio="none" height="120"><path d="M0 60 Q75 30 150 60 T300 60 T450 60 T600 60 V120 H0Z" fill="rgba(87,196,201,.18)"/><path d="M0 80 Q75 52 150 80 T300 80 T450 80 T600 80 V120 H0Z" fill="rgba(87,196,201,.12)"/></svg>
  <div class="meta"><span>数据由巡查员现场录入</span><span>不接入实时水质设备</span></div>
</div>
<div class="right"><div class="card">
  <h2>登录</h2><p class="sub">请使用河长办分配的账号登录</p>
  <form onsubmit="return false">
    <div class="f"><label>账号</label><input value="admin" placeholder="请输入账号"></div>
    <div class="f"><label>密码</label><input type="password" value="admin123" placeholder="请输入密码"></div>
    <div class="row"><label><input type="checkbox" checked> 记住账号</label><a href="#">忘记密码？</a></div>
    <button class="btn" onclick="location.href='dashboard.html'">登 录</button>
  </form>
  <div class="tip">默认管理员：admin / admin123<br>连续 5 次密码错误将锁定 10 分钟。所有账号密码均以 BCrypt 存储。</div>
</div></div></body></html>"""


if __name__ == "__main__":
    (PAGES / "login.html").write_text(login_page(), encoding="utf-8")
    meta = {"dashboard.html": ("水环境热点看板", "工作台"),
            "section-list.html": ("河道断面档案", "河道档案"),
            "section-detail.html": ("断面详情", "河道档案"),
            "task-list.html": ("巡查计划任务", "巡查管理"),
            "task-execute.html": ("巡查记录录入", "巡查管理"),
            "issue-report.html": ("问题上报", "问题处置"),
            "dispatch.html": ("调度派单台", "问题处置"),
            "disposal.html": ("整改跟踪", "问题处置"),
            "review.html": ("复核销号", "问题处置"),
            "hotspot.html": ("水环境热点看板", "统计分析"),
            "rule-config.html": ("热点识别规则配置", "统计分析"),
            "sys.html": ("用户与权限", "系统管理")}
    for name, (title, crumb) in meta.items():
        role = {"section-detail.html": "河道巡查员 周志远", "task-execute.html": "河道巡查员 周志远",
                "issue-report.html": "河道巡查员 周志远", "disposal.html": "处置单位 刘宏伟",
                "review.html": "复查人员 赵敏"}.get(name, "河长办调度员 张启明")
        (PAGES / name).write_text(shell(title, crumb, name, PAGES_CONTENT[name], role), encoding="utf-8")
        print("ok", name)
