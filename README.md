# 快速抠图 API 服务

本项目是一个基于 Python、FastAPI 和 `rembg` 库构建的轻量级图片背景移除（抠图）Web 服务。它提供了一个简单的 API，可以接收上传的图片，智能移除背景，并返回处理后的图片。项目还包含一个独立的 HTML 前端页面，方便用户与 API 交互。

## 主要功能

- **AI 抠图**: 使用 `rembg` 库（底层为 U2-Net 模型）自动识别并移除图片前景。
- **API 驱动**: 提供 `/remove-bg` 接口，易于集成。
- **格式转换**: 支持输出为 PNG（背景透明）或 JPEG（自定义纯色背景）格式。
- **简单前端**: 提供一个独立的 `index.html`，可通过浏览器直接使用服务。
- **Docker 支持**: 内置 `Dockerfile`，方便快速部署和隔离环境。

## 技术栈

- **后端**: Python 3.11, FastAPI
- **AI 模型**: `rembg` (U2-Net)
- **前端**: HTML, CSS, JavaScript (无框架)
- **部署**: Uvicorn, Docker

## 项目结构

```
.
├── Dockerfile              # Docker 配置文件
├── frontend/
│   └── index.html          # 独立的前端页面
├── requirements.prod.txt   # 生产环境依赖 (用于 Docker)
├── requirements.txt        # 开发环境依赖
└── server.py               # FastAPI 后端服务
```

## 部署与运行

你可以通过 Docker (推荐) 或在本地直接运行本项目。

### 方法一：使用 Docker (推荐)

这是最简单、最可靠的运行方式，可以避免环境依赖问题。

1.  **构建 Docker 镜像**:
    在项目根目录下执行以下命令：
    ```bash
    docker build -t remove-bg-service .
    ```

2.  **运行 Docker 容器**:
    ```bash
    docker run -p 8000:8000 --name remove-bg-app remove-bg-service
    ```
    服务现在运行在 `http://localhost:8000`。

### 方法二：本地运行

1.  **创建并激活虚拟环境**:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

2.  **安装依赖**:
    根据你的操作系统选择合适的依赖文件。
    -   对于大多数 Linux/Windows 系统，使用 `requirements.prod.txt`:
        ```bash
        pip install -r requirements.prod.txt
        ```
    -   对于 Apple Silicon (M1/M2/M3) Mac，使用 `requirements.txt` 以安装 `onnxruntime-silicon` 优化版本:
        ```bash
        pip install -r requirements.txt
        ```

3.  **启动服务**:
    ```bash
    uvicorn server:app --host 0.0.0.0 --port 8000
    ```
    服务现在运行在 `http://localhost:8000`。

## 如何使用

服务启动后，可以通过两种方式使用它。

### 1. 使用前端页面

1.  在浏览器中直接打开项目中的 `frontend/index.html` 文件。
2.  页面加载后，"接口地址" 输入框会自动填充。如果服务运行在本地 `8000` 端口，则无需修改。如果部署在其他地址，请填入正确的 API 地址 (例如 `http://your-server-ip:8000`) 并点击 "保存"。
3.  拖拽或点击选择一张图片。
4.  选择输出格式（PNG 或 JPEG）。如果选择 JPEG，可以指定背景颜色。
5.  点击 "开始抠图"，等待处理完成即可预览和下载结果。

### 2. 直接调用 API

你可以使用任何 HTTP 客户端 (如 `curl`, Postman) 直接调用 API。

**Endpoint**: `POST /remove-bg`

**参数**:
- `file`: (multipart/form-data) 包含图片数据的文件。
- `format`: (query string, 可选) 输出格式，`png` (默认) 或 `jpeg`。
- `background`: (query string, 可选) 如果 `format` 为 `jpeg`，可以提供一个十六进制颜色值作为背景，例如 `#FFFFFF`。

**示例 (使用 curl)**:

```bash
# 上传图片并移除背景，保存为 output.png
curl -X POST -F "file=@/path/to/your/image.jpg" "http://localhost:8000/remove-bg" -o output.png

# 上传图片，输出为 JPEG 格式，背景为蓝色
curl -X POST -F "file=@/path/to/your/image.jpg" "http://localhost:8000/remove-bg?format=jpeg&background=%230000FF" -o output.jpg
```

### 3. 内置 Demo 页面

服务器本身也在 `/demo` 路径提供了一个极简的测试页面，可以直接访问 `http://localhost:8000/demo` 来进行快速测试。
