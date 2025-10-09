# SeeTrain 深度学习框架集成

SeeTrain提供了多层次的适配架构，通过不同的集成模式来适配各种深度学习框架，实现统一的实验跟踪体验。

## 核心设计理念

### 1. 统一的适配接口
- **统一的初始化机制**：所有集成都通过 `seetrain.init()` 进行实验初始化
- **统一的日志接口**：通过 `seetrain.log()` 记录各种类型的数据
- **统一的配置管理**：通过 `seetrain.config` 管理超参数和配置

### 2. 框架标识系统
每个集成都会在配置中标记使用的框架，便于识别和管理。

## 四种主要适配模式

### 1. Callback模式（最常用）
适用于：PyTorch Lightning, Keras, Transformers, Ultralytics

**实现原理**：
- 继承框架的回调基类
- 重写关键方法（如 `log_metrics`, `log_hyperparams`）
- 在训练过程中自动调用SeeTrain的日志接口

**使用示例**：
```python
from integration.main import init_pytorch_lightning

# 初始化PyTorch Lightning集成
integration = init_pytorch_lightning(
    project="my_project",
    experiment_name="experiment_1",
    description="PyTorch Lightning训练实验"
)

# 获取Lightning Logger
logger = integration.get_callback()

# 在训练循环中使用
for epoch in range(num_epochs):
    # 记录指标
    logger.log_metrics({
        'train/loss': train_loss,
        'train/accuracy': train_acc
    }, step=epoch)
    
    # 记录超参数
    logger.log_hyperparams({
        'learning_rate': 0.001,
        'batch_size': 32
    })

integration.finish()
```

### 2. Tracker模式
适用于：Hugging Face Accelerate

**实现原理**：
- 实现框架的Tracker接口
- 将框架的日志调用直接转发给SeeTrain

**使用示例**：
```python
from integration.main import init_accelerate

# 初始化Accelerate集成
integration = init_accelerate(
    project="accelerate_project",
    experiment_name="distributed_training"
)

# 获取Tracker
tracker = integration.get_tracker()

# 记录配置
tracker.store_init_configuration({
    'learning_rate': 1e-4,
    'batch_size': 64
})

# 记录指标
tracker.log({
    'train/loss': loss_value,
    'train/accuracy': acc_value
}, step=step)

tracker.finish()
```

### 3. VisBackend模式
适用于：MMEngine, MMDetection

**实现原理**：
- 注册为框架的可视化后端
- 实现框架的可视化接口
- 将可视化数据转换为SeeTrain格式

**使用示例**：
```python
from integration.main import init_mmengine

# 初始化MMEngine集成
integration = init_mmengine(
    project="mmengine_project",
    experiment_name="detection_model"
)

# 获取VisBackend
backend = integration.get_backend()

# 记录配置
backend.add_config(config)

# 记录指标
backend.add_scalar('train/loss', loss_value, step=step)
backend.add_scalars({
    'val/loss': val_loss,
    'val/mAP': val_map
}, step=step)

# 记录图像
backend.add_image('prediction', image, step=step)

backend.close()
```

### 4. Autolog模式（API拦截）
适用于：OpenAI, 智谱AI

**实现原理**：
- Monkey Patching：动态替换API方法
- 请求/响应解析：通过Resolver解析API调用
- 自动日志记录：拦截API调用并自动记录到SeeTrain

**使用示例**：
```python
from integration.main import enable_openai_autolog

# 启用OpenAI自动日志记录
autolog = enable_openai_autolog(
    project="openai_project",
    experiment_name="chat_completion"
)

# 正常使用OpenAI API，会自动记录
import openai
response = openai.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "Hello!"}],
    max_tokens=100
)

# 禁用自动日志记录
autolog.disable()
```

## 统一接口使用

### 基本用法
```python
from integration.main import init, log, log_scalar, log_image, finish

# 初始化集成
integration = init('pytorch_lightning', project="my_project")

# 记录各种类型的数据
log_scalar('loss', 0.5)
log_image('prediction', image_array)
log({'accuracy': 0.95, 'f1_score': 0.92})

# 完成集成
finish()
```

### 多集成同时使用
```python
from integration.main import init, log, finish

# 同时初始化多个集成
pytorch_lightning = init('pytorch_lightning', project="multi_example")
keras = init('keras', project="multi_example")

# 使用统一接口记录到所有集成
log({'loss': 0.5, 'accuracy': 0.95})

# 完成所有集成
finish()
```

### 上下文管理器
```python
from integration.main import with_integration, log_scalar

# 使用上下文管理器
with with_integration('pytorch_lightning', project="context_example") as integration:
    for i in range(10):
        log_scalar('step', i)
        log_scalar('value', i * 2)
```

## 支持的数据类型

### 标量数据
```python
log_scalar('loss', 0.5)
log_scalar('accuracy', 0.95)
```

### 图像数据
```python
import numpy as np

# NumPy数组
image = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
log_image('prediction', image)

# PIL图像
from PIL import Image
pil_image = Image.open('image.jpg')
log_image('input', pil_image)
```

### 音频数据
```python
import numpy as np

# NumPy数组
audio = np.random.randn(16000).astype(np.float32)
log_audio('speech', audio, sample_rate=16000)
```

### 文本数据
```python
log_text('summary', "模型训练完成，准确率达到95%")
```

## 配置管理

### 更新配置
```python
from integration.main import update_config

update_config({
    'learning_rate': 0.001,
    'batch_size': 32,
    'model': 'resnet50'
})
```

### 获取配置
```python
config = integration.get_config()
print(config)
```

## 错误处理和容错机制

### 自动重试
```python
from integration.errors import with_retry

@with_retry(max_retries=3, base_delay=1.0)
def risky_operation():
    # 可能失败的操作
    pass
```

### 熔断器
```python
from integration.errors import with_circuit_breaker

@with_circuit_breaker(failure_threshold=5, recovery_timeout=60.0)
def network_operation():
    # 网络操作
    pass
```

### 优雅降级
```python
from integration.errors import with_graceful_degradation

def fallback_function():
    # 降级函数
    pass

@with_graceful_degradation(fallback_func=fallback_function)
def main_operation():
    # 主要操作
    pass
```

## 性能优化策略

### 懒加载
- 使用 `LazyModule` 延迟加载依赖库
- 避免不必要的导入开销

### 缓存机制
- 自动缓存已加载的模块
- 避免重复导入

### 异步支持
- 支持异步API调用
- 非阻塞的日志记录

## 支持的框架

### Callback模式
- PyTorch Lightning
- Keras/TensorFlow
- Transformers
- Ultralytics

### Tracker模式
- Hugging Face Accelerate
- Ray Tune
- Optuna
- WandB

### VisBackend模式
- MMEngine
- MMDetection
- TensorBoard
- MLflow

### Autolog模式
- OpenAI
- 智谱AI
- Anthropic

## 最佳实践

1. **选择合适的集成模式**：根据框架特性选择最适合的集成方式
2. **使用统一接口**：尽量使用统一的日志接口，便于维护
3. **合理使用上下文管理器**：确保资源正确释放
4. **配置错误处理**：根据实际需求配置重试和熔断机制
5. **监控集成状态**：定期检查集成状态和错误统计

## 故障排除

### 常见问题

1. **框架未找到**
   - 确保已安装相应的深度学习框架
   - 检查Python环境和依赖

2. **版本不兼容**
   - 查看框架版本要求
   - 升级或降级到兼容版本

3. **网络连接问题**
   - 检查网络连接
   - 配置代理设置

4. **权限问题**
   - 检查文件写入权限
   - 确保API密钥有效

### 调试技巧

1. **启用详细日志**
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```

2. **检查集成状态**
   ```python
   stats = integration.get_stats()
   print(stats)
   ```

3. **查看错误统计**
   ```python
   from integration.errors import get_integration_error_stats
   error_stats = get_integration_error_stats()
   print(error_stats)
   ```

## 贡献指南

欢迎贡献新的框架集成！请参考现有集成的实现方式，遵循以下原则：

1. 继承相应的基类
2. 实现必要的抽象方法
3. 添加适当的错误处理
4. 编写测试用例
5. 更新文档

## 许可证

本项目采用MIT许可证。详见LICENSE文件。
