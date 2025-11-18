#!/bin/bash

# 当任何命令失败时立即退出脚本
set -e

# --- 配置部分 ---
# 请根据您服务器的实际情况修改以下变量

# 项目在服务器上的绝对路径
PROJECT_DIR="/opt/remove-bg-service"

# Docker 镜像和容器的名称
IMAGE_NAME="remove-bg-service"
CONTAINER_NAME="remove-bg-app"

# 端口映射 (格式: 主机端口:容器端口)
PORT_MAPPING="8000:8000"

# 您项目使用的主分支 (通常是 main 或 master)
GIT_BRANCH="main"


# --- 部署流程 ---

echo "====== 部署开始 ======"

# 1. 进入项目目录
echo "--> 切换到项目目录: $PROJECT_DIR"
cd "$PROJECT_DIR" || { echo "错误: 项目目录不存在!"; exit 1; }

# 2. 拉取最新代码
echo "--> 从 Git 仓库拉取最新代码 (分支: $GIT_BRANCH)..."
git checkout "$GIT_BRANCH"
git pull origin "$GIT_BRANCH"

# 3. 构建 Docker 镜像
echo "--> 构建新的 Docker 镜像: $IMAGE_NAME..."
docker build -t "$IMAGE_NAME" .

# 4. 停止并移除旧容器
# 使用 || true 来防止在容器不存在时脚本因错误而退出
echo "--> 停止并移除旧的容器: $CONTAINER_NAME..."
docker stop "$CONTAINER_NAME" || true
docker rm "$CONTAINER_NAME" || true

# 5. 启动新容器
echo "--> 启动新的 Docker 容器: $CONTAINER_NAME..."
docker run -d \
    -p "$PORT_MAPPING" \
    --name "$CONTAINER_NAME" \
    --restart always \
    "$IMAGE_NAME"

# (可选) 清理悬空的 Docker 镜像，释放磁盘空间
echo "--> 清理旧的/悬空的 Docker 镜像..."
docker image prune -f

echo "====== 部署成功! ======"
echo "新版本已部署，容器 '$CONTAINER_NAME' 正在运行。"
