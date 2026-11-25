package com.riverpatrol.security;

import com.auth0.jwt.JWT;
import com.auth0.jwt.algorithms.Algorithm;
import com.auth0.jwt.interfaces.DecodedJWT;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

import java.time.Instant;
import java.time.temporal.ChronoUnit;

/** JWT 签发与解析。令牌有效期 12 小时，载荷仅放用户ID与角色，不放敏感信息。 */
@Component
public class JwtUtil {
    @Value("${app.jwt-secret}")
    private String secret;

    private static final String ISSUER = "river-patrol";

    public String create(Long userId, String username, String roleCode) {
        return JWT.create()
                .withIssuer(ISSUER)
                .withClaim("uid", userId)
                .withClaim("username", username)
                .withClaim("role", roleCode)
                .withExpiresAt(Instant.now().plus(12, ChronoUnit.HOURS))
                .sign(Algorithm.HMAC256(secret));
    }

    public DecodedJWT verify(String token) {
        return JWT.require(Algorithm.HMAC256(secret)).withIssuer(ISSUER).build().verify(token);
    }
}
