package com.riverpatrol.security;

import lombok.Data;

/** 当前登录用户上下文（ThreadLocal），请求结束后必须清理 */
public class UserContext {
    @Data
    public static class LoginUser {
        private Long id;
        private String username;
        private String realName;
        private String roleCode;
        private Long deptId;
    }

    private static final ThreadLocal<LoginUser> HOLDER = new ThreadLocal<>();

    public static void set(LoginUser u) {
        HOLDER.set(u);
    }

    public static LoginUser get() {
        return HOLDER.get();
    }

    public static Long id() {
        LoginUser u = HOLDER.get();
        return u == null ? null : u.getId();
    }

    public static String role() {
        LoginUser u = HOLDER.get();
        return u == null ? null : u.getRoleCode();
    }

    public static void clear() {
        HOLDER.remove();
    }
}
