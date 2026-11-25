package com.riverpatrol.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;
import java.math.BigDecimal;
import java.time.LocalDateTime;

/** DisposalProgress 实体，对应表 disposal_progress */
@Data
@TableName("disposal_progress")
public class DisposalProgress {
    @TableId(type = IdType.AUTO)
    private Long id;
    private Long issueId;
    private Long deptId;
    private Long reporterId;
    private String stage;
    private String content;
    private Integer personCount;
    private String material;
    private BigDecimal cost;
    private String result;
    private String images;
    private LocalDateTime progressTime;
    private LocalDateTime createTime;
}
