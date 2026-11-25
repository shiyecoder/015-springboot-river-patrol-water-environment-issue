package com.riverpatrol.controller;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.riverpatrol.common.BizException;
import com.riverpatrol.common.R;
import com.riverpatrol.entity.SysMenu;
import com.riverpatrol.entity.SysRoleMenu;
import com.riverpatrol.entity.SysUser;
import com.riverpatrol.mapper.SysMenuMapper;
import com.riverpatrol.mapper.SysRoleMapper;
import com.riverpatrol.mapper.SysRoleMenuMapper;
import com.riverpatrol.mapper.SysUserMapper;
import com.riverpatrol.security.JwtUtil;
import com.riverpatrol.security.UserContext;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDateTime;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.stream.Collectors;

/** 登录、当前用户、动态菜单 */
@RestController
@RequestMapping("/api/auth")
public class AuthController {

    @Autowired private SysUserMapper userMapper;
    @Autowired private SysRoleMapper roleMapper;
    @Autowired private SysMenuMapper menuMapper;
    @Autowired private SysRoleMenuMapper roleMenuMapper;
    @Autowired private JwtUtil jwtUtil;
    @Autowired private BCryptPasswordEncoder encoder;

    /** 连续失败锁定：5 次错误锁定 10 分钟（内存计数，单机足够） */
    private static final Map<String, int[]> FAIL = new ConcurrentHashMap<>();
    private static final Map<String, Long> LOCK_UNTIL = new ConcurrentHashMap<>();

    @PostMapping("/login")
    public R<Map<String, Object>> login(@RequestBody Map<String, String> body) {
        String username = body.getOrDefault("username", "").trim();
        String password = body.getOrDefault("password", "");
        if (username.isEmpty() || password.isEmpty()) {
            throw new BizException("请输入账号和密码");
        }
        Long lock = LOCK_UNTIL.get(username);
        if (lock != null && lock > System.currentTimeMillis()) {
            throw new BizException("密码错误次数过多，账号已锁定，请 10 分钟后再试");
        }
        SysUser user = userMapper.selectOne(new LambdaQueryWrapper<SysUser>().eq(SysUser::getUsername, username));
        if (user == null || !encoder.matches(password, user.getPassword())) {
            int n = FAIL.merge(username, new int[]{1}, (a, b) -> new int[]{a[0] + 1})[0];
            if (n >= 5) {
                LOCK_UNTIL.put(username, System.currentTimeMillis() + 10 * 60 * 1000L);
                FAIL.remove(username);
                throw new BizException("密码错误 5 次，账号锁定 10 分钟");
            }
            throw new BizException("账号或密码错误，还可尝试 " + (5 - n) + " 次");
        }
        if (user.getStatus() == null || user.getStatus() != 1) {
            throw new BizException("账号已停用，请联系管理员");
        }
        FAIL.remove(username);
        user.setLastLogin(LocalDateTime.now());
        userMapper.updateById(user);

        Map<String, Object> data = new HashMap<>();
        data.put("token", jwtUtil.create(user.getId(), user.getUsername(), user.getRoleCode()));
        data.put("user", safeUser(user));
        data.put("menus", menusOf(user.getRoleCode()));
        return R.ok(data);
    }

    @GetMapping("/info")
    public R<Map<String, Object>> info() {
        SysUser user = userMapper.selectById(UserContext.id());
        if (user == null) {
            throw new BizException(401, "用户不存在");
        }
        Map<String, Object> data = new HashMap<>();
        data.put("user", safeUser(user));
        data.put("menus", menusOf(user.getRoleCode()));
        // 角色名兜底：查不到时返回编码，避免因角色数据缺失导致整个接口 500
        String roleName = roleMapper.selectList(null).stream()
                .filter(r -> user.getRoleCode().equals(r.getCode()))
                .map(r -> r.getName()).findFirst().orElse(user.getRoleCode());
        data.put("roleName", roleName);
        return R.ok(data);
    }

    /** 角色菜单动态获取；菜单管理项对非管理员隐藏（spec 第 12 条） */
    private List<Map<String, Object>> menusOf(String roleCode) {
        List<Long> menuIds = roleMenuMapper.selectList(new LambdaQueryWrapper<SysRoleMenu>()
                        .eq(SysRoleMenu::getRoleId, roleIdOf(roleCode)))
                .stream().map(SysRoleMenu::getMenuId).collect(Collectors.toList());
        List<SysMenu> all = menuMapper.selectList(new LambdaQueryWrapper<SysMenu>()
                .in(!menuIds.isEmpty(), SysMenu::getId, menuIds)
                .eq(SysMenu::getType, "M")
                .orderByAsc(SysMenu::getSort));
        List<Map<String, Object>> tree = new ArrayList<>();
        for (SysMenu m : all) {
            if (m.getParentId() == null || m.getParentId() == 0) {
                Map<String, Object> node = toNode(m);
                List<Map<String, Object>> children = all.stream()
                        .filter(c -> m.getId().equals(c.getParentId()))
                        .map(this::toNode).collect(Collectors.toList());
                node.put("children", children);
                tree.add(node);
            }
        }
        return tree;
    }

    private Long roleIdOf(String code) {
        // 用列表过滤而非 selectOne，避免角色缺失时抛异常
        return roleMapper.selectList(null).stream()
                .filter(r -> code != null && code.equals(r.getCode()))
                .map(com.riverpatrol.entity.SysRole::getId)
                .findFirst().orElse(0L);
    }

    private Map<String, Object> toNode(SysMenu m) {
        Map<String, Object> n = new LinkedHashMap<>();
        n.put("id", m.getId());
        n.put("name", m.getName());
        n.put("path", m.getPath());
        n.put("component", m.getComponent());
        n.put("icon", m.getIcon());
        n.put("perm", m.getPerm());
        n.put("visible", m.getVisible());
        return n;
    }

    /** 任何接口都不返回密码字段 */
    private Map<String, Object> safeUser(SysUser u) {
        Map<String, Object> m = new LinkedHashMap<>();
        m.put("id", u.getId());
        m.put("username", u.getUsername());
        m.put("realName", u.getRealName());
        m.put("phone", u.getPhone());
        m.put("avatar", u.getAvatar());
        m.put("deptId", u.getDeptId());
        m.put("roleCode", u.getRoleCode());
        m.put("lastLogin", u.getLastLogin());
        return m;
    }
}
