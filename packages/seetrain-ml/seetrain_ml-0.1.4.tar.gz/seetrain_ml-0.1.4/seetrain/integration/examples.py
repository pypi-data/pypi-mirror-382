#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
SeeTrain 深度学习框架集成使用示例

展示如何使用各种集成模式来适配不同的深度学习框架
"""

import os
import sys
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset

# 添加项目根目录到 Python 路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.join(current_dir, '..')
sys.path.insert(0, project_root)

from integration.main import (
    init, log, log_scalar, log_image, log_audio, log_text,
    update_config, finish, with_integration,
    init_pytorch_lightning, init_keras, init_transformers,
    init_accelerate, init_mmengine, init_openai,
    enable_openai_autolog, enable_zhipuai_autolog
)


def example_pytorch_lightning():
    """PyTorch Lightning集成示例"""
    print("=== PyTorch Lightning 集成示例 ===")
    
    # 初始化集成
    integration = init_pytorch_lightning(
        project="pytorch_lightning_example",
        experiment_name="simple_model",
        description="PyTorch Lightning集成示例"
    )
    
    # 获取Lightning Logger
    logger = integration.get_callback()
    
    # 模拟训练过程
    for epoch in range(5):
        # 记录训练指标
        train_loss = 1.0 - epoch * 0.1
        train_acc = 0.5 + epoch * 0.1
        
        logger.log_metrics({
            'train/loss': train_loss,
            'train/accuracy': train_acc,
            'epoch': epoch
        }, step=epoch)
        
        # 记录验证指标
        val_loss = train_loss * 1.1
        val_acc = train_acc * 0.95
        
        logger.log_metrics({
            'val/loss': val_loss,
            'val/accuracy': val_acc
        }, step=epoch)
        
        print(f"Epoch {epoch}: train_loss={train_loss:.3f}, train_acc={train_acc:.3f}")
    
    # 记录超参数
    logger.log_hyperparams({
        'learning_rate': 0.001,
        'batch_size': 32,
        'epochs': 5,
        'model': 'simple_mlp'
    })
    
    integration.finish()
    print("PyTorch Lightning集成完成")


def example_keras():
    """Keras集成示例"""
    print("\n=== Keras 集成示例 ===")
    
    # 初始化集成
    integration = init_keras(
        project="keras_example",
        experiment_name="simple_model",
        description="Keras集成示例"
    )
    
    # 获取Keras Callback
    callback = integration.get_callback()
    
    # 模拟训练过程
    for epoch in range(3):
        # 模拟epoch开始
        callback.on_epoch_begin(epoch)
        
        # 模拟batch训练
        for batch in range(10):
            batch_loss = 1.0 - epoch * 0.1 - batch * 0.01
            callback.on_batch_end(batch, {'loss': batch_loss})
        
        # 模拟epoch结束
        epoch_logs = {
            'loss': 1.0 - epoch * 0.1,
            'accuracy': 0.5 + epoch * 0.1,
            'val_loss': 1.1 - epoch * 0.1,
            'val_accuracy': 0.45 + epoch * 0.1
        }
        callback.on_epoch_end(epoch, epoch_logs)
        
        print(f"Epoch {epoch}: loss={epoch_logs['loss']:.3f}, acc={epoch_logs['accuracy']:.3f}")
    
    integration.finish()
    print("Keras集成完成")


def example_transformers():
    """Transformers集成示例"""
    print("\n=== Transformers 集成示例 ===")
    
    # 初始化集成
    integration = init_transformers(
        project="transformers_example",
        experiment_name="bert_training",
        description="Transformers集成示例"
    )
    
    # 获取Transformers Callback
    callback = integration.get_callback()
    
    # 模拟训练过程
    from types import SimpleNamespace
    
    # 模拟训练参数
    args = SimpleNamespace(
        learning_rate=2e-5,
        batch_size=16,
        num_train_epochs=3,
        model_name='bert-base-uncased'
    )
    
    # 模拟训练状态
    state = SimpleNamespace(
        epoch=0,
        global_step=0,
        log_history=[]
    )
    
    # 开始训练
    callback.on_train_begin(args, state, None)
    
    for epoch in range(3):
        state.epoch = epoch
        callback.on_epoch_begin(args, state, None)
        
        # 模拟训练步骤
        for step in range(100):
            state.global_step = step
            state.log_history.append({
                'train_loss': 1.0 - epoch * 0.1 - step * 0.001
            })
            callback.on_step_end(args, state, None)
        
        # 模拟评估
        state.log_history.append({
            'eval_loss': 0.9 - epoch * 0.1,
            'eval_accuracy': 0.8 + epoch * 0.05
        })
        callback.on_evaluate(args, state, None)
        
        callback.on_epoch_end(args, state, None)
        print(f"Epoch {epoch}: global_step={state.global_step}")
    
    callback.on_train_end(args, state, None)
    integration.finish()
    print("Transformers集成完成")


def example_accelerate():
    """Accelerate集成示例"""
    print("\n=== Accelerate 集成示例 ===")
    
    # 初始化集成
    integration = init_accelerate(
        project="accelerate_example",
        experiment_name="distributed_training",
        description="Accelerate集成示例"
    )
    
    # 获取Accelerate Tracker
    tracker = integration.get_tracker()
    
    # 记录初始配置
    tracker.store_init_configuration({
        'learning_rate': 1e-4,
        'batch_size': 64,
        'num_epochs': 10,
        'model': 'transformer'
    })
    
    # 模拟训练过程
    for epoch in range(3):
        # 记录训练指标
        tracker.log({
            'train/loss': 1.0 - epoch * 0.1,
            'train/accuracy': 0.5 + epoch * 0.1,
            'epoch': epoch
        }, step=epoch)
        
        # 记录验证指标
        tracker.log({
            'val/loss': 1.1 - epoch * 0.1,
            'val/accuracy': 0.45 + epoch * 0.1
        }, step=epoch)
        
        print(f"Epoch {epoch}: train_loss={1.0 - epoch * 0.1:.3f}")
    
    tracker.finish()
    print("Accelerate集成完成")


def example_mmengine():
    """MMEngine集成示例"""
    print("\n=== MMEngine 集成示例 ===")
    
    # 初始化集成
    integration = init_mmengine(
        project="mmengine_example",
        experiment_name="detection_model",
        description="MMEngine集成示例"
    )
    
    # 获取MMEngine VisBackend
    backend = integration.get_backend()
    
    # 记录配置
    from types import SimpleNamespace
    config = SimpleNamespace()
    config.model = 'faster_rcnn'
    config.dataset = 'coco'
    config.optimizer = SimpleNamespace()
    config.optimizer.lr = 0.001
    config.optimizer.weight_decay = 0.0001
    
    backend.add_config(config)
    
    # 模拟训练过程
    for epoch in range(3):
        # 记录标量指标
        backend.add_scalar('train/loss', 1.0 - epoch * 0.1, step=epoch)
        backend.add_scalar('train/accuracy', 0.5 + epoch * 0.1, step=epoch)
        
        # 记录多个标量
        backend.add_scalars({
            'val/loss': 1.1 - epoch * 0.1,
            'val/accuracy': 0.45 + epoch * 0.1,
            'val/mAP': 0.3 + epoch * 0.05
        }, step=epoch)
        
        # 记录图像
        if epoch % 2 == 0:
            image = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
            backend.add_image(f'prediction/epoch_{epoch}', image, step=epoch)
        
        print(f"Epoch {epoch}: loss={1.0 - epoch * 0.1:.3f}")
    
    backend.close()
    print("MMEngine集成完成")


def example_openai_autolog():
    """OpenAI自动日志记录示例"""
    print("\n=== OpenAI 自动日志记录示例 ===")
    
    # 启用OpenAI自动日志记录
    autolog = enable_openai_autolog(
        project="openai_example",
        experiment_name="chat_completion",
        description="OpenAI自动日志记录示例"
    )
    
    try:
        # 模拟OpenAI API调用
        import openai
        
        # 这里只是示例，实际使用时需要有效的API密钥
        print("OpenAI自动日志记录已启用")
        print("当调用OpenAI API时，会自动记录请求和响应信息")
        
        # 模拟API调用（实际使用时需要有效的API密钥）
        # response = openai.chat.completions.create(
        #     model="gpt-3.5-turbo",
        #     messages=[{"role": "user", "content": "Hello, world!"}],
        #     max_tokens=100
        # )
        
    except Exception as e:
        print(f"OpenAI API调用失败（这是预期的，因为没有有效的API密钥）: {e}")
    
    # 禁用自动日志记录
    autolog.disable()
    print("OpenAI自动日志记录已禁用")


def example_context_manager():
    """上下文管理器示例"""
    print("\n=== 上下文管理器示例 ===")
    
    # 使用上下文管理器
    with with_integration('pytorch_lightning', project="context_example") as integration:
        # 在上下文中记录数据
        for i in range(3):
            log_scalar('context/step', i)
            log_scalar('context/value', i * 2)
            print(f"Context step {i}")
    
    print("上下文管理器示例完成")


def example_multiple_integrations():
    """多集成同时使用示例"""
    print("\n=== 多集成同时使用示例 ===")
    
    # 同时初始化多个集成
    pytorch_lightning = init_pytorch_lightning(project="multi_example", experiment_name="pytorch_lightning")
    keras = init_keras(project="multi_example", experiment_name="keras")
    
    # 使用统一的日志接口记录到所有集成
    for epoch in range(3):
        log_scalar('multi/loss', 1.0 - epoch * 0.1, step=epoch)
        log_scalar('multi/accuracy', 0.5 + epoch * 0.1, step=epoch)
        print(f"Multi integration epoch {epoch}")
    
    # 完成所有集成
    finish()
    print("多集成示例完成")


def example_custom_data_types():
    """自定义数据类型示例"""
    print("\n=== 自定义数据类型示例 ===")
    
    integration = init_pytorch_lightning(project="custom_data_example")
    
    # 记录图像
    image = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
    log_image('custom/image', image)
    
    # 记录音频
    audio = np.random.randn(16000).astype(np.float32)
    log_audio('custom/audio', audio, sample_rate=16000)
    
    # 记录文本
    log_text('custom/text', "这是一个自定义文本示例")
    
    # 记录标量
    log_scalar('custom/scalar', 42.0)
    
    integration.finish()
    print("自定义数据类型示例完成")


def main():
    """主函数"""
    print("SeeTrain 深度学习框架集成示例")
    print("=" * 50)
    
    try:
        # 运行各种示例
        example_pytorch_lightning()
        example_keras()
        example_transformers()
        example_accelerate()
        example_mmengine()
        example_openai_autolog()
        example_context_manager()
        example_multiple_integrations()
        example_custom_data_types()
        
        print("\n" + "=" * 50)
        print("所有示例运行完成！")
        
    except Exception as e:
        print(f"示例运行出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
