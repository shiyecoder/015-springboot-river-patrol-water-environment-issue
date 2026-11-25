package com.riverpatrol.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;
import java.math.BigDecimal;
import java.time.LocalDateTime;

/** 河道Issue 实体，对应表 river_issue */
@Data
@TableName("river_issue")
public class RiverIssue {
    @TableId(type = IdType.AUTO)
    private Long id;
    private String code;
    private String title;
    private Long sectionId;
    private Long pointId;
    private String issueType;
    private String level;
    private BigDecimal longitude;
    private BigDecimal latitude;
    private String description;
    private String impactScope;
    private String image;
    private Long reporterId;
    private LocalDateTime reportTime;
    private String status;
    private LocalDateTime deadline;
    private Long deptId;
    private Integer supervise;
    private String tempMeasure;
    private Long parentIssueId;
    private LocalDateTime disposeTime;
    private LocalDateTime closeTime;
    private LocalDateTime createTime;
    private LocalDateTime updateTime;
    private Integer deleted;
    private Integer version;
}
