import { useState } from 'react';
import { Users, FileText, Sparkles, FolderOpen } from 'lucide-react';
import { Course } from './course-list';
import { StudentManagement } from './student-management';
import { HomeworkManagement } from './homework-management';
import { AIAssistant } from './ai-assistant';
import { CourseResources } from './course-resources';

interface CourseDetailProps {
  course: Course;
  onBack: () => void;
}

export function CourseDetail({ course, onBack }: CourseDetailProps) {
  const [activeTab, setActiveTab] = useState<'students' | 'resources' | 'homework' | 'ai'>('students');

  return (
    <div>
      <div className="flex items-center gap-3 mb-6">
        <button
          onClick={onBack}
          className="text-gray-600 hover:text-gray-800"
        >
          ← 返回
        </button>
        <h2 className="text-gray-800">{course.name}</h2>
      </div>

      {/* 课程详情标签页 */}
      <div className="bg-white rounded-lg border border-gray-200">
        {/* 标签导航 */}
        <div className="border-b border-gray-200 flex">
          <button
            onClick={() => setActiveTab('students')}
            className={`px-6 py-3 ${
              activeTab === 'students'
                ? 'border-b-2 border-indigo-600 text-indigo-600'
                : 'text-gray-600 hover:text-gray-800'
            }`}
          >
            <Users size={18} className="inline mr-2" />
            学员管理
          </button>
          <button
            onClick={() => setActiveTab('resources')}
            className={`px-6 py-3 ${
              activeTab === 'resources'
                ? 'border-b-2 border-indigo-600 text-indigo-600'
                : 'text-gray-600 hover:text-gray-800'
            }`}
          >
            <FolderOpen size={18} className="inline mr-2" />
            课程资源
          </button>
          <button
            onClick={() => setActiveTab('homework')}
            className={`px-6 py-3 ${
              activeTab === 'homework'
                ? 'border-b-2 border-indigo-600 text-indigo-600'
                : 'text-gray-600 hover:text-gray-800'
            }`}
          >
            <FileText size={18} className="inline mr-2" />
            作业管理
          </button>
          <button
            onClick={() => setActiveTab('ai')}
            className={`px-6 py-3 ${
              activeTab === 'ai'
                ? 'border-b-2 border-indigo-600 text-indigo-600'
                : 'text-gray-600 hover:text-gray-800'
            }`}
          >
            <Sparkles size={18} className="inline mr-2" />
            AI助手
          </button>
        </div>

        {/* 标签内容 */}
        <div className="p-6">
          {activeTab === 'students' && (
            <StudentManagement courseId={course.id} courseName={course.name} />
          )}
          {activeTab === 'resources' && (
            <CourseResources courseId={course.id} />
          )}
          {activeTab === 'homework' && (
            <HomeworkManagement courseId={course.id} courseName={course.name} />
          )}
          {activeTab === 'ai' && (
            <AIAssistant courseId={course.id} courseName={course.name} />
          )}
        </div>
      </div>
    </div>
  );
}