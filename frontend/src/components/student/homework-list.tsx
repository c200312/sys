import { useState, useEffect, useRef } from 'react';
import { FileText, Calendar, CheckCircle, Clock, XCircle, Upload, Image, Paperclip, X, Send } from 'lucide-react';
import { toast } from 'sonner@2.0.3';
import api from '../../utils/api-client';

interface HomeworkSubmission {
  id: string;
  content: string;
  attachments?: Array<{
    name: string;
    type: string;
    size: number;
    content: string;
  }>;
  score?: number;
  feedback?: string;
  submitted_at: string;
  graded_at?: string;
}

interface Homework {
  id: string;
  course_id: string;
  title: string;
  description: string;
  due_date: string;
  created_at: string;
  attachment?: {
    name: string;
    size: number;
    type: string;
    content: string;
  };
  submission: HomeworkSubmission | null;
  status: 'pending' | 'submitted' | 'graded';
}

interface HomeworkListProps {
  studentId: string;
  courseId: string;
}

export function HomeworkList({ studentId, courseId }: HomeworkListProps) {
  const [homeworks, setHomeworks] = useState<Homework[]>([]);
  const [loading, setLoading] = useState(true);
  const [submittingHomework, setSubmittingHomework] = useState<Homework | null>(null);
  const [submissionText, setSubmissionText] = useState('');
  const [attachments, setAttachments] = useState<Array<{
    name: string;
    type: string;
    size: number;
    content: string;
  }>>([]);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    loadHomeworks();
  }, [studentId, courseId]);

  const loadHomeworks = async () => {
    setLoading(true);
    try {
      // 获取课程作业列表
      const result = await api.getCourseHomeworks(courseId);
      console.log('✅ 获取作业列表成功:', result);

      if (result.success && result.data) {
        // 获取学生的提交记录
        const submissionsResult = await api.getStudentSubmissions(studentId);
        const submissions = submissionsResult.success && submissionsResult.data
          ? submissionsResult.data.submissions
          : [];

        // 合并作业和提交状态
        const homeworksWithStatus = result.data.homeworks.map((hw: any) => {
          const submission = submissions.find((s: any) => s.homework_id === hw.id);
          return {
            ...hw,
            due_date: hw.deadline,
            submission: submission || null,
            status: submission
              ? (submission.score != null ? 'graded' : 'submitted')
              : 'pending',
          };
        });

        setHomeworks(homeworksWithStatus as Homework[]);
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

  const getStatusBadge = (homework: Homework) => {
    if (homework.status === 'graded') {
      return (
        <div className="flex items-center gap-1 px-3 py-1 bg-green-100 text-green-700 rounded-full text-sm">
          <CheckCircle size={14} />
          <span>已批改</span>
        </div>
      );
    } else if (homework.status === 'submitted') {
      return (
        <div className="flex items-center gap-1 px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm">
          <Clock size={14} />
          <span>已提交</span>
        </div>
      );
    } else {
      const dueDate = new Date(homework.due_date);
      const now = new Date();
      const isOverdue = dueDate < now;
      
      return (
        <div className={`flex items-center gap-1 px-3 py-1 rounded-full text-sm ${
          isOverdue 
            ? 'bg-red-100 text-red-700' 
            : 'bg-orange-100 text-orange-700'
        }`}>
          {isOverdue ? <XCircle size={14} /> : <Clock size={14} />}
          <span>{isOverdue ? '已逾期' : '待提交'}</span>
        </div>
      );
    }
  };

  // 开始提交作业
  const startSubmit = (homework: Homework) => {
    setSubmittingHomework(homework);
    setSubmissionText(homework.submission?.content || '');
    setAttachments(homework.submission?.attachments || []);
  };

  // 处理文件选择
  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files || files.length === 0) return;

    Array.from(files).forEach(file => {
      const reader = new FileReader();
      reader.onload = (event) => {
        const content = event.target?.result as string;
        setAttachments(prev => [...prev, {
          name: file.name,
          type: file.type,
          size: file.size,
          content,
        }]);
      };
      reader.readAsDataURL(file);
    });

    // 重置input
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  // 删除附件
  const removeAttachment = (index: number) => {
    setAttachments(prev => prev.filter((_, i) => i !== index));
  };

  // 格式化文件大小
  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(2) + ' MB';
  };

  // 提交作业
  const handleSubmit = async () => {
    if (!submittingHomework) return;

    if (!submissionText.trim() && attachments.length === 0) {
      toast.error('请输入作业内容或上传附件');
      return;
    }

    try {
      const result = await api.submitHomework(submittingHomework.id, {
        content: submissionText.trim(),
        attachments: attachments.length > 0 ? attachments : undefined,
      });
      if (result.success) {
        toast.success('作业提交成功');
        setSubmittingHomework(null);
        setSubmissionText('');
        setAttachments([]);
        loadHomeworks();
      } else {
        toast.error(result.error || '提交失败');
      }
    } catch (error: any) {
      console.error('❌ 提交失败:', error);
      toast.error(error.message || '提交失败');
    }
  };

  // 下载教师附件
  const downloadTeacherAttachment = (homework: Homework) => {
    if (!homework.attachment) return;

    const link = document.createElement('a');
    link.href = homework.attachment.content;
    link.download = homework.attachment.name;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-gray-400">加载中...</div>
      </div>
    );
  }

  if (homeworks.length === 0) {
    return (
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-12">
        <div className="text-center">
          <FileText size={64} className="text-gray-300 mx-auto mb-4" />
          <p className="text-gray-500">暂无作业</p>
        </div>
      </div>
    );
  }

  return (
    <div>
      <div className="mb-6">
        <h3 className="text-gray-800">课程作业</h3>
        <p className="text-gray-500 text-sm mt-1">
          共 {homeworks.length} 份作业
        </p>
      </div>

      <div className="space-y-4">
        {homeworks.map((homework) => (
          <div
            key={homework.id}
            className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 hover:shadow-md transition"
          >
            {/* 头部 */}
            <div className="flex items-start justify-between mb-4">
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-2">
                  <h4 className="text-gray-800">{homework.title}</h4>
                  {getStatusBadge(homework)}
                </div>
                <p className="text-gray-600 text-sm">{homework.description}</p>
              </div>
            </div>

            {/* 截止时间 */}
            <div className="flex items-center gap-2 text-gray-500 text-sm mb-2">
              <Calendar size={16} />
              <span>
                截止时间：{new Date(homework.due_date).toLocaleString('zh-CN')}
              </span>
            </div>

            {/* 教师附件 */}
            {homework.attachment && (
              <div className="mb-4">
                <button
                  onClick={() => downloadTeacherAttachment(homework)}
                  className="flex items-center gap-2 text-indigo-600 hover:text-indigo-700 text-sm"
                >
                  <Paperclip size={16} />
                  <span>下载作业附件：{homework.attachment.name} ({formatFileSize(homework.attachment.size)})</span>
                </button>
              </div>
            )}

            {/* 提交信息 */}
            {homework.submission && (
              <div className="pt-4 border-t border-gray-100 space-y-3">
                {/* 提交内容 */}
                {homework.submission.content && (
                  <div>
                    <p className="text-gray-600 text-sm mb-1">提交内容：</p>
                    <p className="text-gray-800 text-sm bg-gray-50 p-3 rounded-lg whitespace-pre-wrap">
                      {homework.submission.content}
                    </p>
                  </div>
                )}

                {/* 提交的附件 */}
                {homework.submission.attachments && homework.submission.attachments.length > 0 && (
                  <div>
                    <p className="text-gray-600 text-sm mb-2">提交附件：</p>
                    <div className="space-y-2">
                      {homework.submission.attachments.map((attachment, index) => (
                        <div
                          key={index}
                          className="flex items-center gap-2 p-3 bg-gray-50 rounded-lg"
                        >
                          {attachment.type.startsWith('image/') ? (
                            <Image size={16} className="text-indigo-600 flex-shrink-0" />
                          ) : (
                            <FileText size={16} className="text-gray-600 flex-shrink-0" />
                          )}
                          <span className="text-gray-700 text-sm">{attachment.name}</span>
                          <span className="text-gray-500 text-xs">
                            ({formatFileSize(attachment.size)})
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* 提交时间 */}
                <p className="text-gray-500 text-xs">
                  提交时间：{new Date(homework.submission.submitted_at).toLocaleString('zh-CN')}
                </p>

                {/* 批改信息 */}
                {homework.status === 'graded' && homework.submission.score != null && (
                  <div className="bg-green-50 p-4 rounded-lg space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-gray-600 text-sm">得分：</span>
                      <span className="text-green-700 text-xl">
                        {homework.submission.score} 分
                      </span>
                    </div>
                    
                    {homework.submission.feedback && (
                      <div>
                        <p className="text-gray-600 text-sm mb-1">教师反馈：</p>
                        <p className="text-gray-700 text-sm">{homework.submission.feedback}</p>
                      </div>
                    )}

                    {homework.submission.graded_at && (
                      <p className="text-gray-500 text-xs">
                        批改时间：{new Date(homework.submission.graded_at).toLocaleString('zh-CN')}
                      </p>
                    )}
                  </div>
                )}
              </div>
            )}

            {/* 待提交/重新提交按钮 */}
            {homework.status !== 'graded' && (
              <div className="pt-4 border-t border-gray-100">
                <button
                  onClick={() => startSubmit(homework)}
                  className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition"
                >
                  <Upload size={16} />
                  <span>{homework.submission ? '重新提交' : '提交作业'}</span>
                </button>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* 提交对话框 */}
      {submittingHomework && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg w-full max-w-3xl max-h-[90vh] overflow-y-auto p-6">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-gray-800">提交作业 - {submittingHomework.title}</h3>
              <button
                onClick={() => {
                  setSubmittingHomework(null);
                  setSubmissionText('');
                  setAttachments([]);
                }}
                className="p-2 text-gray-500 hover:bg-gray-100 rounded-lg"
              >
                <X size={20} />
              </button>
            </div>

            {/* 作业要求 */}
            <div className="mb-6 p-4 bg-blue-50 rounded-lg">
              <p className="text-gray-700 text-sm mb-2">
                <span className="text-gray-600">作业要求：</span>
                {submittingHomework.description}
              </p>
              <p className="text-gray-500 text-xs">
                截止时间：{new Date(submittingHomework.due_date).toLocaleString('zh-CN')}
              </p>
            </div>

            {/* 文本输入 */}
            <div className="mb-4">
              <label className="block text-gray-700 text-sm mb-2">
                作业内容 <span className="text-gray-400">(支持文本输入)</span>
              </label>
              <textarea
                value={submissionText}
                onChange={(e) => setSubmissionText(e.target.value)}
                rows={10}
                placeholder="请输入作业内容..."
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 resize-none"
              />
            </div>

            {/* 附件上传 */}
            <div className="mb-6">
              <label className="block text-gray-700 text-sm mb-2">
                附件上传 <span className="text-gray-400">(支持图片、文档等)</span>
              </label>
              
              <input
                ref={fileInputRef}
                type="file"
                multiple
                onChange={handleFileSelect}
                className="hidden"
                accept="image/*,.pdf,.doc,.docx,.txt,.zip"
              />
              
              <button
                onClick={() => fileInputRef.current?.click()}
                className="flex items-center gap-2 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition text-sm"
              >
                <Paperclip size={16} />
                <span>选择文件</span>
              </button>

              {/* 附件列表 */}
              {attachments.length > 0 && (
                <div className="mt-4 space-y-2">
                  {attachments.map((attachment, index) => (
                    <div
                      key={index}
                      className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                    >
                      <div className="flex items-center gap-2 flex-1 min-w-0">
                        {attachment.type.startsWith('image/') ? (
                          <Image size={16} className="text-indigo-600 flex-shrink-0" />
                        ) : (
                          <FileText size={16} className="text-gray-600 flex-shrink-0" />
                        )}
                        <span className="text-gray-700 text-sm truncate">{attachment.name}</span>
                        <span className="text-gray-500 text-xs flex-shrink-0">
                          ({formatFileSize(attachment.size)})
                        </span>
                      </div>
                      <button
                        onClick={() => removeAttachment(index)}
                        className="p-1 text-red-500 hover:bg-red-50 rounded"
                      >
                        <X size={16} />
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* 按钮 */}
            <div className="flex items-center gap-3">
              <button
                onClick={handleSubmit}
                disabled={!submissionText.trim() && attachments.length === 0}
                className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition disabled:bg-gray-300 disabled:cursor-not-allowed"
              >
                <Send size={16} />
                <span>提交作业</span>
              </button>
              <button
                onClick={() => {
                  setSubmittingHomework(null);
                  setSubmissionText('');
                  setAttachments([]);
                }}
                className="flex-1 px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition"
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