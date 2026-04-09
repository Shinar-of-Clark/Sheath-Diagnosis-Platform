# ⚡ Sheath-Diagnosis-Platform (护套环流深处理与 AI 诊断平台)

基于电磁感应原理与尖端物理现象的电缆护套环流高级分析与 AI 专家诊断系统。
系统通过 Python & Dash 构建，支持从原始波形中提取核心特征（RMS、DC 偏置、各次谐波幅值与相位），并结合 AI 专家诊断矩阵自动判别 18 种底层故障。

## ✨ 核心特性 (Features)

- **🔌 多维信号处理**: 支持去除直流偏置、Butterworth 低通滤波、IIR 梳状滤波以及 EMA 指数滑动平均。
- **📊 黄金周波合成**: 自动截取稳态数据，合成用于高精度傅里叶分析的黄金周波。
- **🧠 AI 专家指纹诊断**: 内置诊断矩阵，精准识别护层断路、箱体进水、多点接地等故障。
- **🛠️ 故障波形发生器**: 内置 `gen_diagnostic_data.py` 和网页端生成器，一键模拟各种复合干扰波形。
- **🐳 容器化部署**: 提供完整的 `Dockerfile`，支持生产级一键部署。

## 🚀 快速启动 (Quick Start)

### 方式一：使用 Docker 运行 (推荐)

确保你的机器上已安装 Docker。

```bash
# 构建镜像 (使用 --progress=plain 可实时查看底层 C/C++ 依赖包的编译进度，避免假死假象)
docker build --progress=plain -t sheath-diagnosis-app .

# 运行容器 (映射到主机的 8051 端口)
docker run -d -p 8051:8000 sheath-diagnosis-app
```
访问浏览器: `http://localhost:8051`

### 方式二：本地 Python 环境运行

```bash
# 安装依赖
pip install -r requirements.txt

# 启动服务
python diagnosis.py
```
访问浏览器: `http://localhost:8051`