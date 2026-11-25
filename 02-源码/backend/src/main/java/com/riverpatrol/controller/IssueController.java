package com.riverpatrol.controller;

import com.riverpatrol.common.R;
import com.riverpatrol.entity.RiverIssue;
import com.riverpatrol.service.IssueService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

/** 问题单：列表、详情、上报、重复提醒、状态流转 */
@RestController
@RequestMapping("/api/issue")
public class IssueController {

    @Autowired
    private IssueService issueService;

    @GetMapping("/page")
    public R<Map<String, Object>> page(@RequestParam(defaultValue = "1") int page,
                                       @RequestParam(defaultValue = "10") int size,
                                       @RequestParam(required = false) String status,
                                       @RequestParam(required = false) String type,
                                       @RequestParam(required = false) String level,
                                       @RequestParam(required = false) String keyword,
                                       @RequestParam(required = false) Long sectionId,
                                       @RequestParam(required = false) String tab) {
        return R.ok(issueService.page(page, size, status, type, level, keyword, sectionId, tab));
    }

    @GetMapping("/{id}")
    public R<Map<String, Object>> detail(@PathVariable Long id) {
        return R.ok(issueService.detail(id));
    }

    @GetMapping("/duplicate")
    public R<List<RiverIssue>> duplicate(@RequestParam Long sectionId, @RequestParam(required = false) String type) {
        return R.ok(issueService.duplicates(sectionId, type));
    }

    @PostMapping
    public R<RiverIssue> create(@RequestBody Map<String, Object> body) {
        return R.ok(issueService.create(body, com.riverpatrol.security.UserContext.id()));
    }

    /** 目标状态流转：submit/dispatch/invalid/submitResult/pass/reject */
    @PostMapping("/{id}/transition")
    public R<RiverIssue> transition(@PathVariable Long id, @RequestBody Map<String, Object> body) {
        String action = String.valueOf(body.get("action"));
        return R.ok(issueService.transition(id, action, body,
                String.valueOf(com.riverpatrol.security.UserContext.get().getUsername()),
                com.riverpatrol.security.UserContext.role()));
    }

    @GetMapping("/counts")
    public R<Map<String, Long>> counts() {
        return R.ok(issueService.counts());
    }

    @GetMapping("/depts")
    public R<List<Map<String, Object>>> depts() {
        return R.ok(issueService.depts());
    }
}
