# SeeTrain 上传指南

## 🎯 问题解决总结

### 原始问题
- 上传到 TestPyPI 时遇到 403 Forbidden 错误
- 终端输入问题导致 API token 输入失败

### 解决方案
1. **包名更改**: 将包名从 `seetrain` 改为 `seetrain-ml` 以避免潜在的命名冲突
2. **创建上传脚本**: 提供交互式上传脚本 `upload.sh` 简化上传过程
3. **配置文件**: 创建 `.pypirc` 配置文件用于 API token 管理

## 📦 当前包信息
- **包名**: `seetrain-ml`
- **版本**: `0.1.0`
- **Python 版本**: >=3.8
- **许可证**: MIT

## 🚀 使用方法

### 1. 构建包
```bash
./build.sh
```

### 2. 上传包
```bash
./upload.sh
```

### 3. 安装包
```bash
# 从 PyPI 安装
pip install seetrain-ml

# 从 TestPyPI 安装（测试）
pip install --index-url https://test.pypi.org/simple/ seetrain-ml
```

## 🔧 配置 API Token

### 1. 获取 API Token
- **TestPyPI**: https://test.pypi.org/manage/account/token/
- **PyPI**: https://pypi.org/manage/account/token/

### 2. 配置 .pypirc 文件
编辑项目根目录的 `.pypirc` 文件：
```ini
[distutils]
index-servers = testpypi pypi

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-your-testpypi-api-token-here

[pypi]
repository = https://upload.pypi.org/legacy/
username = __token__
password = pypi-your-pypi-api-token-here
```

## 📋 文件说明

- `build.sh` - 一键构建脚本
- `upload.sh` - 交互式上传脚本
- `.pypirc` - PyPI 配置文件
- `setup.py` - 包配置
- `pyproject.toml` - 现代包配置
- `requirements.txt` - 依赖管理

## ✅ 验证成功

包已成功构建并测试：
- ✅ 生成了 `seetrain_ml-0.1.0-py3-none-any.whl` (113KB)
- ✅ 生成了 `seetrain_ml-0.1.0.tar.gz` (7.9MB)
- ✅ 包可以正确安装和导入
- ✅ 所有功能模块都可用

## 🎉 下一步

1. 配置 API Token
2. 运行 `./upload.sh` 选择上传目标
3. 验证包在 PyPI 上的可用性
4. 更新文档和示例代码
