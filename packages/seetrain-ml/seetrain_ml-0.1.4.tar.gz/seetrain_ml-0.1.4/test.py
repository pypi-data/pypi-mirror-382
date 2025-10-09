import data as seetrain
from data import Image
from data.modules.audio import Audio
from data.modules.text import Text
from data.modules.video import Video
import random
import time
import numpy as np

if __name__ == '__main__':
    seetrain.init(
        # 设置超参数
        config={
            "learning_rate": 0.02,
            "architecture": "CNN",
            "dataset": "CIFAR-100",
            "epochs": 10
        }
    )

    # 测试视频功能

    # seetrain.log({"Preview/video": Video(data_or_path="/Users/CHENXI/Downloads/IMG_3010.MOV")})
    # # 测试音频功能
    # print("测试音频转换为二进制数据...")
    # try:
    #     # 创建一个简单的音频数据（1秒的440Hz正弦波）
    #     sample_rate = 44100
    #
    #     # 创建Audio对象
    #     seetrain.log({"Preview/audio": Audio(data_or_path="/Users/CHENXI/Downloads/云埔四路6.m4a",
    #                                          sample_rate=sample_rate, caption="测试音频")},
    #                  step=1)
    # except Exception as e:
    #     print(f"音频测试失败: {e}")
    #
    # 模拟一次训练
    seetrain.log({"Preview/image": Image(
        data_or_path="/Users/CHENXI/Downloads/a2132178a29d78676e78e2692fad1fc25cc80c9a28d7-MzqehH_fw658.webp")},
        step=1)
    epochs = 10
    offset = random.random() / 5
    for epoch in range(1, epochs):
        acc = 1 - 2 ** -epoch - random.random() / epoch - offset
        loss = 2 ** -epoch + random.random() / epoch + offset
        seetrain.log({"Preview/text": Text("Hello, World!")}, step=epoch)
        # 记录训练指标
        seetrain.log({"acc": acc, "loss": loss}, step=epoch)
        time.sleep(1)

    # [可选] 完成训练，这在notebook环境中是必要的
    seetrain.finish()
