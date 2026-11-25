package com.riverpatrol.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;
import java.math.BigDecimal;
import java.time.LocalDateTime;

/** WaterQualityRecord 实体，对应表 water_quality_record */
@Data
@TableName("water_quality_record")
public class WaterQualityRecord {
    @TableId(type = IdType.AUTO)
    private Long id;
    private Long taskId;
    private Long sectionId;
    private Long pointId;
    private BigDecimal ph;
    private BigDecimal turbidity;
    private BigDecimal dissolvedOxygen;
    private String level;
    private LocalDateTime recordTime;
    private Long recorderId;
    private String image;
    private String remark;
    private LocalDateTime createTime;
}
