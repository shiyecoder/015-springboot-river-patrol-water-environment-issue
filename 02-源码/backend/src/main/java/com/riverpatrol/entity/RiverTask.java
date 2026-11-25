package com.riverpatrol.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;
import java.math.BigDecimal;
import java.time.LocalDateTime;

/** 河道Task 实体，对应表 river_task */
@Data
@TableName("river_task")
public class RiverTask {
    @TableId(type = IdType.AUTO)
    private Long id;
    private String code;
    private String title;
    private Long sectionId;
    private String taskType;
    private String cycleType;
    private Long assigneeId;
    private LocalDateTime deadline;
    private LocalDateTime finishTime;
    private String status;
    private String remark;
    private LocalDateTime createTime;
}
