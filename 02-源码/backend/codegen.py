#!/usr/bin/env python3
# 依据表结构生成 MyBatis-Plus 实体与 Mapper（避免手写 34 个文件）
import pathlib

BASE = pathlib.Path(__file__).parent / "src/main/java/com/riverpatrol"
(BASE / "entity").mkdir(parents=True, exist_ok=True)
(BASE / "mapper").mkdir(parents=True, exist_ok=True)

L, S, I, D, T = "Long", "String", "Integer", "BigDecimal", "LocalDateTime"

TABLES = {
    "SysUser": ("sys_user", [("id", L), ("username", S), ("password", S), ("realName", S), ("phone", S), ("avatar", S),
                             ("deptId", L), ("roleCode", S), ("status", I), ("lastLogin", T), ("createTime", T), ("deleted", I)]),
    "SysRole": ("sys_role", [("id", L), ("code", S), ("name", S), ("dataScope", S), ("remark", S), ("createTime", T)]),
    "SysMenu": ("sys_menu", [("id", L), ("parentId", L), ("name", S), ("path", S), ("component", S), ("icon", S),
                             ("perm", S), ("type", S), ("sort", I), ("visible", I)]),
    "SysDept": ("sys_dept", [("id", L), ("name", S), ("parentId", L), ("sort", I), ("createTime", T)]),
    "SysMessage": ("sys_message", [("id", L), ("title", S), ("content", S), ("type", S), ("bizNo", S), ("bizId", L),
                                   ("receiverId", L), ("isRead", I), ("createTime", T)]),
    "SysLog": ("sys_log", [("id", L), ("userId", L), ("username", S), ("module", S), ("action", S), ("bizNo", S),
                           ("beforeStatus", S), ("afterStatus", S), ("reason", S), ("ip", S), ("createTime", T)]),
    "SysFile": ("sys_file", [("id", L), ("fileName", S), ("path", S), ("size", L), ("contentType", S),
                             ("uploaderId", L), ("createTime", T)]),
    "River": ("river", [("id", L), ("code", S), ("name", S), ("lengthKm", D), ("area", S), ("level", S),
                        ("manager", S), ("phone", S), ("intro", S), ("createTime", T)]),
    "RiverSection": ("river_section", [("id", L), ("code", S), ("name", S), ("riverId", L), ("startPoint", S),
                                       ("endPoint", S), ("lengthKm", D), ("area", S), ("waterQualityLevel", S),
                                       ("patrolRoute", S), ("manager", S), ("patrolFreq", S), ("status", S),
                                       ("coverImage", S), ("longitude", D), ("latitude", D), ("createTime", T),
                                       ("updateTime", T), ("deleted", I), ("version", I)]),
    "PatrolPoint": ("patrol_point", [("id", L), ("sectionId", L), ("name", S), ("type", S), ("longitude", D),
                                     ("latitude", D), ("facility", S), ("status", S), ("sort", I)]),
    "RiverTask": ("river_task", [("id", L), ("code", S), ("title", S), ("sectionId", L), ("taskType", S),
                                 ("cycleType", S), ("assigneeId", L), ("deadline", T), ("finishTime", T),
                                 ("status", S), ("remark", S), ("createTime", T)]),
    "WaterQualityRecord": ("water_quality_record", [("id", L), ("taskId", L), ("sectionId", L), ("pointId", L),
                                                    ("ph", D), ("turbidity", D), ("dissolvedOxygen", D), ("level", S),
                                                    ("recordTime", T), ("recorderId", L), ("image", S), ("remark", S),
                                                    ("createTime", T)]),
    "RiverIssue": ("river_issue", [("id", L), ("code", S), ("title", S), ("sectionId", L), ("pointId", L),
                                   ("issueType", S), ("level", S), ("longitude", D), ("latitude", D),
                                   ("description", S), ("impactScope", S), ("image", S), ("reporterId", L),
                                   ("reportTime", T), ("status", S), ("deadline", T), ("deptId", L),
                                   ("supervise", I), ("tempMeasure", S), ("parentIssueId", L), ("disposeTime", T),
                                   ("closeTime", T), ("createTime", T), ("updateTime", T), ("deleted", I),
                                   ("version", I)]),
    "DisposalProgress": ("disposal_progress", [("id", L), ("issueId", L), ("deptId", L), ("reporterId", L),
                                               ("stage", S), ("content", S), ("personCount", I), ("material", S),
                                               ("cost", D), ("result", S), ("images", S), ("progressTime", T),
                                               ("createTime", T)]),
    "ReviewRecord": ("review_record", [("id", L), ("issueId", L), ("reviewerId", L), ("reviewTime", T),
                                       ("waterColor", S), ("smell", S), ("ph", D), ("turbidity", D),
                                       ("dissolvedOxygen", D), ("conclusion", S), ("pass", I), ("reason", S),
                                       ("images", S), ("createTime", T)]),
    "PatrolRule": ("river_patrol_rule", [("id", L), ("name", S), ("version", S), ("weightPosition", D),
                                         ("weightType", D), ("weightCount", D), ("weightDuration", D),
                                         ("weightReview", D), ("weightQuality", D), ("thresholdHigh", D),
                                         ("thresholdMid", D), ("windowDays", I), ("countFull", I), ("status", S),
                                         ("effectiveTime", T), ("createBy", S), ("createTime", T)]),
    "PatrolScore": ("river_patrol_score", [("id", L), ("sectionId", L), ("ruleId", L), ("ruleVersion", S),
                                           ("inputSnapshot", S), ("scorePosition", D), ("scoreType", D),
                                           ("scoreCount", D), ("scoreDuration", D), ("scoreReview", D),
                                           ("scoreQuality", D), ("totalScore", D), ("level", S), ("recommend", S),
                                           ("factors", S), ("unmet", S), ("suggestions", S), ("calcTime", T),
                                           ("manualLevel", S), ("manualReason", S), ("adjustUser", S),
                                           ("adjustTime", T)]),
}

ENTITY_TPL = """package com.riverpatrol.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;
import java.math.BigDecimal;
import java.time.LocalDateTime;

/** {cn} 实体，对应表 {table} */
@Data
@TableName("{table}")
public class {cls} {{
{fields}}}
"""

IMPORTS = {L: "", S: "", I: "", D: "", T: ""}

for cls, (table, fields) in TABLES.items():
    lines = []
    for f, t in fields:
        if f == "id":
            lines.append("    @TableId(type = IdType.AUTO)\n    private %s id;" % t)
        else:
            lines.append("    private %s %s;" % (t, f))
    src = ENTITY_TPL.format(cn=cls.replace("Sys", "系统").replace("River", "河道"), table=table, cls=cls,
                            fields="\n".join(lines) + "\n")
    (BASE / "entity" / (cls + ".java")).write_text(src, encoding="utf-8")

    mapper = """package com.riverpatrol.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.riverpatrol.entity.%s;
import org.apache.ibatis.annotations.Mapper;

@Mapper
public interface %sMapper extends BaseMapper<%s> {
}
""" % (cls, cls, cls)
    (BASE / "mapper" / (cls + "Mapper.java")).write_text(mapper, encoding="utf-8")

print("entities", len(TABLES), "mappers", len(TABLES))
