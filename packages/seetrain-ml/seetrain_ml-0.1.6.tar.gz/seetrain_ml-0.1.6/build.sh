#!/bin/bash

# SeeTrain 一键构建打包脚本
# 用于构建和测试 Python 包

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
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

print_info "开始 SeeTrain 包构建流程..."

# 1. 清理之前的构建文件
print_info "清理之前的构建文件..."
rm -rf dist/ build/ *.egg-info/ .pytest_cache/ .coverage htmlcov/

# 2. 检查虚拟环境
if [ ! -d "venv" ]; then
    print_warning "未找到虚拟环境，正在创建..."
    python3 -m venv venv
fi

# 3. 激活虚拟环境
print_info "激活虚拟环境..."
source venv/bin/activate

# 4. 升级pip和安装构建工具
print_info "安装/升级构建工具..."
pip install --upgrade pip
pip install build twine wheel

# 5. 安装项目依赖
print_info "安装项目依赖..."
pip install -r requirements.txt

# 6. 运行代码检查（可选）
if command -v flake8 &> /dev/null; then
    print_info "运行代码风格检查..."
    flake8 seetrain/ --max-line-length=120 --ignore=E203,W503 || print_warning "代码风格检查发现问题，但继续构建"
fi

# 7. 构建包
print_info "构建 Python 包..."
python -m build

# 8. 检查构建结果
print_info "检查构建结果..."
if [ -d "dist" ]; then
    print_success "构建成功！生成的文件："
    ls -la dist/
else
    print_error "构建失败！"
    exit 1
fi

# 9. 测试安装
print_info "测试包安装..."
pip uninstall seetrain-ml -y 2>/dev/null || true
pip install dist/seetrain_ml-*.whl

# 10. 验证安装
print_info "验证包安装..."
python -c "
import seetrain
print(f'SeeTrain version: {seetrain.__version__}')
print('SeeTrain imported successfully!')
print('Available functions:', [f for f in dir(seetrain) if not f.startswith('_')])
"

print_success "包构建和测试完成！"

# 11. 显示上传指令
echo ""
print_info "上传到 PyPI 的指令："
echo "  # 使用上传脚本（推荐）："
echo "  ./upload.sh"
echo ""
echo "  # 或手动上传："
echo "  # 上传到测试环境："
echo "  twine upload --repository testpypi dist/*"
echo ""
echo "  # 上传到正式环境："
echo "  twine upload dist/*"
echo ""
echo "  # 安装测试："
echo "  pip install seetrain-ml"
echo "  # 或从测试环境安装："
echo "  pip install --index-url https://test.pypi.org/simple/ seetrain-ml"

print_success "构建脚本执行完成！"
