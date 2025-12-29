# 教育系统后端开发文档

## 📚 文档概览

本项目为教育系统的后端API开发提供了完整的技术文档。

### 文档列表

| 文档 | 描述 | 路径 |
|------|------|------|
| **API接口文档** | 完整的REST API接口规范，包含所有端点的请求/响应格式 | [API_DOCUMENTATION.md](./API_DOCUMENTATION.md) |
| **数据库设计文档** | 数据库表结构、索引、关系图和优化建议 | [DATABASE_SCHEMA.md](./DATABASE_SCHEMA.md) |
| **后端开发指南** | 从零搭建后端的完整教程和最佳实践 | [BACKEND_DEVELOPMENT_GUIDE.md](./BACKEND_DEVELOPMENT_GUIDE.md) |

---

## 🚀 快速开始

### 1. 配置前端API地址

前端配置文件：`/config/api.ts`

```typescript
export const API_CONFIG = {
  BASE_URL: 'http://localhost:8080',  // 本地开发
};
```

### 2. 搭建后端服务

#### Python + FastAPI（推荐）

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate

# 安装依赖
pip install fastapi uvicorn sqlalchemy pymysql pydantic python-jose passlib

# 创建数据库
mysql -u root -p
CREATE DATABASE edu_system CHARACTER SET utf8mb4;

# 运行服务器
uvicorn main:app --reload --port 8080
```

访问：
- API文档：http://localhost:8080/docs
- 后端API：http://localhost:8080/api

### 3. 初始化数据库

运行数据库迁移脚本，创建所有表结构（见 DATABASE_SCHEMA.md）

---

## 📋 系统架构

```
┌─────────────────┐
│   前端 (React)  │
│   Port: 5173    │
└────────┬────────┘
         │ HTTP/JSON
         ↓
┌─────────────────┐
│ 后端 API        │
│ (FastAPI)       │
│ Port: 8080      │
└────────┬────────┘
         │ SQL
         ↓
┌─────────────────┐
│ 数据库          │
│ (MySQL/PG)      │
└─────────────────┘
```

---

## 🗂️ 数据模型概览

### 核心实体

1. **Users（用户）** - 登录账户（教师/学生）
2. **Teachers（教师）** - 教师详细信息
3. **Students（学生）** - 学生详细信息
4. **Courses（课程）** - 课程信息
5. **CourseEnrollments（选课）** - 学生选课关系
6. **Homeworks（作业）** - 作业信息
7. **HomeworkSubmissions（作业提交）** - 学生作业提交
8. **CourseFolders（课程文件夹）** - 课程资源文件夹
9. **CourseFiles（课程文件）** - 课程资源文件

### 关系说明

```
用户 (1) ──< 教师/学生
教师 (1) ──< 课程 (N)
课程 (N) ──< 学生 (N) [多对多，通过 CourseEnrollments]
课程 (1) ──< 作业 (N)
作业 (N) ──< 作业提交 (N)
课程 (1) ──< 文件夹 (N)
文件夹 (1) ──< 文件 (N)
```

---

## 🔌 API端点概览

### 认证模块
- `POST /api/auth/signup` - 用户注册
- `POST /api/auth/login` - 用户登录
- `POST /api/auth/logout` - 用户登出
- `GET /api/auth/verify` - 验证Token

### 教师管理
- `GET /api/teachers` - 获取教师列表
- `GET /api/teachers/{id}` - 获取教师详情
- `POST /api/teachers` - 创建教师
- `PUT /api/teachers/{id}` - 更新教师
- `DELETE /api/teachers/{id}` - 删除教师

### 学生管理
- `GET /api/students` - 获取学生列表
- `GET /api/students/{id}` - 获取学生详情
- `POST /api/students` - 创建学生
- `PUT /api/students/{id}` - 更新学生
- `DELETE /api/students/{id}` - 删除学生

### 课程管理
- `GET /api/courses` - 获取课程列表
- `GET /api/courses/{id}` - 获取课程详情
- `POST /api/courses` - 创建课程
- `PUT /api/courses/{id}` - 更新课程
- `DELETE /api/courses/{id}` - 删除课程
- `GET /api/courses/{id}/students` - 获取课程学员
- `POST /api/courses/{id}/students` - 添加学员
- `DELETE /api/courses/{id}/students/{studentId}` - 移除学员

### 作业管理
- `GET /api/courses/{id}/homeworks` - 获取课程作业
- `GET /api/homeworks/{id}` - 获取作业详情
- `POST /api/courses/{id}/homeworks` - 创建作业
- `PUT /api/homeworks/{id}` - 更新作业
- `DELETE /api/homeworks/{id}` - 删除作业

### 作业提交管理
- `GET /api/homeworks/{id}/submissions` - 获取作业提交列表
- `GET /api/submissions/{id}` - 获取提交详情
- `POST /api/homeworks/{id}/submissions` - 提交作业
- `PUT /api/submissions/{id}` - 更新提交
- `POST /api/submissions/{id}/grade` - 批改作业
- `DELETE /api/submissions/{id}` - 删除提交

### 课程资源管理
- `GET /api/courses/{id}/folders` - 获取文件夹列表
- `POST /api/courses/{id}/folders` - 创建文件夹
- `GET /api/folders/{id}/files` - 获取文件列表
- `POST /api/folders/{id}/files` - 上传文件
- `PUT /api/files/{id}` - 更新文件
- `DELETE /api/files/{id}` - 删除文件

详细说明见：[API_DOCUMENTATION.md](./API_DOCUMENTATION.md)

---

## 🔐 认证流程

### 1. 用户注册
```
客户端 → POST /api/auth/signup
         {username, password, role}
       ← {success: true, data: {user}}
```

### 2. 用户登录
```
客户端 → POST /api/auth/login
         {username, password}
       ← {success: true, data: {access_token, user}}
```

### 3. 访问受保护的API
```
客户端 → GET /api/courses
         Header: Authorization: Bearer {access_token}
       ← {success: true, data: {courses}}
```

### 4. Token验证
服务器自动验证每个请求的Token：
- Token有效 → 继续处理请求
- Token无效/过期 → 返回401错误

---

## 💾 数据存储说明

### 当前状态（LocalStorage）
前端使用 LocalStorage 模拟后端数据存储：
- 初始化100个学生（student1-100）
- 初始化5个教师（teacher1-5）
- 密码统一为：123456

### 迁移到真实后端
1. 实现所有API端点
2. 将前端的 `localStorage-service.ts` 调用替换为API调用
3. 使用 `/config/api.ts` 中定义的端点

---

## 📊 数据库表结构概览

### 核心表

| 表名 | 主要字段 | 说明 |
|------|---------|------|
| users | id, username, password, role | 用户登录表 |
| teachers | id, teacher_no, name, gender, email | 教师信息表 |
| students | id, student_no, name, class, gender | 学生信息表 |
| courses | id, name, description, teacher_id | 课程表 |
| course_enrollments | course_id, student_id | 选课关系表 |
| homeworks | id, course_id, title, deadline | 作业表 |
| homework_submissions | id, homework_id, student_id, score | 作业提交表 |
| course_folders | id, course_id, name | 课程文件夹表 |
| course_files | id, folder_id, name, content | 课程文件表 |

详细结构见：[DATABASE_SCHEMA.md](./DATABASE_SCHEMA.md)

---

## 🛠️ 开发工具推荐

### API测试
- **Postman** - API测试工具
- **Insomnia** - REST客户端
- **HTTPie** - 命令行HTTP客户端

### 数据库管理
- **DBeaver** - 通用数据库管理工具
- **MySQL Workbench** - MySQL专用工具
- **pgAdmin** - PostgreSQL专用工具

### 开发环境
- **VSCode** + Python/Node.js扩展
- **PyCharm** - Python IDE
- **Docker** - 容器化部署

---

## 📝 开发检查清单

### 后端开发
- [ ] 搭建基础框架（FastAPI/Express）
- [ ] 配置数据库连接
- [ ] 创建数据模型
- [ ] 实现认证模块（注册、登录、JWT）
- [ ] 实现教师管理API
- [ ] 实现学生管理API
- [ ] 实现课程管理API
- [ ] 实现作业管理API
- [ ] 实现文件上传/下载
- [ ] 添加数据验证
- [ ] 添加错误处理
- [ ] 编写单元测试
- [ ] 性能优化
- [ ] 部署上线

### 前端集成
- [ ] 替换LocalStorage为API调用
- [ ] 实现Token管理
- [ ] 处理API错误
- [ ] 添加加载状态
- [ ] 优化用户体验

---

## 🔍 常见问题

### Q1: 如何处理大文件上传？
**A**: 使用分块上传或对象存储（OSS），不要直接存储在数据库中

### Q2: 如何提高API性能？
**A**: 
- 添加数据库索引
- 使用Redis缓存热点数据
- 实现分页查询
- 优化SQL查询

### Q3: 如何保证数据安全？
**A**:
- 密码使用bcrypt加密
- 使用HTTPS传输
- 实现访问控制
- 定期备份数据

### Q4: 如何处理并发请求？
**A**:
- 使用数据库事务
- 实现乐观锁/悲观锁
- 使用消息队列处理异步任务

---

## 📚 参考资源

### 官方文档
- [FastAPI文档](https://fastapi.tiangolo.com/)
- [SQLAlchemy文档](https://www.sqlalchemy.org/)
- [Pydantic文档](https://docs.pydantic.dev/)

### 教程
- [FastAPI完整教程](https://fastapi.tiangolo.com/tutorial/)
- [Python JWT认证](https://realpython.com/token-based-authentication-with-flask/)
- [RESTful API设计指南](https://restfulapi.net/)

---

## 🤝 贡献指南

欢迎提交问题和改进建议！

### 提交流程
1. Fork 项目
2. 创建特性分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

---

## 📄 许可证

本项目采用 MIT 许可证

---

## 📞 联系方式

如有问题，请通过以下方式联系：
- 创建 Issue
- 发送邮件

---

**祝开发顺利！** 🎉
