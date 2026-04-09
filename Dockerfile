# ====================================================================
# Stage 1: "Builder" Stage - 编译和安装所有依赖
# 在这个阶段，我们会安装所有编译工具，但它们不会进入最终镜像。
# ====================================================================
FROM swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/python:3.10-slim AS builder

# 1. 安装编译所需的系统工具 (gcc, gfortran 等)
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc g++ gfortran make pkg-config python3-dev && \
    rm -rf /var/lib/apt/lists/*

# 2. 创建一个虚拟环境，用于干净地打包所有依赖
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

WORKDIR /app
COPY requirements.txt .

# 3. 在虚拟环境中安装所有 Python 依赖
RUN pip install --no-cache-dir --upgrade pip -i https://mirrors.aliyun.com/pypi/simple/ && \
    pip install --no-cache-dir -i https://mirrors.aliyun.com/pypi/simple/ -r requirements.txt gunicorn

# ====================================================================
# Stage 2: "Final" Stage - 最终的轻量级生产镜像
# ====================================================================
FROM swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/python:3.10-slim

WORKDIR /app

# 1. 从 "builder" 阶段复制已安装好的虚拟环境
COPY --from=builder /opt/venv /opt/venv

# 2. 复制你的应用代码 (.py, .so 等)
COPY . .

# 3. 激活虚拟环境
ENV PATH="/opt/venv/bin:$PATH"

# 4. 暴露端口并启动应用
EXPOSE 8000
CMD ["gunicorn", "-b", "0.0.0.0:8000", "--workers", "2", "--threads", "4", "--timeout", "120", "diagnosis:server"]

