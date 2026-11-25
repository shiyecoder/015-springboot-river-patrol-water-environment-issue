package com.riverpatrol.common;

/** 业务异常：由全局异常处理器转换为统一返回结构 */
public class BizException extends RuntimeException {
    private final int code;

    public BizException(String msg) {
        this(400, msg);
    }

    public BizException(int code, String msg) {
        super(msg);
        this.code = code;
    }

    public int getCode() {
        return code;
    }
}
