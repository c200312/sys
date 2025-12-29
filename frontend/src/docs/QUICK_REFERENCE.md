# 快速参考手册

## 🚀 5分钟快速启动

### 前端配置
```typescript
// /config/api.ts
export const API_CONFIG = {
  BASE_URL: 'http://localhost:8080',
};
```

### 后端启动（Python + FastAPI）
```bash
pip install fastapi uvicorn sqlalchemy pymysql pydantic python-jose passlib
uvicorn main:app --reload --port 8080
```

---

## 📋 常用API端点速查

### 认证
```http
POST /api/auth/signup      # 注册
POST /api/auth/login       # 登录
GET  /api/auth/verify      # 验证Token
```

### 教师
```http
GET    /api/teachers           # 列表
GET    /api/teachers/{id}      # 详情
POST   /api/teachers           # 创建
PUT    /api/teachers/{id}      # 更新
DELETE /api/teachers/{id}      # 删除
```

### 学生
```http
GET    /api/students           # 列表
GET    /api/students/{id}      # 详情
POST   /api/students           # 创建
PUT    /api/students/{id}      # 更新
DELETE /api/students/{id}      # 删除
```

### 课程
```http
GET    /api/courses                         # 列表
POST   /api/courses                         # 创建
GET    /api/courses/{id}                    # 详情
PUT    /api/courses/{id}                    # 更新
DELETE /api/courses/{id}                    # 删除
GET    /api/courses/{id}/students           # 学员列表
POST   /api/courses/{id}/students           # 添加学员
DELETE /api/courses/{id}/students/{sid}     # 移除学员
```

### 作业
```http
GET    /api/courses/{id}/homeworks          # 课程作业列表
POST   /api/courses/{id}/homeworks          # 创建作业
GET    /api/homeworks/{id}                  # 作业详情
PUT    /api/homeworks/{id}                  # 更新作业
DELETE /api/homeworks/{id}                  # 删除作业
```

### 作业提交
```http
GET    /api/homeworks/{id}/submissions      # 提交列表
POST   /api/homeworks/{id}/submissions      # 提交作业
GET    /api/submissions/{id}                # 提交详情
PUT    /api/submissions/{id}                # 更新提交
POST   /api/submissions/{id}/grade          # 批改
DELETE /api/submissions/{id}                # 删除提交
```

### 课程资源
```http
GET    /api/courses/{id}/folders            # 文件夹列表
POST   /api/courses/{id}/folders            # 创建文件夹
GET    /api/folders/{id}/files              # 文件列表
POST   /api/folders/{id}/files              # 上传文件
PUT    /api/files/{id}                      # 更新文件
DELETE /api/files/{id}                      # 删除文件
```

---

## 🔐 认证请求示例

### 注册
```json
POST /api/auth/signup
{
  "username": "student101",
  "password": "123456",
  "role": "student"
}
```

### 登录
```json
POST /api/auth/login
{
  "username": "student1",
  "password": "123456"
}

// 响应
{
  "success": true,
  "data": {
    "access_token": "eyJhbGc...",
    "token_type": "Bearer",
    "user": {...}
  }
}
```

### 使用Token
```http
GET /api/courses
Authorization: Bearer eyJhbGc...
```

---

## 💾 数据模型速查

### User（用户）
```typescript
{
  id: string;
  username: string;      // 学号或工号
  password: string;      // 加密后的密码
  role: 'teacher' | 'student';
  created_at: string;
}
```

### Teacher（教师）
```typescript
{
  id: string;
  teacher_no: string;    // 工号
  name: string;
  gender: '男' | '女';
  email: string;
  created_at: string;
}
```

### Student（学生）
```typescript
{
  id: string;
  student_no: string;    // 学号
  name: string;
  class: string;         // 班级
  gender: '男' | '女';
  created_at: string;
}
```

### Course（课程）
```typescript
{
  id: string;
  name: string;
  description: string;
  teacher_id: string;
  student_count: number;
  created_at: string;
}
```

### Homework（作业）
```typescript
{
  id: string;
  course_id: string;
  title: string;
  description: string;
  deadline: string;      // ISO 8601格式
  attachment?: {
    name: string;
    type: string;
    size: number;
    content: string;     // base64
  };
  created_at: string;
}
```

### HomeworkSubmission（作业提交）
```typescript
{
  id: string;
  homework_id: string;
  student_id: string;
  content: string;
  attachments?: Array<{
    name: string;
    type: string;
    size: number;
    content: string;     // base64
  }>;
  score?: number;        // 0-100
  feedback?: string;
  submitted_at: string;
  graded_at?: string;
}
```

---

## 🗄️ 数据库表速查

```sql
users                    -- 用户表
├── id (PK)
├── username (UNIQUE)
├── password
├── role
└── created_at

teachers                 -- 教师表
├── id (PK)
├── teacher_no (UNIQUE, FK → users.username)
├── name
├── gender
├── email
└── created_at

students                 -- 学生表
├── id (PK)
├── student_no (UNIQUE, FK → users.username)
├── name
├── class
├── gender
└── created_at

courses                  -- 课程表
├── id (PK)
├── name
├── description
├── teacher_id (FK → teachers.id)
├── student_count
└── created_at

course_enrollments       -- 选课表
├── id (PK)
├── course_id (FK → courses.id)
├── student_id (FK → students.id)
└── enrolled_at

homeworks                -- 作业表
├── id (PK)
├── course_id (FK → courses.id)
├── title
├── description
├── deadline
├── attachment...
└── created_at

homework_submissions     -- 作业提交表
├── id (PK)
├── homework_id (FK → homeworks.id)
├── student_id (FK → students.id)
├── content
├── score
├── feedback
├── submitted_at
└── graded_at

course_folders           -- 文件夹表
├── id (PK)
├── course_id (FK → courses.id)
├── name
└── created_at

course_files             -- 文件表
├── id (PK)
├── folder_id (FK → course_folders.id)
├── course_id (FK → courses.id)
├── name
├── size
├── type
├── content (base64)
└── created_at
```

---

## 🔧 常用SQL查询

### 获取教师的所有课程
```sql
SELECT c.* FROM courses c
JOIN teachers t ON c.teacher_id = t.id
WHERE t.teacher_no = 'teacher1';
```

### 获取学生的所有课程
```sql
SELECT c.* FROM courses c
JOIN course_enrollments ce ON c.id = ce.course_id
JOIN students s ON ce.student_id = s.id
WHERE s.student_no = 'student1';
```

### 获取课程的学员列表
```sql
SELECT s.* FROM students s
JOIN course_enrollments ce ON s.id = ce.student_id
WHERE ce.course_id = 'course-uuid';
```

### 获取作业提交统计
```sql
SELECT 
  COUNT(*) as total_submissions,
  COUNT(score) as graded_count,
  AVG(score) as avg_score
FROM homework_submissions
WHERE homework_id = 'homework-uuid';
```

### 获取学生的作业完成情况
```sql
SELECT 
  h.title,
  hs.submitted_at,
  hs.score,
  hs.feedback
FROM homeworks h
LEFT JOIN homework_submissions hs 
  ON h.id = hs.homework_id AND hs.student_id = 'student-uuid'
WHERE h.course_id = 'course-uuid'
ORDER BY h.deadline DESC;
```

---

## ⚡ FastAPI 代码模板

### 基础路由
```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from config.database import get_db
from utils.dependencies import get_current_user

router = APIRouter()

@router.get("/")
def get_items(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    items = db.query(Model).all()
    return {"success": True, "data": items}

@router.post("/")
def create_item(
    item: ItemCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    new_item = Model(**item.dict())
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return {"success": True, "data": new_item}
```

### 模型定义
```python
from sqlalchemy import Column, String, Integer
from config.database import Base
import uuid

class Model(Base):
    __tablename__ = "models"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    count = Column(Integer, default=0)
```

### Schema定义
```python
from pydantic import BaseModel

class ItemBase(BaseModel):
    name: str

class ItemCreate(ItemBase):
    pass

class ItemResponse(ItemBase):
    id: str
    
    class Config:
        from_attributes = True
```

---

## 🔒 安全最佳实践

### 密码处理
```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"])

# 加密
hashed = pwd_context.hash("password123")

# 验证
is_valid = pwd_context.verify("password123", hashed)
```

### JWT Token
```python
from jose import jwt
from datetime import datetime, timedelta

# 创建
token = jwt.encode(
    {"sub": user_id, "exp": datetime.utcnow() + timedelta(hours=24)},
    SECRET_KEY,
    algorithm="HS256"
)

# 解码
payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
```

---

## 📊 响应格式

### 成功响应
```json
{
  "success": true,
  "data": {...},
  "message": "操作成功"
}
```

### 错误响应
```json
{
  "success": false,
  "error": "错误信息",
  "code": "ERROR_CODE"
}
```

### 分页响应
```json
{
  "success": true,
  "data": {
    "items": [...],
    "total": 100,
    "page": 1,
    "page_size": 20
  }
}
```

---

## 🐛 常见错误码

| 状态码 | 说明 |
|--------|------|
| 200 | 成功 |
| 201 | 创建成功 |
| 400 | 请求参数错误 |
| 401 | 未授权（未登录） |
| 403 | 禁止访问（无权限） |
| 404 | 资源不存在 |
| 409 | 资源冲突 |
| 500 | 服务器错误 |

---

## 🎯 开发流程

1. **设计API** → 参考 API_DOCUMENTATION.md
2. **设计数据库** → 参考 DATABASE_SCHEMA.md
3. **创建模型** → SQLAlchemy models
4. **创建Schema** → Pydantic schemas
5. **实现路由** → FastAPI routers
6. **测试API** → 使用Postman/curl
7. **集成前端** → 替换localStorage调用
8. **部署上线** → Docker/云服务器

---

## 📦 依赖清单

### Python (FastAPI)
```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
pymysql==1.1.0
pydantic==2.5.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
```

### Node.js (Express)
```json
{
  "express": "^4.18.2",
  "prisma": "^5.0.0",
  "jsonwebtoken": "^9.0.2",
  "bcrypt": "^5.1.1",
  "cors": "^2.8.5"
}
```

---

## 🔗 有用的链接

- [完整API文档](./API_DOCUMENTATION.md)
- [数据库设计](./DATABASE_SCHEMA.md)
- [开发指南](./BACKEND_DEVELOPMENT_GUIDE.md)
- [FastAPI官方文档](https://fastapi.tiangolo.com/)
- [SQLAlchemy文档](https://www.sqlalchemy.org/)

---

**快速开发，高效迭代！** ⚡
