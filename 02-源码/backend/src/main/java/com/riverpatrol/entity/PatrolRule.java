package com.riverpatrol.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;
import java.math.BigDecimal;
import java.time.LocalDateTime;

/** PatrolRule 实体，对应表 river_patrol_rule */
@Data
@TableName("river_patrol_rule")
public class PatrolRule {
    @TableId(type = IdType.AUTO)
    private Long id;
    private String name;
    private String version;
    private BigDecimal weightPosition;
    private BigDecimal weightType;
    private BigDecimal weightCount;
    private BigDecimal weightDuration;
    private BigDecimal weightReview;
    private BigDecimal weightQuality;
    private BigDecimal thresholdHigh;
    private BigDecimal thresholdMid;
    private Integer windowDays;
    private Integer countFull;
    private String status;
    private LocalDateTime effectiveTime;
    private String createBy;
    private LocalDateTime createTime;
}
