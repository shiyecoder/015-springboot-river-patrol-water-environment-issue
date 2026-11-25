package com.riverpatrol.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.riverpatrol.entity.PatrolPoint;
import org.apache.ibatis.annotations.Mapper;

@Mapper
public interface PatrolPointMapper extends BaseMapper<PatrolPoint> {
}
