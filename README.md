# CS231n Assignment 1 学习记录

基于提供的 Assignment 1 教学代码，完成本地 PyCharm/Jupyter 适配及 Q1–Q5 实验。

- [中文学习复盘](学习复盘.md)：做了什么、实现步骤、算法原理、实际结果及复盘建议。
- [本地运行说明](本地运行说明.md)
- [提交说明](提交说明.md)

## 实验结果

| 实验 | 测试准确率 |
|---|---:|
| kNN | 28.2% |
| Softmax | 39.3% |
| 两层网络 | 51.6% |
| 图像特征 + Softmax | 50.6% |
| 图像特征 + 两层网络 | 57.1% |
| 多层全连接网络 | 52.8% |

kNN 使用较小的数据子集，实验训练设置也不同，以上数值不构成严格算法排名。详细配置与限制见复盘文档。

## 快速开始

需要 Python 3.12 或更新版本：

```bash
python -m pip install -r requirements-local.txt
python local_setup.py
python check_environment.py
python -m notebook
```

按 `knn.ipynb`、`softmax.ipynb`、`two_layer_net.ipynb`、`features.ipynb`、`FullyConnectedNets.ipynb` 顺序阅读。已保存运行输出，查看时不必重新训练。

最终 ZIP/PDF 在 `output/pdf/`，模型在 `cs231n/saved/`。数据集按需下载，不纳入版本控制。BatchNorm、LayerNorm、Dropout 和卷积等后续作业功能未实现。

原始教学框架及题目来自 CS231n；本项目用于记录学习实现和实验结果。
