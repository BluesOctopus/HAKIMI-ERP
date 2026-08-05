#!/bin/bash
# HAKIMI ERP Frontend - 本地开发启动脚本 (Git Bash / MSYS)
set -e

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
NODE_DIR="$PROJECT_DIR/.node-runtime/node-v20.15.1-win-x64"

if [ ! -d "$NODE_DIR" ]; then
  echo "[错误] 未找到本地 Node.js 运行时: $NODE_DIR"
  echo "请先运行环境配置脚本，或删除 .node-runtime 后重新下载 Node.js。"
  exit 1
fi

export PATH="$NODE_DIR:$PATH"

echo "[HAKIMI ERP] 启动开发服务器..."
echo "Node 版本: $(node -v)"
echo "npm 版本:  $(npm -v)"
echo "项目目录: $PROJECT_DIR"
echo "访问地址: http://localhost:5173"
echo ""

cd "$PROJECT_DIR"
npm run dev
