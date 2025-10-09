#!/bin/bash

# SeeTrain 上传脚本
# 用于上传包到 PyPI

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查是否在正确的目录
if [ ! -f "setup.py" ]; then
    print_error "请在项目根目录下运行此脚本"
    exit 1
fi

# 检查是否有构建文件
if [ ! -d "dist" ]; then
    print_error "未找到 dist 目录，请先运行 ./build.sh"
    exit 1
fi

print_info "开始上传 SeeTrain 包..."

# 激活虚拟环境
if [ -d "venv" ]; then
    print_info "激活虚拟环境..."
    source venv/bin/activate
fi

# 检查 twine 是否安装
if ! command -v twine &> /dev/null; then
    print_info "安装 twine..."
    pip install twine
fi

# 显示上传选项
echo ""
print_info "请选择上传目标："
echo "1) TestPyPI (推荐先测试)"
echo "2) PyPI (正式环境)"
echo "3) 退出"
echo ""

read -p "请输入选择 (1-3): " choice

case $choice in
    1)
        print_info "上传到 TestPyPI..."
        print_warning "请确保已配置 TestPyPI API Token"
        echo ""
        print_info "如果没有配置 API Token，请："
        echo "1. 访问 https://test.pypi.org/manage/account/token/"
        echo "2. 创建 API Token"
        echo "3. 编辑 .pypirc 文件，将 password 替换为你的 API Token"
        echo ""
        read -p "按 Enter 继续上传到 TestPyPI..."
        twine upload --repository testpypi dist/*
        print_success "上传到 TestPyPI 完成！"
        echo ""
        print_info "安装测试命令："
        echo "pip install --index-url https://test.pypi.org/simple/ seetrain-ml"
        ;;
    2)
        print_info "上传到 PyPI..."
        print_warning "请确保已配置 PyPI API Token"
        echo ""
        print_info "如果没有配置 API Token，请："
        echo "1. 访问 https://pypi.org/manage/account/token/"
        echo "2. 创建 API Token"
        echo "3. 编辑 .pypirc 文件，将 password 替换为你的 API Token"
        echo ""
        read -p "按 Enter 继续上传到 PyPI..."
        twine upload dist/*
        print_success "上传到 PyPI 完成！"
        echo ""
        print_info "安装命令："
        echo "pip install seetrain-ml"
        ;;
    3)
        print_info "退出上传"
        exit 0
        ;;
    *)
        print_error "无效选择"
        exit 1
        ;;
esac

print_success "上传脚本执行完成！"
