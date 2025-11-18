## 问题原因
- 422 来自请求校验：当前接口签名要求 `multipart/form-data` 的 `file` 字段（server.py:25），浏览器直接 POST 或字段名不匹配会触发 422。
- 直接在浏览器打开 POST 接口不会携带文件，因此既看不到图片、又返回 422。正确调用需通过 curl/Postman 或一个上传页面。
- 接口已按输出设置了 `image/png` 或 `image/jpeg`（server.py:35,44），请求正确时会返回二进制图片。

## 解决方案
### 1) 使用方式指引（无代码变更）
- curl 透明 PNG：`curl -X POST -F "file=@/path/to/input.jpg" "http://127.0.0.1:8000/remove-bg" --output output.png`
- curl 白底 JPEG：`curl -X POST -F "file=@/path/to/input.png" "http://127.0.0.1:8000/remove-bg?format=jpeg&background=%23FFFFFF" --output output.jpg`
- Postman：选择 form-data，键为 `file`，类型为 File，值为图片文件。

### 2) 友好错误与更易用的接入（建议代码调整）
- 将 `file: UploadFile = File(...)` 改为可选：`file: UploadFile | None = File(None)`，若未提供则返回 400 + 明确错误信息，避免 422（server.py:25）。
- 支持原始图片二进制：当 `Content-Type: image/*` 时，直接读取原始请求体作为图片数据（兼容非 multipart 调用）。
- 新增简易上传页 `/demo`：提供一个 HTML 表单和 JS，将返回的二进制以 Blob 预览，方便在浏览器内验证。

### 3) 可选增强
- 参数校验更严格：限制文件大小、仅允许特定 `format`/`background`，统一返回结构；加入请求 ID 便于排查。
- 模型选择参数：暴露 `model=u2net|u2netp`，满足更快/更好效果切换。

## 实施步骤
1. 修改接口签名与缺省处理（支持 multipart 与原始体），完善 400 错误描述。
2. 添加 `/demo` 上传页，内置前端预览逻辑，便于本地直接测试。
3. 手动验证两类调用：multipart 与原始体；验证 PNG/JPEG 返回头与内容可视化显示。
4. 保留现有 `/docs` 交互式文档用于开发联调。