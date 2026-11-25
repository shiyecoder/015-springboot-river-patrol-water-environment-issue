package com.riverpatrol.controller;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.riverpatrol.common.BizException;
import com.riverpatrol.common.R;
import com.riverpatrol.entity.SysMessage;
import com.riverpatrol.entity.SysUser;
import com.riverpatrol.mapper.SysMessageMapper;
import com.riverpatrol.mapper.SysUserMapper;
import com.riverpatrol.security.UserContext;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.web.bind.annotation.*;

import java.util.*;

/** 个人中心与站内消息 */
@RestController
@RequestMapping("/api")
public class ProfileController {

    @Autowired private SysUserMapper userMapper;
    @Autowired private SysMessageMapper messageMapper;
    @Autowired private BCryptPasswordEncoder encoder;

    @GetMapping("/profile")
    public R<SysUser> profile() {
        SysUser u = userMapper.selectById(UserContext.id());
        u.setPassword(null);
        return R.ok(u);
    }

    /** 改资料/头像：头像上传后右上角立即同步（前端刷新 user 状态） */
    @PutMapping("/profile")
    public R<SysUser> update(@RequestBody Map<String, String> body) {
        SysUser u = userMapper.selectById(UserContext.id());
        if (body.get("realName") != null && !body.get("realName").isBlank()) {
            u.setRealName(body.get("realName").trim());
        }
        if (body.get("phone") != null) {
            u.setPhone(body.get("phone").trim());
        }
        if (body.get("avatar") != null && !body.get("avatar").isBlank()) {
            u.setAvatar(body.get("avatar"));
        }
        userMapper.updateById(u);
        u.setPassword(null);
        return R.ok(u);
    }

    @PutMapping("/profile/password")
    public R<Void> password(@RequestBody Map<String, String> body) {
        SysUser u = userMapper.selectById(UserContext.id());
        String oldPwd = body.getOrDefault("oldPassword", "");
        String newPwd = body.getOrDefault("newPassword", "");
        if (!encoder.matches(oldPwd, u.getPassword())) {
            throw new BizException("原密码不正确");
        }
        if (newPwd.length() < 6) {
            throw new BizException("新密码不少于 6 位");
        }
        u.setPassword(encoder.encode(newPwd));
        userMapper.updateById(u);
        return R.ok();
    }

    @GetMapping("/message/list")
    public R<List<SysMessage>> messages(@RequestParam(required = false) Integer onlyUnread) {
        LambdaQueryWrapper<SysMessage> w = new LambdaQueryWrapper<SysMessage>()
                .eq(SysMessage::getReceiverId, UserContext.id())
                .eq(onlyUnread != null && onlyUnread == 1, SysMessage::getIsRead, 0)
                .orderByDesc(SysMessage::getCreateTime)
                .last("limit 30");
        return R.ok(messageMapper.selectList(w));
    }

    @PostMapping("/message/{id}/read")
    public R<Void> read(@PathVariable Long id) {
        SysMessage m = messageMapper.selectById(id);
        if (m != null && Objects.equals(m.getReceiverId(), UserContext.id())) {
            m.setIsRead(1);
            messageMapper.updateById(m);
        }
        return R.ok();
    }
}
