package com.riverpatrol.controller;

import com.riverpatrol.common.R;
import com.riverpatrol.entity.PatrolRule;
import com.riverpatrol.entity.PatrolScore;
import com.riverpatrol.service.HotspotService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

/** 创新点接口：热点列表、单断面评估、计算留痕、人工修正、规则配置 */
@RestController
@RequestMapping("/api/hotspot")
public class HotspotController {

    @Autowired
    private HotspotService hotspotService;

    @GetMapping("/list")
    public R<List<Map<String, Object>>> list(@RequestParam(required = false) String level) {
        return R.ok(hotspotService.list(level, null));
    }

    @GetMapping("/stats")
    public R<Map<String, Object>> stats() {
        return R.ok(hotspotService.stats());
    }

    @PostMapping("/evaluate/{sectionId}")
    public R<PatrolScore> evaluate(@PathVariable Long sectionId) {
        return R.ok(hotspotService.evaluate(sectionId, hotspotService.activeRule()));
    }

    @PostMapping("/{id}/adjust")
    public R<PatrolScore> adjust(@PathVariable Long id, @RequestBody Map<String, String> body) {
        return R.ok(hotspotService.adjust(id, body.get("level"), body.get("reason")));
    }

    @GetMapping("/rules")
    public R<List<PatrolRule>> rules() {
        return R.ok(hotspotService.rules());
    }

    @PostMapping("/rules")
    public R<PatrolRule> saveRule(@RequestBody PatrolRule body) {
        return R.ok(hotspotService.saveRule(body));
    }
}
