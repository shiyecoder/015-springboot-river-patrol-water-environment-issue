package com.riverpatrol;

import org.mybatis.spring.annotation.MapperScan;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

/**
 * 河道巡查与水环境问题处置系统启动类。
 * 端口 8084（通道 5），JDK 17，Spring Boot 3.3.5。
 */
@SpringBootApplication
@MapperScan("com.riverpatrol.mapper")
public class RiverPatrolApplication {
    public static void main(String[] args) {
        SpringApplication.run(RiverPatrolApplication.class, args);
    }
}
