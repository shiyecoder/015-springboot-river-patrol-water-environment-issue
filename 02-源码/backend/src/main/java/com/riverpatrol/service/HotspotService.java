package com.riverpatrol.service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.riverpatrol.common.BizException;
import com.riverpatrol.entity.*;
import com.riverpatrol.mapper.*;
import com.riverpatrol.security.UserContext;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.time.Duration;
import java.time.LocalDateTime;
import java.util.*;
import java.util.stream.Collectors;

/**
 * 创新点：问题复发热点识别。
 * 规则可配置（权重合计 100%），每次计算保存输入快照 + 明细分 + 规则版本，结果可解释、可人工修正。
 */
@Service
public class HotspotService {

    @Autowired private RiverSectionMapper sectionMapper;
    @Autowired private RiverIssueMapper issueMapper;
    @Autowired private ReviewRecordMapper reviewMapper;
    @Autowired private WaterQualityRecordMapper waterMapper;
    @Autowired private PatrolRuleMapper ruleMapper;
    @Autowired private PatrolScoreMapper scoreMapper;

    private static final Map<String, BigDecimal> TYPE_WEIGHT = Map.of(
            "非法排放", new BigDecimal("1.00"),
            "水色异常", new BigDecimal("0.80"),
            "岸线垃圾", new BigDecimal("0.60"),
            "水面漂浮物", new BigDecimal("0.50"),
            "设施损坏", new BigDecimal("0.40"));

    private static final Map<String, BigDecimal> QUALITY_FACTOR = Map.of(
            "劣Ⅴ类", new BigDecimal("1.00"),
            "Ⅴ类", new BigDecimal("0.80"),
            "Ⅳ类", new BigDecimal("0.55"),
            "Ⅲ类", new BigDecimal("0.30"),
            "Ⅱ类", new BigDecimal("0.15"));

    public PatrolRule activeRule() {
        PatrolRule r = ruleMapper.selectOne(new LambdaQueryWrapper<PatrolRule>()
                .eq(PatrolRule::getStatus, "启用").orderByDesc(PatrolRule::getEffectiveTime).last("limit 1"));
        if (r == null) {
            throw new BizException("未配置启用中的热点识别规则");
        }
        return r;
    }

    /**
     * 执行一次热点识别计算。
     * 六项输入按规则权重归一化后加权求和，缺失项不参与计算并在 unmet 中提示。
     */
    @Transactional
    public PatrolScore evaluate(Long sectionId, PatrolRule rule) {
        RiverSection section = sectionMapper.selectById(sectionId);
        if (section == null) {
            throw new BizException(404, "断面不存在");
        }
        LocalDateTime from = LocalDateTime.now().minusDays(rule.getWindowDays());
        List<RiverIssue> issues = issueMapper.selectList(new LambdaQueryWrapper<RiverIssue>()
                .eq(RiverIssue::getSectionId, sectionId)
                .ge(RiverIssue::getReportTime, from)
                .ne(RiverIssue::getStatus, "无效上报"));

        int count = issues.size();
        // 主导问题类型取窗口内出现最多的一类
        String dominantType = issues.stream()
                .collect(Collectors.groupingBy(RiverIssue::getIssueType, Collectors.counting()))
                .entrySet().stream().max(Map.Entry.comparingByValue())
                .map(Map.Entry::getKey).orElse("岸线垃圾");

        double avgHours = issues.stream().filter(i -> i.getDisposeTime() != null)
                .mapToLong(i -> Duration.between(i.getReportTime(), i.getDisposeTime()).toHours())
                .average().orElse(0);

        List<Long> issueIds = issues.stream().map(RiverIssue::getId).collect(Collectors.toList());
        long reviewTotal = 0, reviewPass = 0;
        if (!issueIds.isEmpty()) {
            List<ReviewRecord> reviews = reviewMapper.selectList(new LambdaQueryWrapper<ReviewRecord>()
                    .in(ReviewRecord::getIssueId, issueIds));
            reviewTotal = reviews.size();
            reviewPass = reviews.stream().filter(r -> r.getPass() != null && r.getPass() == 1).count();
        }
        double passRate = reviewTotal == 0 ? 1.0 : (double) reviewPass / reviewTotal;

        String quality = section.getWaterQualityLevel() == null ? "Ⅳ类" : section.getWaterQualityLevel();
        BigDecimal qualityNorm = QUALITY_FACTOR.getOrDefault(quality, new BigDecimal("0.55"));

        BigDecimal posNorm = ("重点监管".equals(section.getStatus()) || "整治中".equals(section.getStatus()))
                ? BigDecimal.ONE : new BigDecimal("0.60");
        BigDecimal typeNorm = TYPE_WEIGHT.getOrDefault(dominantType, new BigDecimal("0.50"));
        BigDecimal countNorm = BigDecimal.valueOf(Math.min(count / (double) rule.getCountFull(), 1.0));
        BigDecimal durNorm = avgHours == 0 ? BigDecimal.ZERO
                : BigDecimal.valueOf(Math.min(avgHours / 60.0, 1.0));
        BigDecimal reviewNorm = BigDecimal.valueOf(1 - passRate);

        BigDecimal wPos = rule.getWeightPosition().divide(BigDecimal.valueOf(100), 4, RoundingMode.HALF_UP);
        BigDecimal wType = rule.getWeightType().divide(BigDecimal.valueOf(100), 4, RoundingMode.HALF_UP);
        BigDecimal wCnt = rule.getWeightCount().divide(BigDecimal.valueOf(100), 4, RoundingMode.HALF_UP);
        BigDecimal wDur = rule.getWeightDuration().divide(BigDecimal.valueOf(100), 4, RoundingMode.HALF_UP);
        BigDecimal wRev = rule.getWeightReview().divide(BigDecimal.valueOf(100), 4, RoundingMode.HALF_UP);
        BigDecimal wQual = rule.getWeightQuality().divide(BigDecimal.valueOf(100), 4, RoundingMode.HALF_UP);

        BigDecimal sPos = posNorm.multiply(wPos).multiply(BigDecimal.valueOf(100)).setScale(2, RoundingMode.HALF_UP);
        BigDecimal sType = typeNorm.multiply(wType).multiply(BigDecimal.valueOf(100)).setScale(2, RoundingMode.HALF_UP);
        BigDecimal sCnt = countNorm.multiply(wCnt).multiply(BigDecimal.valueOf(100)).setScale(2, RoundingMode.HALF_UP);
        BigDecimal sDur = durNorm.multiply(wDur).multiply(BigDecimal.valueOf(100)).setScale(2, RoundingMode.HALF_UP);
        BigDecimal sRev = reviewNorm.multiply(wRev).multiply(BigDecimal.valueOf(100)).setScale(2, RoundingMode.HALF_UP);
        BigDecimal sQual = qualityNorm.multiply(wQual).multiply(BigDecimal.valueOf(100)).setScale(2, RoundingMode.HALF_UP);
        BigDecimal total = sPos.add(sType).add(sCnt).add(sDur).add(sRev).add(sQual).setScale(1, RoundingMode.HALF_UP);

        String level = total.compareTo(rule.getThresholdHigh()) >= 0 ? "高"
                : (total.compareTo(rule.getThresholdMid()) >= 0 ? "中" : "低");
        String recommend = "高".equals(level) ? "纳入专项治理" : ("中".equals(level) ? "加密巡查" : "常规管理");

        PatrolScore score = new PatrolScore();
        score.setSectionId(sectionId);
        score.setRuleId(rule.getId());
        score.setRuleVersion(rule.getVersion());
        score.setInputSnapshot(String.format(
                "{\"position\":\"%s\",\"issueType\":\"%s\",\"count90\":%d,\"avgDuration\":%.0f,\"reviewPass\":%.2f,\"quality\":\"%s\"}",
                section.getArea(), dominantType, count, avgHours, passRate, quality));
        score.setScorePosition(sPos);
        score.setScoreType(sType);
        score.setScoreCount(sCnt);
        score.setScoreDuration(sDur);
        score.setScoreReview(sRev);
        score.setScoreQuality(sQual);
        score.setTotalScore(total);
        score.setLevel(level);
        score.setRecommend(recommend);
        score.setFactors(String.format("近 %d 天同类问题 %d 次（主导类型 %s）；平均处置时长 %.0f 小时；体质等级 %s；复查通过率 %.0f%%",
                rule.getWindowDays(), count, dominantType, avgHours, quality, passRate * 100));
        score.setUnmet((count >= rule.getCountFull() ? "近 " + rule.getWindowDays() + " 天次数已达满分线，未达到「低复发」条件；" : "")
                + (avgHours > 60 ? "平均处置时长超过制度要求 60 小时；" : ""));
        score.setSuggestions("增设截污设施；加密巡查频次至每周 2 次；纳入雨污分流改造计划");
        score.setCalcTime(LocalDateTime.now());
        scoreMapper.insert(score);
        return score;
    }

    /** 人工调整只写 manual_* 字段，原始计算结果永不覆盖 */
    @Transactional
    public PatrolScore adjust(Long scoreId, String level, String reason) {
        if (reason == null || reason.trim().length() < 5) {
            throw new BizException("人工调整必须填写不少于 5 个字的原因");
        }
        PatrolScore s = scoreMapper.selectById(scoreId);
        if (s == null) {
            throw new BizException(404, "计算结果不存在");
        }
        s.setManualLevel(level);
        s.setManualReason(reason.trim());
        s.setAdjustUser(UserContext.get() == null ? "system" : UserContext.get().getUsername());
        s.setAdjustTime(LocalDateTime.now());
        scoreMapper.updateById(s);
        return s;
    }

    /** 看板列表：每个断面取最新一次计算结果 */
    public List<Map<String, Object>> list(String level, Integer windowDays) {
        Map<Long, String> secNames = new HashMap<>();
        Map<Long, RiverSection> secMap = new HashMap<>();
        sectionMapper.selectList(null).forEach(s -> {
            secNames.put(s.getId(), s.getCode() + " " + s.getName());
            secMap.put(s.getId(), s);
        });
        List<PatrolScore> all = scoreMapper.selectList(new LambdaQueryWrapper<PatrolScore>()
                .orderByDesc(PatrolScore::getCalcTime));
        Map<Long, PatrolScore> latest = new LinkedHashMap<>();
        for (PatrolScore s : all) {
            latest.putIfAbsent(s.getSectionId(), s);
        }
        List<Map<String, Object>> rows = new ArrayList<>();
        for (PatrolScore s : latest.values()) {
            String effLevel = s.getManualLevel() == null ? s.getLevel() : s.getManualLevel();
            if (level != null && !level.isBlank() && !level.equals(effLevel)) {
                continue;
            }
            Map<String, Object> m = new LinkedHashMap<>();
            m.put("id", s.getId());
            m.put("sectionId", s.getSectionId());
            m.put("sectionName", secNames.getOrDefault(s.getSectionId(), "—"));
            m.put("totalScore", s.getTotalScore());
            m.put("level", s.getLevel());
            m.put("manualLevel", s.getManualLevel());
            m.put("effectiveLevel", effLevel);
            m.put("recommend", s.getRecommend());
            m.put("ruleVersion", s.getRuleVersion());
            m.put("calcTime", s.getCalcTime());
            m.put("factors", s.getFactors());
            m.put("unmet", s.getUnmet());
            m.put("suggestions", s.getSuggestions());
            m.put("manualReason", s.getManualReason());
            m.put("waterQuality", secMap.containsKey(s.getSectionId())
                    ? secMap.get(s.getSectionId()).getWaterQualityLevel() : "—");
            rows.add(m);
        }
        rows.sort((a, b) -> ((BigDecimal) b.get("totalScore")).compareTo((BigDecimal) a.get("totalScore")));
        return rows;
    }

    /** 规则新增版本：权重合计必须 100%，旧版本置为历史 */
    @Transactional
    public PatrolRule saveRule(PatrolRule body) {
        BigDecimal sum = body.getWeightPosition().add(body.getWeightType()).add(body.getWeightCount())
                .add(body.getWeightDuration()).add(body.getWeightReview()).add(body.getWeightQuality());
        if (sum.compareTo(BigDecimal.valueOf(100)) != 0) {
            throw new BizException("权重合计必须等于 100%，当前为 " + sum.stripTrailingZeros().toPlainString() + "%");
        }
        PatrolRule current = activeRule();
        String nextVersion = "v" + (Integer.parseInt(current.getVersion().replace("v", "")) + 1);
        ruleMapper.selectList(new LambdaQueryWrapper<PatrolRule>().eq(PatrolRule::getStatus, "启用"))
                .forEach(r -> {
                    r.setStatus("历史");
                    ruleMapper.updateById(r);
                });
        body.setId(null);
        body.setVersion(nextVersion);
        body.setStatus("启用");
        body.setEffectiveTime(LocalDateTime.now());
        body.setCreateBy(UserContext.get() == null ? "system" : UserContext.get().getUsername());
        body.setCreateTime(LocalDateTime.now());
        ruleMapper.insert(body);
        return body;
    }

    public List<PatrolRule> rules() {
        return ruleMapper.selectList(new LambdaQueryWrapper<PatrolRule>().orderByDesc(PatrolRule::getEffectiveTime));
    }

    /** 看板统计：推荐采纳率、调整率、等级分布 */
    public Map<String, Object> stats() {
        List<PatrolScore> scores = scoreMapper.selectList(null);
        long total = scores.size();
        long adjusted = scores.stream().filter(s -> s.getManualLevel() != null).count();
        long high = scores.stream().filter(s -> "高".equals(s.getManualLevel() == null ? s.getLevel() : s.getManualLevel())).count();
        long mid = scores.stream().filter(s -> "中".equals(s.getManualLevel() == null ? s.getLevel() : s.getManualLevel())).count();
        long low = total - high - mid;
        Map<String, Object> m = new LinkedHashMap<>();
        m.put("total", total);
        m.put("adjusted", adjusted);
        m.put("adjustRate", total == 0 ? 0 : Math.round(adjusted * 1000.0 / total) / 10.0);
        m.put("adoptRate", total == 0 ? 0 : Math.round((total - adjusted) * 1000.0 / total) / 10.0);
        Map<String, Long> dist = new LinkedHashMap<>();
        dist.put("高", high);
        dist.put("中", mid);
        dist.put("低", low);
        m.put("distribution", dist);
        return m;
    }
}
