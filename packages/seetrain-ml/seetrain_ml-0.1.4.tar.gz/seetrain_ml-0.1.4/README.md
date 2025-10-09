# SeeTrain

**SeeTrain** 是一个强大的深度学习实验跟踪和框架集成工具，提供统一的接口来适配各种深度学习框架，实现无缝的实验管理和数据记录。

> **注意**: 本包在 PyPI 上的名称为 `seetrain-ml`，请使用 `pip install seetrain-ml` 进行安装。

## ✨ 特性

- 🔗 **多框架集成** - 支持 PyTorch Lightning、TensorFlow/Keras、Hugging Face、MMEngine 等主流框架
- 📊 **统一实验跟踪** - 提供一致的 API 来记录指标、图像、音频、文本等多媒体数据
- 🎯 **多种适配模式** - Callback、Tracker、VisBackend、Autolog 四种集成模式
- 🚀 **自动日志记录** - 支持 OpenAI、智谱 AI 等 API 的自动拦截和记录
- 📈 **实时监控** - 硬件资源监控、性能指标跟踪
- 🎨 **丰富可视化** - 基于 Rich 库的美观终端输出

## 🚀 快速开始

### 安装

```bash
pip install seetrain-ml
```

### 验证安装

```python
import seetrain
print(f"SeeTrain version: {seetrain.__version__}")
print("SeeTrain 安装成功！")
```

### 基本使用

```python
from seetrain import init, log, log_scalar, log_image, finish

# 初始化实验
experiment = init(
    project="my_project",
    experiment_name="experiment_1",
    description="我的第一个实验"
)

# 记录标量指标
log_scalar('loss', 0.5, step=100)
log_scalar('accuracy', 0.95, step=100)

# 记录图像
import numpy as np
image = np.random.rand(224, 224, 3)
log_image('prediction', image, step=100)

# 记录字典数据
log({
    'train/loss': 0.3,
    'train/accuracy': 0.98,
    'val/loss': 0.4,
    'val/accuracy': 0.96
}, step=100)

# 完成实验
finish()
```


### 多媒体数据记录

```python
# 记录音频
import numpy as np
audio_data = np.random.randn(16000)  # 1秒的音频
log_audio('speech', audio_data, sample_rate=16000, step=100)

# 记录文本
log_text('prediction', "这是一个预测结果", step=100)

# 记录视频
video_frames = np.random.rand(10, 224, 224, 3)  # 10帧视频
log_video('animation', video_frames, fps=30, step=100)
```

### 配置管理

```python
from seetrain import update_config

# 记录超参数
update_config({
    'learning_rate': 0.001,
    'batch_size': 32,
    'model_architecture': 'ResNet50',
    'optimizer': 'Adam'
})
```

## 📦 安装选项

### 基础安装
```bash
pip install seetrain-ml
```