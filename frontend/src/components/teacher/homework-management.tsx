import api, { Homework } from '../../utils/api-client';
import { useState, useEffect, useRef } from 'react';
import { Plus, Trash2, FileText, Clock, Paperclip, FileCheck, Edit } from 'lucide-react';
import { toast } from 'sonner@2.0.3';
import { Grading } from './grading';

interface HomeworkManagementProps {
  courseId: string;
  courseName: string;
}

export function HomeworkManagement({ courseId, courseName }: HomeworkManagementProps) {
  const [homeworks, setHomeworks] = useState<Homework[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [editingHomework, setEditingHomework] = useState<Homework | null>(null); // 编辑中的作业
  const [selectedHomework, setSelectedHomework] = useState<Homework | null>(null);
  const [deletingHomework, setDeletingHomework] = useState<Homework | null>(null); // 待删除的作业

  // 表单字段
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [dueDate, setDueDate] = useState('');
  const [dueTime, setDueTime] = useState({ hour: 23, minute: 59 });
  const [attachment, setAttachment] = useState<{
    name: string;
    size: number;
    type: string;
    content: string;
  } | null>(null);
  const [gradingText, setGradingText] = useState('');

  const attachmentInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    loadHomeworks();
    // 设置默认截止日期为明天
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    setDueDate(tomorrow.toISOString().split('T')[0]);
  }, [courseId]);

  const loadHomeworks = async () => {
    setLoading(true);
    try {
      const result = await api.getCourseHomeworks(courseId);
      console.log('✅ 获取作业列表成功:', result);
      if (result.success && result.data) {
        setHomeworks(result.data.homeworks);

        // 如果当前有选中的作业，更新它的数据
        if (selectedHomework) {
          const updatedHomework = result.data.homeworks.find(hw => hw.id === selectedHomework.id);
          if (updatedHomework) {
            setSelectedHomework(updatedHomework);
          }
        }
      } else {
        toast.error(result.error || '获取作业列表失败');
      }
    } catch (error: any) {
      console.error('❌ 获取作业列表失败:', error);
      toast.error('获取作业列表失败');
    } finally {
      setLoading(false);
    }
  };

  // 处理附件上传
  const handleAttachmentChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = () => {
      setAttachment({
        name: file.name,
        size: file.size,
        type: file.type,
        content: reader.result as string,
      });
      toast.success('附件已添加');
    };
    reader.onerror = () => {
      toast.error('文件读取失败');
    };
    reader.readAsDataURL(file);
  };

  // 删除附件
  const handleRemoveAttachment = () => {
    setAttachment(null);
    if (attachmentInputRef.current) {
      attachmentInputRef.current.value = '';
    }
  };

  // 设置时间（时针）
  const setHour = (hour: number) => {
    setDueTime(prev => ({ ...prev, hour }));
  };

  // 设置时间（分针）
  const setMinute = (minute: number) => {
    setDueTime(prev => ({ ...prev, minute }));
  };

  // 创建作业
  const handleCreateHomework = async () => {
    if (!title.trim()) {
      toast.error('请输入作业标题');
      return;
    }
    if (!description.trim()) {
      toast.error('请输入作业描述');
      return;
    }
    if (!dueDate) {
      toast.error('请选择截止日期');
      return;
    }

    try {
      // 构建完整的截止时间
      const fullDueDate = `${dueDate}T${String(dueTime.hour).padStart(2, '0')}:${String(dueTime.minute).padStart(2, '0')}:00`;

      // 构建评分规则（仅文本）
      let gradingCriteria: {
        type: 'text';
        content: string;
      } | undefined;

      if (gradingText.trim()) {
        gradingCriteria = {
          type: 'text',
          content: gradingText.trim(),
        };
      }

      const result = await api.createHomework(courseId, {
        title: title.trim(),
        description: description.trim(),
        deadline: fullDueDate,
        attachment: attachment || undefined,
        grading_criteria: gradingCriteria,
      });

      if (result.success) {
        toast.success('作业布置成功');
        resetForm();
        setShowCreateDialog(false);
        loadHomeworks();
      } else {
        toast.error(result.error || '创建失败');
      }
    } catch (error: any) {
      console.error('❌ 创建作业失败:', error);
      toast.error(error.message || '创建失败');
    }
  };

  // 重置表单
  const resetForm = () => {
    setTitle('');
    setDescription('');
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    setDueDate(tomorrow.toISOString().split('T')[0]);
    setDueTime({ hour: 23, minute: 59 });
    setAttachment(null);
    setGradingText('');
    if (attachmentInputRef.current) attachmentInputRef.current.value = '';
  };

  // 删除作业
  const handleDeleteHomework = async () => {
    if (!deletingHomework) return;

    try {
      const result = await api.deleteHomework(deletingHomework.id);
      if (result.success) {
        toast.success('作业已删除');
        setDeletingHomework(null);
        loadHomeworks();
      } else {
        toast.error(result.error || '删除失败');
      }
    } catch (error: any) {
      console.error('❌ 删除作业失败:', error);
      toast.error(error.message || '删除失败');
    }
  };

  // 格式化文件大小
  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(2) + ' MB';
  };

  // 判断作业是否已截止
  const isOverdue = (dueDate: string): boolean => {
    return new Date(dueDate) < new Date();
  };

  // 分类作业
  const activeHomeworks = homeworks.filter(hw => !isOverdue(hw.deadline));
  const overdueHomeworks = homeworks.filter(hw => isOverdue(hw.deadline));

  // 如果选中了作业，显示批改界面
  if (selectedHomework) {
    return (
      <div>
        <button
          onClick={() => setSelectedHomework(null)}
          className="mb-4 text-gray-600 hover:text-gray-800"
        >
          ← 返回作业列表
        </button>
        <Grading
          courseId={courseId}
          courseName={courseName}
          homeworkId={selectedHomework.id}
          homeworkTitle={selectedHomework.title}
          homework={selectedHomework}
          onHomeworkUpdated={loadHomeworks}
        />
      </div>
    );
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-gray-400">加载中...</div>
      </div>
    );
  }

  return (
    <div>
      {/* 隐藏的文件输入 */}
      <input
        ref={attachmentInputRef}
        type="file"
        className="hidden"
        onChange={handleAttachmentChange}
      />

      {/* 头部 */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-gray-800">作业列表</h3>
          <p className="text-gray-500 text-sm mt-1">
            {homeworks.length} 份作业
          </p>
        </div>
        <button
          onClick={() => setShowCreateDialog(true)}
          className="flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition"
        >
          <Plus size={20} />
          <span>布置作业</span>
        </button>
      </div>

      {/* 作业列表 */}
      {homeworks.length === 0 ? (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-12">
          <div className="text-center">
            <FileText size={64} className="text-gray-300 mx-auto mb-4" />
            <p className="text-gray-500">还没有布置作业</p>
          </div>
        </div>
      ) : (
        <div className="space-y-8">
          {/* 未截止的作业 */}
          {activeHomeworks.length > 0 && (
            <div>
              <div className="flex items-center gap-2 mb-4">
                <div className="w-1 h-6 bg-green-500 rounded"></div>
                <h4 className="text-gray-800">进行中</h4>
                <span className="text-gray-500 text-sm">({activeHomeworks.length})</span>
              </div>
              <div className="space-y-4">
                {activeHomeworks.map((homework) => (
                  <div
                    key={homework.id}
                    className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 hover:shadow-md transition"
                  >
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex items-start gap-3">
                        <div className="w-2 h-2 bg-green-500 rounded-full mt-2"></div>
                        <h4 className="text-gray-800">{homework.title}</h4>
                      </div>
                      <div className="flex items-center gap-2 text-green-600 text-sm">
                        <Clock size={16} />
                        <span>截止：{new Date(homework.deadline).toLocaleString('zh-CN')}</span>
                      </div>
                    </div>

                    <p className="text-gray-600 text-sm mb-3 ml-5">{homework.description}</p>

                    <div className="ml-5 space-y-2">
                      {/* 发布时间 */}
                      <div className="flex items-center gap-2 text-sm text-gray-500">
                        <Clock size={14} />
                        <span>发布：{new Date(homework.created_at).toLocaleString('zh-CN')}</span>
                      </div>

                      {/* 附件显示 */}
                      {homework.attachment && (
                        <div className="flex items-center gap-2 text-sm text-gray-600">
                          <Paperclip size={14} />
                          <span>附件：{homework.attachment.name} ({formatFileSize(homework.attachment.size)})</span>
                        </div>
                      )}

                      {/* 评分规则显示 */}
                      {homework.grading_criteria && (
                        <div className="flex items-center gap-2 text-sm text-gray-600">
                          <FileCheck size={14} />
                          <span>
                            评分规则：
                            {homework.grading_criteria.type === 'text'
                              ? homework.grading_criteria.content
                              : `${homework.grading_criteria.file_name} (${formatFileSize(homework.grading_criteria.file_size || 0)})`
                            }
                          </span>
                        </div>
                      )}
                    </div>

                    {/* 批改按钮 */}
                    <div className="ml-5 mt-4 flex justify-end gap-2">
                      <button
                        onClick={() => setDeletingHomework(homework)}
                        className="flex items-center gap-2 px-4 py-2 text-red-600 hover:bg-red-50 border border-red-200 rounded-lg transition text-sm"
                      >
                        <Trash2 size={16} />
                        <span>删除</span>
                      </button>
                      <button
                        onClick={() => setSelectedHomework(homework)}
                        className="flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition text-sm"
                      >
                        <Edit size={16} />
                        <span>批改作业</span>
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* 已截止的作业 */}
          {overdueHomeworks.length > 0 && (
            <div>
              <div className="flex items-center gap-2 mb-4">
                <div className="w-1 h-6 bg-gray-400 rounded"></div>
                <h4 className="text-gray-800">已截止</h4>
                <span className="text-gray-500 text-sm">({overdueHomeworks.length})</span>
              </div>
              <div className="space-y-4">
                {overdueHomeworks.map((homework) => (
                  <div
                    key={homework.id}
                    className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 opacity-75 hover:opacity-100 transition"
                  >
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex items-start gap-3">
                        <div className="w-2 h-2 bg-gray-400 rounded-full mt-2"></div>
                        <h4 className="text-gray-800">{homework.title}</h4>
                      </div>
                      <div className="flex items-center gap-2 text-gray-500 text-sm">
                        <Clock size={16} />
                        <span>截止：{new Date(homework.deadline).toLocaleString('zh-CN')}</span>
                      </div>
                    </div>

                    <p className="text-gray-600 text-sm mb-3 ml-5">{homework.description}</p>

                    <div className="ml-5 space-y-2">
                      {/* 发布时间 */}
                      <div className="flex items-center gap-2 text-sm text-gray-500">
                        <Clock size={14} />
                        <span>发布：{new Date(homework.created_at).toLocaleString('zh-CN')}</span>
                      </div>

                      {/* 附件显示 */}
                      {homework.attachment && (
                        <div className="flex items-center gap-2 text-sm text-gray-600">
                          <Paperclip size={14} />
                          <span>附件：{homework.attachment.name} ({formatFileSize(homework.attachment.size)})</span>
                        </div>
                      )}

                      {/* 评分规则显示 */}
                      {homework.grading_criteria && (
                        <div className="flex items-center gap-2 text-sm text-gray-600">
                          <FileCheck size={14} />
                          <span>
                            评分规则：
                            {homework.grading_criteria.type === 'text'
                              ? homework.grading_criteria.content
                              : `${homework.grading_criteria.file_name} (${formatFileSize(homework.grading_criteria.file_size || 0)})`
                            }
                          </span>
                        </div>
                      )}
                    </div>

                    {/* 批改按钮 */}
                    <div className="ml-5 mt-4 flex justify-end">
                      <button
                        onClick={() => setSelectedHomework(homework)}
                        className="flex items-center gap-2 px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition text-sm"
                      >
                        <Edit size={16} />
                        <span>批改作业</span>
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* 删除确认对话框 */}
      {deletingHomework && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg w-full max-w-md p-6">
            <h3 className="text-gray-800 mb-4">确认删除作业？</h3>
            <p className="text-gray-600 text-sm mb-2">
              您确定要删除作业「{deletingHomework.title}」吗？
            </p>
            <p className="text-red-600 text-sm mb-6">
              此操作将删除作业及所有学生的提交记录，且无法撤销！
            </p>

            <div className="flex items-center gap-3">
              <button
                onClick={handleDeleteHomework}
                className="flex-1 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition"
              >
                确认删除
              </button>
              <button
                onClick={() => setDeletingHomework(null)}
                className="flex-1 px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition"
              >
                取消
              </button>
            </div>
          </div>
        </div>
      )}

      {/* 布置作业对话框 */}
      {showCreateDialog && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg w-full max-w-4xl max-h-[90vh] overflow-y-auto">
            <div className="flex">
              {/* 左侧：表单区域 */}
              <div className="flex-1 p-6 border-r border-gray-200">
                <h3 className="text-gray-800 mb-6">布置新作业</h3>

                <div className="space-y-4">
                  {/* 作业标题 */}
                  <div>
                    <label className="block text-gray-700 text-sm mb-2">
                      作业标题 <span className="text-red-500">*</span>
                    </label>
                    <input
                      type="text"
                      value={title}
                      onChange={(e) => setTitle(e.target.value)}
                      placeholder="例如：第一章课后习题"
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    />
                  </div>

                  {/* 作业描述 */}
                  <div>
                    <label className="block text-gray-700 text-sm mb-2">
                      作业描述 <span className="text-red-500">*</span>
                    </label>
                    <textarea
                      value={description}
                      onChange={(e) => setDescription(e.target.value)}
                      placeholder="详细描述作业要求..."
                      rows={4}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 resize-none"
                    />
                  </div>

                  {/* 上传附件 */}
                  <div>
                    <label className="block text-gray-700 text-sm mb-2">
                      上传附件（可选）
                    </label>
                    {!attachment ? (
                      <button
                        onClick={() => attachmentInputRef.current?.click()}
                        className="flex items-center gap-2 px-4 py-2 border-2 border-dashed border-gray-300 rounded-lg hover:border-indigo-400 hover:bg-indigo-50 transition text-gray-600 hover:text-indigo-600"
                      >
                        <Paperclip size={16} />
                        <span className="text-sm">点击上传附件</span>
                      </button>
                    ) : (
                      <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                        <div className="flex items-center gap-2">
                          <FileText size={16} className="text-blue-500" />
                          <div>
                            <p className="text-gray-800 text-sm">{attachment.name}</p>
                            <p className="text-gray-500 text-xs">{formatFileSize(attachment.size)}</p>
                          </div>
                        </div>
                        <button
                          onClick={handleRemoveAttachment}
                          className="p-1 text-red-600 hover:bg-red-50 rounded"
                        >
                          <Trash2 size={16} />
                        </button>
                      </div>
                    )}
                  </div>

                  {/* 评分规则 */}
                  <div>
                    <label className="block text-gray-700 text-sm mb-2">
                      评分规则（可选）
                    </label>
                    <textarea
                      value={gradingText}
                      onChange={(e) => setGradingText(e.target.value)}
                      placeholder="例如：满分100分，按要点给分..."
                      rows={3}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 resize-none"
                    />
                  </div>

                </div>

                {/* 底部按钮 */}
                <div className="flex items-center gap-3 mt-6 pt-6 border-t border-gray-200">
                  <button
                    onClick={handleCreateHomework}
                    className="flex-1 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition"
                  >
                    确认布置
                  </button>
                  <button
                    onClick={() => {
                      setShowCreateDialog(false);
                      resetForm();
                    }}
                    className="flex-1 px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition"
                  >
                    取消
                  </button>
                </div>
              </div>

              {/* 右侧：截止时间选择器 */}
              <div className="w-80 p-6 bg-gray-50">
                <h4 className="text-gray-800 mb-4">截止时间</h4>

                {/* 日期选择 */}
                <div className="mb-6">
                  <label className="block text-gray-700 text-sm mb-2">日期</label>
                  <input
                    type="date"
                    value={dueDate}
                    onChange={(e) => setDueDate(e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  />
                </div>

                {/* 时间选择（钟表形式） */}
                <div>
                  <label className="block text-gray-700 text-sm mb-2">时间</label>

                  {/* 时间显示 */}
                  <div className="text-center mb-4">
                    <div className="text-4xl text-gray-800">
                      {String(dueTime.hour).padStart(2, '0')}:{String(dueTime.minute).padStart(2, '0')}
                    </div>
                  </div>

                  {/* 钟表界面 */}
                  <div className="bg-white rounded-lg p-4 mb-4">
                    {/* 小时选择 */}
                    <div className="mb-4">
                      <p className="text-gray-600 text-sm mb-2 text-center">选择小时</p>
                      <div className="grid grid-cols-6 gap-2">
                        {Array.from({ length: 24 }, (_, i) => i).map((hour) => (
                          <button
                            key={hour}
                            onClick={() => setHour(hour)}
                            className={`p-2 rounded text-sm transition ${dueTime.hour === hour
                              ? 'bg-indigo-600 text-white'
                              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                              }`}
                          >
                            {String(hour).padStart(2, '0')}
                          </button>
                        ))}
                      </div>
                    </div>

                    {/* 分钟选择 */}
                    <div>
                      <p className="text-gray-600 text-sm mb-2 text-center">选择分钟</p>
                      <div className="grid grid-cols-6 gap-2">
                        {[0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55].map((minute) => (
                          <button
                            key={minute}
                            onClick={() => setMinute(minute)}
                            className={`p-2 rounded text-sm transition ${dueTime.minute === minute
                              ? 'bg-indigo-600 text-white'
                              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                              }`}
                          >
                            {String(minute).padStart(2, '0')}
                          </button>
                        ))}
                      </div>
                    </div>
                  </div>

                  {/* 预览 */}
                  <div className="bg-white rounded-lg p-3 text-sm text-gray-600">
                    <p className="mb-1">截止时间预览：</p>
                    <p className="text-gray-800">
                      {dueDate && new Date(`${dueDate}T${String(dueTime.hour).padStart(2, '0')}:${String(dueTime.minute).padStart(2, '0')}:00`).toLocaleString('zh-CN', {
                        year: 'numeric',
                        month: 'long',
                        day: 'numeric',
                        hour: '2-digit',
                        minute: '2-digit',
                      })}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}