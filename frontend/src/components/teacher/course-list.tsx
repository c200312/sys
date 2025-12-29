import { useState, useEffect } from 'react';
import { Plus, Edit2, Trash2, Users, ChevronRight } from 'lucide-react';
import { toast } from 'sonner@2.0.3';
import api from '../../utils/api-client';

export interface Course {
  id: string;  // UUID
  name: string;
  description: string;
  student_count: number;
  teacher_id: string;
}

interface CourseListProps {
  teacherId: string;  // 教师 UUID
  onSelectCourse: (course: Course) => void;
}

export function CourseList({ teacherId, onSelectCourse }: CourseListProps) {
  const [courses, setCourses] = useState<Course[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCourseForm, setShowCourseForm] = useState(false);
  const [editingCourse, setEditingCourse] = useState<Course | null>(null);
  const [courseName, setCourseName] = useState('');
  const [courseDescription, setCourseDescription] = useState('');

  // 加载课程列表
  const loadCourses = async () => {
    setLoading(true);
    try {
      const result = await api.getCourses();
      console.log('✅ 获取课程列表成功:', result);

      if (result.success && result.data) {
        // 过滤当前教师的课程
        const teacherCourses = result.data.courses?.filter(
          (course: Course) => course.teacher_id === teacherId
        ) || [];

        setCourses(teacherCourses);
      } else {
        toast.error(result.error || '获取课程列表失败');
      }
    } catch (error) {
      console.error('❌ 获取课程列表失败:', error);
      toast.error('获取课程列表失败');
    } finally {
      setLoading(false);
    }
  };

  // 初始化时加载课程
  useEffect(() => {
    loadCourses();
  }, [teacherId]);

  // 创建/编辑课程
  const handleSaveCourse = async () => {
    if (!courseName.trim()) {
      toast.error('请输入课程名称');
      return;
    }

    try {
      if (editingCourse) {
        // 更新课程
        const result = await api.updateCourse(editingCourse.id, {
          name: courseName,
          description: courseDescription,
        });
        if (result.success) {
          toast.success('课程更新成功');
        } else {
          toast.error(result.error || '课程更新失败');
          return;
        }
      } else {
        // 创建新课程
        const result = await api.createCourse({
          name: courseName,
          description: courseDescription,
        });
        if (result.success) {
          toast.success('课程创建成功');
        } else {
          toast.error(result.error || '课程创建失败');
          return;
        }
      }

      // 重新加载课程列表
      await loadCourses();

      setShowCourseForm(false);
      setEditingCourse(null);
      setCourseName('');
      setCourseDescription('');
    } catch (error: any) {
      console.error('❌ 保存课程失败:', error);
      toast.error(error.message || '保存课程失败');
    }
  };

  // 删除课程
  const handleDeleteCourse = async (id: string, name: string) => {
    if (!confirm(`确定要删除课程"${name}"吗？删除后无法恢复。`)) {
      return;
    }

    try {
      const result = await api.deleteCourse(id);
      if (result.success) {
        toast.success('课程删除成功');
        await loadCourses();
      } else {
        toast.error(result.error || '课程删除失败');
      }
    } catch (error: any) {
      console.error('❌ 删除课程失败:', error);
      toast.error(error.message || '删除课程失败');
    }
  };

  // 编辑课程
  const handleEditCourse = (course: Course) => {
    setEditingCourse(course);
    setCourseName(course.name);
    setCourseDescription(course.description);
    setShowCourseForm(true);
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-gray-800">课程列表</h2>
        <button
          onClick={() => setShowCourseForm(true)}
          className="flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition"
        >
          <Plus size={20} />
          创建课程
        </button>
      </div>

      {/* 加载状态 */}
      {loading ? (
        <div className="text-center py-12 text-gray-400">
          <p>加载中...</p>
        </div>
      ) : courses.length === 0 ? (
        <div className="text-center py-12 text-gray-400">
          <p>暂无课程</p>
          <p className="text-sm mt-1">点击"创建课程"按钮开始创建您的第一门课程</p>
        </div>
      ) : (
        /* 课程卡片列表 */
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {courses.map((course) => (
            <div
              key={course.id}
              className="bg-white rounded-lg border border-gray-200 p-5 hover:shadow-md transition"
            >
              <div className="flex items-start justify-between mb-3">
                <h3 className="text-gray-800">{course.name}</h3>
                <div className="flex gap-1">
                  <button
                    onClick={() => handleEditCourse(course)}
                    className="p-1 text-gray-400 hover:text-blue-600 transition"
                    title="编辑"
                  >
                    <Edit2 size={16} />
                  </button>
                  <button
                    onClick={() => handleDeleteCourse(course.id, course.name)}
                    className="p-1 text-gray-400 hover:text-red-600 transition"
                    title="删除"
                  >
                    <Trash2 size={16} />
                  </button>
                </div>
              </div>
              <p className="text-gray-500 text-sm mb-4">
                {course.description || '暂无描述'}
              </p>
              <div className="flex items-center justify-between">
                <span className="text-gray-400 text-sm flex items-center gap-1">
                  <Users size={14} />
                  {course.student_count || 0} 名学员
                </span>
                <button
                  onClick={() => onSelectCourse(course)}
                  className="text-indigo-600 text-sm hover:text-indigo-700 flex items-center gap-1"
                >
                  进入课程
                  <ChevronRight size={14} />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* 创建/编辑课程表单 */}
      {showCourseForm && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h3 className="text-gray-800 mb-4">
              {editingCourse ? '编辑课程' : '创建新课程'}
            </h3>
            <div className="space-y-4">
              <div>
                <label className="block text-gray-700 text-sm mb-2">课程名称</label>
                <input
                  type="text"
                  value={courseName}
                  onChange={(e) => setCourseName(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                  placeholder="输入课程名称"
                />
              </div>
              <div>
                <label className="block text-gray-700 text-sm mb-2">课程描述</label>
                <textarea
                  value={courseDescription}
                  onChange={(e) => setCourseDescription(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                  rows={3}
                  placeholder="输入课程描述"
                />
              </div>
              <div className="flex gap-3">
                <button
                  onClick={handleSaveCourse}
                  className="flex-1 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition"
                >
                  保存
                </button>
                <button
                  onClick={() => {
                    setShowCourseForm(false);
                    setEditingCourse(null);
                    setCourseName('');
                    setCourseDescription('');
                  }}
                  className="flex-1 px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition"
                >
                  取消
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}