package com.riverpatrol.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;
import java.math.BigDecimal;
import java.time.LocalDateTime;

/** PatrolPoint 实体，对应表 patrol_point */
@Data
@TableName("patrol_point")
public class PatrolPoint {
    @TableId(type = IdType.AUTO)
    private Long id;
    private Long sectionId;
    private String name;
    private String type;
    private BigDecimal longitude;
    private BigDecimal latitude;
    private String facility;
    private String status;
    private Integer sort;
}
