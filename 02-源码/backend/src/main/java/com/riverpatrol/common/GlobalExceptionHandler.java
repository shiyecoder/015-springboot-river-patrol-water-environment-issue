package com.riverpatrol.common;

import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;
import org.springframework.web.servlet.resource.NoResourceFoundException;

/** 全局异常处理：业务异常返回 400，其余 500，且不返回堆栈给前端 */
@RestControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler(BizException.class)
    public R<Void> biz(BizException e) {
        return R.fail(e.getCode(), e.getMessage());
    }

    @ExceptionHandler(MethodArgumentNotValidException.class)
    public R<Void> valid(MethodArgumentNotValidException e) {
        String msg = e.getBindingResult().getFieldErrors().stream()
                .findFirst().map(f -> f.getField() + " " + f.getDefaultMessage()).orElse("参数校验失败");
        return R.fail(400, msg);
    }

    @ExceptionHandler(NoResourceFoundException.class)
    public R<Void> notFound(NoResourceFoundException e) {
        return R.fail(404, "资源不存在");
    }

    @ExceptionHandler(Exception.class)
    public R<Void> other(Exception e) {
        e.printStackTrace();
        return R.fail(500, "服务异常：" + e.getMessage());
    }
}
