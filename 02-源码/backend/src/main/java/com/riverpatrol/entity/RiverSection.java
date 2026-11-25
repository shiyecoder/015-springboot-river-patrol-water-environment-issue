package com.riverpatrol.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;
import java.math.BigDecimal;
import java.time.LocalDateTime;

/** 河道Section 实体，对应表 river_section */
@Data
@TableName("river_section")
public class RiverSection {
    @TableId(type = IdType.AUTO)
    private Long id;
    private String code;
    private String name;
    private Long riverId;
    private String startPoint;
    private String endPoint;
    private BigDecimal lengthKm;
    private String area;
    private String waterQualityLevel;
    private String patrolRoute;
    private String manager;
    private String patrolFreq;
    private String status;
    private String coverImage;
    private BigDecimal longitude;
    private BigDecimal latitude;
    private LocalDateTime createTime;
    private LocalDateTime updateTime;
    private Integer deleted;
    private Integer version;
}
