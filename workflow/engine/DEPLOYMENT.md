# Workflow Engine 部署指南

> **版本**: 2.0.0
> **部署方式**: Docker Compose

---

## 快速开始

### 1. 准备环境

确保已安装：
- Docker 20.10+
- Docker Compose 2.0+

### 2. 配置环境变量

```bash
cd workflow/engine
cp .env.example .env
# 编辑.env文件，修改配置
```

### 3. 启动服务

```bash
# 启动核心服务（Agent Interface + Redis）
docker-compose up -d

# 启动完整服务（包含监控）
docker-compose --profile monitoring up -d
```

### 4. 验证部署

```bash
# 检查健康状态
curl http://localhost:8000/health

# 预期输出：
# {"status":"healthy","service":"agent-interface"}
```

---

## 服务说明

### Agent Interface（端口8000）
- **职责**: Agent与Workflow引擎的REST API网关
- **健康检查**: `GET /health`
- **API文档**: `http://localhost:8000/docs`

### Redis（端口6379）
- **职责**: Workflow执行状态存储
- **数据持久化**: 是（redis_data volume）

### Prometheus（端口9090，可选）
- **职责**: 指标收集
- **访问**: `http://localhost:9090`

### Grafana（端口3000，可选）
- **职责**: 监控Dashboard
- **默认账号**: admin / admin
- **访问**: `http://localhost:3000`

---

## 常用命令

### 查看日志

```bash
# 查看所有服务日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f agent-interface
```

### 重启服务

```bash
# 重启所有服务
docker-compose restart

# 重启特定服务
docker-compose restart agent-interface
```

### 停止服务

```bash
# 停止所有服务
docker-compose down

# 停止并删除数据卷（谨慎！）
docker-compose down -v
```

### 扩展服务

```bash
# 扩展Agent Interface为4个实例
docker-compose up -d --scale agent-interface=4
```

---

## 生产环境部署

### 1. 使用外部Redis

修改`.env`:
```bash
REDIS_HOST=your-redis-host
REDIS_PORT=6379
REDIS_PASSWORD=your-redis-password
```

修改`docker-compose.yml`:
```yaml
services:
  agent-interface:
    # 移除depends_on中的redis
```

### 2. 配置HTTPS

使用Nginx反向代理：

```nginx
server {
    listen 443 ssl;
    server_name your-domain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 3. 资源限制

在`docker-compose.yml`中添加：

```yaml
services:
  agent-interface:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
```

---

## 监控和告警

### Prometheus指标

访问 `http://localhost:9090` 查看指标。

### Grafana Dashboard

1. 访问 `http://localhost:3000`
2. 登录（admin/admin）
3. 添加Prometheus数据源
4. 导入Dashboard（ID: 待添加）

---

## 故障排查

### 问题1：服务无法启动

```bash
# 查看详细日志
docker-compose logs agent-interface

# 常见原因：
# - 端口被占用：修改docker-compose.yml中的ports
# - Redis连接失败：检查Redis是否启动
```

### 问题2：健康检查失败

```bash
# 检查服务状态
docker-compose ps

# 手动测试API
curl http://localhost:8000/health
```

### 问题3：性能问题

```bash
# 查看资源使用
docker stats

# 调整配置
# - 增加AGENT_INTERFACE_WORKERS
# - 扩展agent-interface实例
```

---

## 升级和回滚

### 升级

```bash
# 拉取最新镜像
docker-compose pull

# 重启服务
docker-compose up -d
```

### 回滚

```bash
# 切换到旧版本镜像
docker-compose down
docker-compose up -d --image old-version:tag
```

---

## 支持

如有问题，请：
1. 查看日志: `docker-compose logs`
2. 检查配置: `.env` 文件
3. 参考文档: `docs/workflow-v2/architecture-update.md`
4. 提交Issue: [GitHub Issues](链接)
