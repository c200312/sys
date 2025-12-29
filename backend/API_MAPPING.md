# 接口对照表

本文档列出所有 API 接口与后端实现文件、前端调用点的对应关系。

## 1. 认证模块 (Authentication)

| 接口 | 后端实现 | 前端调用 |
|-----|---------|---------|
| POST /api/auth/signup | routers/auth.py:signup | api-client.ts:signup |
| POST /api/auth/login | routers/auth.py:login | api-client.ts:login |
| POST /api/auth/logout | routers/auth.py:logout | api-client.ts:logout |
| GET /api/auth/verify | routers/auth.py:verify_token | api-client.ts:verifyToken |

**Service**: services/auth.py:AuthService

## 2. 用户模块 (Users)

| 接口 | 后端实现 | 前端调用 |
|-----|---------|---------|
| GET /api/users/me | routers/users.py:get_current_user | api-client.ts:getCurrentUser |
| PUT /api/users/password | routers/users.py:change_password | api-client.ts:changePassword |

**Service**: services/auth.py:AuthService

## 3. 教师模块 (Teachers)

| 接口 | 后端实现 | 前端调用 |
|-----|---------|---------|
| GET /api/teachers | routers/teachers.py:get_teachers | api-client.ts:getTeachers |
| GET /api/teachers/{id} | routers/teachers.py:get_teacher | api-client.ts:getTeacher |
| POST /api/teachers | routers/teachers.py:create_teacher | api-client.ts:createTeacher |
| PUT /api/teachers/{id} | routers/teachers.py:update_teacher | api-client.ts:updateTeacher |
| DELETE /api/teachers/{id} | routers/teachers.py:delete_teacher | api-client.ts:deleteTeacher |
| GET /api/teachers/{id}/courses | routers/teachers.py:get_teacher_courses | api-client.ts:getTeacherCourses |

**Service**: services/teacher.py:TeacherService

## 4. 学生模块 (Students)

| 接口 | 后端实现 | 前端调用 |
|-----|---------|---------|
| GET /api/students | routers/students.py:get_students | api-client.ts:getStudents |
| GET /api/students/{id} | routers/students.py:get_student | api-client.ts:getStudent |
| GET /api/students/user/{userId} | routers/students.py:get_student_by_user_id | api-client.ts:getStudentByUserId |
| GET /api/students/classes | routers/students.py:get_class_list | api-client.ts:getClassList |
| POST /api/students | routers/students.py:create_student | api-client.ts:createStudent |
| PUT /api/students/{id} | routers/students.py:update_student | api-client.ts:updateStudent |
| DELETE /api/students/{id} | routers/students.py:delete_student | api-client.ts:deleteStudent |
| GET /api/students/{id}/courses | routers/students.py:get_student_courses | api-client.ts:getStudentCourses |
| GET /api/students/{id}/submissions | routers/students.py:get_student_submissions | api-client.ts:getStudentSubmissions |

**Service**: services/student.py:StudentService

## 5. 课程模块 (Courses)

| 接口 | 后端实现 | 前端调用 |
|-----|---------|---------|
| GET /api/courses | routers/courses.py:get_courses | api-client.ts:getCourses |
| GET /api/courses/{id} | routers/courses.py:get_course | api-client.ts:getCourse |
| POST /api/courses | routers/courses.py:create_course | api-client.ts:createCourse |
| PUT /api/courses/{id} | routers/courses.py:update_course | api-client.ts:updateCourse |
| DELETE /api/courses/{id} | routers/courses.py:delete_course | api-client.ts:deleteCourse |

**Service**: services/course.py:CourseService

## 6. 课程学员管理 (Course Enrollment)

| 接口 | 后端实现 | 前端调用 |
|-----|---------|---------|
| GET /api/courses/{id}/students | routers/courses.py:get_course_students | api-client.ts:getCourseStudents |
| POST /api/courses/{id}/students | routers/courses.py:add_student_to_course | api-client.ts:addStudentToCourse |
| POST /api/courses/{id}/students/batch | routers/courses.py:batch_add_students | api-client.ts:batchAddStudents |
| DELETE /api/courses/{id}/students/{sid} | routers/courses.py:remove_student_from_course | api-client.ts:removeStudentFromCourse |

**Service**: services/course.py:CourseService

## 7. 作业模块 (Homeworks)

| 接口 | 后端实现 | 前端调用 |
|-----|---------|---------|
| GET /api/courses/{id}/homeworks | routers/courses.py:get_course_homeworks | api-client.ts:getCourseHomeworks |
| GET /api/homeworks/{id} | routers/homeworks.py:get_homework | api-client.ts:getHomework |
| POST /api/courses/{id}/homeworks | routers/courses.py:create_homework | api-client.ts:createHomework |
| PUT /api/homeworks/{id} | routers/homeworks.py:update_homework | api-client.ts:updateHomework |
| DELETE /api/homeworks/{id} | routers/homeworks.py:delete_homework | api-client.ts:deleteHomework |

**Service**: services/homework.py:HomeworkService

## 8. 作业提交模块 (Submissions)

| 接口 | 后端实现 | 前端调用 |
|-----|---------|---------|
| GET /api/homeworks/{id}/submissions | routers/homeworks.py:get_homework_submissions | api-client.ts:getHomeworkSubmissions |
| GET /api/submissions/{id} | routers/submissions.py:get_submission | api-client.ts:getSubmission |
| POST /api/homeworks/{id}/submissions | routers/homeworks.py:submit_homework | api-client.ts:submitHomework |
| PUT /api/submissions/{id} | routers/submissions.py:update_submission | api-client.ts:updateSubmission |
| POST /api/submissions/{id}/grade | routers/submissions.py:grade_submission | api-client.ts:gradeSubmission |
| DELETE /api/submissions/{id} | routers/submissions.py:delete_submission | api-client.ts:deleteSubmission |

**Service**: services/submission.py:SubmissionService

## 9. 文件夹模块 (Folders)

| 接口 | 后端实现 | 前端调用 |
|-----|---------|---------|
| GET /api/courses/{id}/folders | routers/courses.py:get_course_folders | api-client.ts:getCourseFolders |
| GET /api/courses/{id}/resources | routers/courses.py:get_course_resources | api-client.ts:getCourseResources |
| GET /api/folders/{id} | routers/resources.py:get_folder | api-client.ts:getFolder |
| POST /api/courses/{id}/folders | routers/courses.py:create_folder | api-client.ts:createFolder |
| PUT /api/folders/{id} | routers/resources.py:update_folder | api-client.ts:updateFolder |
| DELETE /api/folders/{id} | routers/resources.py:delete_folder | api-client.ts:deleteFolder |

**Service**: services/resource.py:ResourceService

## 10. 文件模块 (Files)

| 接口 | 后端实现 | 前端调用 |
|-----|---------|---------|
| GET /api/folders/{id}/files | routers/resources.py:get_folder_files | api-client.ts:getFolderFiles |
| GET /api/files/{id} | routers/resources.py:get_file | api-client.ts:getFile |
| POST /api/folders/{id}/files | routers/resources.py:upload_file | api-client.ts:uploadFile |
| PUT /api/files/{id} | routers/resources.py:update_file | api-client.ts:updateFile |
| DELETE /api/files/{id} | routers/resources.py:delete_file | api-client.ts:deleteFile |
| GET /api/files/{id}/download | routers/resources.py:download_file | api-client.ts:getFileDownloadUrl |

**Service**: services/resource.py:ResourceService

## 11. AI 模块 (AI)

| 接口 | 后端实现 | 前端调用 | 备注 |
|-----|---------|---------|-----|
| POST /api/ai/ppt/generate | routers/ai.py:generate_ppt | api-client.ts:generatePPT | ai/ppt |
| POST /api/ai/content/generate | routers/ai.py:generate_content | api-client.ts:generateContent | ai/content |
| POST /api/ai/content/edit | routers/ai.py:edit_content | api-client.ts:editContent | ai/edit |
| POST /api/ai/chat | routers/ai.py:chat | api-client.ts:chat | ai/chat |

**Provider**: providers/mock.py:MockAIProvider

---

## 后端目录结构

```
backend/
├── app/
│   ├── core/           # 核心配置
│   │   ├── config.py       # 配置管理
│   │   ├── security.py     # JWT/密码
│   │   ├── deps.py         # 依赖注入
│   │   ├── exceptions.py   # 异常定义
│   │   └── logging.py      # 日志配置
│   ├── db/             # 数据库
│   │   ├── session.py      # 会话管理
│   │   └── init_data.py    # 初始数据
│   ├── models/         # 数据模型
│   │   └── models.py       # SQLModel 模型
│   ├── schemas/        # Pydantic Schema
│   │   ├── auth.py
│   │   ├── teacher.py
│   │   ├── student.py
│   │   ├── course.py
│   │   ├── homework.py
│   │   ├── submission.py
│   │   ├── resource.py
│   │   └── ai.py
│   ├── repositories/   # 数据访问层
│   │   ├── base.py
│   │   ├── user.py
│   │   ├── teacher.py
│   │   ├── student.py
│   │   ├── course.py
│   │   ├── homework.py
│   │   ├── submission.py
│   │   └── resource.py
│   ├── services/       # 业务逻辑层
│   │   ├── auth.py
│   │   ├── teacher.py
│   │   ├── student.py
│   │   ├── course.py
│   │   ├── homework.py
│   │   ├── submission.py
│   │   └── resource.py
│   ├── routers/        # 路由层
│   │   ├── auth.py
│   │   ├── users.py
│   │   ├── teachers.py
│   │   ├── students.py
│   │   ├── courses.py
│   │   ├── homeworks.py
│   │   ├── submissions.py
│   │   ├── resources.py
│   │   └── ai.py
│   ├── providers/      # AI 提供者
│   │   ├── base.py
│   │   └── mock.py
│   └── main.py         # 应用入口
├── requirements.txt
├── .env
├── .env.example
├── run.py
└── README.md
```

## 前端改动点

需要修改的文件清单：

| 文件 | 改动说明 |
|-----|---------|
| src/utils/api-client.ts | **新增** API 客户端 |
| src/utils/localStorage-service.ts | 替换为调用 api-client |
| src/App.tsx | 登录逻辑改为调用 api |
| src/components/teacher/* | 数据操作改为调用 api |
| src/components/student/* | 数据操作改为调用 api |

详细改动见下一章节。
