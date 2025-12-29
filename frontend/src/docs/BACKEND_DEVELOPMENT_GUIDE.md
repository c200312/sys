# 后端开发指南

## 快速开始

### 技术栈推荐

**方案1：Python + FastAPI**
- FastAPI（Web框架）
- SQLAlchemy（ORM）
- Pydantic（数据验证）
- PyJWT（JWT认证）
- bcrypt（密码加密）
- uvicorn（ASGI服务器）

**方案2：Node.js + Express**
- Express（Web框架）
- Prisma / Sequelize（ORM）
- jsonwebtoken（JWT认证）
- bcrypt（密码加密）

**方案3：Python + Flask**
- Flask（Web框架）
- SQLAlchemy（ORM）
- Flask-JWT-Extended（JWT认证）
- bcrypt（密码加密）

---

## 项目结构（以 FastAPI 为例）

```
backend/
├── main.py                 # 应用入口
├── requirements.txt        # 依赖列表
├── config/
│   ├── __init__.py
│   ├── database.py        # 数据库配置
│   └── settings.py        # 应用配置
├── models/                # 数据模型
│   ├── __init__.py
│   ├── user.py
│   ├── teacher.py
│   ├── student.py
│   ├── course.py
│   ├── homework.py
│   └── ...
├── schemas/               # Pydantic schemas（请求/响应模型）
│   ├── __init__.py
│   ├── user.py
│   ├── teacher.py
│   ├── student.py
│   ├── course.py
│   └── ...
├── routers/              # 路由（API端点）
│   ├── __init__.py
│   ├── auth.py          # 认证相关
│   ├── teachers.py      # 教师管理
│   ├── students.py      # 学生管理
│   ├── courses.py       # 课程管理
│   ├── homeworks.py     # 作业管理
│   └── ...
├── services/             # 业务逻辑
│   ├── __init__.py
│   ├── auth_service.py
│   ├── user_service.py
│   ├── course_service.py
│   └── ...
├── utils/                # 工具函数
│   ├── __init__.py
│   ├── security.py      # 密码加密、JWT等
│   ├── validators.py    # 数据验证
│   └── response.py      # 统一响应格式
└── migrations/           # 数据库迁移
    └── versions/
```

---

## 快速搭建步骤

### 1. 安装依赖

**Python + FastAPI**
```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install fastapi uvicorn sqlalchemy pymysql pydantic python-jose[cryptography] passlib[bcrypt] python-multipart
```

**requirements.txt**
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

---

### 2. 创建主应用（main.py）

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import auth, teachers, students, courses, homeworks
from config.database import engine, Base

# 创建数据库表
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="教育系统API",
    description="教育系统后端API文档",
    version="1.0.0"
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该指定具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth.router, prefix="/api/auth", tags=["认证"])
app.include_router(teachers.router, prefix="/api/teachers", tags=["教师管理"])
app.include_router(students.router, prefix="/api/students", tags=["学生管理"])
app.include_router(courses.router, prefix="/api/courses", tags=["课程管理"])
app.include_router(homeworks.router, prefix="/api/homeworks", tags=["作业管理"])

@app.get("/")
def read_root():
    return {"message": "教育系统API", "version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
```

---

### 3. 数据库配置（config/database.py）

```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 数据库连接URL
# MySQL: mysql+pymysql://user:password@localhost/dbname
# PostgreSQL: postgresql://user:password@localhost/dbname
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:password@localhost/edu_system"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# 依赖注入：获取数据库会话
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

---

### 4. 数据模型示例（models/user.py）

```python
from sqlalchemy import Column, String, Enum, DateTime
from sqlalchemy.sql import func
from config.database import Base
import uuid

class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String(50), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False)
    role = Column(Enum('teacher', 'student'), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
```

---

### 5. Pydantic Schema示例（schemas/user.py）

```python
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    role: str = Field(..., pattern="^(teacher|student)$")

class UserCreate(UserBase):
    password: str = Field(..., min_length=6)

class UserResponse(UserBase):
    id: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "Bearer"
    user: UserResponse
```

---

### 6. 安全工具（utils/security.py）

```python
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT配置
SECRET_KEY = "your-secret-key-change-this-in-production"  # 生产环境使用环境变量
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24小时

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """加密密码"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """创建JWT token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str):
    """解码JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
```

---

### 7. 统一响应格式（utils/response.py）

```python
from typing import Any, Optional
from fastapi.responses import JSONResponse

def success_response(data: Any = None, message: str = "操作成功"):
    """成功响应"""
    return {
        "success": True,
        "data": data,
        "message": message
    }

def error_response(error: str, code: str = "ERROR", status_code: int = 400):
    """错误响应"""
    return JSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "error": error,
            "code": code
        }
    )
```

---

### 8. 认证路由示例（routers/auth.py）

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from schemas.user import UserCreate, UserLogin, Token, UserResponse
from models.user import User
from config.database import get_db
from utils.security import verify_password, get_password_hash, create_access_token
from utils.response import success_response, error_response

router = APIRouter()

@router.post("/signup", response_model=dict)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    """用户注册"""
    # 检查用户名是否已存在
    existing_user = db.query(User).filter(User.username == user.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="用户名已存在"
        )
    
    # 创建新用户
    hashed_password = get_password_hash(user.password)
    new_user = User(
        username=user.username,
        password=hashed_password,
        role=user.role
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return success_response(
        data=UserResponse.from_orm(new_user),
        message="注册成功"
    )

@router.post("/login", response_model=dict)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """用户登录"""
    # 查找用户
    user = db.query(User).filter(User.username == credentials.username).first()
    if not user or not verify_password(credentials.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )
    
    # 创建访问令牌
    access_token = create_access_token(data={"sub": user.id, "role": user.role})
    
    return success_response(
        data={
            "access_token": access_token,
            "token_type": "Bearer",
            "user": UserResponse.from_orm(user)
        },
        message="登录成功"
    )
```

---

### 9. 依赖注入：获取当前用户

```python
# utils/dependencies.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from config.database import get_db
from models.user import User
from utils.security import decode_access_token

security = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """获取当前登录用户"""
    token = credentials.credentials
    payload = decode_access_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证凭据"
        )
    
    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    return user

def require_teacher(current_user: User = Depends(get_current_user)) -> User:
    """要求教师权限"""
    if current_user.role != "teacher":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要教师权限"
        )
    return current_user

def require_student(current_user: User = Depends(get_current_user)) -> User:
    """要求学生权限"""
    if current_user.role != "student":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要学生权限"
        )
    return current_user
```

---

### 10. 使用权限保护的路由示例

```python
# routers/courses.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from models.user import User
from models.course import Course
from config.database import get_db
from utils.dependencies import get_current_user, require_teacher
from schemas.course import CourseCreate, CourseResponse
from utils.response import success_response

router = APIRouter()

@router.get("/", response_model=dict)
def get_courses(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取课程列表"""
    courses = db.query(Course).all()
    return success_response(data={"courses": courses, "total": len(courses)})

@router.post("/", response_model=dict)
def create_course(
    course: CourseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher)  # 需要教师权限
):
    """创建课程"""
    new_course = Course(
        name=course.name,
        description=course.description,
        teacher_id=current_user.id
    )
    db.add(new_course)
    db.commit()
    db.refresh(new_course)
    
    return success_response(
        data=CourseResponse.from_orm(new_course),
        message="课程创建成功"
    )
```

---

## 运行应用

### 开发环境

```bash
# 启动服务器（自动重载）
uvicorn main:app --reload --host 0.0.0.0 --port 8080

# 或者直接运行
python main.py
```

### 访问API文档

FastAPI 自动生成交互式API文档：

- Swagger UI: http://localhost:8080/docs
- ReDoc: http://localhost:8080/redoc

---

## 数据库迁移（使用 Alembic）

### 安装
```bash
pip install alembic
```

### 初始化
```bash
alembic init migrations
```

### 配置（migrations/env.py）
```python
from config.database import Base
from models import user, teacher, student, course, homework  # 导入所有模型

target_metadata = Base.metadata
```

### 创建迁移
```bash
# 自动生成迁移脚本
alembic revision --autogenerate -m "Initial migration"

# 执行迁移
alembic upgrade head
```

---

## 测试

### 使用 pytest

```bash
pip install pytest httpx
```

**tests/test_auth.py**
```python
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_signup():
    response = client.post(
        "/api/auth/signup",
        json={
            "username": "test_user",
            "password": "test123",
            "role": "student"
        }
    )
    assert response.status_code == 200
    assert response.json()["success"] == True

def test_login():
    response = client.post(
        "/api/auth/login",
        json={
            "username": "test_user",
            "password": "test123"
        }
    )
    assert response.status_code == 200
    assert "access_token" in response.json()["data"]
```

运行测试：
```bash
pytest
```

---

## 部署建议

### 生产环境配置

1. **使用环境变量**
```python
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")
```

2. **使用 Gunicorn + Uvicorn**
```bash
pip install gunicorn

# 启动
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8080
```

3. **使用 Docker**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
```

---

## 常见问题

### 1. CORS 错误
确保在 `main.py` 中配置了 CORS 中间件

### 2. 数据库连接失败
检查数据库URL、用户名、密码是否正确

### 3. JWT Token 过期
调整 `ACCESS_TOKEN_EXPIRE_MINUTES` 参数

### 4. 密码加密慢
这是正常的，bcrypt 设计为慢速以防止暴力破解

---

## 下一步

1. ✅ 完成所有API端点的实现
2. ✅ 添加数据验证和错误处理
3. ✅ 编写单元测试
4. ✅ 添加日志记录
5. ✅ 性能优化（缓存、索引）
6. ✅ 部署到生产环境

祝开发顺利！🚀
