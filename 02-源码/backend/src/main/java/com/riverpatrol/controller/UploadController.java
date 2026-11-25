package com.riverpatrol.controller;

import com.riverpatrol.common.BizException;
import com.riverpatrol.common.R;
import com.riverpatrol.entity.SysFile;
import com.riverpatrol.mapper.SysFileMapper;
import com.riverpatrol.security.UserContext;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.*;

/** 文件上传：只保存到项目根 uploads/，返回相对路径；不接收任何外部 URL */
@RestController
@RequestMapping("/api/upload")
public class UploadController {

    @Autowired private SysFileMapper fileMapper;

    @Value("${app.upload-dir}")
    private String uploadDir;

    private static final Set<String> IMG = Set.of("jpg", "jpeg", "png", "webp");
    private static final Set<String> DOC = Set.of("pdf", "doc", "docx", "xls", "xlsx", "mp4");

    @PostMapping
    public R<Map<String, Object>> upload(@RequestParam("file") MultipartFile file,
                                         @RequestParam(defaultValue = "common") String biz) throws IOException {
        if (file == null || file.isEmpty()) {
            throw new BizException("请选择要上传的文件");
        }
        String original = file.getOriginalFilename() == null ? "file" : file.getOriginalFilename();
        String ext = original.contains(".") ? original.substring(original.lastIndexOf('.') + 1).toLowerCase() : "";
        if (!IMG.contains(ext) && !DOC.contains(ext)) {
            throw new BizException("不支持的文件类型：" + ext + "（允许 jpg/png/webp/pdf/doc/xls/mp4）");
        }
        if (file.getSize() > 20 * 1024 * 1024) {
            throw new BizException("文件过大，单个文件不超过 20MB");
        }
        String day = LocalDate.now().format(DateTimeFormatter.ofPattern("yyyyMM"));
        Path dir = Paths.get(uploadDir, biz, day).toAbsolutePath().normalize();
        Files.createDirectories(dir);
        String name = UUID.randomUUID().toString().replace("-", "").substring(0, 16) + "." + ext;
        file.transferTo(dir.resolve(name).toFile());

        String rel = "/uploads/" + biz + "/" + day + "/" + name;
        SysFile f = new SysFile();
        f.setFileName(original);
        f.setPath(rel);
        f.setSize(file.getSize());
        f.setContentType(file.getContentType());
        f.setUploaderId(UserContext.id());
        f.setCreateTime(LocalDateTime.now());
        fileMapper.insert(f);

        Map<String, Object> data = new LinkedHashMap<>();
        data.put("path", rel);
        data.put("fileName", original);
        data.put("size", file.getSize());
        return R.ok(data);
    }
}
