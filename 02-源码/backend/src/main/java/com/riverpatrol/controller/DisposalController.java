package com.riverpatrol.controller;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.riverpatrol.common.BizException;
import com.riverpatrol.common.R;
import com.riverpatrol.entity.*;
import com.riverpatrol.mapper.*;
import com.riverpatrol.security.UserContext;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.*;

/** 整改跟踪：处置单位分阶段上报进度、费用、物资与凭证 */
@RestController
@RequestMapping("/api/disposal")
public class DisposalController {

    @Autowired private RiverIssueMapper issueMapper;
    @Autowired private DisposalProgressMapper progressMapper;
    @Autowired private RiverSectionMapper sectionMapper;
    @Autowired private SysUserMapper userMapper;

    @GetMapping("/page")
    public R<Map<String, Object>> page(@RequestParam(defaultValue = "1") int page,
                                       @RequestParam(defaultValue = "10") int size,
                                       @RequestParam(required = false) String status,
                                       @RequestParam(required = false) String keyword) {
        LambdaQueryWrapper<RiverIssue> w = new LambdaQueryWrapper<>();
        w.in(RiverIssue::getStatus, status != null && !status.isBlank()
                ? List.of(status) : List.of("处置中", "待复查"));
        w.and(keyword != null && !keyword.isBlank(),
                q -> q.like(RiverIssue::getTitle, keyword).or().like(RiverIssue::getCode, keyword));
        if ("handler".equals(UserContext.role())) {
            w.eq(RiverIssue::getDeptId, UserContext.get().getDeptId());
        }
        w.orderByAsc(RiverIssue::getDeadline);
        Page<RiverIssue> p = issueMapper.selectPage(new Page<>(page, size), w);

        Map<Long, String> secNames = new HashMap<>();
        sectionMapper.selectList(null).forEach(s -> secNames.put(s.getId(), s.getName()));
        List<Map<String, Object>> rows = new ArrayList<>();
        for (RiverIssue i : p.getRecords()) {
            Map<String, Object> m = new LinkedHashMap<>();
            m.put("id", i.getId());
            m.put("code", i.getCode());
            m.put("title", i.getTitle());
            m.put("sectionName", secNames.getOrDefault(i.getSectionId(), "—"));
            m.put("level", i.getLevel());
            m.put("status", i.getStatus());
            m.put("deadline", i.getDeadline());
            m.put("supervise", i.getSupervise());
            List<DisposalProgress> ps = progressMapper.selectList(new LambdaQueryWrapper<DisposalProgress>()
                    .eq(DisposalProgress::getIssueId, i.getId()).orderByAsc(DisposalProgress::getProgressTime));
            m.put("progressCount", ps.size());
            m.put("lastStage", ps.isEmpty() ? "待接单" : ps.get(ps.size() - 1).getStage());
            m.put("overdue", i.getDeadline() != null && i.getDeadline().isBefore(LocalDateTime.now()));
            rows.add(m);
        }
        Map<String, Object> data = new LinkedHashMap<>();
        data.put("total", p.getTotal());
        data.put("page", page);
        data.put("size", size);
        data.put("records", rows);
        return R.ok(data);
    }

    @GetMapping("/{issueId}")
    public R<List<DisposalProgress>> list(@PathVariable Long issueId) {
        return R.ok(progressMapper.selectList(new LambdaQueryWrapper<DisposalProgress>()
                .eq(DisposalProgress::getIssueId, issueId).orderByAsc(DisposalProgress::getProgressTime)));
    }

    @PostMapping
    public R<DisposalProgress> add(@RequestBody Map<String, Object> body) {
        String role = UserContext.role();
        if (!"handler".equals(role) && !"admin".equals(role)) {
            throw new BizException(403, "仅处置单位人员可填报整改");
        }
        Long issueId = Long.valueOf(String.valueOf(body.get("issueId")));
        RiverIssue issue = issueMapper.selectById(issueId);
        if (issue == null) {
            throw new BizException(404, "问题单不存在");
        }
        if (!"处置中".equals(issue.getStatus())) {
            throw new BizException("当前状态为「" + issue.getStatus() + "」，不可填报整改进度");
        }
        String content = String.valueOf(body.getOrDefault("content", "")).trim();
        if (content.length() < 5) {
            throw new BizException("处置内容不少于 5 个字");
        }
        DisposalProgress p = new DisposalProgress();
        p.setIssueId(issueId);
        p.setDeptId(issue.getDeptId());
        p.setReporterId(UserContext.id());
        p.setStage(String.valueOf(body.getOrDefault("stage", "整改实施")));
        p.setContent(content);
        p.setPersonCount(body.get("personCount") == null ? 0 : Integer.parseInt(String.valueOf(body.get("personCount"))));
        p.setMaterial(String.valueOf(body.getOrDefault("material", "")));
        p.setCost(body.get("cost") == null ? BigDecimal.ZERO : new BigDecimal(String.valueOf(body.get("cost"))));
        p.setResult(String.valueOf(body.getOrDefault("result", "")));
        p.setImages(String.valueOf(body.getOrDefault("images", "")));
        p.setProgressTime(LocalDateTime.now());
        p.setCreateTime(LocalDateTime.now());
        progressMapper.insert(p);
        return R.ok(p);
    }
}
