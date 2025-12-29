# 前端改动点清单

本文档列出将前端从 localStorage 迁移到 API 调用需要修改的文件和具体改动。

## 已完成的改动

### 1. 新增文件

| 文件 | 说明 |
|-----|-----|
| `src/utils/api-client.ts` | API 客户端，封装所有后端接口调用 |

## 待修改的文件

### 2. App.tsx

**改动说明**: 登录/登出逻辑改为调用 API

**改动点**:

```typescript
// 原代码 (localStorage)
import { login as localLogin } from './utils/localStorage-service'

const handleLogin = async (username: string, password: string) => {
  const result = await localLogin(username, password)
  // ...
}

// 新代码 (API)
import api from './utils/api-client'

const handleLogin = async (username: string, password: string) => {
  const result = await api.login(username, password)
  if (result.success && result.data) {
    localStorage.setItem('access_token', result.data.access_token)
    localStorage.setItem('username', result.data.user.username)
    localStorage.setItem('user_id', result.data.user.id)
    localStorage.setItem('role', result.data.user.role)
    // ...
  }
}
```

### 3. src/utils/localStorage-service.ts

**改动说明**: 将所有函数改为调用 API（或直接删除，由组件直接调用 api-client）

**方案一：保留为适配层**

```typescript
import api from './api-client'

export async function login(username: string, password: string) {
  const result = await api.login(username, password)
  return result
}

export async function getStudentDetails(page: number, pageSize: number, q?: string, classFilter?: string) {
  const result = await api.getStudents(page, pageSize, q, classFilter)
  return result.success ? result.data : { students: [], total: 0 }
}
// ... 其他函数类似
```

**方案二：删除文件，直接使用 api-client**

### 4. 教师端组件

#### 4.1 components/teacher/course-management.tsx

**改动点**:
- `getCourses()` → `api.getCourses()`
- `createCourse()` → `api.createCourse()`
- `updateCourse()` → `api.updateCourse()`
- `deleteCourse()` → `api.deleteCourse()`

#### 4.2 components/teacher/student-list.tsx

**改动点**:
- `getStudentDetails()` → `api.getStudents()`
- `getClassList()` → `api.getClassList()`

#### 4.3 components/teacher/course-students.tsx

**改动点**:
- `getCourseStudents()` → `api.getCourseStudents()`
- `addStudentToCourse()` → `api.addStudentToCourse()`
- `removeStudentFromCourse()` → `api.removeStudentFromCourse()`

#### 4.4 components/teacher/homework-management.tsx

**改动点**:
- `getHomeworks()` → `api.getCourseHomeworks()`
- `createHomework()` → `api.createHomework()`
- `updateHomework()` → `api.updateHomework()`
- `deleteHomework()` → `api.deleteHomework()`

#### 4.5 components/teacher/homework-grading.tsx

**改动点**:
- `getHomeworkSubmissions()` → `api.getHomeworkSubmissions()`
- `gradeSubmission()` → `api.gradeSubmission()`

#### 4.6 components/teacher/course-resources.tsx

**改动点**:
- `getCourseResources()` → `api.getCourseResources()`
- `createFolder()` → `api.createFolder()`
- `deleteFolder()` → `api.deleteFolder()`
- `uploadFile()` → `api.uploadFile()`
- `deleteFile()` → `api.deleteFile()`
- `downloadFile()` → `api.getFileDownloadUrl()` + fetch

#### 4.7 components/teacher/ai-assistant.tsx

**改动点**:
- 模拟响应 → `api.chat()`

#### 4.8 components/teacher/ai-ppt-dialog.tsx

**改动点**:
- 模拟生成 → `api.generatePPT()`

#### 4.9 components/teacher/ai-writing-dialog.tsx

**改动点**:
- 模拟生成 → `api.generateContent()`
- 模拟二改 → `api.editContent()`

### 5. 学生端组件

#### 5.1 components/student/my-courses.tsx

**改动点**:
- `getStudentCourses()` → `api.getStudentCourses()`

#### 5.2 components/student/course-detail.tsx

**改动点**:
- `getStudentHomeworks()` → `api.getCourseHomeworks()` + 查询提交状态
- `getCourseResources()` → `api.getCourseResources()`

#### 5.3 components/student/homework-submit.tsx

**改动点**:
- `submitHomework()` → `api.submitHomework()`

#### 5.4 components/student/ai-assistant.tsx

**改动点**:
- 模拟响应 → `api.chat()`

---

## 改动模式示例

### 原代码模式 (localStorage)

```typescript
import { getCourses, createCourse } from '@/utils/localStorage-service'

const loadCourses = async () => {
  const result = await getCourses()
  setCourses(result.courses)
}

const handleCreate = async (data) => {
  await createCourse(data.name, data.description, teacherId)
  loadCourses()
}
```

### 新代码模式 (API)

```typescript
import api from '@/utils/api-client'

const loadCourses = async () => {
  const result = await api.getCourses()
  if (result.success && result.data) {
    setCourses(result.data.courses)
  } else {
    // 错误处理
    console.error(result.error)
  }
}

const handleCreate = async (data) => {
  const result = await api.createCourse(data)
  if (result.success) {
    loadCourses()
  } else {
    // 错误处理
    alert(result.error)
  }
}
```

---

## 环境变量配置

在前端项目根目录创建 `.env.local`：

```ini
VITE_API_URL=http://localhost:8080
```

---

## 注意事项

1. **错误处理**: API 调用需要检查 `result.success`，处理错误情况
2. **Loading 状态**: 建议添加 loading 状态，提升用户体验
3. **Token 过期**: api-client 已处理 401 错误，自动跳转登录页
4. **字段名差异**: 注意 `class` vs `class_name` 的转换（API 返回 `class`）

---

## 迁移优先级

建议按以下顺序迁移：

1. **高优先级**: 认证相关 (App.tsx)
2. **中优先级**: 教师端核心功能 (课程、作业、学员管理)
3. **低优先级**: AI 功能 (目前仍是 Mock)
