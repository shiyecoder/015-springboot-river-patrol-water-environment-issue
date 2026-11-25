package com.riverpatrol.controller;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.riverpatrol.common.BizException;
import com.riverpatrol.common.R;
import com.riverpatrol.entity.*;
import com.riverpatrol.mapper.*;
import com.riverpatrol.security.UserContext;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDateTime;
import java.util.*;
import java.util.stream.Collectors;

/** 系统管理：用户、角色、菜单、部门、操作日志 */
@RestController
@RequestMapping("/api/sys")
public class SysController {

    @Autowired private SysUserMapper userMapper;
    @Autowired private SysRoleMapper roleMapper;
    @Autowired private SysMenuMapper menuMapper;
    @Autowired private SysRoleMenuMapper roleMenuMapper;
    @Autowired private SysDeptMapper deptMapper;
    @Autowired private SysLogMapper logMapper;
    @Autowired private BCryptPasswordEncoder encoder;

    @GetMapping("/user/page")
    public R<Map<String, Object>> userPage(@RequestParam(defaultValue = "1") int page,
                                          @RequestParam(defaultValue = "10") int size,
                                          @RequestParam(required = false) String keyword,
                                          @RequestParam(required = false) String roleCode) {
        LambdaQueryWrapper<SysUser> w = new LambdaQueryWrapper<>();
        if (keyword != null && !keyword.isBlank()) {
            w.and(q -> q.like(SysUser::getRealName, keyword).or().like(SysUser::getUsername, keyword));
        }
        w.eq(roleCode != null && !roleCode.isBlank(), SysUser::getRoleCode, roleCode).orderByAsc(SysUser::getId);
        Page<SysUser> p = userMapper.selectPage(new Page<>(page, size), w);
        Map<Long, String> deptNames = new HashMap<>();
        deptMapper.selectList(null).forEach(d -> deptNames.put(d.getId(), d.getName()));
        Map<String, String> roleNames = new HashMap<>();
        roleMapper.selectList(null).forEach(r -> roleNames.put(r.getCode(), r.getName()));

        List<Map<String, Object>> rows = p.getRecords().stream().map(u -> {
            Map<String, Object> m = new LinkedHashMap<>();
            m.put("id", u.getId());
            m.put("username", u.getUsername());
            m.put("realName", u.getRealName());
            m.put("phone", u.getPhone());
            m.put("avatar", u.getAvatar());
            m.put("roleCode", u.getRoleCode());
            m.put("roleName", roleNames.getOrDefault(u.getRoleCode(), u.getRoleCode()));
            m.put("deptName", deptNames.getOrDefault(u.getDeptId(), "—"));
            m.put("deptId", u.getDeptId());
            m.put("status", u.getStatus());
            m.put("lastLogin", u.getLastLogin());
            return m;
        }).collect(Collectors.toList());
        Map<String, Object> data = new LinkedHashMap<>();
        data.put("total", p.getTotal());
        data.put("page", page);
        data.put("size", size);
        data.put("records", rows);
        return R.ok(data);
    }

    @PostMapping("/user")
    public R<Void> saveUser(@RequestBody Map<String, Object> body) {
        requireAdmin();
        Long id = body.get("id") == null ? null : Long.valueOf(String.valueOf(body.get("id")));
        SysUser u = id == null ? new SysUser() : userMapper.selectById(id);
        u.setUsername(String.valueOf(body.get("username")).trim());
        u.setRealName(String.valueOf(body.get("realName")).trim());
        u.setPhone(String.valueOf(body.getOrDefault("phone", "")));
        u.setRoleCode(String.valueOf(body.get("roleCode")));
        u.setDeptId(body.get("deptId") == null ? null : Long.valueOf(String.valueOf(body.get("deptId"))));
        u.setAvatar(String.valueOf(body.getOrDefault("avatar", "")));
        if (id == null) {
            Long dup = userMapper.selectCount(new LambdaQueryWrapper<SysUser>().eq(SysUser::getUsername, u.getUsername()));
            if (dup > 0) {
                throw new BizException("账号已存在");
            }
            u.setPassword(encoder.encode("admin123"));
            u.setStatus(1);
            u.setCreateTime(LocalDateTime.now());
            u.setDeleted(0);
            userMapper.insert(u);
        } else {
            userMapper.updateById(u);
        }
        return R.ok();
    }

    @PostMapping("/user/{id}/status")
    public R<Void> toggle(@PathVariable Long id) {
        requireAdmin();
        SysUser u = userMapper.selectById(id);
        if (u == null) {
            throw new BizException(404, "用户不存在");
        }
        u.setStatus(u.getStatus() != null && u.getStatus() == 1 ? 0 : 1);
        userMapper.updateById(u);
        return R.ok();
    }

    @PostMapping("/user/{id}/reset")
    public R<Void> reset(@PathVariable Long id) {
        requireAdmin();
        SysUser u = userMapper.selectById(id);
        u.setPassword(encoder.encode("admin123"));
        userMapper.updateById(u);
        return R.ok();
    }

    @GetMapping("/role/list")
    public R<List<SysRole>> roles() {
        return R.ok(roleMapper.selectList(null));
    }

    @GetMapping("/role/{id}/menus")
    public R<List<Long>> roleMenus(@PathVariable Long id) {
        return R.ok(roleMenuMapper.selectList(new LambdaQueryWrapper<SysRoleMenu>().eq(SysRoleMenu::getRoleId, id))
                .stream().map(SysRoleMenu::getMenuId).collect(Collectors.toList()));
    }

    @PutMapping("/role/{id}/menus")
    public R<Void> assignMenus(@PathVariable Long id, @RequestBody List<Long> menuIds) {
        requireAdmin();
        roleMenuMapper.delete(new LambdaQueryWrapper<SysRoleMenu>().eq(SysRoleMenu::getRoleId, id));
        for (Long mid : menuIds) {
            SysRoleMenu rm = new SysRoleMenu();
            rm.setRoleId(id);
            rm.setMenuId(mid);
            roleMenuMapper.insert(rm);
        }
        return R.ok();
    }

    /** 菜单管理项自身不对外呈现（visible=0），但数据保留以便授权 */
    @GetMapping("/menu/list")
    public R<List<SysMenu>> menus() {
        return R.ok(menuMapper.selectList(new LambdaQueryWrapper<SysMenu>().orderByAsc(SysMenu::getParentId)
                .orderByAsc(SysMenu::getSort)));
    }

    @GetMapping("/dept/list")
    public R<List<SysDept>> depts() {
        return R.ok(deptMapper.selectList(null));
    }

    @GetMapping("/log/page")
    public R<Map<String, Object>> logs(@RequestParam(defaultValue = "1") int page,
                                       @RequestParam(defaultValue = "10") int size,
                                       @RequestParam(required = false) String bizNo) {
        LambdaQueryWrapper<SysLog> w = new LambdaQueryWrapper<>();
        w.eq(bizNo != null && !bizNo.isBlank(), SysLog::getBizNo, bizNo).orderByDesc(SysLog::getCreateTime);
        Page<SysLog> p = logMapper.selectPage(new Page<>(page, size), w);
        Map<String, Object> data = new LinkedHashMap<>();
        data.put("total", p.getTotal());
        data.put("page", page);
        data.put("size", size);
        data.put("records", p.getRecords());
        return R.ok(data);
    }

    private void requireAdmin() {
        if (!"admin".equals(UserContext.role())) {
            throw new BizException(403, "仅管理员可执行该操作");
        }
    }
}
