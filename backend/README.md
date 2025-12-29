# 教育系统后端 - 启动与联调说明

## 1. 环境要求

- Python 3.10+
- pip 或 poetry

## 2. 后端启动

### 2.1 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

### 2.2 配置环境变量

复制 `.env.example` 为 `.env`：

```bash
cp .env.example .env
```

`.env` 配置说明：

```ini
# 数据库配置
# SQLite (默认，开发环境)
DATABASE_URL=sqlite+aiosqlite:///./edu_system.db

# PostgreSQL (生产环境示例)
# DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/edu_system

# MySQL (生产环境示例)
# DATABASE_URL=mysql+pymysql://user:password@localhost:3306/edu_system

# JWT 配置
SECRET_KEY=your-super-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# CORS 配置 (多个用逗号分隔)
CORS_ORIGINS=http://localhost:5173,http://localhost:3000

# 服务配置
HOST=0.0.0.0
PORT=8080
DEBUG=true

# AI 配置 (预留)
AI_PROVIDER=mock
```

### 2.3 启动服务

方式一：使用 uvicorn 直接启动

```bash
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
```

方式二：使用启动脚本

```bash
cd backend
python run.py
```

### 2.4 验证启动

访问以下地址：

- API 文档: http://localhost:8080/docs
- 健康检查: http://localhost:8080/health

## 3. 前端配置

### 3.1 配置 API 地址

在前端项目根目录创建 `.env.local`：

```ini
VITE_API_URL=http://localhost:8080
```

### 3.2 启动前端

```bash
cd frontend
npm install
npm run dev
```

## 4. 默认账号

系统启动时会自动创建以下测试账号：

| 角色 | 账号 | 密码 |
|-----|-----|-----|
| 教师 | teacher1 ~ teacher5 | 123456 |
| 学生 | student1 ~ student100 | 123456 |

## 5. API 测试示例

### 5.1 登录

```bash
# 教师登录
curl -X POST http://localhost:8080/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "teacher1", "password": "123456"}'

# 学生登录
curl -X POST http://localhost:8080/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "student1", "password": "123456"}'
```

### 5.2 获取用户信息

```bash
# 替换 YOUR_TOKEN 为登录返回的 access_token
curl -X GET http://localhost:8080/api/users/me \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 5.3 获取学生列表

```bash
curl -X GET "http://localhost:8080/api/students?page=1&page_size=10" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 5.4 创建课程

```bash
curl -X POST http://localhost:8080/api/courses \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"name": "Python入门", "description": "学习Python基础知识"}'
```

## 6. 数据库切换

### 6.1 切换到 PostgreSQL

```ini
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/edu_system
```

### 6.2 切换到 MySQL

```ini
DATABASE_URL=mysql+pymysql://user:password@localhost:3306/edu_system
```

注意：切换数据库后需要重启服务，系统会自动创建表结构。

## 7. CORS 配置

如果前端运行在不同端口，需要在 `.env` 中添加：

```ini
CORS_ORIGINS=http://localhost:5173,http://localhost:3000,http://localhost:4000
```

## 8. 生产部署

### 8.1 关闭调试模式

```ini
DEBUG=false
```

### 8.2 使用 Gunicorn (Linux)

```bash
pip install gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8080
```

### 8.3 使用 Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
```

## 9. 常见问题

### Q1: 数据库文件在哪里？

默认 SQLite 数据库文件位于 `backend/edu_system.db`

### Q2: 如何重置数据？

删除 `edu_system.db` 文件后重启服务即可

### Q3: Token 过期怎么办？

默认 Token 有效期 24 小时，可在 `.env` 中调整 `ACCESS_TOKEN_EXPIRE_MINUTES`

### Q4: 如何查看 API 文档？

访问 http://localhost:8080/docs 查看 Swagger UI 文档
