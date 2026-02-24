# Gunicorn 生产环境配置
import multiprocessing
import os

# 服务器配置
bind = "127.0.0.1:8000"
workers = min(multiprocessing.cpu_count() * 2 + 1, 4)  # 限制最大worker数
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
timeout = 30
keepalive = 5

# 日志配置 - 输出到指定文件
accesslog = "/opt/wenyanwen/logs/gunicorn_access.log"
errorlog = "/opt/wenyanwen/logs/gunicorn_error.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# 进程管理
preload_app = True
daemon = False
pidfile = None
user = "ubuntu"
group = "ubuntu"

# 性能调优
worker_tmp_dir = "/dev/shm"

# 环境变量
raw_env = [
    "ENVIRONMENT=production",
    "RELOAD=false"
]

# 安全设置
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190