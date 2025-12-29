import { useState, useEffect } from 'react';
import { BookOpen, LogOut, User, Sparkles } from 'lucide-react';
import { toast } from 'sonner@2.0.3';
import api, { Student } from '../utils/api-client';
import { CourseList, StudentCourse } from './student/course-list';
import { CourseDetail } from './student/course-detail';
import { StudentAIAssistant } from './student/ai-assistant';

interface StudentPageProps {
  username: string;
  userId: string;
  onLogout: () => void;
}

type MenuTab = 'courses' | 'ai-assistant';

export function StudentPage({ username, userId, onLogout }: StudentPageProps) {
  const [studentInfo, setStudentInfo] = useState<Student | null>(null);
  const [showStudentInfo, setShowStudentInfo] = useState(false);
  const [selectedCourse, setSelectedCourse] = useState<StudentCourse | null>(null);
  const [activeTab, setActiveTab] = useState<MenuTab>('courses');

  // 加载学生信息
  useEffect(() => {
    const loadStudentInfo = async () => {
      try {
        const result = await api.getStudentByUserId(userId);
        if (result.success && result.data) {
          console.log('✅ 获取学生信息成功:', result.data);
          setStudentInfo(result.data);
        } else {
          console.error('❌ 获取学生信息失败:', result.error);
          toast.error(result.error || '获取学生信息失败');
        }
      } catch (error) {
        console.error('❌ 获取学生信息失败:', error);
        toast.error('获取学生信息失败');
      }
    };

    loadStudentInfo();
  }, [userId]);

  // 选择课程
  const handleSelectCourse = (course: StudentCourse) => {
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
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-cyan-600 rounded-lg flex items-center justify-center">
              <BookOpen className="text-white" size={24} />
            </div>
            <div>
              <h1 className="text-gray-800">学生学习中心</h1>
              <p className="text-gray-500 text-sm">
                你好，{studentInfo?.name || username} 同学
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            {/* 学生信息卡片 */}
            {studentInfo && (
              <button
                onClick={() => setShowStudentInfo(true)}
                className="flex items-center gap-3 px-4 py-2 bg-gray-50 hover:bg-gray-100 rounded-lg transition"
              >
                <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-cyan-600 rounded-full flex items-center justify-center">
                  <User className="text-white" size={16} />
                </div>
                <div className="text-left">
                  <p className="text-gray-800 text-sm">{studentInfo.name}</p>
                  <p className="text-gray-500 text-xs">{studentInfo.student_no}</p>
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

      {/* 学生信息详情弹窗 */}
      {showStudentInfo && studentInfo && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg w-full max-w-md p-6">
            {/* 头部 */}
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-gray-800">学生信息</h3>
              <button
                onClick={() => setShowStudentInfo(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <span className="text-xl">×</span>
              </button>
            </div>

            {/* 学生信息内容 */}
            <div className="space-y-4">
              {/* 头像 */}
              <div className="flex justify-center">
                <div className="w-20 h-20 bg-gradient-to-br from-blue-500 to-cyan-600 rounded-full flex items-center justify-center">
                  <User className="text-white" size={40} />
                </div>
              </div>

              {/* 信息列表 */}
              <div className="space-y-3">
                <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
                  <User size={20} className="text-gray-400" />
                  <div className="flex-1">
                    <p className="text-gray-500 text-sm">姓名</p>
                    <p className="text-gray-800">{studentInfo.name}</p>
                  </div>
                </div>

                <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
                  <BookOpen size={20} className="text-gray-400" />
                  <div className="flex-1">
                    <p className="text-gray-500 text-sm">学号</p>
                    <p className="text-gray-800">{studentInfo.student_no}</p>
                  </div>
                </div>

                <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
                  <BookOpen size={20} className="text-gray-400" />
                  <div className="flex-1">
                    <p className="text-gray-500 text-sm">班级</p>
                    <p className="text-gray-800">{studentInfo.class}</p>
                  </div>
                </div>

                <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
                  <User size={20} className="text-gray-400" />
                  <div className="flex-1">
                    <p className="text-gray-500 text-sm">性别</p>
                    <p className="text-gray-800">{studentInfo.gender}</p>
                  </div>
                </div>
              </div>

              {/* 关闭按钮 */}
              <button
                onClick={() => setShowStudentInfo(false)}
                className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition mt-4"
              >
                关闭
              </button>
            </div>
          </div>
        </div>
      )}

      {/* 主要内容区 */}
      <div className="flex flex-1 max-w-7xl w-full mx-auto">
        {/* 左侧菜单栏 */}
        <aside className="w-64 bg-white border-r border-gray-200 p-4">
          <nav className="space-y-2">
            <button
              onClick={() => {
                setActiveTab('courses');
                setSelectedCourse(null);
              }}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition ${
                activeTab === 'courses'
                  ? 'bg-blue-50 text-blue-600'
                  : 'text-gray-600 hover:bg-gray-50'
              }`}
            >
              <BookOpen size={20} />
              <span>我的课程</span>
            </button>
            
            <button
              onClick={() => setActiveTab('ai-assistant')}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition ${
                activeTab === 'ai-assistant'
                  ? 'bg-blue-50 text-blue-600'
                  : 'text-gray-600 hover:bg-gray-50'
              }`}
            >
              <Sparkles size={20} />
              <span>AI助手</span>
            </button>
          </nav>
        </aside>

        {/* 右侧内容区 */}
        <main className="flex-1 px-6 py-8 overflow-auto">
          {activeTab === 'courses' ? (
            !selectedCourse ? (
              <CourseList
                studentId={studentInfo?.id || ''}
                userId={userId}
                onSelectCourse={handleSelectCourse}
              />
            ) : (
              <CourseDetail
                course={selectedCourse}
                studentId={studentInfo?.id || ''}
                onBack={handleBackToCourseList}
              />
            )
          ) : (
            <StudentAIAssistant studentId={studentInfo?.id || ''} />
          )}
        </main>
      </div>
    </div>
  );
}