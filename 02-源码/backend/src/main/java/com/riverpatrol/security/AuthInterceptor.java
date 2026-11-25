package com.riverpatrol.security;

import com.auth0.jwt.exceptions.JWTVerificationException;
import com.auth0.jwt.interfaces.DecodedJWT;
import com.riverpatrol.entity.SysUser;
import com.riverpatrol.mapper.SysUserMapper;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;
import org.springframework.web.servlet.HandlerInterceptor;

/**
 * JWT 鉴权拦截器。
 * 说明：仅做身份识别，具体写操作权限由各接口内部校验角色，避免"只有菜单权限就能调用写接口"。
 */
@Component
public class AuthInterceptor implements HandlerInterceptor {

    @Autowired
    private JwtUtil jwtUtil;
    @Autowired
    private SysUserMapper userMapper;

    @Override
    public boolean preHandle(HttpServletRequest req, HttpServletResponse resp, Object handler) throws Exception {
        if ("OPTIONS".equalsIgnoreCase(req.getMethod())) {
            return true;
        }
        String token = req.getHeader("Authorization");
        if (token != null && token.startsWith("Bearer ")) {
            token = token.substring(7);
        }
        if (token == null || token.isBlank()) {
            return reject(resp, "未登录或登录已过期");
        }
        try {
            DecodedJWT jwt = jwtUtil.verify(token);
            Long uid = jwt.getClaim("uid").asLong();
            SysUser user = userMapper.selectById(uid);
            if (user == null || user.getStatus() == null || user.getStatus() != 1) {
                return reject(resp, "账号不存在或已停用");
            }
            UserContext.LoginUser lu = new UserContext.LoginUser();
            lu.setId(user.getId());
            lu.setUsername(user.getUsername());
            lu.setRealName(user.getRealName());
            lu.setRoleCode(user.getRoleCode());
            lu.setDeptId(user.getDeptId());
            UserContext.set(lu);
            return true;
        } catch (JWTVerificationException e) {
            return reject(resp, "登录凭证无效，请重新登录");
        }
    }

    @Override
    public void afterCompletion(HttpServletRequest req, HttpServletResponse resp, Object handler, Exception ex) {
        UserContext.clear();
    }

    private boolean reject(HttpServletResponse resp, String msg) throws Exception {
        resp.setStatus(200);
        resp.setContentType("application/json;charset=UTF-8");
        resp.getWriter().write("{\"code\":401,\"msg\":\"" + msg + "\",\"data\":null}");
        return false;
    }
}
