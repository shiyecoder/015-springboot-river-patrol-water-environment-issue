package com.riverpatrol.controller;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.riverpatrol.common.R;
import com.riverpatrol.entity.*;
import com.riverpatrol.mapper.*;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.*;

/** 首页统计：核心指标与 6 个图表数据，全部后端聚合，前端不做全表二次计算 */
@RestController
@RequestMapping("/api/dashboard")
public class DashboardController {

    @Autowired private RiverTaskMapper taskMapper;
    @Autowired private RiverIssueMapper issueMapper;
    @Autowired private ReviewRecordMapper reviewMapper;
    @Autowired private RiverSectionMapper sectionMapper;
    @Autowired private SysDeptMapper deptMapper;
    @Autowired private PatrolScoreMapper scoreMapper;
    @Autowired private SysMessageMapper messageMapper;

    @GetMapping("/overview")
    public R<Map<String, Object>> overview() {
        LocalDateTime from = LocalDateTime.now().minusDays(30);
        List<RiverTask> tasks = taskMapper.selectList(new LambdaQueryWrapper<RiverTask>()
                .ge(RiverTask::getCreateTime, from));
        List<RiverIssue> issues = issueMapper.selectList(new LambdaQueryWrapper<RiverIssue>()
                .ge(RiverIssue::getReportTime, from));
        List<RiverIssue> allIssues = issueMapper.selectList(null);
        List<ReviewRecord> reviews = reviewMapper.selectList(null);
        List<RiverSection> sections = sectionMapper.selectList(null);

        long doneTask = tasks.stream().filter(t -> "已完成".equals(t.getStatus())).count();
        long overdue = allIssues.stream().filter(i -> i.getDeadline() != null
                && i.getDeadline().isBefore(LocalDateTime.now())
                && !"已关闭".equals(i.getStatus()) && !"无效上报".equals(i.getStatus())).count();
        long closed = allIssues.stream().filter(i -> "已关闭".equals(i.getStatus())).count();
        long onTime = allIssues.stream().filter(i -> "已关闭".equals(i.getStatus()) && i.getCloseTime() != null
                && i.getDeadline() != null && !i.getCloseTime().isAfter(i.getDeadline())).count();
        long passCount = reviews.stream().filter(r -> r.getPass() != null && r.getPass() == 1).count();
        // 复发：同一断面 90 天内同类问题 >=2 次
        Map<String, Long> keyCount = new HashMap<>();
        for (RiverIssue i : allIssues) {
            keyCount.merge(i.getSectionId() + "|" + i.getIssueType(), 1L, Long::sum);
        }
        long recur = keyCount.values().stream().filter(v -> v >= 2).count();

        Map<String, Object> metrics = new LinkedHashMap<>();
        metrics.put("patrolRate", tasks.isEmpty() ? 0 : pct(doneTask, tasks.size()));
        metrics.put("issueCount", issues.size());
        metrics.put("majorCount", issues.stream().filter(i -> "重大".equals(i.getLevel())).count());
        metrics.put("onTimeRate", allIssues.isEmpty() ? 0 : pct(onTime, Math.max(closed, 1)));
        metrics.put("recurRate", allIssues.isEmpty() ? 0 : pct(recur, Math.max(keyCount.size(), 1)));
        metrics.put("reviewPassRate", reviews.isEmpty() ? 0 : pct(passCount, reviews.size()));
        metrics.put("overdue", overdue);
        metrics.put("sectionCount", sections.size());

        // 1. 近 6 个月上报/关闭趋势
        List<String> months = new ArrayList<>();
        List<Long> reportSeries = new ArrayList<>();
        List<Long> closeSeries = new ArrayList<>();
        DateTimeFormatter mf = DateTimeFormatter.ofPattern("yyyy-MM");
        for (int k = 5; k >= 0; k--) {
            LocalDate d = LocalDate.now().minusMonths(k);
            months.add(d.format(mf));
            String mk = d.format(mf);
            reportSeries.add(allIssues.stream()
                    .filter(i -> i.getReportTime() != null && i.getReportTime().format(mf).equals(mk)).count());
            closeSeries.add(allIssues.stream()
                    .filter(i -> i.getCloseTime() != null && i.getCloseTime().format(mf).equals(mk)).count());
        }
        Map<String, Object> trend = new LinkedHashMap<>();
        trend.put("months", months);
        trend.put("report", reportSeries);
        trend.put("close", closeSeries);

        // 2. 状态分布
        Map<String, Long> statusDist = new LinkedHashMap<>();
        for (String s : List.of("待确认", "待派单", "处置中", "待复查", "已关闭", "无效上报")) {
            statusDist.put(s, allIssues.stream().filter(i -> s.equals(i.getStatus())).count());
        }
        // 3. 类型构成
        Map<String, Long> typeDist = new LinkedHashMap<>();
        for (String t : List.of("非法排放", "岸线垃圾", "水面漂浮物", "设施损坏", "水色异常")) {
            typeDist.put(t, allIssues.stream().filter(i -> t.equals(i.getIssueType())).count());
        }
        // 4. 责任单位排行
        Map<Long, String> deptNames = new HashMap<>();
        deptMapper.selectList(null).forEach(d -> deptNames.put(d.getId(), d.getName()));
        Map<String, Long> deptRank = new LinkedHashMap<>();
        allIssues.stream().filter(i -> i.getDeptId() != null)
                .collect(java.util.stream.Collectors.groupingBy(i -> deptNames.getOrDefault(i.getDeptId(), "其他"),
                        java.util.stream.Collectors.counting()))
                .entrySet().stream().sorted(Map.Entry.<String, Long>comparingByValue().reversed())
                .limit(5).forEach(e -> deptRank.put(e.getKey(), e.getValue()));
        // 5. 水质等级分布
        Map<String, Long> qualityDist = new LinkedHashMap<>();
        for (String q : List.of("Ⅱ类", "Ⅲ类", "Ⅳ类", "Ⅴ类", "劣Ⅴ类")) {
            qualityDist.put(q, sections.stream().filter(s -> q.equals(s.getWaterQualityLevel())).count());
        }
        // 6. 热点识别等级分布
        List<PatrolScore> scores = scoreMapper.selectList(null);
        Map<Long, PatrolScore> latest = new HashMap<>();
        scores.stream().sorted(Comparator.comparing(PatrolScore::getCalcTime).reversed())
                .forEach(s -> latest.putIfAbsent(s.getSectionId(), s));
        Map<String, Long> hotspotDist = new LinkedHashMap<>();
        for (String lv : List.of("高", "中", "低")) {
            hotspotDist.put(lv, latest.values().stream()
                    .filter(s -> lv.equals(s.getManualLevel() == null ? s.getLevel() : s.getManualLevel())).count());
        }

        Map<String, Object> data = new LinkedHashMap<>();
        data.put("metrics", metrics);
        data.put("trend", trend);
        data.put("statusDist", statusDist);
        data.put("typeDist", typeDist);
        data.put("deptRank", deptRank);
        data.put("qualityDist", qualityDist);
        data.put("hotspotDist", hotspotDist);
        data.put("unread", messageMapper.selectCount(new LambdaQueryWrapper<SysMessage>()
                .eq(SysMessage::getIsRead, 0)));
        return R.ok(data);
    }

    private double pct(long a, long b) {
        return b == 0 ? 0 : Math.round(a * 1000.0 / b) / 10.0;
    }
}
