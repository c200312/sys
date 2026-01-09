import { useState, useEffect, useRef } from 'react';
import { Edit2, X, Download, Users, FileArchive, FileText, Image, Paperclip, FileCheck, Trash2, Sparkles } from 'lucide-react';
import { toast } from 'sonner@2.0.3';
import JSZip from 'jszip';
import api, { Homework, Submission } from '../../utils/api-client';

interface SubmissionWithStudent extends Submission {
  student_name: string;
  student_class: string;
}

interface GradingProps {
  courseId: string;
  courseName: string;
  homeworkId: string;
  homeworkTitle: string;
  homework: Homework; // 添加完整的作业对象
  onHomeworkUpdated?: () => void; // 添加回调函数
}

export function Grading({ courseId, courseName, homeworkId, homeworkTitle, homework, onHomeworkUpdated }: GradingProps) {
  const [submissions, setSubmissions] = useState<SubmissionWithStudent[]>([]);
  const [loading, setLoading] = useState(true);
  const [gradingSubmission, setGradingSubmission] = useState<SubmissionWithStudent | null>(null);
  const [score, setScore] = useState('');
  const [feedback, setFeedback] = useState('');
  const [isAIGrading, setIsAIGrading] = useState(false);

  // 编辑作业的状态
  const [isEditingHomework, setIsEditingHomework] = useState(false);
  const [editTitle, setEditTitle] = useState(homework.title);
  const [editDescription, setEditDescription] = useState(homework.description);
  const [editDeadline, setEditDeadline] = useState('');
  const [editAttachment, setEditAttachment] = useState<{
    name: string;
    type: string;
    size: number;
    content: string;
  } | null>(homework.attachment || null);
  const [editGradingText, setEditGradingText] = useState(
    homework.grading_criteria?.content || ''
  );

  // 文件输入引用
  const editAttachmentInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    // 初始化编辑字段
    setEditTitle(homework.title);
    setEditDescription(homework.description);

    // 解析deadline到日期时间
    try {
      const deadline = new Date(homework.deadline);

      // 检查日期是否有效
      if (isNaN(deadline.getTime())) {
        console.error('无效的截止时间:', homework.deadline);
        // 使用当前时间作为默认值
        const now = new Date();
        const dateStr = now.toISOString().split('T')[0];
        const timeStr = now.toTimeString().slice(0, 5);
        setEditDeadline(`${dateStr}T${timeStr}`);
      } else {
        const dateStr = deadline.toISOString().split('T')[0];
        const timeStr = deadline.toTimeString().slice(0, 5);
        setEditDeadline(`${dateStr}T${timeStr}`);
      }
    } catch (error) {
      console.error('解析截止时间失败:', error);
      // 使用当前时间作为默认值
      const now = new Date();
      const dateStr = now.toISOString().split('T')[0];
      const timeStr = now.toTimeString().slice(0, 5);
      setEditDeadline(`${dateStr}T${timeStr}`);
    }
  }, [homework]);

  // 格式化文件大小
  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(2) + ' MB';
  };

  //加载作业提交
  const loadSubmissions = async () => {
    setLoading(true);
    try {
      const result = await api.getHomeworkSubmissions(homeworkId);
      console.log('✅ 获取作业提交成功:', result);

      if (result.success && result.data) {
        // API已经返回了学生信息（包括班级）
        const submissionsWithStudents = result.data.submissions.map((sub: any) => ({
          ...sub,
          student_name: sub.student_name || '未知学生',
          student_class: sub.student_class || '未知班级',
        }));

        setSubmissions(submissionsWithStudents);
      } else {
        toast.error(result.error || '获取作业提交失败');
      }
    } catch (error) {
      console.error('❌ 获取作业提交失败:', error);
      toast.error('获取作业提交失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadSubmissions();
  }, [homeworkId]);

  // 批改作业
  const handleGrade = async () => {
    if (!gradingSubmission) return;

    const scoreNum = Number(score);
    if (isNaN(scoreNum) || scoreNum < 0 || scoreNum > 100) {
      toast.error('请输入0-100之间的分数');
      return;
    }

    try {
      const result = await api.gradeSubmission(gradingSubmission.id, {
        score: scoreNum,
        feedback: feedback || undefined,
      });
      if (result.success) {
        toast.success('批改成功');
        setGradingSubmission(null);
        setScore('');
        setFeedback('');
        loadSubmissions();
      } else {
        toast.error(result.error || '批改失败');
      }
    } catch (error: any) {
      console.error('❌ 批改失败:', error);
      toast.error(error.message || '批改失败');
    }
  };

  // 开始批改
  const startGrading = (submission: SubmissionWithStudent) => {
    setGradingSubmission(submission);
    setScore(submission.score?.toString() || '');
    setFeedback(submission.feedback || '');
  };

  // AI评分 - 调用后端 AI 评分服务
  const handleAIGrade = async () => {
    if (!gradingSubmission) return;

    // 检查是否有评分规则
    if (!homework.grading_criteria?.content) {
      toast.error('请先设置评分规则后再使用 AI 评分');
      return;
    }

    setIsAIGrading(true);

    try {
      const result = await api.gradeSubmissionWithAI({
        student_content: gradingSubmission.content,
        grading_criteria: homework.grading_criteria.content,
        homework_title: homework.title,
        homework_description: homework.description,
      });

      if (result.success) {
        setScore(result.score.toString());
        setFeedback(result.feedback);
        toast.success('AI 评分完成！您可以根据实际情况调整分数和批语。');
      } else {
        toast.error(result.error || 'AI 评分失败，请手动评分');
      }
    } catch (error) {
      console.error('AI评分失败:', error);
      toast.error('AI 评分失败，请手动评分');
    } finally {
      setIsAIGrading(false);
    }
  };


  // 处理编辑附件上传
  const handleEditAttachmentChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = () => {
      setEditAttachment({
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

  // 删除编辑附件
  const handleRemoveEditAttachment = () => {
    setEditAttachment(null);
    if (editAttachmentInputRef.current) {
      editAttachmentInputRef.current.value = '';
    }
  };

  // 更新作业
  const handleUpdateHomework = async () => {
    if (!editTitle.trim()) {
      toast.error('请输入作业标题');
      return;
    }
    if (!editDescription.trim()) {
      toast.error('请输入作业描述');
      return;
    }
    if (!editDeadline) {
      toast.error('请选择截止时间');
      return;
    }

    try {
      // 构建评分规则（仅文本）
      let gradingCriteria: {
        type: 'text';
        content: string;
      } | undefined;

      if (editGradingText.trim()) {
        gradingCriteria = {
          type: 'text',
          content: editGradingText.trim(),
        };
      }

      const result = await api.updateHomework(homeworkId, {
        title: editTitle.trim(),
        description: editDescription.trim(),
        deadline: editDeadline,
        attachment: editAttachment || undefined,
        grading_criteria: gradingCriteria,
      });

      if (result.success) {
        toast.success('作业已更新');
        setIsEditingHomework(false);
        // 调用回调函数
        if (onHomeworkUpdated) {
          onHomeworkUpdated();
        }
      } else {
        toast.error(result.error || '更新失败');
      }
    } catch (error: any) {
      console.error('❌ 更新作业失败:', error);
      toast.error(error.message || '更新失败');
    }
  };

  // 下载单个学生的作业
  const downloadSingleSubmission = async (submission: SubmissionWithStudent) => {
    try {
      const zip = new JSZip();

      // 创建学生名文件夹
      const studentFolder = zip.folder(submission.student_name);
      if (!studentFolder) {
        throw new Error('创建文件夹失败');
      }

      // 添加作业内容文本文件
      if (submission.content) {
        studentFolder.file('作业内容.txt', submission.content);
      }

      // 如果有附件，添加附件
      if (submission.attachments && submission.attachments.length > 0) {
        for (const attachment of submission.attachments) {
          try {
            // 从 MinIO URL 下载文件
            if (attachment.url) {
              const response = await fetch(attachment.url);
              const blob = await response.blob();
              studentFolder.file(attachment.name, blob);
            }
          } catch (error) {
            console.error(`处理附件 ${attachment.name} 失败:`, error);
          }
        }
      }

      // 生成zip文件
      const content = await zip.generateAsync({ type: 'blob' });

      // 创建下载链接
      const url = URL.createObjectURL(content);
      const link = document.createElement('a');
      link.href = url;
      link.download = `${submission.student_name}_${homeworkTitle}.zip`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);

      toast.success('下载成功');
    } catch (error: any) {
      console.error('❌ 下载失败:', error);
      toast.error('下载失败');
    }
  };

  // 下载所有学生的作业
  const downloadAllSubmissions = async () => {
    if (submissions.length === 0) {
      toast.error('暂无提交记录');
      return;
    }

    try {
      toast.info('正在打包，请稍候...');
      const zip = new JSZip();

      // 为每个学生创建文件夹
      for (const submission of submissions) {
        const studentFolder = zip.folder(submission.student_name);
        if (!studentFolder) continue;

        // 添加作业内容文本文件
        if (submission.content) {
          studentFolder.file('作业内容.txt', submission.content);
        }

        // 如果有附件，添加附件
        if (submission.attachments && submission.attachments.length > 0) {
          for (const attachment of submission.attachments) {
            try {
              // 从 MinIO URL 下载文件
              if (attachment.url) {
                const response = await fetch(attachment.url);
                const blob = await response.blob();
                studentFolder.file(attachment.name, blob);
              }
            } catch (error) {
              console.error(`处理${submission.student_name}的附件失败:`, error);
            }
          }
        }
      }

      // 生成zip文件
      const content = await zip.generateAsync({ type: 'blob' });

      // 创建下载链接
      const url = URL.createObjectURL(content);
      const link = document.createElement('a');
      link.href = url;
      link.download = `${homeworkTitle}_全部提交.zip`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);

      toast.success('下载成功');
    } catch (error: any) {
      console.error('❌ 下载失败:', error);
      toast.error('下载失败');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-gray-400">加载中...</div>
      </div>
    );
  }

  return (
    <div className="flex gap-6">
      {/* 左侧：作业详情 */}
      <div className="w-96 flex-shrink-0">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 sticky top-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-gray-800">作业详情</h3>
            <button
              onClick={() => setIsEditingHomework(true)}
              className="flex items-center gap-1 px-3 py-1.5 text-indigo-600 hover:bg-indigo-50 rounded-lg transition text-sm"
            >
              <Edit2 size={14} />
              <span>编辑</span>
            </button>
          </div>

          {/* 作业标题 */}
          <div className="mb-4">
            <label className="block text-gray-600 text-sm mb-1">标题</label>
            <p className="text-gray-800">{homework.title}</p>
          </div>

          {/* 作业描述 */}
          <div className="mb-4">
            <label className="block text-gray-600 text-sm mb-1">作业描述</label>
            <p className="text-gray-700 text-sm whitespace-pre-wrap bg-gray-50 p-3 rounded-lg">
              {homework.description}
            </p>
          </div>

          {/* 附件 */}
          {homework.attachment && (
            <div className="mb-4">
              <label className="block text-gray-600 text-sm mb-1">附件</label>
              <div className="flex items-center gap-2 p-3 bg-blue-50 rounded-lg">
                <FileText size={16} className="text-blue-500 flex-shrink-0" />
                <div className="flex-1 min-w-0">
                  <p className="text-gray-800 text-sm truncate">{homework.attachment.name}</p>
                  <p className="text-gray-500 text-xs">{formatFileSize(homework.attachment.size)}</p>
                </div>
                <a
                  href={homework.attachment.url || '#'}
                  download={homework.attachment.name}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="p-2 text-blue-600 hover:bg-blue-100 rounded transition"
                  title="下载附件"
                >
                  <Download size={16} />
                </a>
              </div>
            </div>
          )}

          {/* 评分标准 */}
          {homework.grading_criteria && (
            <div className="mb-4">
              <label className="block text-gray-600 text-sm mb-1">评分标准</label>
              {homework.grading_criteria.type === 'text' ? (
                <p className="text-gray-700 text-sm whitespace-pre-wrap bg-green-50 p-3 rounded-lg">
                  {homework.grading_criteria.content}
                </p>
              ) : (
                <div className="flex items-center gap-2 p-3 bg-green-50 rounded-lg">
                  <FileText size={16} className="text-green-500 flex-shrink-0" />
                  <div className="flex-1 min-w-0">
                    <p className="text-gray-800 text-sm truncate">{homework.grading_criteria.file_name}</p>
                    <p className="text-gray-500 text-xs">{formatFileSize(homework.grading_criteria.file_size || 0)}</p>
                  </div>
                  <a
                    href={homework.grading_criteria.url || '#'}
                    download={homework.grading_criteria.file_name}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="p-2 text-green-600 hover:bg-green-100 rounded transition"
                    title="下载评分标准"
                  >
                    <Download size={16} />
                  </a>
                </div>
              )}
            </div>
          )}

          {/* 截止时间 */}
          <div className="mb-4">
            <label className="block text-gray-600 text-sm mb-1">截止时间</label>
            <p className="text-gray-800 text-sm">
              {(() => {
                try {
                  const date = new Date(homework.deadline);
                  if (isNaN(date.getTime())) {
                    return '无效日期';
                  }
                  return date.toLocaleString('zh-CN');
                } catch (error) {
                  return '无效日期';
                }
              })()}
            </p>
          </div>

          {/* 发布时间 */}
          <div className="mb-4">
            <label className="block text-gray-600 text-sm mb-1">发布时间</label>
            <p className="text-gray-500 text-sm">
              {(() => {
                try {
                  const date = new Date(homework.created_at);
                  if (isNaN(date.getTime())) {
                    return '无效日期';
                  }
                  return date.toLocaleString('zh-CN');
                } catch (error) {
                  return '无效日期';
                }
              })()}
            </p>
          </div>
        </div>
      </div>

      {/* 右侧：提交列表 */}
      <div className="flex-1">
        {/* 头部 */}
        <div className="flex items-center justify-between mb-6">
          <div>
            <h3 className="text-gray-800">学生提交</h3>
            <p className="text-gray-500 text-sm mt-1">
              {submissions.length} 人已提交
            </p>
          </div>
          <button
            onClick={downloadAllSubmissions}
            className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition"
            disabled={submissions.length === 0}
          >
            <FileArchive size={20} />
            <span>下载全部</span>
          </button>
        </div>

        {/* 提交列表 */}
        {submissions.length === 0 ? (
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-12">
            <div className="text-center">
              <Users size={64} className="text-gray-300 mx-auto mb-4" />
              <p className="text-gray-500">还没有学生提交作业</p>
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            {submissions.map((submission) => (
              <div
                key={submission.id}
                className="bg-white rounded-xl shadow-sm border border-gray-200 p-6"
              >
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <div className="flex items-center gap-3">
                      <h4 className="text-gray-800">{submission.student_name}</h4>
                      <span className="text-gray-500 text-sm">{submission.student_class}</span>
                      {submission.score != null && (
                        <span className="px-3 py-1 bg-indigo-100 text-indigo-700 rounded-full text-sm">
                          {submission.score}分
                        </span>
                      )}
                    </div>
                    <p className="text-gray-500 text-sm mt-1">
                      提交时间：{new Date(submission.submitted_at).toLocaleString('zh-CN')}
                    </p>
                  </div>

                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => downloadSingleSubmission(submission)}
                      className="flex items-center gap-2 px-3 py-2 text-green-600 hover:bg-green-50 rounded-lg transition text-sm"
                    >
                      <Download size={16} />
                      <span>下载</span>
                    </button>
                    <button
                      onClick={() => startGrading(submission)}
                      className="flex items-center gap-2 px-3 py-2 text-indigo-600 hover:bg-indigo-50 rounded-lg transition text-sm"
                    >
                      <Edit2 size={16} />
                      <span>{submission.score != null ? '修改批改' : '批改'}</span>
                    </button>
                  </div>
                </div>

                {/* 作业内容 */}
                <div className="bg-gray-50 rounded-lg p-4">
                  <p className="text-gray-700 text-sm whitespace-pre-wrap">{submission.content}</p>
                </div>

                {/* 提交的附件 */}
                {submission.attachments && submission.attachments.length > 0 && (
                  <div className="mt-3">
                    <p className="text-gray-600 text-sm mb-2">提交附件：</p>
                    <div className="space-y-2">
                      {submission.attachments.map((attachment, index) => (
                        <div
                          key={index}
                          className="flex items-center gap-2 p-3 bg-gray-50 rounded-lg text-sm"
                        >
                          {attachment.type.startsWith('image/') ? (
                            <Image size={16} className="text-indigo-600 flex-shrink-0" />
                          ) : (
                            <FileText size={16} className="text-gray-600 flex-shrink-0" />
                          )}
                          <span className="text-gray-700">{attachment.name}</span>
                          <span className="text-gray-500 text-xs">
                            ({formatFileSize(attachment.size)})
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* 批改反馈 */}
                {submission.feedback && (
                  <div className="mt-4 p-4 bg-blue-50 rounded-lg">
                    <p className="text-gray-700 text-sm">
                      <span className="text-gray-600">教师批语：</span>
                      {submission.feedback}
                    </p>
                    {submission.graded_at && (
                      <p className="text-gray-500 text-xs mt-2">
                        批改时间：{new Date(submission.graded_at).toLocaleString('zh-CN')}
                      </p>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* 批改对话框 */}
      {gradingSubmission && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg w-full max-w-2xl p-6">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-gray-800">批改作业 - {gradingSubmission.student_name}</h3>
              <button
                onClick={() => {
                  setGradingSubmission(null);
                  setScore('');
                  setFeedback('');
                }}
                className="p-2 text-gray-500 hover:bg-gray-100 rounded-lg"
              >
                <X size={20} />
              </button>
            </div>

            {/* 作业内容 */}
            <div className="mb-6">
              <label className="block text-gray-700 text-sm mb-2">作业内容</label>
              <div className="bg-gray-50 rounded-lg p-4 max-h-48 overflow-y-auto">
                <p className="text-gray-700 text-sm whitespace-pre-wrap">{gradingSubmission.content}</p>
              </div>
            </div>

            {/* 提交的附件 */}
            {gradingSubmission.attachments && gradingSubmission.attachments.length > 0 && (
              <div className="mb-6">
                <label className="block text-gray-700 text-sm mb-2">提交附件</label>
                <div className="space-y-2">
                  {gradingSubmission.attachments.map((attachment, index) => (
                    <div
                      key={index}
                      className="flex items-center gap-2 p-3 bg-gray-50 rounded-lg text-sm"
                    >
                      {attachment.type.startsWith('image/') ? (
                        <Image size={16} className="text-indigo-600 flex-shrink-0" />
                      ) : (
                        <FileText size={16} className="text-gray-600 flex-shrink-0" />
                      )}
                      <span className="text-gray-700">{attachment.name}</span>
                      <span className="text-gray-500 text-xs">
                        ({formatFileSize(attachment.size)})
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* 分数 */}
            <div className="mb-4">
              <div className="flex items-center justify-between mb-2">
                <label className="block text-gray-700 text-sm">
                  分数（0-100）<span className="text-red-500">*</span>
                </label>
                <button
                  onClick={handleAIGrade}
                  disabled={isAIGrading}
                  className="flex items-center gap-2 px-3 py-1.5 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-lg hover:from-purple-700 hover:to-blue-700 transition text-sm disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <Sparkles size={14} className={isAIGrading ? 'animate-spin' : ''} />
                  <span>{isAIGrading ? 'AI评分中...' : 'AI评分'}</span>
                </button>
              </div>
              <input
                type="number"
                value={score}
                onChange={(e) => setScore(e.target.value)}
                min="0"
                max="100"
                placeholder="请输入分数"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </div>

            {/* 批语 */}
            <div className="mb-6">
              <label className="block text-gray-700 text-sm mb-2">批语（可选）</label>
              <textarea
                value={feedback}
                onChange={(e) => setFeedback(e.target.value)}
                rows={4}
                placeholder="输入批改意见..."
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 resize-none"
              />
            </div>

            {/* 按钮 */}
            <div className="flex items-center gap-3">
              <button
                onClick={handleGrade}
                className="flex-1 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition"
              >
                确认批改
              </button>
              <button
                onClick={() => {
                  setGradingSubmission(null);
                  setScore('');
                  setFeedback('');
                }}
                className="flex-1 px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition"
              >
                取消
              </button>
            </div>
          </div>
        </div>
      )}

      {/* 编辑作业对话框 */}
      {isEditingHomework && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg w-full max-w-2xl p-6">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-gray-800">编辑作业 - {homework.title}</h3>
              <button
                onClick={() => setIsEditingHomework(false)}
                className="p-2 text-gray-500 hover:bg-gray-100 rounded-lg"
              >
                <X size={20} />
              </button>
            </div>

            {/* 作业标题 */}
            <div className="mb-4">
              <label className="block text-gray-700 text-sm mb-2">标题</label>
              <input
                type="text"
                value={editTitle}
                onChange={(e) => setEditTitle(e.target.value)}
                placeholder="请输入作业标题"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </div>

            {/* 作业描述 */}
            <div className="mb-4">
              <label className="block text-gray-700 text-sm mb-2">作业要求</label>
              <textarea
                value={editDescription}
                onChange={(e) => setEditDescription(e.target.value)}
                rows={4}
                placeholder="输入作业要求..."
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 resize-none"
              />
            </div>

            {/* 截止时间 */}
            <div className="mb-4">
              <label className="block text-gray-700 text-sm mb-2">截止时间</label>
              <input
                type="datetime-local"
                value={editDeadline}
                onChange={(e) => setEditDeadline(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </div>

            {/* 附件 */}
            <div className="mb-4">
              <label className="block text-gray-700 text-sm mb-2">附件（可选）</label>
              <div className="flex items-center gap-2">
                <input
                  type="file"
                  ref={editAttachmentInputRef}
                  onChange={handleEditAttachmentChange}
                  className="hidden"
                />
                <button
                  onClick={() => editAttachmentInputRef.current?.click()}
                  className="flex items-center gap-2 px-3 py-2 text-blue-600 hover:bg-blue-50 rounded-lg transition text-sm"
                >
                  <Paperclip size={16} />
                  <span>上传附件</span>
                </button>
                {editAttachment && (
                  <div className="flex items-center gap-2 p-3 bg-blue-50 rounded-lg text-sm">
                    {editAttachment.type.startsWith('image/') ? (
                      <Image size={16} className="text-indigo-600 flex-shrink-0" />
                    ) : (
                      <FileText size={16} className="text-gray-600 flex-shrink-0" />
                    )}
                    <span className="text-gray-700">{editAttachment.name}</span>
                    <span className="text-gray-500 text-xs">
                      ({formatFileSize(editAttachment.size)})
                    </span>
                    <button
                      onClick={handleRemoveEditAttachment}
                      className="p-2 text-gray-500 hover:bg-gray-100 rounded-lg"
                    >
                      <X size={16} />
                    </button>
                  </div>
                )}
              </div>
            </div>

            {/* 评分标准 */}
            <div className="mb-4">
              <label className="block text-gray-700 text-sm mb-2">评分标准</label>
              <textarea
                value={editGradingText}
                onChange={(e) => setEditGradingText(e.target.value)}
                rows={4}
                placeholder="输入评分标准..."
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 resize-none"
              />
            </div>


            {/* 按钮 */}
            <div className="flex items-center gap-3">
              <button
                onClick={handleUpdateHomework}
                className="flex-1 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition"
              >
                确认更新
              </button>
              <button
                onClick={() => setIsEditingHomework(false)}
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