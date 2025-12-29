# API 验收测试用例

本文档提供每个 API 接口的 curl 测试命令。

## 前置步骤

首先获取 Token：

```bash
# 教师登录
TOKEN=$(curl -s -X POST http://localhost:8080/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "teacher1", "password": "123456"}' | jq -r '.data.access_token')

echo "Token: $TOKEN"
```

---

## 1. 认证模块

### 1.1 用户注册
```bash
curl -X POST http://localhost:8080/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"username": "newuser", "password": "123456", "role": "student"}'
```

### 1.2 用户登录
```bash
curl -X POST http://localhost:8080/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "teacher1", "password": "123456"}'
```

### 1.3 Token 验证
```bash
curl -X GET http://localhost:8080/api/auth/verify \
  -H "Authorization: Bearer $TOKEN"
```

### 1.4 用户登出
```bash
curl -X POST http://localhost:8080/api/auth/logout \
  -H "Authorization: Bearer $TOKEN"
```

---

## 2. 用户模块

### 2.1 获取当前用户
```bash
curl -X GET http://localhost:8080/api/users/me \
  -H "Authorization: Bearer $TOKEN"
```

### 2.2 修改密码
```bash
curl -X PUT http://localhost:8080/api/users/password \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"old_password": "123456", "new_password": "newpass123"}'
```

---

## 3. 教师模块

### 3.1 获取教师列表
```bash
curl -X GET "http://localhost:8080/api/teachers?page=1&page_size=10" \
  -H "Authorization: Bearer $TOKEN"
```

### 3.2 获取单个教师
```bash
# 先获取教师 ID
TEACHER_ID=$(curl -s -X GET "http://localhost:8080/api/teachers?page=1&page_size=1" \
  -H "Authorization: Bearer $TOKEN" | jq -r '.data.teachers[0].id')

curl -X GET "http://localhost:8080/api/teachers/$TEACHER_ID" \
  -H "Authorization: Bearer $TOKEN"
```

### 3.3 创建教师
```bash
curl -X POST http://localhost:8080/api/teachers \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"teacher_no": "teacher99", "name": "测试教师", "gender": "男", "email": "test@example.com", "password": "123456"}'
```

### 3.4 更新教师
```bash
curl -X PUT "http://localhost:8080/api/teachers/$TEACHER_ID" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"name": "更新后的名字"}'
```

### 3.5 获取教师课程
```bash
curl -X GET "http://localhost:8080/api/teachers/$TEACHER_ID/courses" \
  -H "Authorization: Bearer $TOKEN"
```

---

## 4. 学生模块

### 4.1 获取学生列表
```bash
curl -X GET "http://localhost:8080/api/students?page=1&page_size=10" \
  -H "Authorization: Bearer $TOKEN"
```

### 4.2 按班级筛选
```bash
curl -X GET "http://localhost:8080/api/students?page=1&page_size=10&class=一班" \
  -H "Authorization: Bearer $TOKEN"
```

### 4.3 获取班级列表
```bash
curl -X GET http://localhost:8080/api/students/classes \
  -H "Authorization: Bearer $TOKEN"
```

### 4.4 获取单个学生
```bash
STUDENT_ID=$(curl -s -X GET "http://localhost:8080/api/students?page=1&page_size=1" \
  -H "Authorization: Bearer $TOKEN" | jq -r '.data.students[0].id')

curl -X GET "http://localhost:8080/api/students/$STUDENT_ID" \
  -H "Authorization: Bearer $TOKEN"
```

### 4.5 创建学生
```bash
curl -X POST http://localhost:8080/api/students \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"student_no": "student999", "name": "测试学生", "class": "一班", "gender": "女", "password": "123456"}'
```

---

## 5. 课程模块

### 5.1 获取课程列表
```bash
curl -X GET "http://localhost:8080/api/courses?page=1&page_size=10" \
  -H "Authorization: Bearer $TOKEN"
```

### 5.2 创建课程
```bash
curl -X POST http://localhost:8080/api/courses \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"name": "Python编程", "description": "学习Python基础知识"}'
```

### 5.3 获取单个课程
```bash
COURSE_ID=$(curl -s -X GET "http://localhost:8080/api/courses?page=1&page_size=1" \
  -H "Authorization: Bearer $TOKEN" | jq -r '.data.courses[0].id')

curl -X GET "http://localhost:8080/api/courses/$COURSE_ID" \
  -H "Authorization: Bearer $TOKEN"
```

### 5.4 更新课程
```bash
curl -X PUT "http://localhost:8080/api/courses/$COURSE_ID" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"name": "Python高级编程"}'
```

---

## 6. 课程学员管理

### 6.1 获取课程学员
```bash
curl -X GET "http://localhost:8080/api/courses/$COURSE_ID/students" \
  -H "Authorization: Bearer $TOKEN"
```

### 6.2 添加学员
```bash
curl -X POST "http://localhost:8080/api/courses/$COURSE_ID/students" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d "{\"student_id\": \"$STUDENT_ID\"}"
```

### 6.3 批量添加学员
```bash
curl -X POST "http://localhost:8080/api/courses/$COURSE_ID/students/batch" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"student_ids": ["id1", "id2"]}'
```

### 6.4 移除学员
```bash
curl -X DELETE "http://localhost:8080/api/courses/$COURSE_ID/students/$STUDENT_ID" \
  -H "Authorization: Bearer $TOKEN"
```

---

## 7. 作业模块

### 7.1 获取课程作业
```bash
curl -X GET "http://localhost:8080/api/courses/$COURSE_ID/homeworks" \
  -H "Authorization: Bearer $TOKEN"
```

### 7.2 创建作业
```bash
curl -X POST "http://localhost:8080/api/courses/$COURSE_ID/homeworks" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"title": "第一次作业", "description": "完成练习题", "deadline": "2025-12-31T23:59:59Z"}'
```

### 7.3 获取单个作业
```bash
HOMEWORK_ID=$(curl -s -X GET "http://localhost:8080/api/courses/$COURSE_ID/homeworks" \
  -H "Authorization: Bearer $TOKEN" | jq -r '.data.homeworks[0].id')

curl -X GET "http://localhost:8080/api/homeworks/$HOMEWORK_ID" \
  -H "Authorization: Bearer $TOKEN"
```

### 7.4 更新作业
```bash
curl -X PUT "http://localhost:8080/api/homeworks/$HOMEWORK_ID" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"title": "更新后的作业标题"}'
```

---

## 8. 作业提交

### 8.1 获取提交列表
```bash
curl -X GET "http://localhost:8080/api/homeworks/$HOMEWORK_ID/submissions" \
  -H "Authorization: Bearer $TOKEN"
```

### 8.2 提交作业 (需要学生 Token)
```bash
# 先用学生账号登录获取 Token
STUDENT_TOKEN=$(curl -s -X POST http://localhost:8080/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "student1", "password": "123456"}' | jq -r '.data.access_token')

curl -X POST "http://localhost:8080/api/homeworks/$HOMEWORK_ID/submissions" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $STUDENT_TOKEN" \
  -d '{"content": "这是我的作业答案..."}'
```

### 8.3 批改作业
```bash
SUBMISSION_ID="提交ID"

curl -X POST "http://localhost:8080/api/submissions/$SUBMISSION_ID/grade" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"score": 95, "feedback": "完成得很好！"}'
```

---

## 9. 课程资源

### 9.1 获取文件夹列表
```bash
curl -X GET "http://localhost:8080/api/courses/$COURSE_ID/folders" \
  -H "Authorization: Bearer $TOKEN"
```

### 9.2 创建文件夹
```bash
curl -X POST "http://localhost:8080/api/courses/$COURSE_ID/folders" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"name": "课件资料"}'
```

### 9.3 获取课程资源（带文件）
```bash
curl -X GET "http://localhost:8080/api/courses/$COURSE_ID/resources" \
  -H "Authorization: Bearer $TOKEN"
```

### 9.4 上传文件
```bash
FOLDER_ID="文件夹ID"

curl -X POST "http://localhost:8080/api/folders/$FOLDER_ID/files" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"name": "test.txt", "size": 100, "type": "text/plain", "content": "SGVsbG8gV29ybGQ="}'
```

---

## 10. AI 模块

### 10.1 生成 PPT
```bash
curl -X POST http://localhost:8080/api/ai/ppt/generate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"title": "Python入门", "requirements": "适合初学者"}'
```

### 10.2 生成教学资源
```bash
curl -X POST http://localhost:8080/api/ai/content/generate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"title": "Python基础教案", "requirements": "包含代码示例"}'
```

### 10.3 AI 二改
```bash
curl -X POST http://localhost:8080/api/ai/content/edit \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"original_text": "这是原始文本", "action": "expand"}'
```

### 10.4 AI 聊天
```bash
curl -X POST http://localhost:8080/api/ai/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"message": "如何学好Python？"}'
```

---

## 11. 健康检查

```bash
curl http://localhost:8080/health
```

---

## HTTPie 替代命令

如果安装了 HTTPie，可以使用更简洁的命令：

```bash
# 登录
http POST localhost:8080/api/auth/login username=teacher1 password=123456

# 获取学生列表
http GET localhost:8080/api/students "Authorization: Bearer $TOKEN"

# 创建课程
http POST localhost:8080/api/courses name="Python" description="学习Python" "Authorization: Bearer $TOKEN"
```
