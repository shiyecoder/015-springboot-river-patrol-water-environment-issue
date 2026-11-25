package com.riverpatrol.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;
import java.math.BigDecimal;
import java.time.LocalDateTime;

/** PatrolScore 实体，对应表 river_patrol_score */
@Data
@TableName("river_patrol_score")
public class PatrolScore {
    @TableId(type = IdType.AUTO)
    private Long id;
    private Long sectionId;
    private Long ruleId;
    private String ruleVersion;
    private String inputSnapshot;
    private BigDecimal scorePosition;
    private BigDecimal scoreType;
    private BigDecimal scoreCount;
    private BigDecimal scoreDuration;
    private BigDecimal scoreReview;
    private BigDecimal scoreQuality;
    private BigDecimal totalScore;
    private String level;
    private String recommend;
    private String factors;
    private String unmet;
    private String suggestions;
    private LocalDateTime calcTime;
    private String manualLevel;
    private String manualReason;
    private String adjustUser;
    private LocalDateTime adjustTime;
}
