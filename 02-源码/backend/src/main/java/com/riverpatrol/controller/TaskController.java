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

/** 巡查任务：计划任务列表、临时任务、逐点录入水质、完成任务 */
@RestController
@RequestMapping("/api/task")
public class TaskController {

    @Autowired private RiverTaskMapper taskMapper;
    @Autowired private RiverSectionMapper sectionMapper;
    @Autowired private SysUserMapper userMapper;
    @Autowired private WaterQualityRecordMapper waterMapper;
    @Autowired private PatrolPointMapper pointMapper;

    @GetMapping("/page")
    public R<Map<String, Object>> page(@RequestParam(defaultValue = "1") int page,
                                       @RequestParam(defaultValue = "10") int size,
                                       @RequestParam(required = false) String status,
                                       @RequestParam(required = false) String taskType,
                                       @RequestParam(required = false) Long assigneeId,
                                       @RequestParam(required = false) String keyword) {
        LambdaQueryWrapper<RiverTask> w = new LambdaQueryWrapper<>();
        w.eq(status != null && !status.isBlank(), RiverTask::getStatus, status)
                .eq(taskType != null && !taskType.isBlank(), RiverTask::getTaskType, taskType)
                .eq(assigneeId != null, RiverTask::getAssigneeId, assigneeId)
                .and(keyword != null && !keyword.isBlank(),
                        q -> q.like(RiverTask::getTitle, keyword).or().like(RiverTask::getCode, keyword));
        if ("patroller".equals(UserContext.role())) {
            w.eq(RiverTask::getAssigneeId, UserContext.id());
        }
        w.orderByAsc(RiverTask::getStatus).orderByAsc(RiverTask::getDeadline);
        Page<RiverTask> p = taskMapper.selectPage(new Page<>(page, size), w);

        Map<Long, RiverSection> secMap = new HashMap<>();
        sectionMapper.selectList(null).forEach(s -> secMap.put(s.getId(), s));
        Map<Long, String> userNames = new HashMap<>();
        userMapper.selectList(null).forEach(u -> userNames.put(u.getId(), u.getRealName()));

        List<Map<String, Object>> rows = new ArrayList<>();
        for (RiverTask t : p.getRecords()) {
            RiverSection sec = secMap.get(t.getSectionId());
            Map<String, Object> m = new LinkedHashMap<>();
            m.put("id", t.getId());
            m.put("code", t.getCode());
            m.put("title", t.getTitle());
            m.put("sectionId", t.getSectionId());
            m.put("sectionName", sec == null ? "—" : sec.getName());
            m.put("taskType", t.getTaskType());
            m.put("cycleType", t.getCycleType());
            m.put("assigneeName", userNames.getOrDefault(t.getAssigneeId(), "—"));
            m.put("deadline", t.getDeadline());
            m.put("finishTime", t.getFinishTime());
            m.put("status", t.getStatus());
            m.put("overdue", t.getDeadline() != null && t.getDeadline().isBefore(LocalDateTime.now())
                    && !"已完成".equals(t.getStatus()));
            rows.add(m);
        }
        Map<String, Object> data = new LinkedHashMap<>();
        data.put("total", p.getTotal());
        data.put("page", page);
        data.put("size", size);
        data.put("records", rows);
        return R.ok(data);
    }

    @GetMapping("/{id}")
    public R<Map<String, Object>> detail(@PathVariable Long id) {
        RiverTask t = taskMapper.selectById(id);
        if (t == null) {
            throw new BizException(404, "任务不存在");
        }
        Map<String, Object> data = new LinkedHashMap<>();
        data.put("task", t);
        data.put("section", sectionMapper.selectById(t.getSectionId()));
        data.put("points", pointMapper.selectList(new LambdaQueryWrapper<PatrolPoint>()
                .eq(PatrolPoint::getSectionId, t.getSectionId()).orderByAsc(PatrolPoint::getSort)));
        data.put("records", waterMapper.selectList(new LambdaQueryWrapper<WaterQualityRecord>()
                .eq(WaterQualityRecord::getTaskId, id).orderByAsc(WaterQualityRecord::getId)));
        data.put("history", waterMapper.selectList(new LambdaQueryWrapper<WaterQualityRecord>()
                .eq(WaterQualityRecord::getSectionId, t.getSectionId())
                .orderByDesc(WaterQualityRecord::getRecordTime).last("limit 6")));
        return R.ok(data);
    }

    /** 新建临时任务（特殊天气后加密巡查） */
    @PostMapping
    public R<RiverTask> create(@RequestBody Map<String, Object> body) {
        String role = UserContext.role();
        if (!"dispatcher".equals(role) && !"admin".equals(role)) {
            throw new BizException(403, "仅调度员或管理员可新建任务");
        }
        RiverTask t = new RiverTask();
        t.setCode("RW-" + LocalDateTime.now().getYear() + "-" + (1000 + taskMapper.selectCount(null) + 1));
        t.setTitle(String.valueOf(body.getOrDefault("title", "临时巡查任务")));
        t.setSectionId(Long.valueOf(String.valueOf(body.get("sectionId"))));
        t.setTaskType("临时任务");
        t.setCycleType("一次性");
        t.setAssigneeId(Long.valueOf(String.valueOf(body.get("assigneeId"))));
        t.setDeadline(body.get("deadline") == null ? LocalDateTime.now().plusDays(2)
                : LocalDateTime.parse(String.valueOf(body.get("deadline")).replace(" ", "T")));
        t.setStatus("待执行");
        t.setRemark(String.valueOf(body.getOrDefault("remark", "特殊天气后加密巡查")));
        t.setCreateTime(LocalDateTime.now());
        taskMapper.insert(t);
        return R.ok(t);
    }

    /** 逐点录入：水质 + 现场情况，记录人取当前登录用户 */
    @PostMapping("/{id}/record")
    public R<WaterQualityRecord> record(@PathVariable Long id, @RequestBody Map<String, Object> body) {
        RiverTask t = taskMapper.selectById(id);
        if (t == null) {
            throw new BizException(404, "任务不存在");
        }
        if ("已完成".equals(t.getStatus())) {
            throw new BizException("任务已完成，不能重复提交");
        }
        WaterQualityRecord r = new WaterQualityRecord();
        r.setTaskId(id);
        r.setSectionId(t.getSectionId());
        r.setPointId(body.get("pointId") == null ? null : Long.valueOf(String.valueOf(body.get("pointId"))));
        r.setPh(dec(body.get("ph")));
        r.setTurbidity(dec(body.get("turbidity")));
        r.setDissolvedOxygen(dec(body.get("dissolvedOxygen")));
        r.setLevel(String.valueOf(body.getOrDefault("level", "Ⅳ类")));
        r.setRecordTime(LocalDateTime.now());
        r.setRecorderId(UserContext.id());
        r.setImage(String.valueOf(body.getOrDefault("image", "")));
        r.setRemark(String.valueOf(body.getOrDefault("remark", "现场快速检测")));
        r.setCreateTime(LocalDateTime.now());
        waterMapper.insert(r);
        if ("待执行".equals(t.getStatus())) {
            t.setStatus("执行中");
            taskMapper.updateById(t);
        }
        return R.ok(r);
    }

    /** 提交完成：至少一条水质/点位记录 */
    @PostMapping("/{id}/finish")
    public R<RiverTask> finish(@PathVariable Long id) {
        RiverTask t = taskMapper.selectById(id);
        if (t == null) {
            throw new BizException(404, "任务不存在");
        }
        long n = waterMapper.selectCount(new LambdaQueryWrapper<WaterQualityRecord>().eq(WaterQualityRecord::getTaskId, id));
        if (n == 0) {
            throw new BizException("请先录入至少一个点位的巡查记录");
        }
        t.setStatus("已完成");
        t.setFinishTime(LocalDateTime.now());
        taskMapper.updateById(t);
        return R.ok(t);
    }

    private java.math.BigDecimal dec(Object o) {
        if (o == null || String.valueOf(o).isBlank()) {
            return null;
        }
        return new java.math.BigDecimal(String.valueOf(o));
    }
}
