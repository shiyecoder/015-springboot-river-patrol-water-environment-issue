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

import java.time.LocalDateTime;
import java.util.*;

/** 河道断面档案：分页、详情（含点位/关联问题/时间轴）、新增与编辑 */
@RestController
@RequestMapping("/api/section")
public class SectionController {

    @Autowired private RiverSectionMapper sectionMapper;
    @Autowired private RiverMapper riverMapper;
    @Autowired private PatrolPointMapper pointMapper;
    @Autowired private RiverIssueMapper issueMapper;
    @Autowired private SysLogMapper logMapper;
    @Autowired private WaterQualityRecordMapper waterMapper;
    @Autowired private SysUserMapper userMapper;

    @GetMapping("/page")
    public R<Map<String, Object>> page(@RequestParam(defaultValue = "1") int page,
                                       @RequestParam(defaultValue = "10") int size,
                                       @RequestParam(required = false) String keyword,
                                       @RequestParam(required = false) String area,
                                       @RequestParam(required = false) String level,
                                       @RequestParam(required = false) String status,
                                       @RequestParam(required = false) Long riverId) {
        LambdaQueryWrapper<RiverSection> w = new LambdaQueryWrapper<>();
        if (keyword != null && !keyword.isBlank()) {
            w.and(q -> q.like(RiverSection::getName, keyword).or().like(RiverSection::getCode, keyword));
        }
        w.eq(area != null && !area.isBlank(), RiverSection::getArea, area)
                .eq(level != null && !level.isBlank(), RiverSection::getWaterQualityLevel, level)
                .eq(status != null && !status.isBlank(), RiverSection::getStatus, status)
                .eq(riverId != null, RiverSection::getRiverId, riverId)
                .orderByAsc(RiverSection::getCode);
        Page<RiverSection> p = sectionMapper.selectPage(new Page<>(page, size), w);
        Map<Long, String> riverNames = new HashMap<>();
        riverMapper.selectList(null).forEach(r -> riverNames.put(r.getId(), r.getName()));
        List<Map<String, Object>> list = new ArrayList<>();
        for (RiverSection s : p.getRecords()) {
            Map<String, Object> m = new LinkedHashMap<>();
            m.put("id", s.getId());
            m.put("code", s.getCode());
            m.put("name", s.getName());
            m.put("riverName", riverNames.getOrDefault(s.getRiverId(), "—"));
            m.put("area", s.getArea());
            m.put("waterQualityLevel", s.getWaterQualityLevel());
            m.put("manager", s.getManager());
            m.put("patrolFreq", s.getPatrolFreq());
            m.put("status", s.getStatus());
            m.put("coverImage", s.getCoverImage());
            m.put("lengthKm", s.getLengthKm());
            list.add(m);
        }
        Map<String, Object> data = new LinkedHashMap<>();
        data.put("total", p.getTotal());
        data.put("page", page);
        data.put("size", size);
        data.put("records", list);
        return R.ok(data);
    }

    @GetMapping("/rivers")
    public R<List<River>> rivers() {
        return R.ok(riverMapper.selectList(null));
    }

    @GetMapping("/options")
    public R<List<Map<String, Object>>> options() {
        List<Map<String, Object>> list = new ArrayList<>();
        for (RiverSection s : sectionMapper.selectList(new LambdaQueryWrapper<RiverSection>().orderByAsc(RiverSection::getCode))) {
            Map<String, Object> m = new LinkedHashMap<>();
            m.put("id", s.getId());
            m.put("code", s.getCode());
            m.put("name", s.getName());
            m.put("area", s.getArea());
            list.add(m);
        }
        return R.ok(list);
    }

    @GetMapping("/{id}")
    public R<Map<String, Object>> detail(@PathVariable Long id) {
        RiverSection s = sectionMapper.selectById(id);
        if (s == null) {
            throw new BizException(404, "断面不存在");
        }
        Map<String, Object> data = new LinkedHashMap<>();
        data.put("section", s);
        data.put("river", riverMapper.selectById(s.getRiverId()));
        data.put("points", pointMapper.selectList(new LambdaQueryWrapper<PatrolPoint>()
                .eq(PatrolPoint::getSectionId, id).orderByAsc(PatrolPoint::getSort)));
        List<RiverIssue> issues = issueMapper.selectList(new LambdaQueryWrapper<RiverIssue>()
                .eq(RiverIssue::getSectionId, id).orderByDesc(RiverIssue::getReportTime).last("limit 8"));
        data.put("issues", issues);
        data.put("waterRecords", waterMapper.selectList(new LambdaQueryWrapper<WaterQualityRecord>()
                .eq(WaterQualityRecord::getSectionId, id).orderByDesc(WaterQualityRecord::getRecordTime).last("limit 6")));
        data.put("logs", logMapper.selectList(new LambdaQueryWrapper<SysLog>()
                .eq(SysLog::getBizNo, s.getCode()).orderByDesc(SysLog::getCreateTime).last("limit 8")));
        return R.ok(data);
    }

    /** 断面编号唯一 + 去掉首尾空格；编号由后端生成不再接受前端传入 */
    @PostMapping
    public R<RiverSection> create(@RequestBody RiverSection body) {
        requireAdminOrDispatcher();
        body.setCode(body.getCode() == null ? null : body.getCode().trim());
        if (body.getCode() == null || body.getCode().isEmpty()) {
            body.setCode("HD-" + String.format("%04d", new Random().nextInt(9000) + 1000));
        }
        if (sectionMapper.selectCount(new LambdaQueryWrapper<RiverSection>().eq(RiverSection::getCode, body.getCode())) > 0) {
            throw new BizException("断面编号已存在");
        }
        body.setDeleted(0);
        body.setVersion(0);
        body.setCreateTime(LocalDateTime.now());
        sectionMapper.insert(body);
        return R.ok(body);
    }

    @PutMapping("/{id}")
    public R<RiverSection> update(@PathVariable Long id, @RequestBody RiverSection body) {
        requireAdminOrDispatcher();
        RiverSection db = sectionMapper.selectById(id);
        if (db == null) {
            throw new BizException(404, "断面不存在");
        }
        // 乐观锁：前端回传版本号，不一致说明他人已修改
        if (body.getVersion() != null && !body.getVersion().equals(db.getVersion())) {
            throw new BizException(409, "数据已被他人更新，请刷新后再提交");
        }
        body.setId(id);
        body.setVersion(db.getVersion() + 1);
        body.setUpdateTime(LocalDateTime.now());
        sectionMapper.updateById(body);
        return R.ok(sectionMapper.selectById(id));
    }

    private void requireAdminOrDispatcher() {
        String role = UserContext.role();
        if (!"admin".equals(role) && !"dispatcher".equals(role)) {
            throw new BizException(403, "仅管理员或调度员可维护断面档案");
        }
    }
}
