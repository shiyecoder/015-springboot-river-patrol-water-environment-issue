package com.riverpatrol.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;
import java.math.BigDecimal;
import java.time.LocalDateTime;

/** ReviewRecord 实体，对应表 review_record */
@Data
@TableName("review_record")
public class ReviewRecord {
    @TableId(type = IdType.AUTO)
    private Long id;
    private Long issueId;
    private Long reviewerId;
    private LocalDateTime reviewTime;
    private String waterColor;
    private String smell;
    private BigDecimal ph;
    private BigDecimal turbidity;
    private BigDecimal dissolvedOxygen;
    private String conclusion;
    private Integer pass;
    private String reason;
    private String images;
    private LocalDateTime createTime;
}
