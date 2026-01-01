# 智能教学系统技术文档

## 1. 项目概述

智能教学系统是一款面向高校的在线学习平台，旨在通过人工智能技术提升教学效率和学习体验。系统采用前后端分离架构，支持多种教学场景，包括课程管理、资源共享、在线考试、AI辅助学习等功能模块。

项目于2024年1月启动，由张三担任技术负责人，李四负责前端开发，王五负责后端开发，赵六负责AI模块开发。团队共计15人，历时8个月完成第一版本开发。

## 2. 系统架构

### 2.1 前端架构

前端采用 React 18 + TypeScript 技术栈，使用 Vite 作为构建工具。主要依赖包括：

- React Router v6：路由管理
- Zustand：状态管理
- Tailwind CSS：样式框架
- Shadcn/ui：UI组件库
- Axios：HTTP请求

前端项目结构如下：
```
frontend/
├── src/
│   ├── components/    # 可复用组件
│   ├── pages/         # 页面组件
│   ├── stores/        # 状态管理
│   ├── hooks/         # 自定义Hook
│   ├── utils/         # 工具函数
│   └── api/           # API接口
├── public/            # 静态资源
└── package.json
```

### 2.2 后端架构

后端采用 Python FastAPI 框架，数据库使用 PostgreSQL，缓存使用 Redis。主要模块包括：

- 用户认证模块（JWT Token）
- 课程管理模块
- 资源管理模块
- 考试系统模块
- AI服务模块

后端API遵循RESTful规范，所有接口返回统一的JSON格式：
```json
{
  "success": true,
  "data": {},
  "message": "操作成功"
}
```

### 2.3 AI模块架构

AI模块采用 RAG（检索增强生成）架构，主要组件包括：

1. **文档解析器**：支持PDF、Word、PPT等格式
2. **向量数据库**：使用ChromaDB存储文档向量
3. **检索器**：混合检索（向量+BM25）
4. **大语言模型**：接入OpenAI API

## 3. 核心功能

### 3.1 课程管理

教师可以创建和管理课程，包括：
- 课程基本信息设置（名称、描述、封面）
- 课程资源上传（视频、文档、PPT）
- 学生名单管理（导入、导出）
- 课程公告发布

课程资源支持的文件格式：PDF、DOCX、PPTX、MP4、PNG、JPG

### 3.2 在线考试

考试系统支持多种题型：
- 单选题（4个选项）
- 多选题（4-6个选项）
- 判断题
- 填空题
- 简答题

考试配置选项：
- 考试时长：30-180分钟
- 及格分数：默认60分
- 是否允许查看答案
- 是否随机出题
- 防作弊设置（切屏检测、摄像头监控）

### 3.3 AI学习助手

AI学习助手基于RAG技术，能够：
- 回答课程相关问题
- 生成学习摘要
- 智能推荐学习资源
- 自动批改简答题

使用流程：
1. 学生选择要查询的知识库（课程资源或个人上传）
2. 输入问题
3. 系统检索相关文档片段
4. AI生成回答并标注引用来源

## 4. 数据库设计

### 4.1 用户表（users）

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | UUID | 主键 |
| username | VARCHAR(50) | 用户名 |
| email | VARCHAR(100) | 邮箱 |
| password_hash | VARCHAR(255) | 密码哈希 |
| role | ENUM | 角色（student/teacher/admin） |
| created_at | TIMESTAMP | 创建时间 |

### 4.2 课程表（courses）

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | UUID | 主键 |
| name | VARCHAR(100) | 课程名称 |
| description | TEXT | 课程描述 |
| teacher_id | UUID | 教师ID（外键） |
| cover_url | VARCHAR(255) | 封面图片URL |
| status | ENUM | 状态（draft/published/archived） |
| created_at | TIMESTAMP | 创建时间 |

### 4.3 资源表（resources）

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | UUID | 主键 |
| course_id | UUID | 课程ID（外键） |
| name | VARCHAR(100) | 资源名称 |
| file_path | VARCHAR(255) | 文件路径 |
| file_type | VARCHAR(20) | 文件类型 |
| file_size | BIGINT | 文件大小（字节） |
| download_count | INT | 下载次数 |
| created_at | TIMESTAMP | 创建时间 |

## 5. API接口文档

### 5.1 用户认证

**登录接口**
- 路径：POST /api/auth/login
- 请求体：
```json
{
  "username": "string",
  "password": "string"
}
```
- 响应：
```json
{
  "success": true,
  "data": {
    "token": "jwt_token_here",
    "user": {
      "id": "uuid",
      "username": "string",
      "role": "student"
    }
  }
}
```

### 5.2 课程接口

**获取课程列表**
- 路径：GET /api/courses
- 参数：page（页码）、size（每页数量）、keyword（搜索关键词）
- 响应：课程列表及分页信息

**创建课程**
- 路径：POST /api/courses
- 权限：仅教师和管理员
- 请求体：课程基本信息

### 5.3 AI聊天接口

**发送消息**
- 路径：POST /api/ai/chat
- 请求体：
```json
{
  "message": "问题内容",
  "knowledge_ids": ["知识库ID列表"],
  "history": [{"role": "user", "content": "历史消息"}]
}
```
- 响应：
```json
{
  "success": true,
  "message": "AI回答内容",
  "sources": [
    {
      "name": "来源文件名",
      "content": "引用内容",
      "score": 0.85
    }
  ]
}
```

## 6. 部署说明

### 6.1 环境要求

- Python 3.10+
- Node.js 18+
- PostgreSQL 14+
- Redis 7+
- Docker（可选）

### 6.2 配置文件

后端配置文件 `.env`：
```
DATABASE_URL=postgresql://user:pass@localhost:5432/dbname
REDIS_URL=redis://localhost:6379
OPENAI_API_KEY=sk-xxx
JWT_SECRET=your_secret_key
```

### 6.3 启动命令

开发环境：
```bash
# 后端
cd backend && uvicorn app.main:app --reload

# 前端
cd frontend && npm run dev
```

生产环境：
```bash
docker-compose up -d
```

## 7. 性能优化

### 7.1 前端优化

- 代码分割：使用React.lazy进行路由级别代码分割
- 图片优化：使用WebP格式，配合CDN加速
- 缓存策略：使用Service Worker缓存静态资源

### 7.2 后端优化

- 数据库索引：为常用查询字段添加索引
- 连接池：使用连接池管理数据库连接
- 异步处理：文件上传、AI推理等耗时操作使用异步任务队列

### 7.3 AI模块优化

- 向量缓存：热门查询结果缓存
- 批量处理：文档批量向量化
- 模型选择：根据问题复杂度选择不同模型

## 8. 常见问题

### Q1: 如何重置用户密码？

管理员可以在后台管理系统中选择用户，点击"重置密码"按钮。系统会发送重置链接到用户邮箱。

### Q2: 支持多大的文件上传？

默认支持最大100MB的文件上传。如需调整，修改配置文件中的 `MAX_UPLOAD_SIZE` 参数。

### Q3: AI回答不准确怎么办？

1. 检查知识库是否包含相关内容
2. 尝试调整问题表述
3. 上传更多相关资料到知识库

### Q4: 如何联系技术支持？

- 邮箱：support@example.com
- 电话：400-123-4567
- 工作时间：周一至周五 9:00-18:00
