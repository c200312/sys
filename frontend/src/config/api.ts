// API 配置文件
export const API_CONFIG = {
  BASE_URL: 'http://localhost:8080',
};

// API 端点
export const API_ENDPOINTS = {
  // 认证相关
  SIGNUP: '/api/auth/signup',
  LOGIN: '/api/auth/login',
  LOGOUT: '/api/auth/logout',
  VERIFY_TOKEN: '/api/auth/verify',
  
  // 用户管理
  GET_USER_INFO: '/api/users/me',
  UPDATE_PASSWORD: '/api/users/password',
  
  // 教师管理
  GET_TEACHERS: '/api/teachers',
  GET_TEACHER: (teacherId: string) => `/api/teachers/${teacherId}`,
  CREATE_TEACHER: '/api/teachers',
  UPDATE_TEACHER: (teacherId: string) => `/api/teachers/${teacherId}`,
  DELETE_TEACHER: (teacherId: string) => `/api/teachers/${teacherId}`,
  
  // 学生管理
  GET_STUDENTS: '/api/students',
  GET_STUDENT: (studentId: string) => `/api/students/${studentId}`,
  CREATE_STUDENT: '/api/students',
  UPDATE_STUDENT: (studentId: string) => `/api/students/${studentId}`,
  DELETE_STUDENT: (studentId: string) => `/api/students/${studentId}`,
  GET_STUDENT_BY_USER_ID: (userId: string) => `/api/students/user/${userId}`,
  
  // 课程管理
  GET_COURSES: '/api/courses',
  GET_COURSE: (courseId: string) => `/api/courses/${courseId}`,
  CREATE_COURSE: '/api/courses',
  UPDATE_COURSE: (courseId: string) => `/api/courses/${courseId}`,
  DELETE_COURSE: (courseId: string) => `/api/courses/${courseId}`,
  GET_TEACHER_COURSES: (teacherId: string) => `/api/teachers/${teacherId}/courses`,
  GET_STUDENT_COURSES: (studentId: string) => `/api/students/${studentId}/courses`,
  
  // 课程学员管理
  GET_COURSE_STUDENTS: (courseId: string) => `/api/courses/${courseId}/students`,
  ADD_COURSE_STUDENT: (courseId: string) => `/api/courses/${courseId}/students`,
  REMOVE_COURSE_STUDENT: (courseId: string, studentId: string) => 
    `/api/courses/${courseId}/students/${studentId}`,
  BATCH_ADD_STUDENTS: (courseId: string) => `/api/courses/${courseId}/students/batch`,
  
  // 作业管理
  GET_HOMEWORKS: (courseId: string) => `/api/courses/${courseId}/homeworks`,
  GET_HOMEWORK: (homeworkId: string) => `/api/homeworks/${homeworkId}`,
  CREATE_HOMEWORK: (courseId: string) => `/api/courses/${courseId}/homeworks`,
  UPDATE_HOMEWORK: (homeworkId: string) => `/api/homeworks/${homeworkId}`,
  DELETE_HOMEWORK: (homeworkId: string) => `/api/homeworks/${homeworkId}`,
  
  // 作业提交管理
  GET_HOMEWORK_SUBMISSIONS: (homeworkId: string) => `/api/homeworks/${homeworkId}/submissions`,
  GET_SUBMISSION: (submissionId: string) => `/api/submissions/${submissionId}`,
  CREATE_SUBMISSION: (homeworkId: string) => `/api/homeworks/${homeworkId}/submissions`,
  UPDATE_SUBMISSION: (submissionId: string) => `/api/submissions/${submissionId}`,
  DELETE_SUBMISSION: (submissionId: string) => `/api/submissions/${submissionId}`,
  GRADE_SUBMISSION: (submissionId: string) => `/api/submissions/${submissionId}/grade`,
  GET_STUDENT_SUBMISSIONS: (studentId: string) => `/api/students/${studentId}/submissions`,
  
  // 课程资源管理（文件夹）
  GET_COURSE_FOLDERS: (courseId: string) => `/api/courses/${courseId}/folders`,
  GET_FOLDER: (folderId: string) => `/api/folders/${folderId}`,
  CREATE_FOLDER: (courseId: string) => `/api/courses/${courseId}/folders`,
  UPDATE_FOLDER: (folderId: string) => `/api/folders/${folderId}`,
  DELETE_FOLDER: (folderId: string) => `/api/folders/${folderId}`,
  
  // 课程资源管理（文件）
  GET_FOLDER_FILES: (folderId: string) => `/api/folders/${folderId}/files`,
  GET_FILE: (fileId: string) => `/api/files/${fileId}`,
  UPLOAD_FILE: (folderId: string) => `/api/folders/${folderId}/files`,
  UPDATE_FILE: (fileId: string) => `/api/files/${fileId}`,
  DELETE_FILE: (fileId: string) => `/api/files/${fileId}`,
  DOWNLOAD_FILE: (fileId: string) => `/api/files/${fileId}/download`,
};

// HTTP 请求方法
export const HTTP_METHODS = {
  GET: 'GET',
  POST: 'POST',
  PUT: 'PUT',
  DELETE: 'DELETE',
  PATCH: 'PATCH',
} as const;

// 响应状态码
export const HTTP_STATUS = {
  OK: 200,
  CREATED: 201,
  NO_CONTENT: 204,
  BAD_REQUEST: 400,
  UNAUTHORIZED: 401,
  FORBIDDEN: 403,
  NOT_FOUND: 404,
  CONFLICT: 409,
  INTERNAL_SERVER_ERROR: 500,
} as const;
