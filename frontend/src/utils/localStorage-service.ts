// LocalStorage 服务 - 模拟后端数据存储
import { v4 as uuidv4 } from 'uuid';

// 数据类型定义
export interface User {
  id: string;
  username: string; // 学号或工号（登录用）
  password: string;
  role: 'teacher' | 'student';
  created_at: string;
}

// 教师详细信息表
export interface Teacher {
  id: string;
  teacher_no: string; // 工号（关联 User.username）
  name: string; // 姓名
  gender: '男' | '女'; // 性别
  email: string; // 邮箱
  created_at: string;
}

// 学生详细信息表
export interface Student {
  id: string;
  student_no: string; // 学号（关联 User.username）
  name: string; // 姓名
  class: string; // 班级
  gender: '男' | '女'; // 性别
  created_at: string;
}

export interface Course {
  id: string;
  name: string;
  description: string;
  teacher_id: string;
  student_count: number;
  created_at: string;
}

export interface CourseEnrollment {
  course_id: string;
  student_id: string;
  enrolled_at: string;
}

export interface Homework {
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
    content: string; // Base64数据
  };
  grading_criteria?: {
    type: 'text' | 'file';
    content: string;
    file_name?: string;
    file_size?: number;
  };
}

export interface HomeworkSubmission {
  id: string;
  homework_id: string;
  student_id: string;
  content: string; // 纯文本内容
  attachments?: Array<{
    name: string;
    type: string;
    size: number;
    content: string; // Base64数据
  }>; // 附件单独存储
  score?: number;
  feedback?: string;
  submitted_at: string;
  graded_at?: string;
}

// 课程文件夹
export interface CourseFolder {
  id: string;
  course_id: string;
  name: string; // 文件夹名称
  created_at: string;
}

// 课程文件
export interface CourseFile {
  id: string;
  folder_id: string;
  course_id: string;
  name: string; // 文件名
  size: number; // 文件大小（字节）
  type: string; // 文件类型（MIME类型）
  content: string; // 文件内容（base64编码）
  created_at: string;
}

// 存储键
const STORAGE_KEYS = {
  USERS: 'edu_system_users',
  TEACHERS: 'edu_system_teachers', // 新增教师表
  STUDENTS: 'edu_system_students',
  COURSES: 'edu_system_courses',
  ENROLLMENTS: 'edu_system_enrollments',
  HOMEWORKS: 'edu_system_homeworks',
  SUBMISSIONS: 'edu_system_submissions',
  FOLDERS: 'edu_system_folders', // 课程文件夹
  FILES: 'edu_system_files', // 课程文件
};

// 初始化数据
function initializeData() {
  // 初始化用户数据
  if (!localStorage.getItem(STORAGE_KEYS.USERS)) {
    const initialUsers: User[] = [];
    const now = new Date().toISOString();
    
    // 添加5个老师：teacher1 - teacher5
    for (let i = 1; i <= 5; i++) {
      initialUsers.push({
        id: uuidv4(),
        username: `teacher${i}`,
        password: '123456',
        role: 'teacher',
        created_at: now,
      });
    }
    
    // 添加100个学生：student1 - student100
    // 1-40: 一班，41-80: 二班，81-100: 三班
    for (let i = 1; i <= 100; i++) {
      let className = '一班';
      if (i >= 41 && i <= 80) {
        className = '二班';
      } else if (i >= 81 && i <= 100) {
        className = '三班';
      }
      
      initialUsers.push({
        id: uuidv4(),
        username: `student${i}`,
        password: '123456',
        role: 'student',
        created_at: now,
      });
    }
    
    console.log(`✅ 初始化完成：创建了 ${initialUsers.length} 个用户 (5个老师 + 100个学生，分为3个班级)`);
    localStorage.setItem(STORAGE_KEYS.USERS, JSON.stringify(initialUsers));
  }

  // 初始化教师详细信息表
  if (!localStorage.getItem(STORAGE_KEYS.TEACHERS)) {
    const initialTeachers: Teacher[] = [];
    const users = getData<User>(STORAGE_KEYS.USERS);
    const now = new Date().toISOString();
    
    // 添加5个教师详细信息
    for (let i = 1; i <= 5; i++) {
      initialTeachers.push({
        id: uuidv4(),
        teacher_no: `teacher${i}`,
        name: `教师${i}`,
        gender: i % 2 === 0 ? '男' : '女',
        email: `teacher${i}@example.com`,
        created_at: now,
      });
    }
    
    console.log(`✅ 初始化完成：创建了 ${initialTeachers.length} 个教师详细信息`);
    localStorage.setItem(STORAGE_KEYS.TEACHERS, JSON.stringify(initialTeachers));
  }

  // 初始化学生详细信息表
  if (!localStorage.getItem(STORAGE_KEYS.STUDENTS)) {
    const initialStudents: Student[] = [];
    const users = getData<User>(STORAGE_KEYS.USERS);
    const now = new Date().toISOString();
    
    // 添加100个学生详细信息
    for (let i = 1; i <= 100; i++) {
      let className = '一班';
      if (i >= 41 && i <= 80) {
        className = '二班';
      } else if (i >= 81 && i <= 100) {
        className = '三班';
      }
      
      initialStudents.push({
        id: uuidv4(),
        student_no: `student${i}`,
        name: `学生${i}`,
        class: className,
        gender: i % 2 === 0 ? '男' : '女',
        created_at: now,
      });
    }
    
    console.log(`✅ 初始化完成：创建了 ${initialStudents.length} 个学生详细信息`);
    localStorage.setItem(STORAGE_KEYS.STUDENTS, JSON.stringify(initialStudents));
  }

  // 初始化其他数据
  if (!localStorage.getItem(STORAGE_KEYS.COURSES)) {
    localStorage.setItem(STORAGE_KEYS.COURSES, JSON.stringify([]));
  }
  if (!localStorage.getItem(STORAGE_KEYS.ENROLLMENTS)) {
    localStorage.setItem(STORAGE_KEYS.ENROLLMENTS, JSON.stringify([]));
  }
  if (!localStorage.getItem(STORAGE_KEYS.HOMEWORKS)) {
    localStorage.setItem(STORAGE_KEYS.HOMEWORKS, JSON.stringify([]));
  }
  if (!localStorage.getItem(STORAGE_KEYS.SUBMISSIONS)) {
    localStorage.setItem(STORAGE_KEYS.SUBMISSIONS, JSON.stringify([]));
  }
  if (!localStorage.getItem(STORAGE_KEYS.FOLDERS)) {
    localStorage.setItem(STORAGE_KEYS.FOLDERS, JSON.stringify([]));
  }
  if (!localStorage.getItem(STORAGE_KEYS.FILES)) {
    localStorage.setItem(STORAGE_KEYS.FILES, JSON.stringify([]));
  }
}

// 获取数据
function getData<T>(key: string): T[] {
  const data = localStorage.getItem(key);
  return data ? JSON.parse(data) : [];
}

// 保存数据
function saveData<T>(key: string, data: T[]) {
  localStorage.setItem(key, JSON.stringify(data));
}

// 重置所有数据（用于测试）
export function resetAllData() {
  localStorage.removeItem(STORAGE_KEYS.USERS);
  localStorage.removeItem(STORAGE_KEYS.TEACHERS); // 新增教师表
  localStorage.removeItem(STORAGE_KEYS.STUDENTS);
  localStorage.removeItem(STORAGE_KEYS.COURSES);
  localStorage.removeItem(STORAGE_KEYS.ENROLLMENTS);
  localStorage.removeItem(STORAGE_KEYS.HOMEWORKS);
  localStorage.removeItem(STORAGE_KEYS.SUBMISSIONS);
  localStorage.removeItem(STORAGE_KEYS.FOLDERS);
  localStorage.removeItem(STORAGE_KEYS.FILES);
  console.log('🗑️ 已清空所有数据，刷新页面将重初始化');
}

// ==================== 认证相关 ====================

export async function signup(username: string, password: string, role: 'teacher' | 'student') {
  initializeData();
  const users = getData<User>(STORAGE_KEYS.USERS);

  // 检查用户名是否已存在
  if (users.find(u => u.username === username)) {
    throw new Error('用户名已存在');
  }

  // 创建新用户
  const newUser: User = {
    id: uuidv4(),
    username,
    password,
    role,
    created_at: new Date().toISOString(),
  };

  users.push(newUser);
  saveData(STORAGE_KEYS.USERS, users);

  // 返回用户信息（不包含密码）
  const { password: _, ...userInfo } = newUser;
  return {
    message: '注册成功',
    user: userInfo,
  };
}

export async function login(username: string, password: string) {
  initializeData();
  const users = getData<User>(STORAGE_KEYS.USERS);

  const user = users.find(u => u.username === username && u.password === password);
  if (!user) {
    throw new Error('用户名或密码错误');
  }

  // 生成访问令牌（简单模拟）
  const accessToken = `token_${user.id}_${Date.now()}`;

  // 返回用户信息（不包密码）
  const { password: _, ...userInfo } = user;
  return {
    access_token: accessToken,
    user: userInfo,
  };
}

// ==================== 学生管理 ====================

// 获取教师详细信息（通过工号）
export async function getTeacherByTeacherNo(teacherNo: string) {
  initializeData();
  const teachers = getData<Teacher>(STORAGE_KEYS.TEACHERS);
  const teacher = teachers.find(t => t.teacher_no === teacherNo);
  if (!teacher) {
    throw new Error('教师不存在');
  }
  return teacher;
}

// 获取教师详细信息（通过User ID）
export async function getTeacherByUserId(userId: string) {
  initializeData();
  const teachers = getData<Teacher>(STORAGE_KEYS.TEACHERS);
  const users = getData<User>(STORAGE_KEYS.USERS);
  
  const user = users.find(u => u.id === userId && u.role === 'teacher');
  if (!user) {
    throw new Error('用户不存在或不是教师');
  }
  
  const teacher = teachers.find(t => t.teacher_no === user.username);
  if (!teacher) {
    throw new Error('教师详细信息不存在');
  }
  
  return teacher;
}

// 获取学生详细信息列表（从student表，并关联user表获取ID）
export async function getStudentDetails(page: number = 1, pageSize: number = 20, q?: string, classFilter?: string) {
  initializeData();
  const students = getData<Student>(STORAGE_KEYS.STUDENTS);
  const users = getData<User>(STORAGE_KEYS.USERS);
  let filteredStudents = [...students];

  // 班级筛选
  if (classFilter && classFilter !== 'all') {
    filteredStudents = filteredStudents.filter(s => s.class === classFilter);
  }

  // 搜索过滤（学号、姓名、班级）
  if (q) {
    const query = q.toLowerCase();
    filteredStudents = filteredStudents.filter(s => 
      s.student_no.toLowerCase().includes(query) ||
      s.name.toLowerCase().includes(query) ||
      s.class.toLowerCase().includes(query)
    );
  }

  const total = filteredStudents.length;

  // 分页
  const start = (page - 1) * pageSize;
  const end = start + pageSize;
  const paginatedStudents = filteredStudents.slice(start, end);

  // 关联user表，获取user ID
  const studentsWithUserId = paginatedStudents.map(student => {
    const user = users.find(u => u.username === student.student_no);
    return {
      ...student,
      user_id: user?.id || '', // 添加user ID字段
    };
  });

  return {
    students: studentsWithUserId,
    total,
  };
}

// 获取所有班级列表（去重）
export async function getClassList() {
  initializeData();
  const students = getData<Student>(STORAGE_KEYS.STUDENTS);
  const classes = [...new Set(students.map(s => s.class))].sort();
  return { classes };
}

// 根据学号获取学生详细信息
export async function getStudentByStudentNo(studentNo: string) {
  initializeData();
  const students = getData<Student>(STORAGE_KEYS.STUDENTS);
  const student = students.find(s => s.student_no === studentNo);
  if (!student) {
    throw new Error('学生不存在');
  }
  return student;
}

// 根据User ID获取学生详细信息
export async function getStudentByUserId(userId: string) {
  initializeData();
  const students = getData<Student>(STORAGE_KEYS.STUDENTS);
  const users = getData<User>(STORAGE_KEYS.USERS);
  
  const user = users.find(u => u.id === userId && u.role === 'student');
  if (!user) {
    throw new Error('用户不存在或不是学生');
  }
  
  const student = students.find(s => s.student_no === user.username);
  if (!student) {
    throw new Error('学生详细信息不存在');
  }
  
  return student;
}

// 获取学生的课程列表（包含教师信息）
export async function getStudentCourses(studentId: string) {
  initializeData();
  const courses = getData<Course>(STORAGE_KEYS.COURSES);
  const enrollments = getData<CourseEnrollment>(STORAGE_KEYS.ENROLLMENTS);
  const users = getData<User>(STORAGE_KEYS.USERS);
  const teachers = getData<Teacher>(STORAGE_KEYS.TEACHERS);

  // 获取学生的选课记录
  const studentEnrollments = enrollments.filter(e => e.student_id === studentId);

  // 获取课程详细信息
  const studentCourses = studentEnrollments.map(enrollment => {
    const course = courses.find(c => c.id === enrollment.course_id);
    if (!course) return null;

    // 获取授课教师信息
    const teacherUser = users.find(u => u.id === course.teacher_id);
    const teacherInfo = teacherUser ? teachers.find(t => t.teacher_no === teacherUser.username) : null;

    return {
      ...course,
      teacher_name: teacherInfo?.name || '未知',
      teacher_no: teacherInfo?.teacher_no || '',
      enrolled_at: enrollment.enrolled_at,
    };
  }).filter((c): c is NonNullable<typeof c> => c !== null);

  return {
    courses: studentCourses,
    total: studentCourses.length,
  };
}

// 获取学生在某个课程的作业列表
export async function getStudentHomeworks(studentId: string, courseId: string) {
  initializeData();
  const homeworks = getData<Homework>(STORAGE_KEYS.HOMEWORKS);
  const submissions = getData<HomeworkSubmission>(STORAGE_KEYS.SUBMISSIONS);

  // 获取该课程的所有作业
  const courseHomeworks = homeworks.filter(h => h.course_id === courseId);

  // 获取学生的提交记录
  const studentSubmissions = submissions.filter(s => s.student_id === studentId);

  // 组合作业和提交信息
  const homeworkList = courseHomeworks.map(homework => {
    const submission = studentSubmissions.find(s => s.homework_id === homework.id);
    
    return {
      ...homework,
      submission: submission ? {
        id: submission.id,
        content: submission.content,
        attachments: submission.attachments,
        score: submission.score,
        feedback: submission.feedback,
        submitted_at: submission.submitted_at,
        graded_at: submission.graded_at,
      } : null,
      status: submission 
        ? (submission.score !== undefined ? 'graded' : 'submitted') 
        : 'pending',
    };
  });

  return {
    homeworks: homeworkList,
    total: homeworkList.length,
  };
}

export async function getStudents(page: number = 1, pageSize: number = 20, q?: string) {
  initializeData();
  const users = getData<User>(STORAGE_KEYS.USERS);
  let students = users.filter(u => u.role === 'student');

  // 搜索过滤
  if (q) {
    students = students.filter(s => s.username.includes(q));
  }

  const total = students.length;

  // 分页
  const start = (page - 1) * pageSize;
  const end = start + pageSize;
  const paginatedStudents = students.slice(start, end);

  // 移除密码字段
  const studentsWithoutPassword = paginatedStudents.map(({ password: _, ...rest }) => rest);

  return {
    users: studentsWithoutPassword,
    total,
  };
}

export async function createStudent(username: string, password: string) {
  initializeData();
  const users = getData<User>(STORAGE_KEYS.USERS);

  // 检查用户名是否已存在
  if (users.find(u => u.username === username)) {
    throw new Error('用户名已存在');
  }

  const newStudent: User = {
    id: uuidv4(),
    username,
    password,
    role: 'student',
    created_at: new Date().toISOString(),
  };

  users.push(newStudent);
  saveData(STORAGE_KEYS.USERS, users);

  const { password: _, ...studentInfo } = newStudent;
  return studentInfo;
}

export async function updateStudent(userId: string, updates: { username?: string; password?: string }) {
  initializeData();
  const users = getData<User>(STORAGE_KEYS.USERS);
  const userIndex = users.findIndex(u => u.id === userId && u.role === 'student');

  if (userIndex === -1) {
    throw new Error('学生不存在');
  }

  // 如果更新用户名，检查是否重复
  if (updates.username && updates.username !== users[userIndex].username) {
    if (users.find(u => u.username === updates.username)) {
      throw new Error('用户名已存在');
    }
  }

  // 更新用户信息
  users[userIndex] = {
    ...users[userIndex],
    ...updates,
  };

  saveData(STORAGE_KEYS.USERS, users);

  const { password: _, ...studentInfo } = users[userIndex];
  return studentInfo;
}

export async function deleteStudent(userId: string) {
  initializeData();
  const users = getData<User>(STORAGE_KEYS.USERS);
  const enrollments = getData<CourseEnrollment>(STORAGE_KEYS.ENROLLMENTS);

  // 检查学生是否已加入课程
  if (enrollments.some(e => e.student_id === userId)) {
    throw new Error('该学生已加入课程，无法删除');
  }

  const filteredUsers = users.filter(u => u.id !== userId);
  saveData(STORAGE_KEYS.USERS, filteredUsers);

  return { message: '删除成功' };
}

// ==================== 课程管理 ====================

export async function getCourses() {
  initializeData();
  const courses = getData<Course>(STORAGE_KEYS.COURSES);
  return { courses };
}

export async function createCourse(name: string, description: string, teacherId: string) {
  initializeData();
  const courses = getData<Course>(STORAGE_KEYS.COURSES);

  const newCourse: Course = {
    id: uuidv4(),
    name,
    description,
    teacher_id: teacherId,
    student_count: 0,
    created_at: new Date().toISOString(),
  };

  courses.push(newCourse);
  saveData(STORAGE_KEYS.COURSES, courses);

  return newCourse;
}

export async function updateCourse(courseId: string, updates: { name?: string; description?: string }) {
  initializeData();
  const courses = getData<Course>(STORAGE_KEYS.COURSES);
  const courseIndex = courses.findIndex(c => c.id === courseId);

  if (courseIndex === -1) {
    throw new Error('课程不存在');
  }

  courses[courseIndex] = {
    ...courses[courseIndex],
    ...updates,
  };

  saveData(STORAGE_KEYS.COURSES, courses);
  return courses[courseIndex];
}

export async function deleteCourse(courseId: string) {
  initializeData();
  const courses = getData<Course>(STORAGE_KEYS.COURSES);
  const enrollments = getData<CourseEnrollment>(STORAGE_KEYS.ENROLLMENTS);
  const homeworks = getData<Homework>(STORAGE_KEYS.HOMEWORKS);

  // 删除课程相关数据
  const filteredCourses = courses.filter(c => c.id !== courseId);
  const filteredEnrollments = enrollments.filter(e => e.course_id !== courseId);
  const filteredHomeworks = homeworks.filter(h => h.course_id !== courseId);

  saveData(STORAGE_KEYS.COURSES, filteredCourses);
  saveData(STORAGE_KEYS.ENROLLMENTS, filteredEnrollments);
  saveData(STORAGE_KEYS.HOMEWORKS, filteredHomeworks);

  return { message: '删除成功' };
}

// ==================== 课程学员管理 ====================

export async function getCourseStudents(courseId: string) {
  initializeData();
  const courses = getData<Course>(STORAGE_KEYS.COURSES);
  const users = getData<User>(STORAGE_KEYS.USERS);
  const students = getData<Student>(STORAGE_KEYS.STUDENTS); // 获取学生详细信息
  const enrollments = getData<CourseEnrollment>(STORAGE_KEYS.ENROLLMENTS);

  const course = courses.find(c => c.id === courseId);
  if (!course) {
    throw new Error('课程不存在');
  }

  const courseEnrollments = enrollments.filter(e => e.course_id === courseId);
  const studentList = courseEnrollments.map(enrollment => {
    const user = users.find(u => u.id === enrollment.student_id);
    if (user) {
      // 从student表获取详细信息
      const studentDetail = students.find(s => s.student_no === user.username);
      return {
        id: user.id,
        student_no: user.username,
        name: studentDetail?.name || '未知',
        class: studentDetail?.class || '未知',
        gender: studentDetail?.gender || '未知',
        enrolled_at: enrollment.enrolled_at,
      };
    }
    return null;
  }).filter((s): s is NonNullable<typeof s> => s !== null);

  return {
    course_id: courseId,
    course_name: course.name,
    students: studentList,
  };
}

export async function addStudentToCourse(courseId: string, studentId: string) {
  initializeData();
  const courses = getData<Course>(STORAGE_KEYS.COURSES);
  const users = getData<User>(STORAGE_KEYS.USERS);
  const enrollments = getData<CourseEnrollment>(STORAGE_KEYS.ENROLLMENTS);

  // 检查课程和学生是否存在
  const course = courses.find(c => c.id === courseId);
  if (!course) {
    throw new Error('课程不存在');
  }

  const student = users.find(u => u.id === studentId && u.role === 'student');
  if (!student) {
    throw new Error('学生不存在');
  }

  // 检查是否已加入
  if (enrollments.some(e => e.course_id === courseId && e.student_id === studentId)) {
    throw new Error('该学员已在课程中');
  }

  // 添加学员
  const enrollment: CourseEnrollment = {
    course_id: courseId,
    student_id: studentId,
    enrolled_at: new Date().toISOString(),
  };

  enrollments.push(enrollment);
  saveData(STORAGE_KEYS.ENROLLMENTS, enrollments);

  // 更新课程学员数
  const courseIndex = courses.findIndex(c => c.id === courseId);
  courses[courseIndex].student_count += 1;
  saveData(STORAGE_KEYS.COURSES, courses);

  return {
    message: '学员添加成功',
    course_id: courseId,
    student_id: studentId,
    enrolled_at: enrollment.enrolled_at,
  };
}

export async function removeStudentFromCourse(courseId: string, studentId: string) {
  console.log('📦 removeStudentFromCourse 被调用:', { courseId, studentId });
  initializeData();
  const courses = getData<Course>(STORAGE_KEYS.COURSES);
  const enrollments = getData<CourseEnrollment>(STORAGE_KEYS.ENROLLMENTS);

  console.log('当前所有选课记录:', enrollments);

  const enrollmentIndex = enrollments.findIndex(
    e => e.course_id === courseId && e.student_id === studentId
  );

  console.log('找到的选课记录索引:', enrollmentIndex);

  if (enrollmentIndex === -1) {
    console.error('❌ 未找到选课记录');
    throw new Error('该学员不在课程中');
  }

  enrollments.splice(enrollmentIndex, 1);
  saveData(STORAGE_KEYS.ENROLLMENTS, enrollments);
  console.log('✅ 选课记录已删除，剩余记录:', enrollments);

  // 更新课程学员数
  const courseIndex = courses.findIndex(c => c.id === courseId);
  if (courseIndex !== -1) {
    courses[courseIndex].student_count -= 1;
    saveData(STORAGE_KEYS.COURSES, courses);
    console.log('✅ 课程学员数已更新:', courses[courseIndex].student_count);
  }

  return {
    message: '学员已移除',
    course_id: courseId,
    student_id: studentId,
  };
}

// ==================== 作业管理 ====================

export async function getHomeworks(courseId: string) {
  initializeData();
  const homeworks = getData<Homework>(STORAGE_KEYS.HOMEWORKS);
  const courseHomeworks = homeworks.filter(h => h.course_id === courseId);
  return { homeworks: courseHomeworks };
}

export async function createHomework(
  courseId: string, 
  title: string, 
  description: string, 
  deadline: string,
  attachment?: {
    name: string;
    type: string;
    size: number;
    content: string;
  },
  gradingCriteria?: {
    type: 'text' | 'file';
    content: string;
    file_name?: string;
    file_size?: number;
  }
) {
  initializeData();
  const homeworks = getData<Homework>(STORAGE_KEYS.HOMEWORKS);

  const newHomework: Homework = {
    id: uuidv4(),
    course_id: courseId,
    title,
    description,
    deadline,
    created_at: new Date().toISOString(),
    attachment,
    grading_criteria: gradingCriteria,
  };

  homeworks.push(newHomework);
  saveData(STORAGE_KEYS.HOMEWORKS, homeworks);
  return newHomework;
}

export async function updateHomework(
  homeworkId: string, 
  title: string, 
  description: string, 
  deadline: string,
  attachment?: {
    name: string;
    type: string;
    size: number;
    content: string;
  },
  gradingCriteria?: {
    type: 'text' | 'file';
    content: string;
    file_name?: string;
    file_size?: number;
  }
) {
  initializeData();
  const homeworks = getData<Homework>(STORAGE_KEYS.HOMEWORKS);

  const homeworkIndex = homeworks.findIndex(h => h.id === homeworkId);
  if (homeworkIndex === -1) {
    throw new Error('作业不存在');
  }

  homeworks[homeworkIndex] = {
    ...homeworks[homeworkIndex],
    title,
    description,
    deadline,
    attachment,
    grading_criteria: gradingCriteria,
  };

  saveData(STORAGE_KEYS.HOMEWORKS, homeworks);
  return homeworks[homeworkIndex];
}

export async function deleteHomework(homeworkId: string) {
  initializeData();
  const homeworks = getData<Homework>(STORAGE_KEYS.HOMEWORKS);
  const submissions = getData<HomeworkSubmission>(STORAGE_KEYS.SUBMISSIONS);

  const homeworkIndex = homeworks.findIndex(h => h.id === homeworkId);
  if (homeworkIndex === -1) {
    throw new Error('作业不存在');
  }

  // 删除作业
  homeworks.splice(homeworkIndex, 1);
  saveData(STORAGE_KEYS.HOMEWORKS, homeworks);

  // 删除相关的提交记录
  const filteredSubmissions = submissions.filter(s => s.homework_id !== homeworkId);
  saveData(STORAGE_KEYS.SUBMISSIONS, filteredSubmissions);
}

export async function getHomeworkSubmissions(homeworkId: string) {
  initializeData();
  const submissions = getData<HomeworkSubmission>(STORAGE_KEYS.SUBMISSIONS);
  const users = getData<User>(STORAGE_KEYS.USERS);

  const homeworkSubmissions = submissions
    .filter(s => s.homework_id === homeworkId)
    .map(submission => {
      const student = users.find(u => u.id === submission.student_id);
      return {
        ...submission,
        student_username: student?.username || '未知',
      };
    });

  return { submissions: homeworkSubmissions };
}

export async function gradeSubmission(submissionId: string, score: number, feedback: string) {
  initializeData();
  const submissions = getData<HomeworkSubmission>(STORAGE_KEYS.SUBMISSIONS);
  const submissionIndex = submissions.findIndex(s => s.id === submissionId);

  if (submissionIndex === -1) {
    throw new Error('作业提交不存在');
  }

  submissions[submissionIndex] = {
    ...submissions[submissionIndex],
    score,
    feedback,
    graded_at: new Date().toISOString(),
  };

  saveData(STORAGE_KEYS.SUBMISSIONS, submissions);

  return submissions[submissionIndex];
}

// 学生提交作业
export async function submitHomework(
  homeworkId: string, 
  studentId: string, 
  content: string,
  attachments?: Array<{
    name: string;
    type: string;
    size: number;
    content: string;
  }>
) {
  initializeData();
  const submissions = getData<HomeworkSubmission>(STORAGE_KEYS.SUBMISSIONS);
  const homeworks = getData<Homework>(STORAGE_KEYS.HOMEWORKS);

  // 检查作业是否存在
  const homework = homeworks.find(h => h.id === homeworkId);
  if (!homework) {
    throw new Error('作业不存在');
  }

  // 检查是否已经提交过
  const existingSubmission = submissions.find(
    s => s.homework_id === homeworkId && s.student_id === studentId
  );

  if (existingSubmission) {
    // 更新已有的提交
    const submissionIndex = submissions.findIndex(s => s.id === existingSubmission.id);
    submissions[submissionIndex] = {
      ...submissions[submissionIndex],
      content,
      attachments,
      submitted_at: new Date().toISOString(),
      // 清除之前的批改结果
      score: undefined,
      feedback: undefined,
      graded_at: undefined,
    };
    saveData(STORAGE_KEYS.SUBMISSIONS, submissions);
    return submissions[submissionIndex];
  } else {
    // 创建新的提交
    const newSubmission: HomeworkSubmission = {
      id: uuidv4(),
      homework_id: homeworkId,
      student_id: studentId,
      content,
      attachments,
      submitted_at: new Date().toISOString(),
    };

    submissions.push(newSubmission);
    saveData(STORAGE_KEYS.SUBMISSIONS, submissions);
    return newSubmission;
  }
}

// ==================== 课程资源管理 ====================

// 获取课程的所有文件夹和文件
export async function getCourseResources(courseId: string) {
  initializeData();
  const folders = getData<CourseFolder>(STORAGE_KEYS.FOLDERS);
  const files = getData<CourseFile>(STORAGE_KEYS.FILES);

  const courseFolders = folders.filter(f => f.course_id === courseId);
  
  // 为每个文件夹获取其文件
  const foldersWithFiles = courseFolders.map(folder => {
    const folderFiles = files.filter(f => f.folder_id === folder.id);
    return {
      ...folder,
      files: folderFiles,
      file_count: folderFiles.length,
    };
  });

  return {
    folders: foldersWithFiles,
    total: foldersWithFiles.length,
  };
}

// 创建文件夹
export async function createFolder(courseId: string, name: string) {
  initializeData();
  const folders = getData<CourseFolder>(STORAGE_KEYS.FOLDERS);

  // 检查同一课程下是否有重名文件夹
  if (folders.some(f => f.course_id === courseId && f.name === name)) {
    throw new Error('文件夹名称已存在');
  }

  const newFolder: CourseFolder = {
    id: uuidv4(),
    course_id: courseId,
    name,
    created_at: new Date().toISOString(),
  };

  folders.push(newFolder);
  saveData(STORAGE_KEYS.FOLDERS, folders);

  return newFolder;
}

// 删除文件夹（会同时删除文件夹内的所有文件）
export async function deleteFolder(folderId: string) {
  initializeData();
  const folders = getData<CourseFolder>(STORAGE_KEYS.FOLDERS);
  const files = getData<CourseFile>(STORAGE_KEYS.FILES);

  // 删除文件夹
  const filteredFolders = folders.filter(f => f.id !== folderId);
  saveData(STORAGE_KEYS.FOLDERS, filteredFolders);

  // 删除文件夹内的所有文件
  const filteredFiles = files.filter(f => f.folder_id !== folderId);
  saveData(STORAGE_KEYS.FILES, filteredFiles);

  return { message: '删除成功' };
}

// 上传文件
export async function uploadFile(
  folderId: string,
  courseId: string,
  name: string,
  size: number,
  type: string,
  content: string
) {
  initializeData();
  const files = getData<CourseFile>(STORAGE_KEYS.FILES);
  const folders = getData<CourseFolder>(STORAGE_KEYS.FOLDERS);

  // 检查文件夹是否存在
  const folder = folders.find(f => f.id === folderId);
  if (!folder) {
    throw new Error('文件夹不存在');
  }

  // 检查同一文件夹下是否有重名文件
  if (files.some(f => f.folder_id === folderId && f.name === name)) {
    throw new Error('文件名称已存在');
  }

  const newFile: CourseFile = {
    id: uuidv4(),
    folder_id: folderId,
    course_id: courseId,
    name,
    size,
    type,
    content,
    created_at: new Date().toISOString(),
  };

  files.push(newFile);
  saveData(STORAGE_KEYS.FILES, files);

  return newFile;
}

// 删除文件
export async function deleteFile(fileId: string) {
  initializeData();
  const files = getData<CourseFile>(STORAGE_KEYS.FILES);

  const filteredFiles = files.filter(f => f.id !== fileId);
  saveData(STORAGE_KEYS.FILES, filteredFiles);

  return { message: '删除成功' };
}

// 下载文件（返回文件信息）
export async function downloadFile(fileId: string) {
  initializeData();
  const files = getData<CourseFile>(STORAGE_KEYS.FILES);

  const file = files.find(f => f.id === fileId);
  if (!file) {
    throw new Error('文件不存在');
  }

  return file;
}

// 更新文件内容
export async function updateFile(fileId: string, content: string) {
  initializeData();
  const files = getData<CourseFile>(STORAGE_KEYS.FILES);

  const fileIndex = files.findIndex(f => f.id === fileId);
  if (fileIndex === -1) {
    throw new Error('文件不存在');
  }

  // 更新文件内容
  files[fileIndex].content = content;
  saveData(STORAGE_KEYS.FILES, files);

  return files[fileIndex];
}

// 获取学生（通过学号）
export async function getStudent(studentId: string) {
  initializeData();
  const students = getData<Student>(STORAGE_KEYS.STUDENTS);
  
  const student = students.find(s => s.id === studentId);
  if (!student) {
    throw new Error('学生不存在');
  }

  return student;
}