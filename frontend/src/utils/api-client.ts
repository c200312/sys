/**
 * API 客户端
 * 封装所有后端 API 调用
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8080';

// ============= 类型定义 =============

export interface ApiResponse<T = unknown> {
  success: boolean;
  data?: T;
  message?: string;
  error?: string;
  code?: string;
}

export interface User {
  id: string;
  username: string;
  role: 'teacher' | 'student';
  created_at?: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface Teacher {
  id: string;
  teacher_no: string;
  name: string;
  gender: '男' | '女';
  email: string;
  created_at: string;
}

export interface Student {
  id: string;
  student_no: string;
  name: string;
  class: string;
  gender: '男' | '女';
  created_at: string;
  enrolled_at?: string;
}

export interface Course {
  id: string;
  name: string;
  description: string;
  teacher_id: string;
  teacher_name?: string;
  student_count: number;
  enrolled_at?: string;
  created_at: string;
}

export interface FileAttachment {
  name: string;
  type: string;
  size: number;
  content: string;
}

export interface GradingCriteria {
  type: 'text' | 'file';
  content: string;
  file_name?: string;
  file_size?: number;
}

export interface Homework {
  id: string;
  course_id: string;
  title: string;
  description: string;
  deadline: string;
  created_at: string;
  attachment?: FileAttachment;
  grading_criteria?: GradingCriteria;
  status?: 'pending' | 'submitted' | 'graded';
  submission_id?: string;
  score?: number;
  feedback?: string;
}

export interface Submission {
  id: string;
  homework_id: string;
  student_id: string;
  student_name?: string;
  student_no?: string;
  content: string;
  attachments?: FileAttachment[];
  score?: number;
  feedback?: string;
  submitted_at: string;
  graded_at?: string;
  homework_title?: string;
  course_name?: string;
}

export interface CourseFolder {
  id: string;
  course_id: string;
  name: string;
  created_at: string;
  files?: CourseFile[];
}

export interface CourseFile {
  id: string;
  folder_id: string;
  course_id: string;
  name: string;
  size: number;
  type: string;
  content?: string;
  created_at: string;
}

// ============= HTTP 客户端 =============

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  private getToken(): string | null {
    return localStorage.getItem('access_token');
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    const url = `${this.baseUrl}${endpoint}`;
    const token = this.getToken();

    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...options.headers,
    };

    if (token) {
      (headers as Record<string, string>)['Authorization'] = `Bearer ${token}`;
    }

    try {
      const response = await fetch(url, {
        ...options,
        headers,
      });

      const data = await response.json();

      if (!response.ok) {
        // 处理 401 错误
        if (response.status === 401) {
          localStorage.removeItem('access_token');
          localStorage.removeItem('username');
          localStorage.removeItem('user_id');
          localStorage.removeItem('role');
          // 刷新页面回到登录状态
          window.location.reload();
        }
        return data;
      }

      return data;
    } catch (error) {
      console.error('API 请求错误:', error);
      return {
        success: false,
        error: '网络请求失败',
        code: 'NETWORK_ERROR',
      };
    }
  }

  // ============= 认证 API =============

  async signup(username: string, password: string, role: string) {
    return this.request<User>('/api/auth/signup', {
      method: 'POST',
      body: JSON.stringify({ username, password, role }),
    });
  }

  async login(username: string, password: string) {
    return this.request<LoginResponse>('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify({ username, password }),
    });
  }

  async logout() {
    return this.request<void>('/api/auth/logout', {
      method: 'POST',
    });
  }

  async verifyToken() {
    return this.request<User>('/api/auth/verify');
  }

  // ============= 用户 API =============

  async getCurrentUser() {
    return this.request<User>('/api/users/me');
  }

  async changePassword(oldPassword: string, newPassword: string) {
    return this.request<void>('/api/users/password', {
      method: 'PUT',
      body: JSON.stringify({ old_password: oldPassword, new_password: newPassword }),
    });
  }

  // ============= 教师 API =============

  async getTeachers(page = 1, pageSize = 20, search?: string) {
    const params = new URLSearchParams({ page: String(page), page_size: String(pageSize) });
    if (search) params.append('search', search);
    return this.request<{ teachers: Teacher[]; total: number; page: number; page_size: number }>(
      `/api/teachers?${params}`
    );
  }

  async getTeacher(teacherId: string) {
    return this.request<Teacher>(`/api/teachers/${teacherId}`);
  }

  async createTeacher(data: { teacher_no: string; name: string; gender: string; email: string; password: string }) {
    return this.request<Teacher>('/api/teachers', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updateTeacher(teacherId: string, data: { name?: string; gender?: string; email?: string }) {
    return this.request<Teacher>(`/api/teachers/${teacherId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async deleteTeacher(teacherId: string) {
    return this.request<void>(`/api/teachers/${teacherId}`, {
      method: 'DELETE',
    });
  }

  async getTeacherCourses(teacherId: string) {
    return this.request<{ courses: Course[]; total: number }>(`/api/teachers/${teacherId}/courses`);
  }

  async getTeacherByUserId(userId: string) {
    return this.request<Teacher>(`/api/teachers/user/${userId}`);
  }

  // ============= 学生 API =============

  async getStudents(page = 1, pageSize = 20, search?: string, classFilter?: string) {
    const params = new URLSearchParams({ page: String(page), page_size: String(pageSize) });
    if (search) params.append('search', search);
    if (classFilter) params.append('class', classFilter);
    return this.request<{ students: Student[]; total: number; page: number; page_size: number }>(
      `/api/students?${params}`
    );
  }

  async getStudent(studentId: string) {
    return this.request<Student>(`/api/students/${studentId}`);
  }

  async getStudentByUserId(userId: string) {
    return this.request<Student>(`/api/students/user/${userId}`);
  }

  async getClassList() {
    return this.request<{ classes: string[] }>('/api/students/classes');
  }

  async createStudent(data: { student_no: string; name: string; class: string; gender: string; password: string }) {
    return this.request<Student>('/api/students', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updateStudent(studentId: string, data: { name?: string; class?: string; gender?: string }) {
    return this.request<Student>(`/api/students/${studentId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async deleteStudent(studentId: string) {
    return this.request<void>(`/api/students/${studentId}`, {
      method: 'DELETE',
    });
  }

  async getStudentCourses(studentId: string) {
    return this.request<{ courses: Course[]; total: number }>(`/api/students/${studentId}/courses`);
  }

  async getStudentSubmissions(studentId: string) {
    return this.request<{ submissions: Submission[]; total: number }>(`/api/students/${studentId}/submissions`);
  }

  // ============= 课程 API =============

  async getCourses(page = 1, pageSize = 20, search?: string) {
    const params = new URLSearchParams({ page: String(page), page_size: String(pageSize) });
    if (search) params.append('search', search);
    return this.request<{ courses: Course[]; total: number; page: number; page_size: number }>(
      `/api/courses?${params}`
    );
  }

  async getCourse(courseId: string) {
    return this.request<Course>(`/api/courses/${courseId}`);
  }

  async createCourse(data: { name: string; description: string }) {
    return this.request<Course>('/api/courses', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updateCourse(courseId: string, data: { name?: string; description?: string }) {
    return this.request<Course>(`/api/courses/${courseId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async deleteCourse(courseId: string) {
    return this.request<void>(`/api/courses/${courseId}`, {
      method: 'DELETE',
    });
  }

  // ============= 课程学员 API =============

  async getCourseStudents(courseId: string, page = 1, pageSize = 1000, search?: string) {
    const params = new URLSearchParams({ page: String(page), page_size: String(pageSize) });
    if (search) params.append('search', search);
    return this.request<{ students: Student[]; total: number; page: number; page_size: number }>(
      `/api/courses/${courseId}/students?${params}`
    );
  }

  async addStudentToCourse(courseId: string, studentId: string) {
    return this.request<void>(`/api/courses/${courseId}/students`, {
      method: 'POST',
      body: JSON.stringify({ student_id: studentId }),
    });
  }

  async batchAddStudents(courseId: string, studentIds: string[]) {
    return this.request<{ added_count: number; failed_count: number }>(`/api/courses/${courseId}/students/batch`, {
      method: 'POST',
      body: JSON.stringify({ student_ids: studentIds }),
    });
  }

  async removeStudentFromCourse(courseId: string, studentId: string) {
    return this.request<void>(`/api/courses/${courseId}/students/${studentId}`, {
      method: 'DELETE',
    });
  }

  // ============= 作业 API =============

  async getCourseHomeworks(courseId: string) {
    return this.request<{ homeworks: Homework[]; total: number }>(`/api/courses/${courseId}/homeworks`);
  }

  async getHomework(homeworkId: string) {
    return this.request<Homework>(`/api/homeworks/${homeworkId}`);
  }

  async createHomework(courseId: string, data: {
    title: string;
    description: string;
    deadline: string;
    attachment?: FileAttachment;
    grading_criteria?: GradingCriteria;
  }) {
    return this.request<Homework>(`/api/courses/${courseId}/homeworks`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updateHomework(homeworkId: string, data: {
    title?: string;
    description?: string;
    deadline?: string;
    attachment?: FileAttachment;
    grading_criteria?: GradingCriteria;
  }) {
    return this.request<Homework>(`/api/homeworks/${homeworkId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async deleteHomework(homeworkId: string) {
    return this.request<void>(`/api/homeworks/${homeworkId}`, {
      method: 'DELETE',
    });
  }

  // ============= 作业提交 API =============

  async getHomeworkSubmissions(homeworkId: string) {
    return this.request<{ submissions: Submission[]; total: number }>(`/api/homeworks/${homeworkId}/submissions`);
  }

  async getSubmission(submissionId: string) {
    return this.request<Submission>(`/api/submissions/${submissionId}`);
  }

  async submitHomework(homeworkId: string, data: { content: string; attachments?: FileAttachment[] }) {
    return this.request<Submission>(`/api/homeworks/${homeworkId}/submissions`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updateSubmission(submissionId: string, data: { content?: string; attachments?: FileAttachment[] }) {
    return this.request<Submission>(`/api/submissions/${submissionId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async gradeSubmission(submissionId: string, data: { score: number; feedback?: string }) {
    return this.request<{ id: string; score: number; feedback?: string; graded_at: string }>(
      `/api/submissions/${submissionId}/grade`,
      {
        method: 'POST',
        body: JSON.stringify(data),
      }
    );
  }

  async deleteSubmission(submissionId: string) {
    return this.request<void>(`/api/submissions/${submissionId}`, {
      method: 'DELETE',
    });
  }

  // ============= 课程资源 API =============

  async getCourseFolders(courseId: string) {
    return this.request<{ folders: CourseFolder[]; total: number }>(`/api/courses/${courseId}/folders`);
  }

  async getCourseResources(courseId: string) {
    return this.request<{ folders: CourseFolder[]; total: number }>(`/api/courses/${courseId}/resources`);
  }

  async getFolder(folderId: string) {
    return this.request<CourseFolder>(`/api/folders/${folderId}`);
  }

  async createFolder(courseId: string, name: string) {
    return this.request<CourseFolder>(`/api/courses/${courseId}/folders`, {
      method: 'POST',
      body: JSON.stringify({ name }),
    });
  }

  async updateFolder(folderId: string, name: string) {
    return this.request<CourseFolder>(`/api/folders/${folderId}`, {
      method: 'PUT',
      body: JSON.stringify({ name }),
    });
  }

  async deleteFolder(folderId: string) {
    return this.request<void>(`/api/folders/${folderId}`, {
      method: 'DELETE',
    });
  }

  async getFolderFiles(folderId: string) {
    return this.request<{ files: CourseFile[]; total: number }>(`/api/folders/${folderId}/files`);
  }

  async getFile(fileId: string) {
    return this.request<CourseFile>(`/api/files/${fileId}`);
  }

  async uploadFile(folderId: string, data: { name: string; size: number; type: string; content: string }) {
    return this.request<CourseFile>(`/api/folders/${folderId}/files`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updateFile(fileId: string, data: { name?: string; content?: string }) {
    return this.request<CourseFile>(`/api/files/${fileId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async deleteFile(fileId: string) {
    return this.request<void>(`/api/files/${fileId}`, {
      method: 'DELETE',
    });
  }

  getFileDownloadUrl(fileId: string): string {
    const token = this.getToken();
    return `${this.baseUrl}/api/files/${fileId}/download?token=${token}`;
  }

  // ============= AI API =============

  async generatePPT(title: string, requirements: string) {
    return this.request<{ content: string; title: string }>('/api/ai/ppt/generate', {
      method: 'POST',
      body: JSON.stringify({ title, requirements }),
    });
  }

  async generateContent(title: string, requirements: string, references?: { name: string; content: string }[]) {
    return this.request<{ content: string; title: string }>('/api/ai/content/generate', {
      method: 'POST',
      body: JSON.stringify({ title, requirements, references }),
    });
  }

  async editContent(originalText: string, action: 'rewrite' | 'expand' | 'custom', customInstruction?: string) {
    return this.request<{ original_text: string; edited_text: string }>('/api/ai/content/edit', {
      method: 'POST',
      body: JSON.stringify({ original_text: originalText, action, custom_instruction: customInstruction }),
    });
  }

  async chat(message: string, history?: { role: string; content: string }[], context?: string) {
    return this.request<{ message: string; role: string }>('/api/ai/chat', {
      method: 'POST',
      body: JSON.stringify({ message, history, context }),
    });
  }
}

// 导出单例
export const api = new ApiClient(API_BASE_URL);
export default api;
