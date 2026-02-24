# 服务器部署说明

## 📋 部署文件
- gunicorn.conf.py - Gunicorn配置（已适配ubuntu用户）
- nginx.conf - Nginx配置
- systemd-service.conf - Systemd服务配置

## 🚀 部署步骤

### 1. 服务器环境准备
```bash
# 创建应用目录
sudo mkdir -p /opt/wenyanwen
sudo chown ubuntu:ubuntu /opt/wenyanwen

# 创建日志目录
mkdir -p /opt/wenyanwen/logs
sudo chown ubuntu:ubuntu /opt/wenyanwen/logs
```

### 2. 上传后端文件
将以下文件上传到服务器 /opt/wenyanwen/ 目录：
- src/ 目录
- data/words.json
- gunicorn.conf.py
- nginx.conf
- .env.production （重命名为 .env）

### 3. 部署前端应用
```bash
# 1. 在服务器上创建前端目录
sudo mkdir -p /var/www/vue
sudo chown ubuntu:ubuntu /var/www/vue

# 2. 将Vue构建产物上传到服务器
# 本地执行：npm run build 生成 dist/ 目录
scp -r dist/* ubuntu@server:/var/www/vue/

# 3. 设置目录权限
sudo chown -R ubuntu:ubuntu /var/www/vue
```

### 4. 安装后端依赖（使用conda）
```bash
cd /opt/wenyanwen
conda create -n wenyanwen python=3.11
conda activate wenyanwen
pip install -e .
```

### 5. 创建Systemd服务
```bash
sudo tee /etc/systemd/system/wenyanwen.service > /dev/null <<EOF
[Unit]
Description=Wenyanwen FastAPI Application
After=network.target

[Service]
Type=simple
User=ubuntu
Group=ubuntu
WorkingDirectory=/opt/wenyanwen
Environment=PATH=/home/ubuntu/miniconda3/envs/wenyanwen/bin
Environment=ENVIRONMENT=production
ExecStart=/home/ubuntu/miniconda3/envs/wenyanwen/bin/gunicorn -c gunicorn.conf.py wenyanwen.__main__:app
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable wenyanwen.service
```

### 6. 配置Nginx
```bash
sudo cp /opt/wenyanwen/nginx.conf /etc/nginx/sites-available/wenyanwen
sudo ln -sf /etc/nginx/sites-available/wenyanwen /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 7. 启动服务
```bash
sudo systemctl start wenyanwen.service
sudo systemctl status wenyanwen.service
```

## 🔧 前端更新
```bash
# 1. 本地重新构建
npm run build

# 2. 上传新版本到服务器
scp -r dist/* ubuntu@server:/var/www/vue/

# 3. 重启Nginx（如果需要）
sudo systemctl reload nginx
```

## 🔧 日常管理
```bash
# 服务管理
sudo systemctl start|stop|restart|status wenyanwen

# 查看日志
tail -f /opt/wenyanwen/logs/gunicorn_access.log
tail -f /opt/wenyanwen/logs/gunicorn_error.log
```