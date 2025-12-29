import { useState, useEffect } from 'react';
import { BookOpen, LogOut, FileText, User, Mail } from 'lucide-react';
import { CourseList, Course } from './teacher/course-list';
import { CourseDetail } from './teacher/course-detail';
import api, { Teacher } from '../utils/api-client';
import { toast } from 'sonner@2.0.3';

interface TeacherPageProps {
  username: string;
  userId: string;  // 教师 UUID
  onLogout: () => void;
}

export function TeacherPage({ username, userId, onLogout }: TeacherPageProps) {
  const [activeMenu, setActiveMenu] = useState<'courses' | 'others'>('courses');
  const [selectedCourse, setSelectedCourse] = useState<Course | null>(null);
  const [teacherInfo, setTeacherInfo] = useState<Teacher | null>(null);
  const [showTeacherInfo, setShowTeacherInfo] = useState(false); // 控制教师信息弹窗

  // 加载教师信息
  useEffect(() => {
    const loadTeacherInfo = async () => {
      try {
        const result = await api.getTeacherByUserId(userId);
        if (result.success && result.data) {
          console.log('✅ 获取教师信息成功:', result.data);
          setTeacherInfo(result.data);
        } else {
          console.error('❌ 获取教师信息失败:', result.error);
          toast.error(result.error || '获取教师信息失败');
        }
      } catch (error) {
        console.error('❌ 获取教师信息失败:', error);
        toast.error('获取教师信息失败');
      }
    };

    loadTeacherInfo();
  }, [userId]);

  // 选择课程
  const handleSelectCourse = (course: Course) => {
    setSelectedCourse(course);
  };

  // 返回课程列表
  const handleBackToCourseList = () => {
    setSelectedCourse(null);
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      {/* 顶部导航栏 */}
      <header className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-indigo-600 rounded-lg flex items-center justify-center">
              <BookOpen className="text-white" size={24} />
            </div>
            <div>
              <h1 className="text-gray-800">教师工作台</h1>
              <p className="text-gray-500 text-sm">
                欢迎回来，{teacherInfo?.name || username} 老师
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            {/* 教师信息卡片 */}
            {teacherInfo && (
              <button
                onClick={() => setShowTeacherInfo(true)}
                className="flex items-center gap-3 px-4 py-2 bg-gray-50 hover:bg-gray-100 rounded-lg transition"
              >
                <div className="w-8 h-8 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-full flex items-center justify-center">
                  <User className="text-white" size={16} />
                </div>
                <div className="text-left">
                  <p className="text-gray-800 text-sm">{teacherInfo.name}</p>
                  <p className="text-gray-500 text-xs">{teacherInfo.teacher_no}</p>
                </div>
              </button>
            )}

            <button
              onClick={onLogout}
              className="flex items-center gap-2 px-4 py-2 text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-lg transition"
            >
              <LogOut size={20} />
              <span>退出登录</span>
            </button>
          </div>
        </div>
      </header>

      {/* 教师信息详情弹窗 */}
      {showTeacherInfo && teacherInfo && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg w-full max-w-md p-6">
            {/* 头部 */}
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-gray-800">教师信息</h3>
              <button
                onClick={() => setShowTeacherInfo(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <span className="text-xl">×</span>
              </button>
            </div>

            {/* 教师信息内容 */}
            <div className="space-y-4">
              {/* 头像 */}
              <div className="flex justify-center">
                <div className="w-20 h-20 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-full flex items-center justify-center">
                  <User className="text-white" size={40} />
                </div>
              </div>

              {/* 信息列表 */}
              <div className="space-y-3">
                <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
                  <User size={20} className="text-gray-400" />
                  <div className="flex-1">
                    <p className="text-gray-500 text-sm">姓名</p>
                    <p className="text-gray-800">{teacherInfo.name}</p>
                  </div>
                </div>

                <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
                  <BookOpen size={20} className="text-gray-400" />
                  <div className="flex-1">
                    <p className="text-gray-500 text-sm">工号</p>
                    <p className="text-gray-800">{teacherInfo.teacher_no}</p>
                  </div>
                </div>

                <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
                  <User size={20} className="text-gray-400" />
                  <div className="flex-1">
                    <p className="text-gray-500 text-sm">性别</p>
                    <p className="text-gray-800">{teacherInfo.gender}</p>
                  </div>
                </div>

                <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
                  <Mail size={20} className="text-gray-400" />
                  <div className="flex-1">
                    <p className="text-gray-500 text-sm">邮箱</p>
                    <p className="text-gray-800">{teacherInfo.email}</p>
                  </div>
                </div>
              </div>

              {/* 关闭按钮 */}
              <button
                onClick={() => setShowTeacherInfo(false)}
                className="w-full px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition mt-4"
              >
                关闭
              </button>
            </div>
          </div>
        </div>
      )}

      {/* 主体区域 */}
      <div className="flex flex-1">
        {/* 左侧导航 */}
        <aside className="w-64 bg-white border-r border-gray-200 p-4">
          <nav className="space-y-2">
            <button
              onClick={() => {
                setActiveMenu('courses');
                setSelectedCourse(null);
              }}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition ${
                activeMenu === 'courses'
                  ? 'bg-indigo-50 text-indigo-600'
                  : 'text-gray-700 hover:bg-gray-50'
              }`}
            >
              <BookOpen size={20} />
              <span>课程管理</span>
            </button>
            <button
              onClick={() => setActiveMenu('others')}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition ${
                activeMenu === 'others'
                  ? 'bg-indigo-50 text-indigo-600'
                  : 'text-gray-700 hover:bg-gray-50'
              }`}
            >
              <FileText size={20} />
              <span>其他功能</span>
              <span className="ml-auto text-xs bg-gray-200 text-gray-600 px-2 py-1 rounded">敬请期待</span>
            </button>
          </nav>
        </aside>

        {/* 右侧内容区 */}
        <main className="flex-1 p-6">
          {activeMenu === 'courses' && (
            <>
              {!selectedCourse ? (
                <CourseList
                  teacherId={userId}
                  onSelectCourse={handleSelectCourse}
                />
              ) : (
                <CourseDetail
                  course={selectedCourse}
                  onBack={handleBackToCourseList}
                />
              )}
            </>
          )}

          {activeMenu === 'others' && (
            <div className="flex items-center justify-center h-full">
              <div className="text-center">
                <FileText size={64} className="text-gray-300 mx-auto mb-4" />
                <p className="text-gray-500">其他功能正在开发中</p>
                <p className="text-gray-400 text-sm mt-2">敬请期待...</p>
              </div>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}