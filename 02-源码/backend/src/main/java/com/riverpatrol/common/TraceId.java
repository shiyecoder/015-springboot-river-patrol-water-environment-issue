package com.riverpatrol.common;

import java.util.concurrent.atomic.AtomicLong;

/** 轻量请求编号，便于日志串联（不引入链路追踪依赖） */
public class TraceId {
    private static final AtomicLong SEQ = new AtomicLong(1000);

    public static String next() {
        return "T" + System.currentTimeMillis() % 100000 + "-" + SEQ.incrementAndGet();
    }
}
