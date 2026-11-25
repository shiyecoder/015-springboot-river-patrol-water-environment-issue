#!/usr/bin/env python3
# 生成 sql/init.sql：建库建表 + 真实分布测试数据（时间跨度近 6 个月）
import pathlib, datetime, random

random.seed(20261031)
OUT = pathlib.Path(__file__).with_name("init.sql")
NOW = datetime.datetime(2026, 10, 31, 17, 0, 0)


def ts(d):
    return d.strftime("%Y-%m-%d %H:%M:%S")


def q(s):
    if s is None:
        return "NULL"
    return "'" + str(s).replace("\\", "\\\\").replace("'", "''") + "'"


DDL = r"""
DROP DATABASE IF EXISTS new_015;
CREATE DATABASE new_015 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE new_015;

-- ========== 组织与权限 ==========
CREATE TABLE sys_dept (
  id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '部门ID',
  name VARCHAR(64) NOT NULL COMMENT '部门名称',
  parent_id BIGINT DEFAULT 0 COMMENT '上级部门',
  sort INT DEFAULT 0 COMMENT '排序',
  create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间'
) COMMENT '部门表';

CREATE TABLE sys_role (
  id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '角色ID',
  code VARCHAR(32) NOT NULL UNIQUE COMMENT '角色编码',
  name VARCHAR(64) NOT NULL COMMENT '角色名称',
  data_scope VARCHAR(16) NOT NULL DEFAULT 'SELF' COMMENT '数据范围 ALL/DEPT/SELF',
  remark VARCHAR(200) COMMENT '说明',
  create_time DATETIME DEFAULT CURRENT_TIMESTAMP
) COMMENT '角色表';

CREATE TABLE sys_user (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  username VARCHAR(50) NOT NULL UNIQUE COMMENT '账号',
  password VARCHAR(100) NOT NULL COMMENT 'BCrypt 密码',
  real_name VARCHAR(50) NOT NULL COMMENT '姓名',
  phone VARCHAR(20) COMMENT '手机号',
  avatar VARCHAR(200) COMMENT '头像相对路径',
  dept_id BIGINT COMMENT '部门ID',
  role_code VARCHAR(32) NOT NULL COMMENT '角色编码',
  status TINYINT DEFAULT 1 COMMENT '1启用 0停用',
  last_login DATETIME COMMENT '最近登录',
  create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
  deleted TINYINT DEFAULT 0
) COMMENT '用户表';
CREATE INDEX idx_user_dept ON sys_user(dept_id);
CREATE INDEX idx_user_role ON sys_user(role_code);

CREATE TABLE sys_menu (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  parent_id BIGINT DEFAULT 0 COMMENT '上级菜单',
  name VARCHAR(64) NOT NULL COMMENT '菜单名称',
  path VARCHAR(120) COMMENT '路由地址',
  component VARCHAR(120) COMMENT '前端组件',
  icon VARCHAR(40) COMMENT '图标标识',
  perm VARCHAR(80) COMMENT '权限标识',
  type CHAR(1) DEFAULT 'M' COMMENT 'M菜单 B按钮',
  sort INT DEFAULT 0,
  visible TINYINT DEFAULT 1 COMMENT '1显示 0隐藏'
) COMMENT '菜单表';

CREATE TABLE sys_role_menu (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  role_id BIGINT NOT NULL,
  menu_id BIGINT NOT NULL COMMENT '菜单ID（不含菜单管理项）',
  UNIQUE KEY uk_role_menu (role_id, menu_id)
) COMMENT '角色菜单关联表';

CREATE TABLE sys_message (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  title VARCHAR(120) NOT NULL,
  content VARCHAR(400) COMMENT '消息内容，含业务编号',
  type VARCHAR(20) COMMENT 'APPROVE/TIMEOUT/REJECT/REVIEW/DONE',
  biz_no VARCHAR(40) COMMENT '业务编号',
  biz_id BIGINT COMMENT '业务ID，用于详情跳转',
  receiver_id BIGINT NOT NULL COMMENT '接收人',
  is_read TINYINT DEFAULT 0,
  create_time DATETIME DEFAULT CURRENT_TIMESTAMP
) COMMENT '站内消息表';
CREATE INDEX idx_msg_receiver ON sys_message(receiver_id, is_read);

CREATE TABLE sys_file (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  file_name VARCHAR(200) NOT NULL COMMENT '原始文件名',
  path VARCHAR(300) NOT NULL COMMENT '相对路径',
  size BIGINT COMMENT '字节数',
  content_type VARCHAR(80),
  uploader_id BIGINT,
  create_time DATETIME DEFAULT CURRENT_TIMESTAMP
) COMMENT '上传文件表（仅存相对路径，不存外链）';

CREATE TABLE sys_log (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  user_id BIGINT,
  username VARCHAR(50),
  module VARCHAR(40) COMMENT '业务模块',
  action VARCHAR(60) COMMENT '操作',
  biz_no VARCHAR(40) COMMENT '业务编号',
  before_status VARCHAR(20) COMMENT '变更前状态',
  after_status VARCHAR(20) COMMENT '变更后状态',
  reason VARCHAR(300) COMMENT '原因（驳回/退回必填≥5字）',
  ip VARCHAR(40),
  create_time DATETIME DEFAULT CURRENT_TIMESTAMP
) COMMENT '操作日志（状态流转留痕）';
CREATE INDEX idx_log_biz ON sys_log(biz_no);

-- ========== 河道档案 ==========
CREATE TABLE river (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  code VARCHAR(30) NOT NULL UNIQUE COMMENT '河流编码',
  name VARCHAR(60) NOT NULL COMMENT '河流名称',
  length_km DECIMAL(6,2) COMMENT '全长 km',
  area VARCHAR(40) COMMENT '所属区域',
  level VARCHAR(20) COMMENT '河道等级',
  manager VARCHAR(30) COMMENT '河长',
  phone VARCHAR(20),
  intro VARCHAR(500),
  create_time DATETIME DEFAULT CURRENT_TIMESTAMP
) COMMENT '河流表';

CREATE TABLE river_section (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  code VARCHAR(50) NOT NULL COMMENT '断面编号（唯一，≤50字符）',
  name VARCHAR(80) NOT NULL COMMENT '断面名称',
  river_id BIGINT NOT NULL,
  start_point VARCHAR(120) COMMENT '起点位置',
  end_point VARCHAR(120) COMMENT '终点位置',
  length_km DECIMAL(6,2) COMMENT '断面长度 km',
  area VARCHAR(40) NOT NULL COMMENT '所属区域',
  water_quality_level VARCHAR(10) COMMENT '水质等级字典值',
  patrol_route VARCHAR(300) NOT NULL COMMENT '巡查路线',
  manager VARCHAR(30) NOT NULL COMMENT '责任人',
  patrol_freq VARCHAR(100) COMMENT '巡查频次（≤100字符）',
  status VARCHAR(20) DEFAULT '正常' COMMENT '断面状态字典值',
  cover_image VARCHAR(200) COMMENT '现场图片相对路径',
  longitude DECIMAL(10,6),
  latitude DECIMAL(10,6),
  create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
  update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  deleted TINYINT DEFAULT 0,
  version INT DEFAULT 0 COMMENT '乐观锁版本号',
  UNIQUE KEY uk_section_code (code),
  KEY idx_section_river (river_id),
  KEY idx_section_area (area)
) COMMENT '河道断面主档';

CREATE TABLE patrol_point (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  section_id BIGINT NOT NULL,
  name VARCHAR(80) NOT NULL COMMENT '点位名称',
  type VARCHAR(20) NOT NULL COMMENT '巡查点/排口/关键设施',
  longitude DECIMAL(10,6),
  latitude DECIMAL(10,6),
  facility VARCHAR(120) COMMENT '关键设施',
  status VARCHAR(20) DEFAULT '正常',
  sort INT DEFAULT 0,
  KEY idx_point_section (section_id)
) COMMENT '巡查点与排口';

-- ========== 巡查 ==========
CREATE TABLE river_task (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  code VARCHAR(40) NOT NULL UNIQUE COMMENT '任务编号',
  title VARCHAR(120) NOT NULL,
  section_id BIGINT NOT NULL,
  task_type VARCHAR(20) NOT NULL COMMENT '周期任务/临时任务',
  cycle_type VARCHAR(20) COMMENT '每周2次/每日1次等',
  assignee_id BIGINT NOT NULL COMMENT '巡查员',
  deadline DATETIME NOT NULL COMMENT '完成时限',
  finish_time DATETIME COMMENT '完成时间',
  status VARCHAR(20) DEFAULT '待执行' COMMENT '待执行/执行中/已完成/已逾期',
  remark VARCHAR(300),
  create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
  KEY idx_task_section (section_id),
  KEY idx_task_assignee (assignee_id, status)
) COMMENT '巡查任务表';

CREATE TABLE water_quality_record (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  task_id BIGINT,
  section_id BIGINT NOT NULL,
  point_id BIGINT,
  ph DECIMAL(4,1) COMMENT 'pH',
  turbidity DECIMAL(6,1) COMMENT '浊度 NTU',
  dissolved_oxygen DECIMAL(5,1) COMMENT '溶解氧 mg/L',
  level VARCHAR(10) COMMENT '判定水质等级',
  record_time DATETIME NOT NULL,
  recorder_id BIGINT NOT NULL,
  image VARCHAR(200) COMMENT '现场图片相对路径',
  remark VARCHAR(200),
  create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
  KEY idx_wq_section_time (section_id, record_time)
) COMMENT '快速水质记录';

-- ========== 问题与处置 ==========
CREATE TABLE river_issue (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  code VARCHAR(40) NOT NULL UNIQUE COMMENT '问题编号',
  title VARCHAR(150) NOT NULL,
  section_id BIGINT NOT NULL,
  point_id BIGINT,
  issue_type VARCHAR(30) NOT NULL COMMENT '非法排放/水面漂浮物/岸线垃圾/设施损坏/水色异常',
  level VARCHAR(10) NOT NULL COMMENT '重大/一般',
  longitude DECIMAL(10,6),
  latitude DECIMAL(10,6),
  description VARCHAR(600) NOT NULL,
  impact_scope VARCHAR(300) NOT NULL COMMENT '影响范围',
  image VARCHAR(300) COMMENT '证据图片相对路径（多张逗号分隔）',
  reporter_id BIGINT NOT NULL,
  report_time DATETIME NOT NULL,
  status VARCHAR(20) NOT NULL DEFAULT '待确认' COMMENT '待确认/待派单/处置中/待复查/已关闭/无效上报',
  deadline DATETIME COMMENT '处置期限',
  dept_id BIGINT COMMENT '责任单位',
  supervise TINYINT DEFAULT 0 COMMENT '是否督办',
  temp_measure VARCHAR(300) COMMENT '临时措施（重大问题必填）',
  parent_issue_id BIGINT COMMENT '关联的历史问题（复发建新单）',
  dispose_time DATETIME COMMENT '完成处置时间',
  close_time DATETIME COMMENT '关闭时间',
  create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
  update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  deleted TINYINT DEFAULT 0,
  version INT DEFAULT 0,
  KEY idx_issue_section (section_id),
  KEY idx_issue_status (status),
  KEY idx_issue_report (report_time)
) COMMENT '巡查问题单';

CREATE TABLE disposal_progress (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  issue_id BIGINT NOT NULL,
  dept_id BIGINT,
  reporter_id BIGINT NOT NULL COMMENT '处置单位上报人',
  stage VARCHAR(60) NOT NULL COMMENT '阶段',
  content VARCHAR(600) NOT NULL COMMENT '处置内容',
  person_count INT DEFAULT 0 COMMENT '处置人数',
  material VARCHAR(300) COMMENT '物资',
  cost DECIMAL(10,2) DEFAULT 0 COMMENT '费用',
  result VARCHAR(300) COMMENT '阶段结果',
  images VARCHAR(300) COMMENT '整改凭证相对路径',
  progress_time DATETIME NOT NULL,
  create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
  KEY idx_dp_issue (issue_id)
) COMMENT '整改进度';

CREATE TABLE review_record (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  issue_id BIGINT NOT NULL,
  reviewer_id BIGINT NOT NULL,
  review_time DATETIME NOT NULL,
  water_color VARCHAR(20) COMMENT '现场水色',
  smell VARCHAR(20) COMMENT '气味',
  ph DECIMAL(4,1),
  turbidity DECIMAL(6,1),
  dissolved_oxygen DECIMAL(5,1),
  conclusion VARCHAR(500) NOT NULL COMMENT '复核结论',
  pass TINYINT NOT NULL COMMENT '1通过 0驳回',
  reason VARCHAR(300) COMMENT '驳回原因（≥5字）',
  images VARCHAR(300),
  create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
  KEY idx_review_issue (issue_id)
) COMMENT '复查记录';

-- ========== 创新点：问题复发热点识别 ==========
CREATE TABLE river_patrol_rule (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(60) NOT NULL,
  version VARCHAR(20) NOT NULL COMMENT '规则版本号',
  weight_position DECIMAL(5,2) NOT NULL DEFAULT 15 COMMENT '河段位置权重%',
  weight_type DECIMAL(5,2) NOT NULL DEFAULT 20 COMMENT '问题类型权重%',
  weight_count DECIMAL(5,2) NOT NULL DEFAULT 25 COMMENT '近90天次数权重%',
  weight_duration DECIMAL(5,2) NOT NULL DEFAULT 15 COMMENT '处置时长权重%',
  weight_review DECIMAL(5,2) NOT NULL DEFAULT 15 COMMENT '复核结果权重%',
  weight_quality DECIMAL(5,2) NOT NULL DEFAULT 10 COMMENT '水质变化权重%',
  threshold_high DECIMAL(5,2) NOT NULL DEFAULT 75 COMMENT '高风险阈值',
  threshold_mid DECIMAL(5,2) NOT NULL DEFAULT 50 COMMENT '中风险阈值',
  window_days INT NOT NULL DEFAULT 90 COMMENT '统计窗口天数',
  count_full INT NOT NULL DEFAULT 5 COMMENT '次数满分线',
  status VARCHAR(10) DEFAULT '启用',
  effective_time DATETIME NOT NULL,
  create_by VARCHAR(30),
  create_time DATETIME DEFAULT CURRENT_TIMESTAMP
) COMMENT '热点识别规则（权重合计必须=100）';

CREATE TABLE river_patrol_score (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  section_id BIGINT NOT NULL,
  rule_id BIGINT NOT NULL,
  rule_version VARCHAR(20) NOT NULL COMMENT '计算时使用的规则版本',
  input_snapshot VARCHAR(1000) NOT NULL COMMENT '输入快照JSON',
  score_position DECIMAL(6,2) DEFAULT 0,
  score_type DECIMAL(6,2) DEFAULT 0,
  score_count DECIMAL(6,2) DEFAULT 0,
  score_duration DECIMAL(6,2) DEFAULT 0,
  score_review DECIMAL(6,2) DEFAULT 0,
  score_quality DECIMAL(6,2) DEFAULT 0,
  total_score DECIMAL(6,2) NOT NULL,
  level VARCHAR(10) NOT NULL COMMENT '高/中/低',
  recommend VARCHAR(40) NOT NULL COMMENT '推荐措施',
  factors VARCHAR(600) COMMENT '主要影响因素',
  unmet VARCHAR(600) COMMENT '未满足条件',
  suggestions VARCHAR(600) COMMENT '可改进项',
  calc_time DATETIME NOT NULL,
  manual_level VARCHAR(10) COMMENT '人工调整后的等级',
  manual_reason VARCHAR(300) COMMENT '人工调整原因',
  adjust_user VARCHAR(30),
  adjust_time DATETIME,
  KEY idx_score_section (section_id, calc_time)
) COMMENT '热点识别计算留痕';
"""

# ---------- 基础数据 ----------
DEPT = [(1, "河长制办公室", 0), (2, "城东片区工作组", 1), (3, "城南片区工作组", 1),
        (4, "城西片区工作组", 1), (5, "城北片区工作组", 1), (6, "园区管委会", 0),
        (7, "水务集团", 0), (8, "环卫中心", 0), (9, "生态环境分局", 0)]

ROLE = [("admin", "管理员", "ALL"), ("dispatcher", "河长办调度员", "DEPT"),
        ("patroller", "河道巡查员", "SELF"), ("handler", "处置单位人员", "DEPT"),
        ("reviewer", "复查人员", "DEPT")]

USERS = [
    ("admin", "系统管理员", "13800000001", 1, "admin", "/uploads/seed/avatar/02.jpg"),
    ("zhangqm", "张启明", "13800000002", 1, "dispatcher", "/uploads/seed/avatar/02.jpg"),
    ("liuyj", "刘雅静", "13800000003", 1, "dispatcher", "/uploads/seed/avatar/03.jpg"),
    ("zhouzy", "周志远", "13800000004", 2, "patroller", "/uploads/seed/avatar/01.jpg"),
    ("chenli", "陈立", "13800000005", 4, "patroller", "/uploads/seed/avatar/01.jpg"),
    ("wangq", "王倩", "13800000006", 5, "patroller", "/uploads/seed/avatar/03.jpg"),
    ("liuhb", "刘宏伟", "13800000007", 6, "handler", "/uploads/seed/avatar/04.jpg"),
    ("huanghx", "黄海星", "13800000008", 7, "handler", "/uploads/seed/avatar/04.jpg"),
    ("zhaomin", "赵敏", "13800000009", 1, "reviewer", "/uploads/seed/avatar/03.jpg"),
    ("sunyq", "孙玉清", "13800000010", 1, "reviewer", "/uploads/seed/avatar/02.jpg"),
]

# 菜单：id, parent, name, path, component, icon, perm, type, sort, visible
MENU = [
    (1, 0, "水环境热点看板", "/dashboard", "Dashboard", "dashboard", "dashboard:view", "M", 1, 1),
    (2, 0, "河道档案", "/section", "Section", "river", "section:list", "M", 2, 1),
    (3, 2, "断面详情", "/section/:id", "SectionDetail", "point", "section:detail", "M", 1, 0),
    (4, 0, "巡查管理", "/task", "Task", "task", "task:list", "M", 3, 1),
    (5, 4, "巡查记录录入", "/task/:id/execute", "TaskExecute", "water", "task:record", "M", 1, 0),
    (6, 0, "问题上报", "/issue", "Issue", "issue", "issue:list", "M", 4, 1),
    (7, 0, "调度派单", "/dispatch", "Dispatch", "dispatch", "dispatch:list", "M", 5, 1),
    (8, 0, "整改跟踪", "/disposal", "Disposal", "disposal", "disposal:list", "M", 6, 1),
    (9, 0, "复核销号", "/review", "Review", "review", "review:list", "M", 7, 1),
    (10, 0, "热点分析", "/hotspot", "Hotspot", "chart", "hotspot:view", "M", 8, 1),
    (11, 10, "规则配置", "/rule", "RuleConfig", "rule", "rule:config", "M", 1, 1),
    (12, 0, "系统管理", "/sys", "Sys", "user", "sys:view", "M", 9, 1),
    (13, 12, "用户管理", "/sys/user", "SysUser", "user", "sys:user", "M", 1, 1),
    (14, 12, "角色管理", "/sys/role", "SysRole", "role", "sys:role", "M", 2, 1),
    (15, 12, "菜单管理", "/sys/menu", "SysMenu", "menu", "sys:menu", "M", 3, 0),
    (16, 12, "部门管理", "/sys/dept", "SysDept", "menu", "sys:dept", "M", 4, 1),
    (17, 6, "提交上报", "", "", "", "issue:add", "B", 1, 1),
    (18, 7, "执行派单", "", "", "", "dispatch:do", "B", 1, 1),
    (19, 8, "填报进度", "", "", "", "disposal:add", "B", 1, 1),
    (20, 9, "复核操作", "", "", "", "review:do", "B", 1, 1),
    (21, 11, "保存规则", "", "", "", "rule:save", "B", 1, 1),
    (22, 1, "导出统计", "", "", "", "dashboard:export", "B", 1, 1),
]
ROLE_MENU = {
    "admin": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22],
    "dispatcher": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 17, 18, 19, 20, 21, 22],
    "patroller": [1, 2, 3, 4, 5, 6, 17],
    "handler": [1, 2, 8, 19],
    "reviewer": [1, 2, 3, 7, 8, 9, 10, 20],
}

RIVERS = [(1, "RV-01", "白鹭溪", 8.6, "城东片区", "Ⅲ类", "周志远", "13900000011", "流经城东工业园与老城区，下游汇入青枫河"),
          (2, "RV-02", "青枫河", 12.4, "城南片区", "Ⅳ类", "李慧", "13900000012", "城区主要行洪河道，沿线有湿地公园与南闸口"),
          (3, "RV-03", "石鼓渠", 9.8, "城西片区", "Ⅴ类", "陈立", "13900000013", "农灌与集镇混合功能渠道，雨污分流尚未完成"),
          (4, "RV-04", "东湖连通渠", 6.2, "城北片区", "Ⅳ类", "王倩", "13900000014", "新区景观补水通道，两岸新建绿化"),
          (5, "RV-05", "锦绣河", 7.5, "城中心", "Ⅲ类", "张启明", "13900000015", "中心城区景观河道，人流密集")]

SEC_DEF = [
    ("HD-0012", "白鹭溪·工业园段", 1, "城东片区", "Ⅲ类", "周志远", "每周 2 次", "正常"),
    ("HD-0013", "白鹭溪·老桥段", 1, "城东片区", "Ⅳ类", "周志远", "每周 2 次", "预警"),
    ("HD-0014", "白鹭溪·入河口段", 1, "城东片区", "Ⅳ类", "周志远", "每周 1 次", "正常"),
    ("HD-0015", "白鹭溪·橡胶坝段", 1, "城东片区", "Ⅲ类", "周志远", "每周 1 次", "正常"),
    ("HD-0021", "青枫河·湿地公园段", 2, "城南片区", "Ⅱ类", "李慧", "每周 1 次", "正常"),
    ("HD-0022", "青枫河·南闸口段", 2, "城南片区", "Ⅴ类", "李慧", "每日 1 次", "整治中"),
    ("HD-0023", "青枫河·体育公园段", 2, "城南片区", "Ⅲ类", "李慧", "每周 2 次", "正常"),
    ("HD-0024", "青枫河·工业南区段", 2, "城南片区", "Ⅳ类", "李慧", "每周 2 次", "预警"),
    ("HD-0025", "青枫河·闸站上游段", 2, "城南片区", "Ⅲ类", "李慧", "每周 1 次", "正常"),
    ("HD-0031", "石鼓渠·农灌段", 3, "城西片区", "Ⅳ类", "陈立", "每两周 1 次", "正常"),
    ("HD-0032", "石鼓渠·集镇段", 3, "城西片区", "劣Ⅴ类", "陈立", "每日 1 次", "重点监管"),
    ("HD-0033", "石鼓渠·养殖场段", 3, "城西片区", "Ⅴ类", "陈立", "每周 2 次", "预警"),
    ("HD-0034", "石鼓渠·汇入口段", 3, "城西片区", "Ⅳ类", "陈立", "每周 1 次", "正常"),
    ("HD-0035", "石鼓渠·涵闸段", 3, "城西片区", "Ⅳ类", "陈立", "每两周 1 次", "正常"),
    ("HD-0041", "东湖连通渠·北段", 4, "城北片区", "Ⅲ类", "王倩", "每周 1 次", "正常"),
    ("HD-0042", "东湖连通渠·南段", 4, "城北片区", "Ⅳ类", "王倩", "每周 1 次", "预警"),
    ("HD-0043", "东湖连通渠·泵站段", 4, "城北片区", "Ⅲ类", "王倩", "每周 2 次", "正常"),
    ("HD-0044", "东湖连通渠·景观桥段", 4, "城北片区", "Ⅱ类", "王倩", "每两周 1 次", "正常"),
    ("HD-0045", "东湖连通渠·退水口段", 4, "城北片区", "Ⅳ类", "王倩", "每周 1 次", "正常"),
    ("HD-0051", "锦绣河·中心广场段", 5, "城中心", "Ⅲ类", "张启明", "每日 1 次", "正常"),
    ("HD-0052", "锦绣河·文化街段", 5, "城中心", "Ⅳ类", "张启明", "每日 1 次", "预警"),
    ("HD-0053", "锦绣河·夜市段", 5, "城中心", "Ⅳ类", "张启明", "每日 1 次", "正常"),
    ("HD-0054", "锦绣河·公园东段", 5, "城中心", "Ⅲ类", "张启明", "每周 2 次", "正常"),
    ("HD-0055", "锦绣河·尾水段", 5, "城中心", "Ⅴ类", "张启明", "每周 2 次", "整治中"),
]

POINT_NAMES = [("巡查起点", "巡查点"), ("步道中段", "巡查点"), ("排口 P-07", "排口"),
               ("截污井", "关键设施"), ("巡查终点", "巡查点"), ("雨水排口", "排口")]


def build_sections():
    rows = []
    for i, (code, name, rid, area, lvl, mgr, freq, st) in enumerate(SEC_DEF, 1):
        img = "/uploads/seed/section/%02d.jpg" % (((i * 7) % 6) + 1)
        rows.append((i, code, name, rid, "起点桩号 K0+%03d" % (i * 40), "终点桩号 K0+%03d" % (i * 40 + 180),
                     round(1.2 + (i % 5) * 0.4, 2), area, lvl,
                     "沿%s岸步道自起点巡查至终点，途经排口与关键设施" % name.split("·")[1][:6], mgr, freq, st, img,
                     121.40 + i * 0.0037, 31.20 + i * 0.0021,
                     ts(datetime.datetime(2026, 4, 10 + (i % 20), 9, 30))))
    return rows


def build_points():
    rows, pid = [], 1
    for sid in range(1, 25):
        n = 4 + (sid % 3)
        for k in range(n):
            nm, tp = POINT_NAMES[k % len(POINT_NAMES)]
            rows.append((pid, sid, "%s-%s" % (SEC_DEF[sid - 1][0], nm), tp,
                         121.40 + sid * 0.0037 + k * 0.0004, 31.20 + sid * 0.0021 + k * 0.0002,
                         "护栏、垃圾桶" if tp == "巡查点" else ("在线流量计" if tp == "排口" else "截污井盖"),
                         "预警" if (sid in (2, 6, 11, 12, 16, 21) and k == 2) else "正常", k + 1))
            pid += 1
    return rows


ISSUE_T = [
    ("非法排放", "工业园排口持续性泡沫排放", 1, "重大", "排口 P-07 持续排出灰白色泡沫状废水，下游 30 米水面有明显泡沫带，伴有刺鼻异味。", "下游约 200 米河段，涉及西岸步道亲水平台。"),
    ("岸线垃圾", "老桥下岸线垃圾堆积约 30㎡", 2, "一般", "桥下隐蔽处堆积生活垃圾与枯枝，约 30 平方米，紧邻亲水步道。", "沿岸线 60 米范围，影响步道通行与观感。"),
    ("水面漂浮物", "湿地公园段水面漂浮物聚集", 5, "一般", "公园东侧水面聚集大量浮萍与水草，覆盖面积约 120 平方米。", "湿地公园景观水域约 300 平方米。"),
    ("水色异常", "南闸口氨氮异常，水色发黑", 6, "重大", "闸前水体发黑并伴有明显臭味，快速检测氨氮超标，疑似上游污水直排。", "闸前 400 米河段，下游为饮用水源二级保护区边界。"),
    ("设施损坏", "农灌段护栏缺失 12 米", 10, "一般", "渠道东岸防护栏缺失约 12 米，缺口紧邻农田机耕道，存在坠落风险。", "农灌段东岸 12 米范围，涉及 3 户农田通行。"),
    ("非法排放", "集镇段生活污水直排", 11, "重大", "集镇沿河两处住户污水管直接接入河道，水面有灰白色污水带。", "集镇段 500 米河段，涉及沿河 26 户居民。"),
    ("水面漂浮物", "北段水面油膜", 15, "一般", "北段景观桥附近水面出现片状油膜，面积约 20 平方米。", "景观桥上下游各 50 米。"),
    ("岸线垃圾", "南段疑似偷倒建筑渣土", 16, "一般", "岸边发现新倾倒建筑渣土约 8 立方米，无明显来源标识。", "南段右岸 15 米岸线。"),
    ("设施损坏", "泵站段警示牌倾倒", 17, "一般", "泵站进水口警示牌被车辆撞倒，基座松动。", "泵站进水口周边 5 米。"),
    ("水色异常", "景观桥段水体发绿", 18, "一般", "景观桥下水体呈明显绿色，透明度下降，疑为藻类繁殖。", "景观桥至退水口 200 米。"),
    ("岸线垃圾", "中心广场段绿化带垃圾", 20, "一般", "广场段绿化带内散落塑料瓶与包装袋，约 15 米范围。", "广场段左岸 15 米。"),
    ("非法排放", "文化街段餐饮废水入河", 21, "一般", "沿河餐饮商户将洗碗水直接倒入河道，水面有油花。", "文化街段 80 米河段。"),
    ("水面漂浮物", "夜市段水面漂浮塑料袋", 22, "一般", "夜市结束后水面漂浮大量塑料袋与餐盒。", "夜市段 120 米河段。"),
    ("设施损坏", "尾水段护岸塌陷", 24, "重大", "护岸石砌体局部塌陷约 6 米，河岸土体裸露。", "尾水段右岸 6 米，临近人行通道。"),
    ("水色异常", "入河口段水体浑浊", 3, "一般", "入河口处水体浑浊，悬浮物明显增多。", "入河口上下游 100 米。"),
    ("非法排放", "养殖场段粪污渗漏", 12, "重大", "养殖场化粪池渗漏，渠边可见粪污痕迹并伴有强烈臭味。", "养殖场段 300 米渠道，下游为农灌取水口。"),
    ("岸线垃圾", "涵闸段闸前垃圾聚集", 14, "一般", "涵闸闸前聚集塑料瓶、泡沫板等垃圾约 5 立方米。", "涵闸前 30 米范围。"),
    ("水面漂浮物", "退水口段浮渣带", 19, "一般", "退水口下游形成长约 80 米浮渣带。", "退水口下游 80 米。"),
    ("设施损坏", "体育公园段座椅损坏", 7, "一般", "亲水平台两处座椅木板断裂，存在安全隐患。", "体育公园段亲水平台。"),
    ("水色异常", "工业南区段水体发红", 8, "重大", "水体呈异常红褐色，疑为工业染料废水排放。", "工业南区段 300 米，下游为农灌渠。"),
    ("岸线垃圾", "闸站上游段水草堆积", 9, "一般", "闸站上游左岸水草与垃圾混合堆积。", "闸站上游 40 米。"),
    ("非法排放", "橡胶坝段夜间偷排", 4, "重大", "夜间巡查发现橡胶坝下游有暗管排放，水体发灰。", "橡胶坝下游 250 米。"),
    ("水面漂浮物", "汇入口段水葫芦蔓延", 13, "一般", "汇入口水面水葫芦蔓延约 200 平方米。", "汇入口 200 米渠道。"),
    ("设施损坏", "公园东段护栏锈蚀", 23, "一般", "公园东段护栏立柱锈蚀严重，3 处松动。", "公园东段 40 米岸线。"),
    ("水色异常", "中心广场段水华", 20, "一般", "高温后中心广场段出现水华，水面有绿色浮沫。", "广场段 200 米。"),
    ("岸线垃圾", "湿地公园段游客垃圾", 5, "一般", "周末游客遗留垃圾散落岸边。", "公园东岸 30 米。"),
    ("非法排放", "集镇段洗车废水", 11, "一般", "洗车点废水沿路面流入河道。", "集镇段 20 米岸线。"),
    ("水面漂浮物", "老桥段浮萍聚集", 2, "一般", "桥墩背水面浮萍聚集，面积约 40 平方米。", "老桥上下游 60 米。"),
    ("设施损坏", "农灌段闸门启闭异常", 10, "一般", "手动启闭机卡阻，闸门无法完全闭合。", "农灌段节制闸。"),
    ("水色异常", "尾水段水体发黑", 24, "重大", "尾水段水体发黑并有臭味，疑与上游管网溢流有关。", "尾水段 300 米。"),
    ("岸线垃圾", "南闸口段渔网丢弃", 6, "一般", "岸边发现废弃渔网与地笼。", "南闸口段 50 米。"),
    ("水面漂浮物", "文化街段落叶堆积", 21, "一般", "秋季落叶在水面回水区堆积。", "文化街段回水区 30 米。"),
]

ISSUE_STATUS_PLAN = (["已关闭"] * 12 + ["待复查"] * 5 + ["处置中"] * 6 + ["待派单"] * 4 +
                     ["待确认"] * 3 + ["无效上报"] * 2)
DEPTS_HANDLE = [6, 7, 8, 6, 7, 8, 6, 7]
PATROLLERS = [4, 5, 6, 4]
REVIEWERS = [9, 10]


def build_issues():
    rows = []
    statuses = ISSUE_STATUS_PLAN[:]
    random.shuffle(statuses)
    for i, (typ, title, sid, lvl, desc, scope) in enumerate(ISSUE_T, 1):
        st = statuses[i - 1]
        base = NOW - datetime.timedelta(days=(i * 5) % 165 + 2, hours=(i * 3) % 10)
        code = "WT-2026-%04d" % (100 + i)
        dept = DEPTS_HANDLE[i % len(DEPTS_HANDLE)] if st in ("处置中", "待复查", "已关闭") else None
        deadline = base + datetime.timedelta(days=3 if lvl == "重大" else 7)
        sup = 1 if lvl == "重大" else 0
        temp = ""
        if lvl == "重大":
            temp = "设置围挡与警示牌，下游 100 米布设吸油毡，暂停亲水平台使用。"
        parent = None
        if i in (7, 19, 24, 30):  # 复发建新单，关联历史问题
            parent = i - 3
        img = "/uploads/seed/issue/%02d.jpg" % (((i * 3) % 5) + 1)
        disp = close = None
        if st in ("待复查", "已关闭"):
            disp = base + datetime.timedelta(days=2, hours=6)
        if st == "已关闭":
            close = disp + datetime.timedelta(days=1, hours=3)
        rows.append((i, code, title, sid, ((i * 2) % 5) + 1, typ, lvl,
                     121.40 + sid * 0.0037, 31.20 + sid * 0.0021, desc, scope, img,
                     PATROLLERS[i % len(PATROLLERS)], base, st, deadline, dept, sup, temp, parent,
                     disp, close, base, base, 0))
    return rows


def build_tasks():
    rows, tid = [], 1
    for i in range(44):
        sid = (i % 24) + 1
        base = NOW - datetime.timedelta(days=(i * 4) % 170, hours=(i * 5) % 12)
        dead = base + datetime.timedelta(days=2)
        if i < 4:
            st = "执行中" if i < 2 else "待执行"
            dead = NOW + datetime.timedelta(hours=6 + i * 12)
        elif i == 5:
            st = "已逾期"
            dead = NOW - datetime.timedelta(hours=20)
        elif i == 6:
            st = "待执行"
            dead = NOW + datetime.timedelta(days=2)
        else:
            st = "已完成"
        ttype = "临时任务" if i % 9 == 0 else "周期任务"
        finish = dead - datetime.timedelta(hours=3) if st == "已完成" else None
        rows.append((tid, "RW-2026-%04d" % (1000 + i), "%s%s" % (SEC_DEF[sid - 1][1], "雨后加密巡查" if ttype == "临时任务" else "常规巡查"),
                     sid, ttype, SEC_DEF[sid - 1][6], PATROLLERS[i % len(PATROLLERS)], dead, finish, st,
                     "特殊天气后加密" if ttype == "临时任务" else "", base))
        tid += 1
    return rows


def build_water():
    rows, wid = [], 1
    for i in range(72):
        sid = (i % 24) + 1
        base = NOW - datetime.timedelta(days=(i * 7) % 175, hours=(i * 2) % 9)
        ph = round(6.6 + (i % 12) * 0.13, 1)
        turb = round(8 + (i * 5) % 46 + (0.5 if i % 3 else 0), 1)
        oxy = round(7.4 - (i % 9) * 0.35, 1)
        lvl = "Ⅱ类" if turb < 15 and oxy > 6 else ("Ⅲ类" if turb < 30 and oxy > 5 else ("Ⅳ类" if turb < 45 and oxy > 4 else "Ⅴ类"))
        rows.append((wid, (i % 44) + 1, sid, ((i % 5) + 1), ph, turb, oxy, lvl, ts(base),
                     PATROLLERS[i % len(PATROLLERS)], "/uploads/seed/section/%02d.jpg" % (((sid * 7) % 6) + 1),
                     "现场快速检测"))
        wid += 1
    return rows


def build_progress(issues):
    rows, pid = [], 1
    stages = ["接单确认", "第一阶段：临时措施", "第二阶段：溯源排查", "第三阶段：整改实施", "第四阶段：提交结果"]
    for it in issues:
        st = it[14]
        if st not in ("处置中", "待复查", "已关闭"):
            continue
        n = 5 if st == "已关闭" else (4 if st == "待复查" else 2 + (it[0] % 2))
        for k in range(n):
            t = it[13] + datetime.timedelta(days=k, hours=4 + k)
            rows.append((pid, it[0], it[16], 7 if it[0] % 2 else 8, stages[k],
                         ["已确认接收，安排现场处置班组", "完成围挡、吸油毡布设与警示",
                          "排查沿河排口与管网，锁定污染来源", "完成封堵与管网整改，清理受污染水体",
                          "提交整改报告与现场照片"][k],
                         6 + k * 2, "围油栏、吸油毡、水泥、波纹管", 8000 + k * 9000,
                         "阶段完成，现场复核无异常", "/uploads/seed/issue/%02d.jpg" % (((k * 3) % 5) + 1), ts(t), ts(t)))
            pid += 1
    return rows


def build_reviews(issues):
    rows, rid = [], 1
    for it in issues:
        st = it[14]
        if st not in ("待复查", "已关闭"):
            continue
        t = (it[21] or it[13]) + datetime.timedelta(hours=6)
        passed = 1 if st == "已关闭" else (1 if it[0] % 3 else 0)
        rows.append((rid, it[0], REVIEWERS[it[0] % 2], ts(t), "正常" if passed else "轻微异常",
                     "无" if passed else "轻微", 7.2, 18.0, 5.6,
                     "排口已封堵，水面无污水流入，水质指标恢复正常，整改到位。" if passed
                     else "现场仍有少量污水渗出，水面泡沫未完全消散，整改不彻底。",
                     passed, "" if passed else "整改不彻底，要求继续处置并补充凭证",
                     "/uploads/seed/section/%02d.jpg" % (((it[0] * 7) % 6) + 1), ts(t)))
        rid += 1
    return rows


def build_scores(sections):
    rows = []
    # 按次数/类型/时长计算，保证同输入同结果
    cnt = {s[0]: 0 for s in sections}
    for it in ISSUES_BUILT:
        cnt[it[3]] = cnt.get(it[3], 0) + 1
    for i, s in enumerate(sections):
        if i % 2 == 1 and i > 12:
            continue
        c = cnt.get(s[0], 0)
        c = min(c, 7)
        sec_type_hot = 0.9 if s[8] in ("劣Ⅴ类", "Ⅴ类") else (0.7 if s[8] == "Ⅳ类" else 0.45)
        cnt_score = min(c / 5.0, 1.0) * 25
        pos_score = 15 * (1.0 if s[3] in (2, 6, 11, 12) else 0.6)
        type_score = 20 * sec_type_hot
        dur = 40 + (i * 13) % 70
        dur_score = 15 * min(dur / 60.0, 1.0)
        rev = 15 * (1.0 - (0.85 if i % 4 else 0.6))
        qual = 10 * (1.0 if s[8] in ("劣Ⅴ类", "Ⅴ类") else 0.5)
        total = round(pos_score + type_score + cnt_score + dur_score + rev + qual, 1)
        lvl = "高" if total >= 75 else ("中" if total >= 50 else "低")
        rec = "纳入专项治理" if lvl == "高" else ("加密巡查" if lvl == "中" else "常规管理")
        dt = NOW - datetime.timedelta(days=(i % 6), hours=i % 8)
        manual = None
        mreason = None
        muser = None
        mtime = None
        if i in (2, 8):
            manual = "中" if lvl == "高" else lvl
            mreason = "该段已列入市级年度整治计划，风险总体可控"
            muser = "张启明"
            mtime = ts(dt + datetime.timedelta(hours=5))
        rows.append((i + 1, s[0], 1, "v3",
                     '{"position":"%s","issueType":"%s","count90":%d,"avgDuration":%d,"reviewPass":%s,"quality":"%s"}'
                     % (s[7], "非法排放", c, dur, "true" if i % 4 else "false", s[8]),
                     round(pos_score, 1), round(type_score, 1), round(cnt_score, 1), round(dur_score, 1),
                     round(rev, 1), round(qual, 1), total, lvl, rec,
                     "近90天同类问题 %d 次；水质等级 %s；平均处置时长 %d 小时" % (c, s[8], dur),
                     "近90天次数未低于阈值 5 次" if c >= 5 else "无",
                     "增设截污设施、加密巡查频次、纳入雨污分流改造",
                     ts(dt), manual, mreason, muser, mtime))
    return rows


def build_rules():
    base = datetime.datetime(2026, 3, 1, 0, 0, 0)
    return [
        (1, "问题复发热点识别规则", "v1", 15, 20, 20, 20, 15, 10, 75, 50, 90, 5, "历史", ts(base), "系统初始化", ts(base)),
        (2, "问题复发热点识别规则", "v2", 15, 20, 22, 18, 15, 10, 75, 50, 90, 5, "历史", ts(base + datetime.timedelta(days=106)), "张启明", ts(base + datetime.timedelta(days=106))),
        (3, "问题复发热点识别规则", "v3", 15, 20, 25, 15, 15, 10, 75, 50, 90, 5, "启用", ts(base + datetime.timedelta(days=184)), "张启明", ts(base + datetime.timedelta(days=184))),
    ]


def dec(v):
    return ("%.2f" % v) if isinstance(v, float) else str(v)


def insert(table, cols, rows):
    out = ["INSERT INTO %s (%s) VALUES" % (table, ",".join(cols))]
    vals = []
    for r in rows:
        vals.append("(" + ",".join(q(x) if not isinstance(x, (int, float)) or isinstance(x, bool) else str(x) for x in r) + ")")
    out.append(",\n".join(vals) + ";")
    return "\n".join(out)


SECTIONS = build_sections()
POINTS = build_points()
ISSUES_BUILT = build_issues()
TASKS = build_tasks()
WATER = build_water()
PROGRESS = build_progress(ISSUES_BUILT)
REVIEWS = build_reviews(ISSUES_BUILT)
SCORES = build_scores(SECTIONS)
RULES = build_rules()

parts = [DDL]

parts.append(insert("sys_dept", ["id", "name", "parent_id"], DEPT) + ";")
parts.append(insert("sys_role", ["code", "name", "data_scope", "remark"],
                    [(r[0], r[1], r[2], "系统内置角色：" + r[1]) for r in ROLE]) + ";")

PWD = "$2b$10$GjXC.nO/HcTT25rA90d4nutIiYaeh8g81IL1khPa.GduSCyrUMx6W"  # admin123
parts.append(insert("sys_user", ["id", "username", "password", "real_name", "phone", "avatar", "dept_id", "role_code", "status", "last_login", "create_time"],
                    [(i, u[0], PWD, u[1], u[2], u[5], u[3], u[4], 1,
                      ts(NOW - datetime.timedelta(hours=i * 3)), ts(datetime.datetime(2026, 4, 8, 9, 0))) for i, u in enumerate(USERS, 1)]) + ";")
parts.append(insert("sys_menu", ["id", "parent_id", "name", "path", "component", "icon", "perm", "type", "sort", "visible"], MENU) + ";")

ROLE_ID = {r[0]: i for i, r in enumerate(ROLE, 1)}
rm_rows, rid = [], 1
for rcode, mids in ROLE_MENU.items():
    for m in mids:
        rm_rows.append((rid, ROLE_ID[rcode], m))
        rid += 1
parts.append(insert("sys_role_menu", ["id", "role_id", "menu_id"], rm_rows) + ";")

parts.append(insert("river", ["id", "code", "name", "length_km", "area", "level", "manager", "phone", "intro", "create_time"],
                    [(r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7], r[8], ts(datetime.datetime(2026, 4, 5, 10, 0))) for r in RIVERS]) + ";")
parts.append(insert("river_section", ["id", "code", "name", "river_id", "start_point", "end_point", "length_km", "area", "water_quality_level", "patrol_route", "manager", "patrol_freq", "status", "cover_image", "longitude", "latitude", "create_time"], SECTIONS) + ";")
parts.append(insert("patrol_point", ["id", "section_id", "name", "type", "longitude", "latitude", "facility", "status", "sort"], POINTS) + ";")
parts.append(insert("river_task", ["id", "code", "title", "section_id", "task_type", "cycle_type", "assignee_id", "deadline", "finish_time", "status", "remark", "create_time"], TASKS) + ";")
parts.append(insert("water_quality_record", ["id", "task_id", "section_id", "point_id", "ph", "turbidity", "dissolved_oxygen", "level", "record_time", "recorder_id", "image", "remark"], WATER) + ";")
parts.append(insert("river_issue", ["id", "code", "title", "section_id", "point_id", "issue_type", "level", "longitude", "latitude", "description", "impact_scope", "image", "reporter_id", "report_time", "status", "deadline", "dept_id", "supervise", "temp_measure", "parent_issue_id", "dispose_time", "close_time", "create_time", "update_time", "deleted"], ISSUES_BUILT) + ";")
parts.append(insert("disposal_progress", ["id", "issue_id", "dept_id", "reporter_id", "stage", "content", "person_count", "material", "cost", "result", "images", "progress_time", "create_time"], PROGRESS) + ";")
parts.append(insert("review_record", ["id", "issue_id", "reviewer_id", "review_time", "water_color", "smell", "ph", "turbidity", "dissolved_oxygen", "conclusion", "pass", "reason", "images", "create_time"], REVIEWS) + ";")
parts.append(insert("river_patrol_rule", ["id", "name", "version", "weight_position", "weight_type", "weight_count", "weight_duration", "weight_review", "weight_quality", "threshold_high", "threshold_mid", "window_days", "count_full", "status", "effective_time", "create_by", "create_time"], RULES) + ";")
parts.append(insert("river_patrol_score", ["id", "section_id", "rule_id", "rule_version", "input_snapshot", "score_position", "score_type", "score_count", "score_duration", "score_review", "score_quality", "total_score", "level", "recommend", "factors", "unmet", "suggestions", "calc_time", "manual_level", "manual_reason", "adjust_user", "adjust_time"], SCORES) + ";")

# 站内消息
msgs = []
for i, it in enumerate(ISSUES_BUILT[:14], 1):
    if it[14] == "待派单":
        msgs.append((i, "新问题待派单：" + it[2], "问题 %s 已提交，请研判并派单。" % it[1], "APPROVE", it[1], it[0], 2, 0, ts(it[13] + datetime.timedelta(minutes=5))))
    elif it[14] == "待复查":
        msgs.append((i, "待复查提醒：" + it[2], "问题 %s 已提交处置结果，请安排现场复查。" % it[1], "REVIEW", it[1], it[0], 9, 0, ts(it[13] + datetime.timedelta(hours=8))))
    elif it[14] == "处置中":
        msgs.append((i, "处置时限提醒：" + it[2], "问题 %s 距要求完成时间不足 24 小时。" % it[1], "TIMEOUT", it[1], it[0], 7, 0, ts(it[13] + datetime.timedelta(hours=10))))
    elif it[14] == "已关闭":
        msgs.append((i, "问题已关闭：" + it[2], "问题 %s 复查通过并销号。" % it[1], "DONE", it[1], it[0], 4, 1, ts(it[13] + datetime.timedelta(days=3))))
parts.append(insert("sys_message", ["id", "title", "content", "type", "biz_no", "biz_id", "receiver_id", "is_read", "create_time"], msgs) + ";")

# 操作日志（状态流转留痕）
logs = []
for i, it in enumerate(ISSUES_BUILT, 1):
    st = it[14]
    logs.append((len(logs) + 1, it[12], "zhouzy", "问题处置", "上报问题", it[1], "", "待确认", "", "127.0.0.1", ts(it[13])))
    logs.append((len(logs) + 1, 2, "zhangqm", "问题处置", "研判定级", it[1], "待确认", "待派单", "", "127.0.0.1", ts(it[13] + datetime.timedelta(hours=2))))
    if st not in ("待确认", "待派单", "无效上报"):
        logs.append((len(logs) + 1, 2, "zhangqm", "问题处置", "派发处置", it[1], "待派单", "处置中", "", "127.0.0.1", ts(it[13] + datetime.timedelta(hours=4))))
    if st in ("待复查", "已关闭"):
        logs.append((len(logs) + 1, 7, "liuhb", "问题处置", "提交处置结果", it[1], "处置中", "待复查", "", "127.0.0.1", ts(it[21] or it[13])))
    if st == "已关闭":
        logs.append((len(logs) + 1, 9, "zhaomin", "复查", "复查通过关闭", it[1], "待复查", "已关闭", "现场整改到位，水质恢复正常", "127.0.0.1", ts(it[22] or it[13])))
    if st == "无效上报":
        logs.append((len(logs) + 1, 2, "zhangqm", "问题处置", "标记无效上报", it[1], "待确认", "无效上报", "经核实为历史遗留问题，不属于新增污染", "127.0.0.1", ts(it[13] + datetime.timedelta(hours=6))))
parts.append(insert("sys_log", ["id", "user_id", "username", "module", "action", "biz_no", "before_status", "after_status", "reason", "ip", "create_time"], logs) + ";")

parts.append("-- 图片字段全部指向项目内真实本地图片：/uploads/seed/<实体>/NN.jpg")
OUT.write_text("\n\n".join(parts), encoding="utf-8")
print("written", OUT, OUT.stat().st_size // 1024, "KB",
      "| sections", len(SECTIONS), "issues", len(ISSUES_BUILT), "tasks", len(TASKS),
      "water", len(WATER), "progress", len(PROGRESS), "reviews", len(REVIEWS), "scores", len(SCORES), "logs", len(logs))
