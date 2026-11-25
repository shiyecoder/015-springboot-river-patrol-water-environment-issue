package com.riverpatrol.service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.riverpatrol.common.BizException;
import com.riverpatrol.entity.*;
import com.riverpatrol.mapper.*;
import com.riverpatrol.security.UserContext;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.*;
import java.util.stream.Collectors;

/**
 * 问题单业务：上报、研判、派单、处置、复查销号。
 * 状态机：待确认 → 待派单 → 处置中 → 待复查 → 已关闭（待确认/待派单 可转无效上报；待复查可驳回回处置中）
 */
@Service
public class IssueService {

    @Autowired private RiverIssueMapper issueMapper;
    @Autowired private RiverSectionMapper sectionMapper;
    @Autowired private SysUserMapper userMapper;
    @Autowired private SysDeptMapper deptMapper;
    @Autowired private SysLogMapper logMapper;
    @Autowired private DisposalProgressMapper progressMapper;
    @Autowired private ReviewRecordMapper reviewMapper;
    @Autowired private SysMessageMapper messageMapper;
    @Autowired private PatrolScoreMapper scoreMapper;

    private static final DateTimeFormatter FMT = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");

    public Map<String, Object> page(int page, int size, String status, String type, String level,
                                    String keyword, Long sectionId, String tab) {
        LambdaQueryWrapper<RiverIssue> w = new LambdaQueryWrapper<>();
        w.eq(status != null && !status.isBlank(), RiverIssue::getStatus, status)
                .eq(type != null && !type.isBlank(), RiverIssue::getIssueType, type)
                .eq(level != null && !level.isBlank(), RiverIssue::getLevel, level)
                .eq(sectionId != null, RiverIssue::getSectionId, sectionId)
                .and(keyword != null && !keyword.isBlank(),
                        q -> q.like(RiverIssue::getTitle, keyword).or().like(RiverIssue::getCode, keyword));
        if ("todo".equals(tab)) {
            w.in(RiverIssue::getStatus, List.of("待确认", "待派单"));
        } else if ("doing".equals(tab)) {
            w.in(RiverIssue::getStatus, List.of("处置中", "待复查"));
        } else if ("done".equals(tab)) {
            w.eq(RiverIssue::getStatus, "已关闭");
        } else if ("abnormal".equals(tab)) {
            w.in(RiverIssue::getStatus, List.of("无效上报"));
        }
        // 数据范围：巡查员只看本人上报；处置单位只看本单位；调度/复查/管理员按部门或全部
        String role = UserContext.role();
        if ("patroller".equals(role)) {
            w.eq(RiverIssue::getReporterId, UserContext.id());
        } else if ("handler".equals(role)) {
            w.eq(RiverIssue::getDeptId, UserContext.get().getDeptId());
        }
        // 默认排序：待本人处理优先（按状态机顺序），同状态按更新时间倒序
        w.last("ORDER BY FIELD(status,'待确认','待派单','处置中','待复查','已关闭','无效上报'), update_time DESC");

        Page<RiverIssue> p = issueMapper.selectPage(new Page<>(page, size), w);
        Map<Long, String> secNames = new HashMap<>();
        sectionMapper.selectList(null).forEach(s -> secNames.put(s.getId(), s.getName()));
        Map<Long, String> userNames = new HashMap<>();
        userMapper.selectList(null).forEach(u -> userNames.put(u.getId(), u.getRealName()));
        Map<Long, String> deptNames = new HashMap<>();
        deptMapper.selectList(null).forEach(d -> deptNames.put(d.getId(), d.getName()));

        List<Map<String, Object>> records = new ArrayList<>();
        for (RiverIssue i : p.getRecords()) {
            Map<String, Object> m = new LinkedHashMap<>();
            m.put("id", i.getId());
            m.put("code", i.getCode());
            m.put("title", i.getTitle());
            m.put("sectionId", i.getSectionId());
            m.put("sectionName", secNames.getOrDefault(i.getSectionId(), "—"));
            m.put("issueType", i.getIssueType());
            m.put("level", i.getLevel());
            m.put("status", i.getStatus());
            m.put("supervise", i.getSupervise());
            m.put("reporterName", userNames.getOrDefault(i.getReporterId(), "—"));
            m.put("deptName", i.getDeptId() == null ? "—" : deptNames.getOrDefault(i.getDeptId(), "—"));
            m.put("reportTime", i.getReportTime() == null ? null : i.getReportTime().format(FMT));
            m.put("deadline", i.getDeadline() == null ? null : i.getDeadline().format(FMT));
            m.put("overdue", i.getDeadline() != null && i.getDeadline().isBefore(LocalDateTime.now())
                    && !"已关闭".equals(i.getStatus()) && !"无效上报".equals(i.getStatus()));
            m.put("image", i.getImage());
            records.add(m);
        }
        Map<String, Object> data = new LinkedHashMap<>();
        data.put("total", p.getTotal());
        data.put("page", page);
        data.put("size", size);
        data.put("records", records);
        return data;
    }

    public Map<String, Object> detail(Long id) {
        RiverIssue issue = issueMapper.selectById(id);
        if (issue == null) {
            throw new BizException(404, "问题单不存在");
        }
        Map<String, Object> data = new LinkedHashMap<>();
        data.put("issue", issue);
        data.put("section", sectionMapper.selectById(issue.getSectionId()));
        data.put("reporter", userMapper.selectById(issue.getReporterId()));
        data.put("progress", progressMapper.selectList(new LambdaQueryWrapper<DisposalProgress>()
                .eq(DisposalProgress::getIssueId, id).orderByAsc(DisposalProgress::getProgressTime)));
        data.put("reviews", reviewMapper.selectList(new LambdaQueryWrapper<ReviewRecord>()
                .eq(ReviewRecord::getIssueId, id).orderByDesc(ReviewRecord::getReviewTime)));
        data.put("logs", logMapper.selectList(new LambdaQueryWrapper<SysLog>()
                .eq(SysLog::getBizNo, issue.getCode()).orderByDesc(SysLog::getCreateTime)));
        data.put("score", scoreMapper.selectList(new LambdaQueryWrapper<PatrolScore>()
                .eq(PatrolScore::getSectionId, issue.getSectionId())
                .orderByDesc(PatrolScore::getCalcTime).last("limit 1")).stream().findFirst().orElse(null));
        if (issue.getDeptId() != null) {
            data.put("dept", deptMapper.selectById(issue.getDeptId()));
        }
        return data;
    }

    /** 重复上报提醒：同断面 500 米内近 30 天同类型未关闭问题 */
    public List<RiverIssue> duplicates(Long sectionId, String type) {
        return issueMapper.selectList(new LambdaQueryWrapper<RiverIssue>()
                .eq(RiverIssue::getSectionId, sectionId)
                .eq(type != null && !type.isBlank(), RiverIssue::getIssueType, type)
                .ge(RiverIssue::getReportTime, LocalDateTime.now().minusDays(30))
                .notIn(RiverIssue::getStatus, List.of("已关闭", "无效上报"))
                .orderByDesc(RiverIssue::getReportTime)
                .last("limit 5"));
    }

    @Transactional
    public RiverIssue create(Map<String, Object> body, Long reporterId) {
        String title = str(body.get("title"));
        if (title.isBlank()) {
            throw new BizException("问题标题不能为空");
        }
        String desc = str(body.get("description"));
        if (desc.length() < 5) {
            throw new BizException("问题描述不少于 5 个字");
        }
        if (str(body.get("impactScope")).isBlank()) {
            throw new BizException("请填写影响范围");
        }
        Long sectionId = Long.valueOf(String.valueOf(body.get("sectionId")));
        RiverIssue issue = new RiverIssue();
        issue.setCode("WT-" + LocalDateTime.now().getYear() + "-" + String.format("%04d",
                (issueMapper.selectCount(null) + 1)));
        issue.setTitle(title);
        issue.setSectionId(sectionId);
        issue.setPointId(body.get("pointId") == null ? null : Long.valueOf(String.valueOf(body.get("pointId"))));
        issue.setIssueType(str(body.get("issueType")));
        issue.setLevel("重大".equals(body.get("level")) ? "重大" : "一般");
        issue.setDescription(desc);
        issue.setImpactScope(str(body.get("impactScope")));
        issue.setImage(str(body.get("image")));
        issue.setReporterId(reporterId);
        issue.setReportTime(LocalDateTime.now());
        issue.setStatus("待确认");
        issue.setSupervise(0);
        issue.setDeleted(0);
        issue.setVersion(0);
        issue.setCreateTime(LocalDateTime.now());
        issue.setUpdateTime(LocalDateTime.now());
        issue.setDeadline(LocalDateTime.now().plusDays("重大".equals(issue.getLevel()) ? 3 : 7));
        issueMapper.insert(issue);

        log(issue.getCode(), "", "待确认", "上报问题", "");
        message("新问题待研判：" + issue.getTitle(), "问题 " + issue.getCode() + " 已提交，请研判并派单。",
                "APPROVE", issue.getCode(), issue.getId(), 2L);
        return issue;
    }

    /**
     * 状态流转统一入口。所有分支均由后端校验，前端按钮只做展示。
     * @param action submit(提交研判) / dispatch(派单) / invalid(无效上报) / submitResult(提交处置结果) / pass(复查通过) / reject(驳回)
     */
    @Transactional
    public RiverIssue transition(Long id, String action, Map<String, Object> body, String operator, String role) {
        RiverIssue issue = issueMapper.selectById(id);
        if (issue == null) {
            throw new BizException(404, "问题单不存在");
        }
        String before = issue.getStatus();
        String reason = str(body == null ? null : body.get("reason"));
        String to;

        switch (action) {
            case "submit" -> {
                require(role, "dispatcher", "admin");
                guard("待确认", before);
                to = "待派单";
            }
            case "invalid" -> {
                require(role, "dispatcher", "admin");
                guard("待确认", before);
                if (reason.length() < 5) {
                    throw new BizException("标记无效上报必须填写不少于 5 个字的原因");
                }
                to = "无效上报";
            }
            case "dispatch" -> {
                require(role, "dispatcher", "admin");
                guard("待派单", before);
                Long deptId = body.get("deptId") == null ? null : Long.valueOf(String.valueOf(body.get("deptId")));
                if (deptId == null) {
                    throw new BizException("请选择责任单位");
                }
                issue.setDeptId(deptId);
                String temp = str(body.get("tempMeasure"));
                // 重大问题必须先落临时措施，否则不允许等待长期方案
                if ("重大".equals(issue.getLevel()) && temp.length() < 5) {
                    throw new BizException("重大问题必须填写临时措施（不少于 5 个字）");
                }
                issue.setTempMeasure(temp);
                issue.setDeadline(LocalDateTime.now().plusDays(body.get("days") == null ? 3
                        : Integer.parseInt(String.valueOf(body.get("days")))));
                issue.setSupervise("重大".equals(issue.getLevel()) || Boolean.TRUE.equals(body.get("supervise")) ? 1 : 0);
                issue.setDisposeTime(null);
                to = "处置中";
            }
            case "submitResult" -> {
                require(role, "handler", "admin");
                guard("处置中", before);
                if (progressMapper.selectCount(new LambdaQueryWrapper<DisposalProgress>()
                        .eq(DisposalProgress::getIssueId, id)) == 0) {
                    throw new BizException("请先填报至少一条整改进度");
                }
                issue.setDisposeTime(LocalDateTime.now());
                to = "待复查";
            }
            case "pass" -> {
                require(role, "reviewer", "admin");
                guard("待复查", before);
                // 处置人不能审核自己提交的复查结果
                if (Objects.equals(issue.getDeptId(), UserContext.get().getDeptId()) && !"admin".equals(role)) {
                    throw new BizException("处置单位人员不得审核本单位处置结果");
                }
                issue.setCloseTime(LocalDateTime.now());
                to = "已关闭";
            }
            case "reject" -> {
                require(role, "reviewer", "admin");
                guard("待复查", before);
                if (reason.length() < 5) {
                    throw new BizException("驳回必须填写不少于 5 个字的原因");
                }
                issue.setDeadline(LocalDateTime.now().plusDays(2));
                to = "处置中";
            }
            default -> throw new BizException("不支持的操作：" + action);
        }

        issue.setStatus(to);
        issue.setUpdateTime(LocalDateTime.now());
        issue.setVersion(issue.getVersion() == null ? 1 : issue.getVersion() + 1);
        issueMapper.updateById(issue);
        log(issue.getCode(), before, to, actionName(action), reason);

        if ("待复查".equals(to)) {
            message("待复查提醒：" + issue.getTitle(), "问题 " + issue.getCode() + " 已提交处置结果，请现场复查。",
                    "REVIEW", issue.getCode(), issue.getId(), 9L);
        }
        if ("处置中".equals(to) && issue.getDeptId() != null) {
            message("新派单：" + issue.getTitle(), "问题 " + issue.getCode() + " 已派发至贵单位，请按期处置。",
                    "APPROVE", issue.getCode(), issue.getId(), 7L);
        }
        return issueMapper.selectById(id);
    }

    private void guard(String expect, String actual) {
        if (!expect.equals(actual)) {
            throw new BizException("当前状态为「" + actual + "」，不允许该操作（需要「" + expect + "」）");
        }
    }

    private void require(String role, String... allowed) {
        for (String a : allowed) {
            if (a.equals(role)) {
                return;
            }
        }
        throw new BizException(403, "当前角色无权执行该操作");
    }

    private String actionName(String a) {
        return switch (a) {
            case "submit" -> "提交研判";
            case "invalid" -> "标记无效上报";
            case "dispatch" -> "派发处置";
            case "submitResult" -> "提交处置结果";
            case "pass" -> "复查通过关闭";
            case "reject" -> "复查驳回";
            default -> a;
        };
    }

    /** 状态变更全部留痕，普通用户不可修改日志 */
    public void log(String bizNo, String before, String after, String action, String reason) {
        SysLog l = new SysLog();
        l.setUserId(UserContext.id());
        l.setUsername(UserContext.get() == null ? "system" : UserContext.get().getUsername());
        l.setModule("问题处置");
        l.setAction(action);
        l.setBizNo(bizNo);
        l.setBeforeStatus(before);
        l.setAfterStatus(after);
        l.setReason(reason);
        l.setIp("127.0.0.1");
        l.setCreateTime(LocalDateTime.now());
        logMapper.insert(l);
    }

    private void message(String title, String content, String type, String bizNo, Long bizId, Long receiver) {
        SysMessage m = new SysMessage();
        m.setTitle(title.length() > 100 ? title.substring(0, 100) : title);
        m.setContent(content);
        m.setType(type);
        m.setBizNo(bizNo);
        m.setBizId(bizId);
        m.setReceiverId(receiver);
        m.setIsRead(0);
        m.setCreateTime(LocalDateTime.now());
        messageMapper.insert(m);
    }

    private String str(Object o) {
        return o == null ? "" : String.valueOf(o).trim();
    }

    public List<String> statusFlow() {
        return List.of("待确认", "待派单", "处置中", "待复查", "已关闭");
    }

    public Map<String, Long> counts() {
        Map<String, Long> m = new LinkedHashMap<>();
        for (String s : statusFlow()) {
            m.put(s, issueMapper.selectCount(new LambdaQueryWrapper<RiverIssue>().eq(RiverIssue::getStatus, s)));
        }
        m.put("无效上报", issueMapper.selectCount(new LambdaQueryWrapper<RiverIssue>().eq(RiverIssue::getStatus, "无效上报")));
        return m;
    }

    public List<Map<String, Object>> depts() {
        return deptMapper.selectList(null).stream().map(d -> {
            Map<String, Object> m = new LinkedHashMap<>();
            m.put("id", d.getId());
            m.put("name", d.getName());
            return m;
        }).collect(Collectors.toList());
    }
}
