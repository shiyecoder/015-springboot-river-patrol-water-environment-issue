package com.riverpatrol.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;
import java.math.BigDecimal;
import java.time.LocalDateTime;

/** 系统File 实体，对应表 sys_file */
@Data
@TableName("sys_file")
public class SysFile {
    @TableId(type = IdType.AUTO)
    private Long id;
    private String fileName;
    private String path;
    private Long size;
    private String contentType;
    private Long uploaderId;
    private LocalDateTime createTime;
}
