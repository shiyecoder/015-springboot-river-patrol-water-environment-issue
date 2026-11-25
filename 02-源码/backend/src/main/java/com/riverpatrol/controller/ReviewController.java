package com.riverpatrol.controller;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.riverpatrol.common.BizException;
import com.riverpatrol.common.R;
import com.riverpatrol.entity.*;
import com.riverpatrol.mapper.*;
import com.riverpatrol.security.UserContext;
import com.riverpatrol.service.IssueService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.bind.annotation.*;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.*;

/** 复核销号：复查人员现场记录并关闭或驳回 */
@RestController
@RequestMapping("/api/review")
public class ReviewController {

    @Autowired private RiverIssueMapper issueMapper;
    @Autowired private ReviewRecordMapper reviewMapper;
    @Autowired private RiverSectionMapper sectionMapper;
    @Autowired private DisposalProgressMapper progressMapper;
    @Autowired private IssueService issueService;
    @Autowired private PatrolScoreMapper scoreMapper;

    @GetMapping("/page")
    public R<Map<String, Object>> page(@RequestParam(defaultValue = "1") int page,
                                       @RequestParam(defaultValue = "10") int size,
                                       @RequestParam(required = false) String status) {
        LambdaQueryWrapper<RiverIssue> w = new LambdaQueryWrapper<>();
        w.in(RiverIssue::getStatus, status != null && !status.isBlank()
                ? List.of(status) : List.of("待复查", "已关闭"));
        // 待复查优先，其次按处置完成时间倒序
        w.last("ORDER BY FIELD(status,'待复查','已关闭'), dispose_time DESC");
        Page<RiverIssue> p = issueMapper.selectPage(new Page<>(page, size), w);

        Map<Long, String> secNames = new HashMap<>();
        sectionMapper.selectList(null).forEach(s -> secNames.put(s.getId(), s.getName()));
        List<Map<String, Object>> rows = new ArrayList<>();
        for (RiverIssue i : p.getRecords()) {
            Map<String, Object> m = new LinkedHashMap<>();
            m.put("id", i.getId());
            m.put("code", i.getCode());
            m.put("title", i.getTitle());
            m.put("sectionId", i.getSectionId());
            m.put("sectionName", secNames.getOrDefault(i.getSectionId(), "—"));
            m.put("level", i.getLevel());
            m.put("status", i.getStatus());
            m.put("disposeTime", i.getDisposeTime());
            m.put("deadline", i.getDeadline());
            m.put("progress", progressMapper.selectList(new LambdaQueryWrapper<DisposalProgress>()
                    .eq(DisposalProgress::getIssueId, i.getId()).orderByAsc(DisposalProgress::getProgressTime)));
            m.put("score", scoreMapper.selectList(new LambdaQueryWrapper<PatrolScore>()
                    .eq(PatrolScore::getSectionId, i.getSectionId())
                    .orderByDesc(PatrolScore::getCalcTime).last("limit 1")).stream().findFirst().orElse(null));
            m.put("reviews", reviewMapper.selectList(new LambdaQueryWrapper<ReviewRecord>()
                    .eq(ReviewRecord::getIssueId, i.getId()).orderByDesc(ReviewRecord::getReviewTime)));
            rows.add(m);
        }
        Map<String, Object> data = new LinkedHashMap<>();
        data.put("total", p.getTotal());
        data.put("page", page);
        data.put("size", size);
        data.put("records", rows);
        return R.ok(data);
    }

    /** 复查提交：写复查记录 + 状态流转（通过→已关闭，驳回→处置中） */
    @PostMapping
    @Transactional
    public R<Void> submit(@RequestBody Map<String, Object> body) {
        String role = UserContext.role();
        if (!"reviewer".equals(role) && !"admin".equals(role)) {
            throw new BizException(403, "仅复查人员可提交复核结论");
        }
        Long issueId = Long.valueOf(String.valueOf(body.get("issueId")));
        boolean pass = Boolean.TRUE.equals(body.get("pass")) || "1".equals(String.valueOf(body.get("pass")));
        String conclusion = String.valueOf(body.getOrDefault("conclusion", "")).trim();
        if (conclusion.length() < 5) {
            throw new BizException("复核结论不少于 5 个字");
        }
        if (!pass) {
            String reason = String.valueOf(body.getOrDefault("reason", "")).trim();
            if (reason.length() < 5) {
                throw new BizException("驳回必须填写不少于 5 个字的原因");
            }
        }
        ReviewRecord r = new ReviewRecord();
        r.setIssueId(issueId);
        r.setReviewerId(UserContext.id());
        r.setReviewTime(LocalDateTime.now());
        r.setWaterColor(String.valueOf(body.getOrDefault("waterColor", "正常")));
        r.setSmell(String.valueOf(body.getOrDefault("smell", "无")));
        r.setPh(body.get("ph") == null ? null : new BigDecimal(String.valueOf(body.get("ph"))));
        r.setTurbidity(body.get("turbidity") == null ? null : new BigDecimal(String.valueOf(body.get("turbidity"))));
        r.setDissolvedOxygen(body.get("dissolvedOxygen") == null ? null : new BigDecimal(String.valueOf(body.get("dissolvedOxygen"))));
        r.setConclusion(conclusion);
        r.setPass(pass ? 1 : 0);
        r.setReason(String.valueOf(body.getOrDefault("reason", "")));
        r.setImages(String.valueOf(body.getOrDefault("images", "")));
        r.setCreateTime(LocalDateTime.now());
        reviewMapper.insert(r);

        Map<String, Object> trans = new HashMap<>();
        trans.put("reason", String.valueOf(body.getOrDefault("reason", conclusion)));
        issueService.transition(issueId, pass ? "pass" : "reject", trans,
                UserContext.get().getUsername(), role);
        return R.ok();
    }
}
