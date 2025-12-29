# 教育系统数据库设计文档

## 数据库概述

- **数据库类型**: PostgreSQL / MySQL (推荐 PostgreSQL)
- **字符集**: UTF-8
- **时区**: UTC
- **ORM**: 可选（SQLAlchemy / Prisma）

---

## 表结构设计

### 1. users（用户表）

**描述**: 存储所有用户的登录信息，包括教师和学生

| 字段名 | 数据类型 | 长度 | 约束 | 默认值 | 说明 |
|--------|---------|------|------|--------|------|
| id | VARCHAR | 36 | PRIMARY KEY | UUID | 用户唯一标识 |
| username | VARCHAR | 50 | NOT NULL, UNIQUE | - | 用户名（学号或工号） |
| password | VARCHAR | 255 | NOT NULL | - | 密码（加密存储） |
| role | ENUM | - | NOT NULL | - | 角色（teacher/student） |
| created_at | TIMESTAMP | - | NOT NULL | CURRENT_TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | - | NOT NULL | CURRENT_TIMESTAMP | 更新时间 |

**索引**:
- PRIMARY KEY: `id`
- UNIQUE INDEX: `username`
- INDEX: `role`

**SQL 创建语句**:
```sql
CREATE TABLE users (
    id VARCHAR(36) PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    role ENUM('teacher', 'student') NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_role (role)
);
```

---

### 2. teachers（教师表）

**描述**: 存储教师的详细信息

| 字段名 | 数据类型 | 长度 | 约束 | 默认值 | 说明 |
|--------|---------|------|------|--------|------|
| id | VARCHAR | 36 | PRIMARY KEY | UUID | 教师唯一标识 |
| teacher_no | VARCHAR | 50 | NOT NULL, UNIQUE | - | 工号（关联 users.username） |
| name | VARCHAR | 100 | NOT NULL | - | 姓名 |
| gender | ENUM | - | NOT NULL | - | 性别（男/女） |
| email | VARCHAR | 255 | NOT NULL | - | 邮箱 |
| created_at | TIMESTAMP | - | NOT NULL | CURRENT_TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | - | NOT NULL | CURRENT_TIMESTAMP | 更新时间 |

**索引**:
- PRIMARY KEY: `id`
- UNIQUE INDEX: `teacher_no`
- INDEX: `email`

**SQL 创建语句**:
```sql
CREATE TABLE teachers (
    id VARCHAR(36) PRIMARY KEY,
    teacher_no VARCHAR(50) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    gender ENUM('男', '女') NOT NULL,
    email VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_email (email),
    FOREIGN KEY (teacher_no) REFERENCES users(username) ON DELETE CASCADE
);
```

---

### 3. students（学生表）

**描述**: 存储学生的详细信息

| 字段名 | 数据类型 | 长度 | 约束 | 默认值 | 说明 |
|--------|---------|------|------|--------|------|
| id | VARCHAR | 36 | PRIMARY KEY | UUID | 学生唯一标识 |
| student_no | VARCHAR | 50 | NOT NULL, UNIQUE | - | 学号（关联 users.username） |
| name | VARCHAR | 100 | NOT NULL | - | 姓名 |
| class | VARCHAR | 50 | NOT NULL | - | 班级 |
| gender | ENUM | - | NOT NULL | - | 性别（男/女） |
| created_at | TIMESTAMP | - | NOT NULL | CURRENT_TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | - | NOT NULL | CURRENT_TIMESTAMP | 更新时间 |

**索引**:
- PRIMARY KEY: `id`
- UNIQUE INDEX: `student_no`
- INDEX: `class`

**SQL 创建语句**:
```sql
CREATE TABLE students (
    id VARCHAR(36) PRIMARY KEY,
    student_no VARCHAR(50) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    class VARCHAR(50) NOT NULL,
    gender ENUM('男', '女') NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_class (class),
    FOREIGN KEY (student_no) REFERENCES users(username) ON DELETE CASCADE
);
```

---

### 4. courses（课程表）

**描述**: 存储课程信息

| 字段名 | 数据类型 | 长度 | 约束 | 默认值 | 说明 |
|--------|---------|------|------|--------|------|
| id | VARCHAR | 36 | PRIMARY KEY | UUID | 课程唯一标识 |
| name | VARCHAR | 255 | NOT NULL | - | 课程名称 |
| description | TEXT | - | NULL | - | 课程描述 |
| teacher_id | VARCHAR | 36 | NOT NULL | - | 教师ID（外键） |
| student_count | INT | - | NOT NULL | 0 | 学员数量 |
| created_at | TIMESTAMP | - | NOT NULL | CURRENT_TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | - | NOT NULL | CURRENT_TIMESTAMP | 更新时间 |

**索引**:
- PRIMARY KEY: `id`
- INDEX: `teacher_id`
- INDEX: `name`

**SQL 创建语句**:
```sql
CREATE TABLE courses (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    teacher_id VARCHAR(36) NOT NULL,
    student_count INT NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_teacher_id (teacher_id),
    INDEX idx_name (name),
    FOREIGN KEY (teacher_id) REFERENCES teachers(id) ON DELETE CASCADE
);
```

---

### 5. course_enrollments（课程选课表）

**描述**: 存储学生选课关系（多对多关系）

| 字段名 | 数据类型 | 长度 | 约束 | 默认值 | 说明 |
|--------|---------|------|------|--------|------|
| id | VARCHAR | 36 | PRIMARY KEY | UUID | 选课记录唯一标识 |
| course_id | VARCHAR | 36 | NOT NULL | - | 课程ID（外键） |
| student_id | VARCHAR | 36 | NOT NULL | - | 学生ID（外键） |
| enrolled_at | TIMESTAMP | - | NOT NULL | CURRENT_TIMESTAMP | 选课时间 |

**索引**:
- PRIMARY KEY: `id`
- UNIQUE INDEX: `course_id, student_id`（防止重复选课）
- INDEX: `course_id`
- INDEX: `student_id`

**SQL 创建语句**:
```sql
CREATE TABLE course_enrollments (
    id VARCHAR(36) PRIMARY KEY,
    course_id VARCHAR(36) NOT NULL,
    student_id VARCHAR(36) NOT NULL,
    enrolled_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY idx_course_student (course_id, student_id),
    INDEX idx_course_id (course_id),
    INDEX idx_student_id (student_id),
    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
);
```

---

### 6. homeworks（作业表）

**描述**: 存储作业信息

| 字段名 | 数据类型 | 长度 | 约束 | 默认值 | 说明 |
|--------|---------|------|------|--------|------|
| id | VARCHAR | 36 | PRIMARY KEY | UUID | 作业唯一标识 |
| course_id | VARCHAR | 36 | NOT NULL | - | 课程ID（外键） |
| title | VARCHAR | 255 | NOT NULL | - | 作业标题 |
| description | TEXT | - | NULL | - | 作业描述 |
| deadline | TIMESTAMP | - | NOT NULL | - | 截止时间 |
| attachment_name | VARCHAR | 255 | NULL | - | 附件名称 |
| attachment_type | VARCHAR | 100 | NULL | - | 附件类型 |
| attachment_size | BIGINT | - | NULL | - | 附件大小（字节） |
| attachment_content | LONGTEXT | - | NULL | - | 附件内容（base64） |
| grading_criteria_type | ENUM | - | NULL | - | 批改标准类型（text/file） |
| grading_criteria_content | TEXT | - | NULL | - | 批改标准内容 |
| grading_criteria_file_name | VARCHAR | 255 | NULL | - | 批改标准文件名 |
| grading_criteria_file_size | BIGINT | - | NULL | - | 批改标准文件大小 |
| created_at | TIMESTAMP | - | NOT NULL | CURRENT_TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | - | NOT NULL | CURRENT_TIMESTAMP | 更新时间 |

**索引**:
- PRIMARY KEY: `id`
- INDEX: `course_id`
- INDEX: `deadline`

**SQL 创建语句**:
```sql
CREATE TABLE homeworks (
    id VARCHAR(36) PRIMARY KEY,
    course_id VARCHAR(36) NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    deadline TIMESTAMP NOT NULL,
    attachment_name VARCHAR(255),
    attachment_type VARCHAR(100),
    attachment_size BIGINT,
    attachment_content LONGTEXT,
    grading_criteria_type ENUM('text', 'file'),
    grading_criteria_content TEXT,
    grading_criteria_file_name VARCHAR(255),
    grading_criteria_file_size BIGINT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_course_id (course_id),
    INDEX idx_deadline (deadline),
    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE
);
```

---

### 7. homework_submissions（作业提交表）

**描述**: 存储学生作业提交记录

| 字段名 | 数据类型 | 长度 | 约束 | 默认值 | 说明 |
|--------|---------|------|------|--------|------|
| id | VARCHAR | 36 | PRIMARY KEY | UUID | 提交唯一标识 |
| homework_id | VARCHAR | 36 | NOT NULL | - | 作业ID（外键） |
| student_id | VARCHAR | 36 | NOT NULL | - | 学生ID（外键） |
| content | TEXT | - | NOT NULL | - | 作业文本内容 |
| score | INT | - | NULL | - | 分数（0-100） |
| feedback | TEXT | - | NULL | - | 批改反馈 |
| submitted_at | TIMESTAMP | - | NOT NULL | CURRENT_TIMESTAMP | 提交时间 |
| graded_at | TIMESTAMP | - | NULL | - | 批改时间 |
| created_at | TIMESTAMP | - | NOT NULL | CURRENT_TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | - | NOT NULL | CURRENT_TIMESTAMP | 更新时间 |

**索引**:
- PRIMARY KEY: `id`
- UNIQUE INDEX: `homework_id, student_id`（每个学生每个作业只能提交一次）
- INDEX: `homework_id`
- INDEX: `student_id`
- INDEX: `submitted_at`

**SQL 创建语句**:
```sql
CREATE TABLE homework_submissions (
    id VARCHAR(36) PRIMARY KEY,
    homework_id VARCHAR(36) NOT NULL,
    student_id VARCHAR(36) NOT NULL,
    content TEXT NOT NULL,
    score INT,
    feedback TEXT,
    submitted_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    graded_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY idx_homework_student (homework_id, student_id),
    INDEX idx_homework_id (homework_id),
    INDEX idx_student_id (student_id),
    INDEX idx_submitted_at (submitted_at),
    FOREIGN KEY (homework_id) REFERENCES homeworks(id) ON DELETE CASCADE,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    CHECK (score >= 0 AND score <= 100)
);
```

---

### 8. submission_attachments（作业提交附件表）

**描述**: 存储作业提交的附件（一对多关系）

| 字段名 | 数据类型 | 长度 | 约束 | 默认值 | 说明 |
|--------|---------|------|------|--------|------|
| id | VARCHAR | 36 | PRIMARY KEY | UUID | 附件唯一标识 |
| submission_id | VARCHAR | 36 | NOT NULL | - | 提交ID（外键） |
| name | VARCHAR | 255 | NOT NULL | - | 文件名 |
| type | VARCHAR | 100 | NOT NULL | - | 文件类型（MIME） |
| size | BIGINT | - | NOT NULL | - | 文件大小（字节） |
| content | LONGTEXT | - | NOT NULL | - | 文件内容（base64） |
| created_at | TIMESTAMP | - | NOT NULL | CURRENT_TIMESTAMP | 上传时间 |

**索引**:
- PRIMARY KEY: `id`
- INDEX: `submission_id`

**SQL 创建语句**:
```sql
CREATE TABLE submission_attachments (
    id VARCHAR(36) PRIMARY KEY,
    submission_id VARCHAR(36) NOT NULL,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(100) NOT NULL,
    size BIGINT NOT NULL,
    content LONGTEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_submission_id (submission_id),
    FOREIGN KEY (submission_id) REFERENCES homework_submissions(id) ON DELETE CASCADE
);
```

---

### 9. course_folders（课程文件夹表）

**描述**: 存储课程资源的文件夹

| 字段名 | 数据类型 | 长度 | 约束 | 默认值 | 说明 |
|--------|---------|------|------|--------|------|
| id | VARCHAR | 36 | PRIMARY KEY | UUID | 文件夹唯一标识 |
| course_id | VARCHAR | 36 | NOT NULL | - | 课程ID（外键） |
| name | VARCHAR | 255 | NOT NULL | - | 文件夹名称 |
| created_at | TIMESTAMP | - | NOT NULL | CURRENT_TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | - | NOT NULL | CURRENT_TIMESTAMP | 更新时间 |

**索引**:
- PRIMARY KEY: `id`
- INDEX: `course_id`
- UNIQUE INDEX: `course_id, name`（同一课程下文件夹名称唯一）

**SQL 创建语句**:
```sql
CREATE TABLE course_folders (
    id VARCHAR(36) PRIMARY KEY,
    course_id VARCHAR(36) NOT NULL,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_course_id (course_id),
    UNIQUE KEY idx_course_name (course_id, name),
    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE
);
```

---

### 10. course_files（课程文件表）

**描述**: 存储课程资源文件

| 字段名 | 数据类型 | 长度 | 约束 | 默认值 | 说明 |
|--------|---------|------|------|--------|------|
| id | VARCHAR | 36 | PRIMARY KEY | UUID | 文件唯一标识 |
| folder_id | VARCHAR | 36 | NOT NULL | - | 文件夹ID（外键） |
| course_id | VARCHAR | 36 | NOT NULL | - | 课程ID（外键） |
| name | VARCHAR | 255 | NOT NULL | - | 文件名 |
| size | BIGINT | - | NOT NULL | - | 文件大小（字节） |
| type | VARCHAR | 100 | NOT NULL | - | 文件类型（MIME） |
| content | LONGTEXT | - | NOT NULL | - | 文件内容（base64） |
| created_at | TIMESTAMP | - | NOT NULL | CURRENT_TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | - | NOT NULL | CURRENT_TIMESTAMP | 更新时间 |

**索引**:
- PRIMARY KEY: `id`
- INDEX: `folder_id`
- INDEX: `course_id`

**SQL 创建语句**:
```sql
CREATE TABLE course_files (
    id VARCHAR(36) PRIMARY KEY,
    folder_id VARCHAR(36) NOT NULL,
    course_id VARCHAR(36) NOT NULL,
    name VARCHAR(255) NOT NULL,
    size BIGINT NOT NULL,
    type VARCHAR(100) NOT NULL,
    content LONGTEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_folder_id (folder_id),
    INDEX idx_course_id (course_id),
    FOREIGN KEY (folder_id) REFERENCES course_folders(id) ON DELETE CASCADE,
    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE
);
```

---

## 表关系图（ER图）

```
┌─────────────┐
│   users     │
│             │
│ - id (PK)   │
│ - username  │◄─────────┐
│ - password  │          │ teacher_no (FK)
│ - role      │          │
└─────────────┘          │
                         │
       ┌─────────────────┴────────────────┐
       │                                  │
┌──────┴──────┐                  ┌────────┴──────┐
│  teachers   │                  │   students    │
│             │                  │               │
│ - id (PK)   │──────┐           │ - id (PK)     │───────┐
│ - teacher_no│      │           │ - student_no  │       │
│ - name      │      │           │ - name        │       │
│ - gender    │      │           │ - class       │       │
│ - email     │      │           │ - gender      │       │
└─────────────┘      │           └───────────────┘       │
                     │                                   │
                     │ teacher_id (FK)                   │ student_id (FK)
                     │                                   │
              ┌──────┴─────────┐                         │
              │   courses      │                         │
              │                │                         │
              │ - id (PK)      │◄────────────────────────┼──────────┐
              │ - name         │                         │          │
              │ - description  │                         │          │
              │ - teacher_id   │                         │          │
              │ - student_count│                         │          │
              └────────┬───────┘                         │          │
                       │                                 │          │
              ┌────────┴───────────────────┬─────────────┴──────┐   │
              │                            │                    │   │
       course_id (FK)             course_id (FK)       course_id (FK)
              │                            │                    │   │
    ┌─────────┴─────────┐        ┌────────┴─────────┐  ┌───────┴───┴────────────┐
    │   homeworks       │        │ course_folders   │  │ course_enrollments     │
    │                   │        │                  │  │                        │
    │ - id (PK)         │◄─┐     │ - id (PK)        │◄─┤ - id (PK)              │
    │ - course_id       │  │     │ - course_id      │  │ - course_id            │
    │ - title           │  │     │ - name           │  │ - student_id           │
    │ - description     │  │     └────────┬─────────┘  │ - enrolled_at          │
    │ - deadline        │  │              │            └────────────────────────┘
    │ - attachment...   │  │     folder_id (FK)
    └───────────────────┘  │              │
                           │     ┌────────┴─────────┐
                  homework_id (FK)│ course_files    │
                           │     │                  │
           ┌───────────────┴───┐ │ - id (PK)        │
           │ homework_         │ │ - folder_id      │
           │   submissions     │ │ - course_id      │
           │                   │ │ - name           │
           │ - id (PK)         │◄┤ - size           │
           │ - homework_id     │ │ - type           │
           │ - student_id      │ │ - content        │
           │ - content         │ └──────────────────┘
           │ - score           │
           │ - feedback        │
           │ - submitted_at    │
           │ - graded_at       │
           └───────┬───────────┘
                   │
          submission_id (FK)
                   │
    ┌──────────────┴──────────────┐
    │ submission_attachments      │
    │                             │
    │ - id (PK)                   │
    │ - submission_id             │
    │ - name                      │
    │ - type                      │
    │ - size                      │
    │ - content                   │
    └─────────────────────────────┘
```

---

## 数据迁移

### 初始化脚本

```sql
-- 创建数据库
CREATE DATABASE edu_system CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE edu_system;

-- 按顺序执行上述所有建表语句

-- 创建初始管理员（可选）
INSERT INTO users (id, username, password, role, created_at) 
VALUES (UUID(), 'admin', '$2b$10$...', 'teacher', NOW());
```

### 初始化数据（示例）

```sql
-- 插入5个教师
INSERT INTO users (id, username, password, role) VALUES
(UUID(), 'teacher1', '$2b$10$hashed_password', 'teacher'),
(UUID(), 'teacher2', '$2b$10$hashed_password', 'teacher'),
(UUID(), 'teacher3', '$2b$10$hashed_password', 'teacher'),
(UUID(), 'teacher4', '$2b$10$hashed_password', 'teacher'),
(UUID(), 'teacher5', '$2b$10$hashed_password', 'teacher');

-- 插入教师详细信息
INSERT INTO teachers (id, teacher_no, name, gender, email) VALUES
(UUID(), 'teacher1', '教师1', '女', 'teacher1@example.com'),
(UUID(), 'teacher2', '教师2', '男', 'teacher2@example.com'),
(UUID(), 'teacher3', '教师3', '女', 'teacher3@example.com'),
(UUID(), 'teacher4', '教师4', '男', 'teacher4@example.com'),
(UUID(), 'teacher5', '教师5', '女', 'teacher5@example.com');

-- 插入100个学生（示例）
-- 使用循环或脚本生成
```

---

## 性能优化建议

### 1. 索引优化
- 为常用查询字段添加索引
- 复合索引用于多字段查询
- 定期分析索引使用情况

### 2. 查询优化
- 使用 JOIN 代替子查询
- 限制 SELECT 字段，避免 SELECT *
- 使用分页查询大数据量

### 3. 存储优化
- 大文件考虑使用对象存储（OSS）
- base64 内容可以考虑压缩
- 定期清理过期数据

### 4. 缓存策略
- 使用 Redis 缓存热点数据
- 课程列表、学生列表等使用缓存
- 设置合理的过期时间

---

## 备份策略

### 1. 定期备份
- 每天凌晨全量备份
- 每小时增量备份
- 保留最近30天备份

### 2. 备份命令（MySQL）
```bash
# 全量备份
mysqldump -u root -p edu_system > backup_$(date +%Y%m%d).sql

# 恢复
mysql -u root -p edu_system < backup_20251202.sql
```

### 3. 备份命令（PostgreSQL）
```bash
# 全量备份
pg_dump -U postgres edu_system > backup_$(date +%Y%m%d).sql

# 恢复
psql -U postgres edu_system < backup_20251202.sql
```

---

## 安全建议

### 1. 数据安全
- 密码使用 bcrypt 加密
- 敏感数据加密存储
- 使用 HTTPS 传输

### 2. 访问控制
- 最小权限原则
- 使用数据库用户权限管理
- 定期审计数据库访问日志

### 3. SQL 注入防护
- 使用参数化查询
- 输入验证和过滤
- 使用 ORM 框架

---

## 附录

### 常用查询示例

#### 1. 获取教师的所有课程及学员数
```sql
SELECT c.id, c.name, c.description, c.student_count, t.name as teacher_name
FROM courses c
JOIN teachers t ON c.teacher_id = t.id
WHERE t.teacher_no = 'teacher1'
ORDER BY c.created_at DESC;
```

#### 2. 获取学生的所有课程
```sql
SELECT c.*, ce.enrolled_at, t.name as teacher_name
FROM courses c
JOIN course_enrollments ce ON c.id = ce.course_id
JOIN students s ON ce.student_id = s.id
JOIN teachers t ON c.teacher_id = t.id
WHERE s.student_no = 'student1'
ORDER BY ce.enrolled_at DESC;
```

#### 3. 获取课程的所有作业及提交情况
```sql
SELECT h.*, 
       COUNT(hs.id) as submission_count,
       AVG(hs.score) as avg_score
FROM homeworks h
LEFT JOIN homework_submissions hs ON h.id = hs.homework_id
WHERE h.course_id = 'course-uuid'
GROUP BY h.id
ORDER BY h.deadline DESC;
```

#### 4. 获取待批改的作业
```sql
SELECT hs.*, h.title, s.name as student_name, s.student_no
FROM homework_submissions hs
JOIN homeworks h ON hs.homework_id = h.id
JOIN students s ON hs.student_id = s.id
WHERE h.course_id = 'course-uuid'
  AND hs.score IS NULL
ORDER BY hs.submitted_at ASC;
```

#### 5. 统计课程学员的作业完成情况
```sql
SELECT s.id, s.name, s.student_no,
       COUNT(DISTINCT h.id) as total_homeworks,
       COUNT(DISTINCT hs.id) as submitted_count,
       AVG(hs.score) as avg_score
FROM students s
JOIN course_enrollments ce ON s.id = ce.student_id
CROSS JOIN homeworks h ON ce.course_id = h.course_id
LEFT JOIN homework_submissions hs ON h.id = hs.homework_id AND s.id = hs.student_id
WHERE ce.course_id = 'course-uuid'
GROUP BY s.id, s.name, s.student_no
ORDER BY avg_score DESC;
```
