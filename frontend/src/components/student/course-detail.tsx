import { useState } from 'react';
import { ArrowLeft, FileText, BookOpen } from 'lucide-react';
import { StudentCourse } from './course-list';
import { HomeworkList } from './homework-list';
import { CourseResources } from './course-resources';

interface CourseDetailProps {
  course: StudentCourse;
  studentId: string;
  onBack: () => void;
}

type TabType = 'resources' | 'homework' | 'others';

export function CourseDetail({ course, studentId, onBack }: CourseDetailProps) {
  const [activeTab, setActiveTab] = useState<TabType>('homework');

  return (
    <div>
      {/* 头部 */}
      <div className="mb-6">
        <button
          onClick={onBack}
          className="flex items-center gap-2 text-gray-600 hover:text-gray-800 mb-4"
        >
          <ArrowLeft size={20} />
          <span>返回课程列表</span>
        </button>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-start gap-4">
            <div className="w-16 h-16 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-lg flex items-center justify-center flex-shrink-0">
              <BookOpen className="text-white" size={32} />
            </div>
            <div className="flex-1">
              <h2 className="text-gray-800 mb-2">{course.name}</h2>
              <p className="text-gray-600 mb-3">{course.description}</p>
              <div className="flex items-center gap-4 text-sm text-gray-500">
                <span>授课教师：{course.teacher_name}</span>
                <span>•</span>
                <span>{course.student_count} 名学员</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* 标签页导航 */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 mb-6">
        <div className="flex border-b border-gray-200">
          <button
            onClick={() => setActiveTab('resources')}
            className={`flex items-center gap-2 px-6 py-4 border-b-2 transition ${
              activeTab === 'resources'
                ? 'border-indigo-600 text-indigo-600'
                : 'border-transparent text-gray-600 hover:text-gray-800'
            }`}
          >
            <BookOpen size={18} />
            <span>课程资源</span>
          </button>
          <button
            onClick={() => setActiveTab('homework')}
            className={`flex items-center gap-2 px-6 py-4 border-b-2 transition ${
              activeTab === 'homework'
                ? 'border-indigo-600 text-indigo-600'
                : 'border-transparent text-gray-600 hover:text-gray-800'
            }`}
          >
            <FileText size={18} />
            <span>课程作业</span>
          </button>
          <button
            onClick={() => setActiveTab('others')}
            className={`flex items-center gap-2 px-6 py-4 border-b-2 transition ${
              activeTab === 'others'
                ? 'border-indigo-600 text-indigo-600'
                : 'border-transparent text-gray-600 hover:text-gray-800'
            }`}
          >
            <FileText size={18} />
            <span>其他</span>
            <span className="text-xs bg-gray-200 text-gray-600 px-2 py-0.5 rounded">待定</span>
          </button>
        </div>
      </div>

      {/* 标签页内容 */}
      <div>
        {activeTab === 'resources' && (
          <CourseResources courseId={course.id} />
        )}
        {activeTab === 'homework' && (
          <HomeworkList studentId={studentId} courseId={course.id} />
        )}
        {activeTab === 'others' && (
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-12">
            <div className="text-center">
              <FileText size={64} className="text-gray-300 mx-auto mb-4" />
              <p className="text-gray-500">其他功能待定</p>
              <p className="text-gray-400 text-sm mt-2">可以添加课程讨论、课程通知等功能</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
