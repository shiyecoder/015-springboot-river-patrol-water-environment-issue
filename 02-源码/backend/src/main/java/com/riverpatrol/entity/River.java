package com.riverpatrol.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;
import java.math.BigDecimal;
import java.time.LocalDateTime;

/** 河道 实体，对应表 river */
@Data
@TableName("river")
public class River {
    @TableId(type = IdType.AUTO)
    private Long id;
    private String code;
    private String name;
    private BigDecimal lengthKm;
    private String area;
    private String level;
    private String manager;
    private String phone;
    private String intro;
    private LocalDateTime createTime;
}
