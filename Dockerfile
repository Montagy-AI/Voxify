FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=backend/start.py
ENV FLASK_ENV=production

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    ffmpeg \
    libsndfile1 \
    libsqlite3-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 复制requirements文件
COPY backend/requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 创建必要的目录
RUN mkdir -p data/voice_clones data/files/synthesis data/files/samples data/files/temp

# 复制应用代码
COPY backend/ backend/

# 设置权限
RUN chmod +x backend/start.py

# 暴露端口
EXPOSE 10000

# 启动应用
CMD ["python", "backend/start.py"] 