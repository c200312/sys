# 教育系统 API 接口文档

## 基本信息

- **基础URL**: `http://localhost:8080`
- **数据格式**: JSON
- **字符编码**: UTF-8
- **认证方式**: Bearer Token (JWT)

## 通用响应格式

### 成功响应
```json
{
  "success": true,
  "data": {},
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

## 状态码说明

| 状态码 | 说明 |
|--------|------|
| 200 | 请求成功 |
| 201 | 创建成功 |
| 204 | 删除成功（无内容） |
| 400 | 请求参数错误 |
| 401 | 未授权（未登录或token过期） |
| 403 | 禁止访问（无权限） |
| 404 | 资源不存在 |
| 409 | 资源冲突（如用户名已存在） |
| 500 | 服务器内部错误 |

---

## 1. 认证模块 (Authentication)

### 1.1 用户注册

**接口**: `POST /api/auth/signup`

**描述**: 新用户注册

**请求头**:
```
Content-Type: application/json
```

**请求参数**:
```json
{
  "username": "student101",
  "password": "123456",
  "role": "student"
}
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| username | string | 是 | 用户名（学号或工号） |
| password | string | 是 | 密码 |
| role | string | 是 | 角色（teacher/student） |

**响应示例**:
```json
{
  "success": true,
  "data": {
    "id": "uuid-xxx",
    "username": "student101",
    "role": "student",
    "created_at": "2025-12-02T10:30:00Z"
  },
  "message": "注册成功"
}
```

---

### 1.2 用户登录

**接口**: `POST /api/auth/login`

**描述**: 用户登录获取访问令牌

**请求参数**:
```json
{
  "username": "student1",
  "password": "123456"
}
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| username | string | 是 | 用户名 |
| password | string | 是 | 密码 |

**响应示例**:
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "Bearer",
    "user": {
      "id": "uuid-xxx",
      "username": "student1",
      "role": "student"
    }
  },
  "message": "登录成功"
}
```

---

### 1.3 用户登出

**接口**: `POST /api/auth/logout`

**描述**: 用户登出

**请求头**:
```
Authorization: Bearer {access_token}
```

**响应示例**:
```json
{
  "success": true,
  "message": "登出成功"
}
```

---

### 1.4 验证Token

**接口**: `GET /api/auth/verify`

**描述**: 验证访问令牌是否有效

**请求头**:
```
Authorization: Bearer {access_token}
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "id": "uuid-xxx",
    "username": "student1",
    "role": "student"
  }
}
```

---

## 2. 用户模块 (Users)

### 2.1 获取当前用户信息

**接口**: `GET /api/users/me`

**描述**: 获取当前登录用户的详细信息

**请求头**:
```
Authorization: Bearer {access_token}
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "id": "uuid-xxx",
    "username": "student1",
    "role": "student",
    "created_at": "2025-12-02T10:00:00Z"
  }
}
```

---

### 2.2 修改密码

**接口**: `PUT /api/users/password`

**描述**: 修改当前用户密码

**请求头**:
```
Authorization: Bearer {access_token}
```

**请求参数**:
```json
{
  "old_password": "123456",
  "new_password": "new_password"
}
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| old_password | string | 是 | 旧密码 |
| new_password | string | 是 | 新密码 |

**响应示例**:
```json
{
  "success": true,
  "message": "密码修改成功"
}
```

---

## 3. 教师模块 (Teachers)

### 3.1 获取教师列表

**接口**: `GET /api/teachers`

**描述**: 获取所有教师信息（支持分页和搜索）

**请求头**:
```
Authorization: Bearer {access_token}
```

**查询参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page | number | 否 | 页码（默认1） |
| page_size | number | 否 | 每页数量（默认20） |
| search | string | 否 | 搜索关键词（姓名、工号） |

**响应示例**:
```json
{
  "success": true,
  "data": {
    "teachers": [
      {
        "id": "uuid-xxx",
        "teacher_no": "teacher1",
        "name": "教师1",
        "gender": "女",
        "email": "teacher1@example.com",
        "created_at": "2025-12-02T10:00:00Z"
      }
    ],
    "total": 5,
    "page": 1,
    "page_size": 20
  }
}
```

---

### 3.2 获取单个教师信息

**接口**: `GET /api/teachers/{teacherId}`

**描述**: 根据ID获取教师详细信息

**请求头**:
```
Authorization: Bearer {access_token}
```

**路径参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| teacherId | string | 是 | 教师ID |

**响应示例**:
```json
{
  "success": true,
  "data": {
    "id": "uuid-xxx",
    "teacher_no": "teacher1",
    "name": "教师1",
    "gender": "女",
    "email": "teacher1@example.com",
    "created_at": "2025-12-02T10:00:00Z"
  }
}
```

---

### 3.3 创建教师

**接口**: `POST /api/teachers`

**描述**: 创建新教师（需管理员权限）

**请求头**:
```
Authorization: Bearer {access_token}
```

**请求参数**:
```json
{
  "teacher_no": "teacher6",
  "name": "教师6",
  "gender": "男",
  "email": "teacher6@example.com",
  "password": "123456"
}
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| teacher_no | string | 是 | 工号（唯一） |
| name | string | 是 | 姓名 |
| gender | string | 是 | 性别（男/女） |
| email | string | 是 | 邮箱 |
| password | string | 是 | 初始密码 |

**响应示例**:
```json
{
  "success": true,
  "data": {
    "id": "uuid-xxx",
    "teacher_no": "teacher6",
    "name": "教师6",
    "gender": "男",
    "email": "teacher6@example.com",
    "created_at": "2025-12-02T10:30:00Z"
  },
  "message": "教师创建成功"
}
```

---

### 3.4 更新教师信息

**接口**: `PUT /api/teachers/{teacherId}`

**描述**: 更新教师信息

**请求头**:
```
Authorization: Bearer {access_token}
```

**路径参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| teacherId | string | 是 | 教师ID |

**请求参数**:
```json
{
  "name": "教师6（新）",
  "gender": "男",
  "email": "teacher6_new@example.com"
}
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "id": "uuid-xxx",
    "teacher_no": "teacher6",
    "name": "教师6（新）",
    "gender": "男",
    "email": "teacher6_new@example.com",
    "created_at": "2025-12-02T10:30:00Z"
  },
  "message": "教师信息更新成功"
}
```

---

### 3.5 删除教师

**接口**: `DELETE /api/teachers/{teacherId}`

**描述**: 删除教师（需管理员权限）

**请求头**:
```
Authorization: Bearer {access_token}
```

**路径参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| teacherId | string | 是 | 教师ID |

**响应示例**:
```json
{
  "success": true,
  "message": "教师删除成功"
}
```

---

## 4. 学生模块 (Students)

### 4.1 获取学生列表

**接口**: `GET /api/students`

**描述**: 获取所有学生信息（支持分页、搜索、班级筛选）

**请求头**:
```
Authorization: Bearer {access_token}
```

**查询参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page | number | 否 | 页码（默认1） |
| page_size | number | 否 | 每页数量（默认20） |
| search | string | 否 | 搜索关键词（姓名、学号） |
| class | string | 否 | 班级筛选 |

**响应示例**:
```json
{
  "success": true,
  "data": {
    "students": [
      {
        "id": "uuid-xxx",
        "student_no": "student1",
        "name": "学生1",
        "class": "一班",
        "gender": "女",
        "created_at": "2025-12-02T10:00:00Z"
      }
    ],
    "total": 100,
    "page": 1,
    "page_size": 20
  }
}
```

---

### 4.2 获取单个学生信息

**接口**: `GET /api/students/{studentId}`

**描述**: 根据ID获取学生详细信息

**请求头**:
```
Authorization: Bearer {access_token}
```

**路径参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| studentId | string | 是 | 学生ID |

**响应示例**:
```json
{
  "success": true,
  "data": {
    "id": "uuid-xxx",
    "student_no": "student1",
    "name": "学生1",
    "class": "一班",
    "gender": "女",
    "created_at": "2025-12-02T10:00:00Z"
  }
}
```

---

### 4.3 根据用户ID获取学生信息

**接口**: `GET /api/students/user/{userId}`

**描述**: 根据用户ID获取学生详细信息

**请求头**:
```
Authorization: Bearer {access_token}
```

**路径参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| userId | string | 是 | 用户ID |

**响应示例**:
```json
{
  "success": true,
  "data": {
    "id": "uuid-xxx",
    "student_no": "student1",
    "name": "学生1",
    "class": "一班",
    "gender": "女",
    "created_at": "2025-12-02T10:00:00Z"
  }
}
```

---

### 4.4 创建学生

**接口**: `POST /api/students`

**描述**: 创建新学生

**请求头**:
```
Authorization: Bearer {access_token}
```

**请求参数**:
```json
{
  "student_no": "student101",
  "name": "学生101",
  "class": "一班",
  "gender": "男",
  "password": "123456"
}
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| student_no | string | 是 | 学号（唯一） |
| name | string | 是 | 姓名 |
| class | string | 是 | 班级 |
| gender | string | 是 | 性别（男/女） |
| password | string | 是 | 初始密码 |

**响应示例**:
```json
{
  "success": true,
  "data": {
    "id": "uuid-xxx",
    "student_no": "student101",
    "name": "学生101",
    "class": "一班",
    "gender": "男",
    "created_at": "2025-12-02T10:30:00Z"
  },
  "message": "学生创建成功"
}
```

---

### 4.5 更新学生信息

**接口**: `PUT /api/students/{studentId}`

**描述**: 更新学生信息

**请求头**:
```
Authorization: Bearer {access_token}
```

**路径参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| studentId | string | 是 | 学生ID |

**请求参数**:
```json
{
  "name": "学生101（新）",
  "class": "二班",
  "gender": "男"
}
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "id": "uuid-xxx",
    "student_no": "student101",
    "name": "学生101（新）",
    "class": "二班",
    "gender": "男",
    "created_at": "2025-12-02T10:30:00Z"
  },
  "message": "学生信息更新成功"
}
```

---

### 4.6 删除学生

**接口**: `DELETE /api/students/{studentId}`

**描述**: 删除学生

**请求头**:
```
Authorization: Bearer {access_token}
```

**路径参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| studentId | string | 是 | 学生ID |

**响应示例**:
```json
{
  "success": true,
  "message": "学生删除成功"
}
```

---

## 5. 课程模块 (Courses)

### 5.1 获取课程列表

**接口**: `GET /api/courses`

**描述**: 获取所有课程（支持分页和搜索）

**请求头**:
```
Authorization: Bearer {access_token}
```

**查询参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page | number | 否 | 页码（默认1） |
| page_size | number | 否 | 每页数量（默认20） |
| search | string | 否 | 搜索关键词（课程名称） |

**响应示例**:
```json
{
  "success": true,
  "data": {
    "courses": [
      {
        "id": "uuid-xxx",
        "name": "React开发入门",
        "description": "学习React基础知识",
        "teacher_id": "uuid-teacher",
        "student_count": 25,
        "created_at": "2025-12-02T10:00:00Z"
      }
    ],
    "total": 10,
    "page": 1,
    "page_size": 20
  }
}
```

---

### 5.2 获取单个课程信息

**接口**: `GET /api/courses/{courseId}`

**描述**: 根据ID获取课程详细信息

**请求头**:
```
Authorization: Bearer {access_token}
```

**路径参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| courseId | string | 是 | 课程ID |

**响应示例**:
```json
{
  "success": true,
  "data": {
    "id": "uuid-xxx",
    "name": "React开发入门",
    "description": "学习React基础知识",
    "teacher_id": "uuid-teacher",
    "student_count": 25,
    "created_at": "2025-12-02T10:00:00Z"
  }
}
```

---

### 5.3 创建课程

**接口**: `POST /api/courses`

**描述**: 创建新课程（需教师权限）

**请求头**:
```
Authorization: Bearer {access_token}
```

**请求参数**:
```json
{
  "name": "React开发入门",
  "description": "学习React基础知识"
}
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| name | string | 是 | 课程名称 |
| description | string | 是 | 课程描述 |

**响应示例**:
```json
{
  "success": true,
  "data": {
    "id": "uuid-xxx",
    "name": "React开发入门",
    "description": "学习React基础知识",
    "teacher_id": "uuid-teacher",
    "student_count": 0,
    "created_at": "2025-12-02T10:30:00Z"
  },
  "message": "课程创建成功"
}
```

---

### 5.4 更新课程信息

**接口**: `PUT /api/courses/{courseId}`

**描述**: 更新课程信息（需课程教师权限）

**请求头**:
```
Authorization: Bearer {access_token}
```

**路径参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| courseId | string | 是 | 课程ID |

**请求参数**:
```json
{
  "name": "React开发进阶",
  "description": "深入学习React高级特性"
}
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "id": "uuid-xxx",
    "name": "React开发进阶",
    "description": "深入学习React高级特性",
    "teacher_id": "uuid-teacher",
    "student_count": 25,
    "created_at": "2025-12-02T10:00:00Z"
  },
  "message": "课程更新成功"
}
```

---

### 5.5 删除课程

**接口**: `DELETE /api/courses/{courseId}`

**描述**: 删除课程（需课程教师权限）

**请求头**:
```
Authorization: Bearer {access_token}
```

**路径参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| courseId | string | 是 | 课程ID |

**响应示例**:
```json
{
  "success": true,
  "message": "课程删除成功"
}
```

---

### 5.6 获取教师的课程列表

**接口**: `GET /api/teachers/{teacherId}/courses`

**描述**: 获取指定教师的所有课程

**请求头**:
```
Authorization: Bearer {access_token}
```

**路径参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| teacherId | string | 是 | 教师ID |

**响应示例**:
```json
{
  "success": true,
  "data": {
    "courses": [
      {
        "id": "uuid-xxx",
        "name": "React开发入门",
        "description": "学习React基础知识",
        "teacher_id": "uuid-teacher",
        "student_count": 25,
        "created_at": "2025-12-02T10:00:00Z"
      }
    ],
    "total": 5
  }
}
```

---

### 5.7 获取学生的课程列表

**接口**: `GET /api/students/{studentId}/courses`

**描述**: 获取指定学生已选的所有课程

**请求头**:
```
Authorization: Bearer {access_token}
```

**路径参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| studentId | string | 是 | 学生ID |

**响应示例**:
```json
{
  "success": true,
  "data": {
    "courses": [
      {
        "id": "uuid-xxx",
        "name": "React开发入门",
        "description": "学习React基础知识",
        "teacher_id": "uuid-teacher",
        "teacher_name": "教师1",
        "student_count": 25,
        "enrolled_at": "2025-12-02T10:30:00Z",
        "created_at": "2025-12-02T10:00:00Z"
      }
    ],
    "total": 3
  }
}
```

---

## 6. 课程学员模块 (Course Enrollment)

### 6.1 获取课程学员列表

**接口**: `GET /api/courses/{courseId}/students`

**描述**: 获取指定课程的所有学员

**请求头**:
```
Authorization: Bearer {access_token}
```

**路径参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| courseId | string | 是 | 课程ID |

**查询参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page | number | 否 | 页码（默认1） |
| page_size | number | 否 | 每页数量（默认20） |
| search | string | 否 | 搜索关键词（姓名、学号） |

**响应示例**:
```json
{
  "success": true,
  "data": {
    "students": [
      {
        "id": "uuid-xxx",
        "student_no": "student1",
        "name": "学生1",
        "class": "一班",
        "gender": "女",
        "enrolled_at": "2025-12-02T10:30:00Z"
      }
    ],
    "total": 25,
    "page": 1,
    "page_size": 20
  }
}
```

---

### 6.2 添加课程学员

**接口**: `POST /api/courses/{courseId}/students`

**描述**: 向课程添加学员（需课程教师权限）

**请求头**:
```
Authorization: Bearer {access_token}
```

**路径参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| courseId | string | 是 | 课程ID |

**请求参数**:
```json
{
  "student_id": "uuid-student"
}
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| student_id | string | 是 | 学生ID |

**响应示例**:
```json
{
  "success": true,
  "message": "学员添加成功"
}
```

---

### 6.3 批量添加课程学员

**接口**: `POST /api/courses/{courseId}/students/batch`

**描述**: 批量向课程添加学员（需课程教师权限）

**请求头**:
```
Authorization: Bearer {access_token}
```

**路径参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| courseId | string | 是 | 课程ID |

**请求参数**:
```json
{
  "student_ids": ["uuid-1", "uuid-2", "uuid-3"]
}
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| student_ids | string[] | 是 | 学生ID数组 |

**响应示例**:
```json
{
  "success": true,
  "data": {
    "added_count": 3,
    "failed_count": 0
  },
  "message": "成功添加3名学员"
}
```

---

### 6.4 移除课程学员

**接口**: `DELETE /api/courses/{courseId}/students/{studentId}`

**描述**: 从课程移除学员（需课程教师权限）

**请求头**:
```
Authorization: Bearer {access_token}
```

**路径参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| courseId | string | 是 | 课程ID |
| studentId | string | 是 | 学生ID |

**响应示例**:
```json
{
  "success": true,
  "message": "学员移除成功"
}
```

---

## 7. 作业模块 (Homeworks)

### 7.1 获取课程作业列表

**接口**: `GET /api/courses/{courseId}/homeworks`

**描述**: 获取指定课程的所有作业

**请求头**:
```
Authorization: Bearer {access_token}
```

**路径参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| courseId | string | 是 | 课程ID |

**响应示例**:
```json
{
  "success": true,
  "data": {
    "homeworks": [
      {
        "id": "uuid-xxx",
        "course_id": "uuid-course",
        "title": "React基础练习",
        "description": "完成React组件开发",
        "deadline": "2025-12-10T23:59:59Z",
        "created_at": "2025-12-02T10:00:00Z",
        "attachment": {
          "name": "作业要求.pdf",
          "type": "application/pdf",
          "size": 102400,
          "content": "base64..."
        },
        "grading_criteria": {
          "type": "text",
          "content": "按功能完整性、代码质量评分"
        }
      }
    ],
    "total": 5
  }
}
```

---

### 7.2 获取单个作业信息

**接口**: `GET /api/homeworks/{homeworkId}`

**描述**: 根据ID获取作业详细信息

**请求头**:
```
Authorization: Bearer {access_token}
```

**路径参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| homeworkId | string | 是 | 作业ID |

**响应示例**:
```json
{
  "success": true,
  "data": {
    "id": "uuid-xxx",
    "course_id": "uuid-course",
    "title": "React基础练习",
    "description": "完成React组件开发",
    "deadline": "2025-12-10T23:59:59Z",
    "created_at": "2025-12-02T10:00:00Z",
    "attachment": {
      "name": "作业要求.pdf",
      "type": "application/pdf",
      "size": 102400,
      "content": "base64..."
    }
  }
}
```

---

### 7.3 创建作业

**接口**: `POST /api/courses/{courseId}/homeworks`

**描述**: 创建新作业（需课程教师权限）

**请求头**:
```
Authorization: Bearer {access_token}
Content-Type: application/json
```

**路径参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| courseId | string | 是 | 课程ID |

**请求参数**:
```json
{
  "title": "React基础练习",
  "description": "完成React组件开发",
  "deadline": "2025-12-10T23:59:59Z",
  "attachment": {
    "name": "作业要求.pdf",
    "type": "application/pdf",
    "size": 102400,
    "content": "base64..."
  },
  "grading_criteria": {
    "type": "text",
    "content": "按功能完整性、代码质量评分"
  }
}
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| title | string | 是 | 作业标题 |
| description | string | 是 | 作业描述 |
| deadline | string | 是 | 截止时间（ISO 8601格式） |
| attachment | object | 否 | 附件 |
| grading_criteria | object | 否 | 批改标准 |

**响应示例**:
```json
{
  "success": true,
  "data": {
    "id": "uuid-xxx",
    "course_id": "uuid-course",
    "title": "React基础练习",
    "description": "完成React组件开发",
    "deadline": "2025-12-10T23:59:59Z",
    "created_at": "2025-12-02T10:30:00Z"
  },
  "message": "作业创建成功"
}
```

---

### 7.4 更新作业

**接口**: `PUT /api/homeworks/{homeworkId}`

**描述**: 更新作业信息（需课程教师权限）

**请求头**:
```
Authorization: Bearer {access_token}
```

**路径参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| homeworkId | string | 是 | 作业ID |

**请求参数**:
```json
{
  "title": "React进阶练习",
  "description": "完成React高级组件开发",
  "deadline": "2025-12-15T23:59:59Z"
}
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "id": "uuid-xxx",
    "course_id": "uuid-course",
    "title": "React进阶练习",
    "description": "完成React高级组件开发",
    "deadline": "2025-12-15T23:59:59Z",
    "created_at": "2025-12-02T10:00:00Z"
  },
  "message": "作业更新成功"
}
```

---

### 7.5 删除作业

**接口**: `DELETE /api/homeworks/{homeworkId}`

**描述**: 删除作业（需课程教师权限）

**请求头**:
```
Authorization: Bearer {access_token}
```

**路径参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| homeworkId | string | 是 | 作业ID |

**响应示例**:
```json
{
  "success": true,
  "message": "作业删除成功"
}
```

---

## 8. 作业提交模块 (Homework Submissions)

### 8.1 获取作业提交列表

**接口**: `GET /api/homeworks/{homeworkId}/submissions`

**描述**: 获取指定作业的所有提交（教师可查看全部，学生只能查看自己的）

**请求头**:
```
Authorization: Bearer {access_token}
```

**路径参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| homeworkId | string | 是 | 作业ID |

**响应示例**:
```json
{
  "success": true,
  "data": {
    "submissions": [
      {
        "id": "uuid-xxx",
        "homework_id": "uuid-homework",
        "student_id": "uuid-student",
        "student_name": "学生1",
        "student_no": "student1",
        "content": "作业内容...",
        "attachments": [
          {
            "name": "作业.zip",
            "type": "application/zip",
            "size": 204800,
            "content": "base64..."
          }
        ],
        "score": 95,
        "feedback": "完成得很好",
        "submitted_at": "2025-12-05T15:30:00Z",
        "graded_at": "2025-12-06T10:00:00Z"
      }
    ],
    "total": 20
  }
}
```

---

### 8.2 获取单个提交详情

**接口**: `GET /api/submissions/{submissionId}`

**描述**: 根据ID获取提交详细信息

**请求头**:
```
Authorization: Bearer {access_token}
```

**路径参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| submissionId | string | 是 | 提交ID |

**响应示例**:
```json
{
  "success": true,
  "data": {
    "id": "uuid-xxx",
    "homework_id": "uuid-homework",
    "student_id": "uuid-student",
    "content": "作业内容...",
    "attachments": [
      {
        "name": "作业.zip",
        "type": "application/zip",
        "size": 204800,
        "content": "base64..."
      }
    ],
    "score": 95,
    "feedback": "完成得很好",
    "submitted_at": "2025-12-05T15:30:00Z",
    "graded_at": "2025-12-06T10:00:00Z"
  }
}
```

---

### 8.3 提交作业

**接口**: `POST /api/homeworks/{homeworkId}/submissions`

**描述**: 学生提交作业

**请求头**:
```
Authorization: Bearer {access_token}
Content-Type: application/json
```

**路径参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| homeworkId | string | 是 | 作业ID |

**请求参数**:
```json
{
  "content": "作业内容...",
  "attachments": [
    {
      "name": "作业.zip",
      "type": "application/zip",
      "size": 204800,
      "content": "base64..."
    }
  ]
}
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| content | string | 是 | 作业文本内容 |
| attachments | array | 否 | 附件数组 |

**响应示例**:
```json
{
  "success": true,
  "data": {
    "id": "uuid-xxx",
    "homework_id": "uuid-homework",
    "student_id": "uuid-student",
    "content": "作业内容...",
    "submitted_at": "2025-12-05T15:30:00Z"
  },
  "message": "作业提交成功"
}
```

---

### 8.4 更新作业提交

**接口**: `PUT /api/submissions/{submissionId}`

**描述**: 更新作业提交（学生只能在批改前修改）

**请求头**:
```
Authorization: Bearer {access_token}
```

**路径参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| submissionId | string | 是 | 提交ID |

**请求参数**:
```json
{
  "content": "修改后的作业内容...",
  "attachments": [
    {
      "name": "作业_v2.zip",
      "type": "application/zip",
      "size": 204800,
      "content": "base64..."
    }
  ]
}
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "id": "uuid-xxx",
    "homework_id": "uuid-homework",
    "student_id": "uuid-student",
    "content": "修改后的作业内容...",
    "submitted_at": "2025-12-05T16:00:00Z"
  },
  "message": "作业更新成功"
}
```

---

### 8.5 批改作业

**接口**: `POST /api/submissions/{submissionId}/grade`

**描述**: 教师批改作业

**请求头**:
```
Authorization: Bearer {access_token}
```

**路径参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| submissionId | string | 是 | 提交ID |

**请求参数**:
```json
{
  "score": 95,
  "feedback": "完成得很好，继续加油！"
}
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| score | number | 是 | 分数（0-100） |
| feedback | string | 否 | 批改反馈 |

**响应示例**:
```json
{
  "success": true,
  "data": {
    "id": "uuid-xxx",
    "score": 95,
    "feedback": "完成得很好，继续加油！",
    "graded_at": "2025-12-06T10:00:00Z"
  },
  "message": "批改成功"
}
```

---

### 8.6 删除作业提交

**接口**: `DELETE /api/submissions/{submissionId}`

**描述**: 删除作业提交（学生只能删除未批改的提交）

**请求头**:
```
Authorization: Bearer {access_token}
```

**路径参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| submissionId | string | 是 | 提交ID |

**响应示例**:
```json
{
  "success": true,
  "message": "提交删除成功"
}
```

---

### 8.7 获取学生的所有作业提交

**接口**: `GET /api/students/{studentId}/submissions`

**描述**: 获取指定学生的所有作业提交

**请求头**:
```
Authorization: Bearer {access_token}
```

**路径参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| studentId | string | 是 | 学生ID |

**响应示例**:
```json
{
  "success": true,
  "data": {
    "submissions": [
      {
        "id": "uuid-xxx",
        "homework_id": "uuid-homework",
        "homework_title": "React基础练习",
        "course_name": "React开发入门",
        "content": "作业内容...",
        "score": 95,
        "feedback": "完成得很好",
        "submitted_at": "2025-12-05T15:30:00Z",
        "graded_at": "2025-12-06T10:00:00Z"
      }
    ],
    "total": 10
  }
}
```

---

## 9. 课程资源模块 - 文件夹 (Course Folders)

### 9.1 获取课程文件夹列表

**接口**: `GET /api/courses/{courseId}/folders`

**描述**: 获取指定课程的所有文件夹

**请求头**:
```
Authorization: Bearer {access_token}
```

**路径参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| courseId | string | 是 | 课程ID |

**响应示例**:
```json
{
  "success": true,
  "data": {
    "folders": [
      {
        "id": "uuid-xxx",
        "course_id": "uuid-course",
        "name": "课件PPT",
        "created_at": "2025-12-02T10:00:00Z"
      },
      {
        "id": "uuid-yyy",
        "course_id": "uuid-course",
        "name": "学习资料",
        "created_at": "2025-12-02T11:00:00Z"
      }
    ],
    "total": 2
  }
}
```

---

### 9.2 获取单个文件夹信息

**接口**: `GET /api/folders/{folderId}`

**描述**: 根据ID获取文件夹详细信息

**请求头**:
```
Authorization: Bearer {access_token}
```

**路径参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| folderId | string | 是 | 文件夹ID |

**响应示例**:
```json
{
  "success": true,
  "data": {
    "id": "uuid-xxx",
    "course_id": "uuid-course",
    "name": "课件PPT",
    "created_at": "2025-12-02T10:00:00Z"
  }
}
```

---

### 9.3 创建文件夹

**接口**: `POST /api/courses/{courseId}/folders`

**描述**: 创建新文件夹（需课程教师权限）

**请求头**:
```
Authorization: Bearer {access_token}
```

**路径参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| courseId | string | 是 | 课程ID |

**请求参数**:
```json
{
  "name": "课件PPT"
}
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| name | string | 是 | 文件夹名称 |

**响应示例**:
```json
{
  "success": true,
  "data": {
    "id": "uuid-xxx",
    "course_id": "uuid-course",
    "name": "课件PPT",
    "created_at": "2025-12-02T10:30:00Z"
  },
  "message": "文件夹创建成功"
}
```

---

### 9.4 更新文件夹

**接口**: `PUT /api/folders/{folderId}`

**描述**: 更新文件夹信息（需课程教师权限）

**请求头**:
```
Authorization: Bearer {access_token}
```

**路径参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| folderId | string | 是 | 文件夹ID |

**请求参数**:
```json
{
  "name": "课件PPT（新）"
}
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "id": "uuid-xxx",
    "course_id": "uuid-course",
    "name": "课件PPT（新）",
    "created_at": "2025-12-02T10:00:00Z"
  },
  "message": "文件夹更新成功"
}
```

---

### 9.5 删除文件夹

**接口**: `DELETE /api/folders/{folderId}`

**描述**: 删除文件夹及其所有文件（需课程教师权限）

**请求头**:
```
Authorization: Bearer {access_token}
```

**路径参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| folderId | string | 是 | 文件夹ID |

**响应示例**:
```json
{
  "success": true,
  "message": "文件夹删除成功"
}
```

---

## 10. 课程资源模块 - 文件 (Course Files)

### 10.1 获取文件夹的文件列表

**接口**: `GET /api/folders/{folderId}/files`

**描述**: 获取指定文件夹的所有文件

**请求头**:
```
Authorization: Bearer {access_token}
```

**路径参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| folderId | string | 是 | 文件夹ID |

**响应示例**:
```json
{
  "success": true,
  "data": {
    "files": [
      {
        "id": "uuid-xxx",
        "folder_id": "uuid-folder",
        "course_id": "uuid-course",
        "name": "第一章.pptx",
        "size": 2048000,
        "type": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        "content": "base64...",
        "created_at": "2025-12-02T10:00:00Z"
      }
    ],
    "total": 5
  }
}
```

---

### 10.2 获取单个文件信息

**接口**: `GET /api/files/{fileId}`

**描述**: 根据ID获取文件详细信息

**请求头**:
```
Authorization: Bearer {access_token}
```

**路径参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| fileId | string | 是 | 文件ID |

**响应示例**:
```json
{
  "success": true,
  "data": {
    "id": "uuid-xxx",
    "folder_id": "uuid-folder",
    "course_id": "uuid-course",
    "name": "第一章.pptx",
    "size": 2048000,
    "type": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    "content": "base64...",
    "created_at": "2025-12-02T10:00:00Z"
  }
}
```

---

### 10.3 上传文件

**接口**: `POST /api/folders/{folderId}/files`

**描述**: 上传文件到文件夹（需课程教师权限）

**请求头**:
```
Authorization: Bearer {access_token}
Content-Type: application/json
```

**路径参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| folderId | string | 是 | 文件夹ID |

**请求参数**:
```json
{
  "name": "第一章.pptx",
  "size": 2048000,
  "type": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
  "content": "base64..."
}
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| name | string | 是 | 文件名 |
| size | number | 是 | 文件大小（字节） |
| type | string | 是 | MIME类型 |
| content | string | 是 | 文件内容（base64编码） |

**响应示例**:
```json
{
  "success": true,
  "data": {
    "id": "uuid-xxx",
    "folder_id": "uuid-folder",
    "course_id": "uuid-course",
    "name": "第一章.pptx",
    "size": 2048000,
    "type": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    "created_at": "2025-12-02T10:30:00Z"
  },
  "message": "文件上传成功"
}
```

---

### 10.4 更新文件

**接口**: `PUT /api/files/{fileId}`

**描述**: 更新文件（需课程教师权限）

**请求头**:
```
Authorization: Bearer {access_token}
```

**路径参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| fileId | string | 是 | 文件ID |

**请求参数**:
```json
{
  "name": "第一章（修订版）.pptx",
  "content": "base64..."
}
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "id": "uuid-xxx",
    "folder_id": "uuid-folder",
    "course_id": "uuid-course",
    "name": "第一章（修订版）.pptx",
    "size": 2048000,
    "type": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    "created_at": "2025-12-02T10:00:00Z"
  },
  "message": "文件更新成功"
}
```

---

### 10.5 删除文件

**接口**: `DELETE /api/files/{fileId}`

**描述**: 删除文件（需课程教师权限）

**请求头**:
```
Authorization: Bearer {access_token}
```

**路径参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| fileId | string | 是 | 文件ID |

**响应示例**:
```json
{
  "success": true,
  "message": "文件删除成功"
}
```

---

### 10.6 下载文件

**接口**: `GET /api/files/{fileId}/download`

**描述**: 下载文件（返回文件内容）

**请求头**:
```
Authorization: Bearer {access_token}
```

**路径参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| fileId | string | 是 | 文件ID |

**响应**: 返回文件的二进制内容，Content-Type 为文件的 MIME 类型

---

## 错误码说明

| 错误码 | 说明 |
|--------|------|
| AUTH_001 | 用户名或密码错误 |
| AUTH_002 | Token无效或已过期 |
| AUTH_003 | 用户名已存在 |
| AUTH_004 | 无权限访问 |
| VALID_001 | 请求参数缺失 |
| VALID_002 | 请求参数格式错误 |
| VALID_003 | 请求参数值无效 |
| RES_001 | 资源不存在 |
| RES_002 | 资源已存在 |
| RES_003 | 资源冲突 |
| SYS_001 | 服务器内部错误 |
| SYS_002 | 数据库操作失败 |

---

## 附录

### 数据类型定义

#### User（用户）
```typescript
interface User {
  id: string;
  username: string;
  password: string;
  role: 'teacher' | 'student';
  created_at: string;
}
```

#### Teacher（教师）
```typescript
interface Teacher {
  id: string;
  teacher_no: string;
  name: string;
  gender: '男' | '女';
  email: string;
  created_at: string;
}
```

#### Student（学生）
```typescript
interface Student {
  id: string;
  student_no: string;
  name: string;
  class: string;
  gender: '男' | '女';
  created_at: string;
}
```

#### Course（课程）
```typescript
interface Course {
  id: string;
  name: string;
  description: string;
  teacher_id: string;
  student_count: number;
  created_at: string;
}
```

#### Homework（作业）
```typescript
interface Homework {
  id: string;
  course_id: string;
  title: string;
  description: string;
  deadline: string;
  created_at: string;
  attachment?: {
    name: string;
    type: string;
    size: number;
    content: string;
  };
  grading_criteria?: {
    type: 'text' | 'file';
    content: string;
    file_name?: string;
    file_size?: number;
  };
}
```

#### HomeworkSubmission（作业提交）
```typescript
interface HomeworkSubmission {
  id: string;
  homework_id: string;
  student_id: string;
  content: string;
  attachments?: Array<{
    name: string;
    type: string;
    size: number;
    content: string;
  }>;
  score?: number;
  feedback?: string;
  submitted_at: string;
  graded_at?: string;
}
```

#### CourseFolder（课程文件夹）
```typescript
interface CourseFolder {
  id: string;
  course_id: string;
  name: string;
  created_at: string;
}
```

#### CourseFile（课程文件）
```typescript
interface CourseFile {
  id: string;
  folder_id: string;
  course_id: string;
  name: string;
  size: number;
  type: string;
  content: string;
  created_at: string;
}
```
