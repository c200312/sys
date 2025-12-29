import { useState, useEffect } from 'react';
import { BookOpen, User, ChevronRight } from 'lucide-react';
import { toast } from 'sonner@2.0.3';
import api from '../../utils/api-client';

export interface StudentCourse {
  id: string;
  name: string;
  description: string;
  teacher_id: string;
  teacher_name: string;
  teacher_no: string;
  student_count: number;
  enrolled_at: string;
  created_at: string;
}

interface CourseListProps {
  studentId: string;  // Student 表的 ID
  userId: string;     // User 表的 ID
  onSelectCourse: (course: StudentCourse) => void;
}

export function CourseList({ studentId, userId, onSelectCourse }: CourseListProps) {
  const [courses, setCourses] = useState<StudentCourse[]>([]);
  const [loading, setLoading] = useState(true);

  // 加载课程列表
  useEffect(() => {
    if (studentId) {
      loadCourses();
    }
  }, [studentId]);

  const loadCourses = async () => {
    if (!studentId) return;
    setLoading(true);
    try {
      const result = await api.getStudentCourses(studentId);
      console.log('✅ 获取学生课程成功:', result);
      if (result.success && result.data) {
        setCourses(result.data.courses as StudentCourse[]);
      } else {
        toast.error(result.error || '获取课程列表失败');
      }
    } catch (error: any) {
      console.error('❌ 获取学生课程失败:', error);
      toast.error('获取课程列表失败');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-gray-400">加载中...</div>
      </div>
    );
  }

  if (courses.length === 0) {
    return (
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-12">
        <div className="text-center">
          <BookOpen size={64} className="text-gray-300 mx-auto mb-4" />
          <p className="text-gray-500 mb-2">还没有加入任何课程</p>
          <p className="text-gray-400 text-sm">
            请联系教师将您添加到课程中
          </p>
        </div>
      </div>
    );
  }

  return (
    <div>
      <div className="mb-6">
        <h2 className="text-gray-800">我的课程</h2>
        <p className="text-gray-500 text-sm mt-1">
          共 {courses.length} 门课程
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {courses.map((course) => (
          <div
            key={course.id}
            onClick={() => onSelectCourse(course)}
            className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 hover:shadow-md hover:border-indigo-200 transition cursor-pointer group"
          >
            {/* 课程图标 */}
            <div className="w-12 h-12 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-lg flex items-center justify-center mb-4">
              <BookOpen className="text-white" size={24} />
            </div>

            {/* 课程名称 */}
            <h3 className="text-gray-800 mb-2 group-hover:text-indigo-600 transition">
              {course.name}
            </h3>

            {/* 课程描述 */}
            <p className="text-gray-500 text-sm mb-4 line-clamp-2">
              {course.description}
            </p>

            {/* 授课教师 */}
            <div className="flex items-center gap-2 text-gray-600 text-sm mb-3">
              <User size={16} />
              <span>授课教师：{course.teacher_name}</span>
            </div>

            {/* 底部信息 */}
            <div className="flex items-center justify-between pt-4 border-t border-gray-100">
              <span className="text-gray-400 text-xs">
                {course.student_count} 名学员
              </span>
              <div className="flex items-center gap-1 text-indigo-600 text-sm group-hover:gap-2 transition-all">
                <span>进入课程</span>
                <ChevronRight size={16} />
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
