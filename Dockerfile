# ==========================================
# 阶段一：使用 Ubuntu 22.04 环境进行编译 (GLIBC 2.35)，确保与 VPS 兼容
# ==========================================
FROM ubuntu:22.04 AS builder

# 避免交互式提示
ENV DEBIAN_FRONTEND=noninteractive

# --- 新增步骤：更换为阿里云镜像源 (针对 Ubuntu 22.04 Jammy) ---
RUN sed -i 's/archive.ubuntu.com/mirrors.aliyun.com/g' /etc/apt/sources.list && \
    sed -i 's/security.ubuntu.com/mirrors.aliyun.com/g' /etc/apt/sources.list

WORKDIR /app

# 安装必要的编译工具和 Python 环境
RUN apt-get update && apt-get install -y \
    python3.10 python3.10-venv python3-pip \
    gcc g++ binutils patchelf ccache zlib1g-dev libglib2.0-0 upx-ucl \
    && rm -rf /var/lib/apt/lists/*

# 1. 升级 pip
RUN python3.10 -m pip install --no-cache-dir --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple

# 2. 强制安装 Nuitka 最新版 (2.1.2)，同时安装 zstandard 提高打包效率
RUN python3.10 -m pip install --no-cache-dir --upgrade "nuitka==2.1.2" zstandard ordered-set -i https://pypi.tuna.tsinghua.edu.cn/simple

# 3. 复制依赖并安装
COPY requirements.txt .
RUN python3.10 -m pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 4. 复制源代码
COPY . .

# 执行编译前先打印版本，确保万无一失
RUN python3.10 -m nuitka --version

# 确保 assets 目录存在（避免因没有 assets 目录导致 nuitka 报错）
RUN mkdir -p assets && touch assets/.keep

# --- 核心修复：替换 diagnosis.py 中的启动参数，关闭热重载并绑定外网 IP ---
RUN sed -i "s/app.run(debug=True, port=8051, dev_tools_hot_reload=True)/app.run(host='0.0.0.0', port=8051, debug=False)/g" diagnosis.py

# 确认版本后，执行纯净编译 (去掉了不存在的 dash 子包)
RUN LDFLAGS="-no-pie" python3.10 -m nuitka \
    --standalone \
    --onefile \
    --remove-output \
    --include-package=dash \
    --include-package=plotly \
    --include-package=flask \
    --include-package=dash_bootstrap_components \
    --include-package=pandas \
    --include-package=scipy \
    --include-data-dir=/usr/local/lib/python3.10/dist-packages/dash_bootstrap_components=dash_bootstrap_components \
    --include-data-dir=/usr/local/lib/python3.10/dist-packages/plotly=plotly \
    --include-data-dir=/usr/local/lib/python3.10/dist-packages/dash=dash \
    --include-data-dir=/usr/local/lib/python3.10/dist-packages/scipy=scipy \
    --include-data-dir=./assets=assets \
    --output-dir=dist \
    --output-filename=Sheath-Diagnosis-Platform \
    diagnosis.py

# ==========================================
# 阶段二：部署环境 (使用 Ubuntu 22.04)
# ==========================================
FROM ubuntu:22.04
WORKDIR /app

# 复制编译好的二进制文件
COPY --from=builder /app/dist/Sheath-Diagnosis-Platform /app/Sheath-Diagnosis-Platform

EXPOSE 8051
RUN chmod +x Sheath-Diagnosis-Platform

# 运行引擎，使用日志重定向确保 1GB VPS 的稳定性
CMD ["/bin/sh", "-c", "./Sheath-Diagnosis-Platform > /app/app.log 2>&1 & tail -f /app/app.log"]