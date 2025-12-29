import { useState, useEffect } from 'react';
import { Plus, Search, X } from 'lucide-react';
import { toast } from 'sonner@2.0.3';
import api, { Student } from '../../utils/api-client';

interface CourseStudent {
  id: string;  // User ID
  student_no: string; // 学号
  name: string; // 姓名
  class: string; // 班级
  gender: string; // 性别
  enrolled_at?: string;
}

interface StudentManagementProps {
  courseId: string;
  courseName: string;
}

export function StudentManagement({ courseId, courseName }: StudentManagementProps) {
  const [courseStudents, setCourseStudents] = useState<CourseStudent[]>([]);
  const [showAddModal, setShowAddModal] = useState(false);
  const [allStudents, setAllStudents] = useState<Student[]>([]);
  const [classList, setClassList] = useState<string[]>([]); // 班级列表
  const [loading, setLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [removingStudent, setRemovingStudent] = useState<{ id: string; name: string } | null>(null);
  const [classFilter, setClassFilter] = useState<string>('all'); // 班级筛选
  const [selectedStudents, setSelectedStudents] = useState<Set<string>>(new Set()); // 已选择的学生ID（这里的ID是student表的ID，不是user表的ID）

  // 加载课程学员列表
  const loadCourseStudents = async () => {
    try {
      const result = await api.getCourseStudents(courseId);
      console.log('✅ 获取课程学员成功:', result);
      if (result.success && result.data) {
        setCourseStudents(result.data.students || []);
      } else {
        toast.error(result.error || '获取课程学员失败');
      }
    } catch (error) {
      console.error('❌ 获取课程学员失败:', error);
      toast.error('获取课程学员失败');
    }
  };

  // 初始化：加载课程学员
  useEffect(() => {
    loadCourseStudents();
  }, [courseId]);

  // 加载班级列表
  const loadClassList = async () => {
    try {
      const result = await api.getClassList();
      console.log('✅ 获取班级列表成功:', result);
      if (result.success && result.data) {
        setClassList(result.data.classes || []);
      }
    } catch (error) {
      console.error('❌ 获取班级列表失败:', error);
    }
  };

  // 获取所有学生（分页获取全部）
  const fetchAllStudents = async () => {
    setLoading(true);
    try {
      // 分页获取所有学生（每次100个）
      let allStudentsList: Student[] = [];
      let page = 1;
      const pageSize = 100;
      let hasMore = true;

      while (hasMore) {
        const result = await api.getStudents(page, pageSize);
        if (result.success && result.data) {
          allStudentsList = [...allStudentsList, ...result.data.students];
          hasMore = result.data.students.length === pageSize;
          page++;
        } else {
          hasMore = false;
          if (page === 1) {
            toast.error(result.error || '获取学生列表失败');
          }
        }
      }

      console.log('✅ 获取学生列表成功:', { total: allStudentsList.length });
      setAllStudents(allStudentsList);
    } catch (error) {
      console.error('❌ 获取学生列表失败:', error);
      toast.error('获取学生列表失败');
      setAllStudents([]);
    } finally {
      setLoading(false);
    }
  };

  // 打开添加学员弹窗
  const handleOpenAddModal = async () => {
    setShowAddModal(true);
    setSearchTerm('');
    setClassFilter('all');
    setSelectedStudents(new Set());
    // 并行加载班级列表、课程学员和全部学生
    await Promise.all([
      loadClassList(),
      loadCourseStudents(), // 重新加载课程学员，确保数据最新
      fetchAllStudents()
    ]);
  };

  // 搜索处理
  const handleSearch = (query: string) => {
    setSearchTerm(query);
  };

  // 班级筛选处理
  const handleClassFilter = (className: string) => {
    setClassFilter(className);
    setSelectedStudents(new Set()); // 切换班级时清空选择
  };

  // 添加学员到课程
  const handleAddStudent = async (student: Student & { user_id?: string }) => {
    // 检查是否已添加（通过学号比较）
    const alreadyAdded = courseStudents.some(s => s.student_no === student.student_no);
    if (alreadyAdded) {
      toast.warning('该学员已在课程中');
      return;
    }

    try {
      // 使用student.id
      const result = await api.addStudentToCourse(courseId, student.id);
      if (result.success) {
        toast.success(`已添加学员：${student.name}（${student.student_no}）`);
        // 重新加载课程学员列表
        await loadCourseStudents();
      } else {
        toast.error(result.error || '添加学员失败');
      }
    } catch (error: any) {
      console.error('❌ 添加学员失败:', error);
      toast.error(error.message || '添加学员失败');
    }
  };

  // 移除学员
  const handleRemoveStudent = async (studentId: string, name: string) => {
    // 显示确认对话框
    setRemovingStudent({ id: studentId, name });
  };

  // 确认移除学员
  const confirmRemoveStudent = async () => {
    if (!removingStudent) return;

    console.log('🗑️ 确认移除学员:', removingStudent);

    try {
      console.log('正在调用 removeStudentFromCourse...');
      const result = await api.removeStudentFromCourse(courseId, removingStudent.id);
      if (result.success) {
        console.log('✅ 移除成功');
        toast.success('学员已移除');
        // 重新加载课程学员列表
        await loadCourseStudents();
      } else {
        toast.error(result.error || '移除学员失败');
      }
    } catch (error: any) {
      console.error('❌ 移除学员失败:', error);
      toast.error(error.message || '移除学员失败');
    } finally {
      setRemovingStudent(null);
    }
  };

  // 过滤可添加的学生（排除已添加的，通过学号比较）
  const availableStudents = allStudents.filter(student => {
    return !courseStudents.some(cs => cs.student_no === student.student_no);
  });

  // 按班级筛选和搜索词过滤学生
  const filteredStudents = availableStudents.filter(student => {
    // 班级筛选
    if (classFilter !== 'all' && student.class !== classFilter) {
      return false;
    }
    
    // 搜索词匹配（学号、姓名、班级）
    if (searchTerm) {
      const searchLower = searchTerm.toLowerCase();
      const matchesStudentNo = student.student_no.toLowerCase().includes(searchLower);
      const matchesName = student.name.toLowerCase().includes(searchLower);
      const matchesClass = student.class.toLowerCase().includes(searchLower);
      return matchesStudentNo || matchesName || matchesClass;
    }
    
    return true;
  });

  // 切换单个学生选择
  const toggleStudentSelection = (studentId: string) => {
    const newSelection = new Set(selectedStudents);
    if (newSelection.has(studentId)) {
      newSelection.delete(studentId);
    } else {
      newSelection.add(studentId);
    }
    setSelectedStudents(newSelection);
  };

  // 全选/取消全选
  const toggleSelectAll = () => {
    if (selectedStudents.size === filteredStudents.length) {
      // 如果全部已选，则清空
      setSelectedStudents(new Set());
    } else {
      // 否则选择全部
      const allIds = new Set(filteredStudents.map(s => s.id));
      setSelectedStudents(allIds);
    }
  };

  // 批量添加学员
  const handleBatchAddStudents = async () => {
    if (selectedStudents.size === 0) {
      toast.warning('请至少选择一个学员');
      return;
    }

    const studentIds = Array.from(selectedStudents);
    try {
      const result = await api.batchAddStudents(courseId, studentIds);
      if (result.success && result.data) {
        toast.success(`成功添加 ${result.data.added_count} 个学员`);
        await loadCourseStudents();
        setSelectedStudents(new Set());
        if (result.data.failed_count > 0) {
          toast.warning(`${result.data.failed_count} 个学员添加失败`);
        }
      } else {
        toast.error(result.error || '批量添加失败');
      }
    } catch (error: any) {
      console.error('批量添加学员失败:', error);
      toast.error(error.message || '批量添加失败');
    }
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-gray-700">课程学员</h3>
        <button
          onClick={handleOpenAddModal}
          className="flex items-center gap-2 px-3 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition text-sm"
        >
          <Plus size={16} />
          添加学员
        </button>
      </div>

      {/* 学员列表 */}
      <div className="space-y-2">
        {courseStudents.length === 0 ? (
          <div className="text-center py-8 text-gray-400">
            <p>暂无学员</p>
            <p className="text-sm mt-1">点击"添加学员"按钮添加学员到课程</p>
          </div>
        ) : (
          courseStudents.map((student) => (
            <div
              key={student.id}
              className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition"
            >
              <div>
                <p className="text-gray-800">
                  {student.name} <span className="text-gray-500">({student.student_no})</span>
                </p>
                <div className="flex gap-4 mt-1">
                  <p className="text-gray-500 text-sm">
                    班级：{student.class}
                  </p>
                  <p className="text-gray-500 text-sm">
                    性别：{student.gender}
                  </p>
                </div>
                {student.enrolled_at && (
                  <p className="text-gray-500 text-sm mt-1">
                    加入时间：{new Date(student.enrolled_at).toLocaleString('zh-CN')}
                  </p>
                )}
              </div>
              <button
                onClick={() => handleRemoveStudent(student.id, student.name)}
                className="text-red-600 hover:text-red-700 text-sm"
              >
                移除
              </button>
            </div>
          ))
        )}
      </div>

      {/* 添加学员弹窗 */}
      {showAddModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg w-full max-w-md max-h-[80vh] flex flex-col">
            {/* 弹窗头部 */}
            <div className="flex items-center justify-between p-4 border-b border-gray-200">
              <h3 className="text-gray-800">添加学员到「{courseName}」</h3>
              <button
                onClick={() => {
                  setShowAddModal(false);
                  setSearchTerm('');
                }}
                className="text-gray-400 hover:text-gray-600"
              >
                <X size={20} />
              </button>
            </div>

            {/* 搜索框和班级筛选 */}
            <div className="p-4 border-b border-gray-200 space-y-3">
              {/* 搜索框 */}
              <div className="relative">
                <Search size={18} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                <input
                  type="text"
                  value={searchTerm}
                  onChange={(e) => handleSearch(e.target.value)}
                  placeholder="搜索学号、姓名或班级..."
                  className="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                />
              </div>

              {/* 班级筛选 */}
              <div className="flex items-center gap-2">
                <span className="text-sm text-gray-600 whitespace-nowrap">班级筛选：</span>
                <div className="flex gap-2 flex-wrap">
                  <button
                    onClick={() => handleClassFilter('all')}
                    className={`px-3 py-1 text-sm rounded transition ${
                      classFilter === 'all'
                        ? 'bg-indigo-600 text-white'
                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                    }`}
                  >
                    全部
                  </button>
                  {classList.map((className) => (
                    <button
                      key={className}
                      onClick={() => handleClassFilter(className)}
                      className={`px-3 py-1 text-sm rounded transition ${
                        classFilter === className
                          ? 'bg-indigo-600 text-white'
                          : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                      }`}
                    >
                      {className}
                    </button>
                  ))}
                </div>
              </div>

              {/* 全选和批量操作 */}
              {filteredStudents.length > 0 && (
                <div className="flex items-center justify-between pt-2 border-t border-gray-200">
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={selectedStudents.size === filteredStudents.length && filteredStudents.length > 0}
                      onChange={toggleSelectAll}
                      className="w-4 h-4 text-indigo-600 rounded focus:ring-2 focus:ring-indigo-500"
                    />
                    <span className="text-sm text-gray-700">
                      全选 ({selectedStudents.size}/{filteredStudents.length})
                    </span>
                  </label>
                  {selectedStudents.size > 0 && (
                    <button
                      onClick={handleBatchAddStudents}
                      className="px-4 py-1 bg-indigo-600 text-white rounded text-sm hover:bg-indigo-700 transition"
                    >
                      批量添加 ({selectedStudents.size})
                    </button>
                  )}
                </div>
              )}
            </div>

            {/* 学生列表 */}
            <div className="flex-1 overflow-y-auto p-4">
              {loading ? (
                <div className="text-center py-8 text-gray-400">加载中...</div>
              ) : availableStudents.length === 0 ? (
                <div className="text-center py-8 text-gray-400">
                  <p>没有可添加的学生</p>
                  {searchTerm ? (
                    <p className="text-sm mt-1">尝试搜索其他学号或姓名</p>
                  ) : (
                    <p className="text-sm mt-1">所有学生都已添加到课程</p>
                  )}
                </div>
              ) : filteredStudents.length === 0 ? (
                <div className="text-center py-8 text-gray-400">
                  <p>当前筛选条件下没有学生</p>
                  <p className="text-sm mt-1">尝试更改筛选条件或搜索词</p>
                </div>
              ) : (
                <>
                  <div className="mb-2 text-sm text-gray-600">
                    显示 {filteredStudents.length} 个学生
                  </div>
                  <div className="space-y-2">
                    {filteredStudents.map((student) => (
                      <div
                        key={student.id}
                        className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition"
                      >
                        <input
                          type="checkbox"
                          checked={selectedStudents.has(student.id)}
                          onChange={() => toggleStudentSelection(student.id)}
                          className="w-4 h-4 text-indigo-600 rounded focus:ring-2 focus:ring-indigo-500"
                        />
                        <div className="flex-1">
                          <p className="text-gray-800">
                            {student.name} <span className="text-gray-500">({student.student_no})</span>
                          </p>
                          <div className="flex gap-4">
                            <p className="text-gray-500 text-sm">
                              班级：{student.class}
                            </p>
                            <p className="text-gray-500 text-sm">
                              性别：{student.gender}
                            </p>
                          </div>
                        </div>
                        <button
                          onClick={() => handleAddStudent(student)}
                          className="px-3 py-1 bg-indigo-600 text-white rounded text-sm hover:bg-indigo-700 transition"
                        >
                          添加
                        </button>
                      </div>
                    ))}
                  </div>
                </>
              )}
            </div>
          </div>
        </div>
      )}

      {/* 移除学员确认对话框 */}
      {removingStudent && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg p-6 w-full max-w-sm">
            <h3 className="text-gray-800 mb-4">确认移除学员</h3>
            <p className="text-gray-600 mb-6">
              确定要将学员 <span className="font-semibold text-gray-800">"{removingStudent.name}"</span> 从课程中移除吗？
            </p>
            <div className="flex gap-3">
              <button
                onClick={confirmRemoveStudent}
                className="flex-1 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition"
              >
                确认移除
              </button>
              <button
                onClick={() => setRemovingStudent(null)}
                className="flex-1 px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition"
              >
                取消
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}