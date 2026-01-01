import { useState, useRef, useEffect } from 'react';
import { Sparkles, Send, Loader, User, Bot, Database, Upload, FileText, X, Trash2, Plus, Folder, ChevronDown, ChevronRight } from 'lucide-react';
import { toast } from 'sonner@2.0.3';
import api, { Course, CourseFolder, CourseFile } from '../../utils/api-client';

// 源数据项类型
interface SourceItem {
  name: string;  // 文件名
  content: string;  // 相关片段内容
  course_name?: string;  // 课程名称
}

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  sources?: SourceItem[];
}

interface StudentAIAssistantProps {
  studentId: string;
}

interface KnowledgeItem {
  id: string;
  name: string;
  source_type: 'personal' | 'course';
  course_id?: string;
  course_name?: string;
  chunks_count: number;
  created_at: string;
  owner_id?: string;
}

// @ts-ignore
const AI_RAG_URL = (import.meta.env?.VITE_AI_RAG_URL as string) || 'http://localhost:8004';

// 解析消息内容，将角标 [1], [2] 等转换为可点击元素
function parseMessageWithCitations(
  content: string,
  sources: SourceItem[],
  onCitationClick: (index: number) => void
): React.ReactNode[] {
  if (!sources || sources.length === 0) {
    return [content];
  }

  // 匹配 [1], [2], [1][2] 等格式的角标
  const citationRegex = /\[(\d+)\]/g;
  const parts: React.ReactNode[] = [];
  let lastIndex = 0;
  let match;

  while ((match = citationRegex.exec(content)) !== null) {
    // 添加角标前的文本
    if (match.index > lastIndex) {
      parts.push(content.slice(lastIndex, match.index));
    }

    const citationNum = parseInt(match[1], 10);
    const sourceIndex = citationNum - 1; // 角标从1开始，数组从0开始

    // 检查是否有对应的源
    if (sourceIndex >= 0 && sourceIndex < sources.length) {
      parts.push(
        <button
          key={`citation-${match.index}`}
          onClick={() => onCitationClick(sourceIndex)}
          className="inline-flex items-center justify-center min-w-[1.25rem] h-5 px-1 mx-0.5 text-xs font-medium text-blue-600 bg-blue-100 rounded hover:bg-blue-200 transition cursor-pointer align-super"
          title={`查看来源: ${sources[sourceIndex].name}`}
        >
          {citationNum}
        </button>
      );
    } else {
      // 没有对应源，保留原文
      parts.push(match[0]);
    }

    lastIndex = match.index + match[0].length;
  }

  // 添加剩余文本
  if (lastIndex < content.length) {
    parts.push(content.slice(lastIndex));
  }

  return parts;
}

// 源引用弹窗组件
function SourcePopup({
  source,
  index,
  onClose
}: {
  source: SourceItem;
  index: number;
  onClose: () => void;
}) {
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" onClick={onClose}>
      <div
        className="bg-white rounded-lg shadow-xl max-w-lg w-full mx-4 max-h-[70vh] flex flex-col"
        onClick={e => e.stopPropagation()}
      >
        {/* 头部 */}
        <div className="p-4 border-b border-gray-200 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="inline-flex items-center justify-center w-6 h-6 text-sm font-medium text-blue-600 bg-blue-100 rounded">
              {index + 1}
            </span>
            <h3 className="text-sm font-medium text-gray-800 truncate">{source.name}</h3>
            {source.course_name && (
              <span className="text-xs text-green-600 bg-green-50 px-1.5 py-0.5 rounded">
                {source.course_name}
              </span>
            )}
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
          >
            <X size={18} />
          </button>
        </div>

        {/* 内容 */}
        <div className="flex-1 overflow-y-auto p-4">
          <p className="text-sm text-gray-700 whitespace-pre-wrap leading-relaxed">
            {source.content}
          </p>
        </div>
      </div>
    </div>
  );
}

// 带角标的消息内容组件
function MessageContent({
  content,
  sources
}: {
  content: string;
  sources?: SourceItem[];
}) {
  const [activeSource, setActiveSource] = useState<number | null>(null);

  const handleCitationClick = (index: number) => {
    setActiveSource(index);
  };

  const parsedContent = sources && sources.length > 0
    ? parseMessageWithCitations(content, sources, handleCitationClick)
    : [content];

  return (
    <>
      <p className="whitespace-pre-wrap text-sm">{parsedContent}</p>

      {/* 底部参考来源列表 */}
      {sources && sources.length > 0 && (
        <div className="mt-2 pt-2 border-t border-gray-200">
          <p className="text-xs text-gray-500 mb-1">参考来源：</p>
          <div className="flex flex-wrap gap-1">
            {sources.map((source, index) => (
              <button
                key={index}
                onClick={() => setActiveSource(index)}
                className="inline-flex items-center gap-1 px-2 py-0.5 text-xs text-gray-600 bg-gray-50 hover:bg-gray-100 rounded border border-gray-200 transition"
              >
                <span className="text-blue-600 font-medium">[{index + 1}]</span>
                <span className="truncate max-w-[120px]">{source.name}</span>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* 源引用弹窗 */}
      {activeSource !== null && sources && sources[activeSource] && (
        <SourcePopup
          source={sources[activeSource]}
          index={activeSource}
          onClose={() => setActiveSource(null)}
        />
      )}
    </>
  );
}

export function StudentAIAssistant({ studentId }: StudentAIAssistantProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // 知识库相关
  const [knowledgeList, setKnowledgeList] = useState<KnowledgeItem[]>([]);
  const [personalKnowledgeIds, setPersonalKnowledgeIds] = useState<Set<string>>(new Set());
  const [showKnowledgeModal, setShowKnowledgeModal] = useState(false);
  const [courses, setCourses] = useState<Course[]>([]);

  // 上传相关
  const [uploadingFile, setUploadingFile] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // 初始化欢迎消息
  useEffect(() => {
    setMessages([
      {
        id: '1',
        role: 'assistant',
        content: '你好！我是你的AI学习助手。\n\n我会自动使用你所在课程的资料来回答问题。你也可以上传自己的学习资料。\n\n💡 点击"资料管理"可以查看和管理你的个人资料。',
        timestamp: new Date(),
      },
    ]);
  }, []);

  // 加载学生课程和知识库
  useEffect(() => {
    if (studentId) {
      loadCoursesAndKnowledge();
    }
  }, [studentId]);

  // 自动滚动到底部
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const loadCoursesAndKnowledge = async () => {
    // 加载课程列表
    const coursesResult = await api.getStudentCourses(studentId);
    if (coursesResult.success && coursesResult.data) {
      setCourses(coursesResult.data.courses);
    }

    // 加载知识库列表
    const courseIds = coursesResult.success && coursesResult.data
      ? coursesResult.data.courses.map((c: Course) => c.id)
      : [];

    const response = await fetch(`${AI_RAG_URL}/knowledge/list`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-user-id': studentId,
      },
      body: JSON.stringify({ course_ids: courseIds })
    });

    const result = await response.json();
    if (result.success) {
      const list = result.knowledge_list || [];
      setKnowledgeList(list);
      // 记录个人知识库ID（个人资料默认选中）
      const personalIds = new Set(
        list.filter((k: KnowledgeItem) => k.source_type === 'personal').map((k: KnowledgeItem) => k.id)
      );
      setPersonalKnowledgeIds(personalIds);
    }
  };

  const handleTogglePersonalKnowledge = (knowledgeId: string) => {
    setPersonalKnowledgeIds(prev => {
      const newSet = new Set(prev);
      if (newSet.has(knowledgeId)) {
        newSet.delete(knowledgeId);
      } else {
        newSet.add(knowledgeId);
      }
      return newSet;
    });
  };

  const handleFileSelect = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const allowedExtensions = ['.pdf', '.docx', '.txt', '.md'];
    const fileExtension = '.' + file.name.split('.').pop()?.toLowerCase();

    if (!allowedExtensions.includes(fileExtension)) {
      toast.error('只支持 PDF、DOCX、TXT、MD 格式的文件');
      return;
    }

    if (file.size > 10 * 1024 * 1024) {
      toast.error('文件大小不能超过 10MB');
      return;
    }

    setUploadingFile(true);

    try {
      const base64 = await fileToBase64(file);

      const response = await fetch(`${AI_RAG_URL}/knowledge/add`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'x-user-id': studentId,
        },
        body: JSON.stringify({
          name: file.name,
          content_base64: base64,
          file_type: fileExtension,
          source_type: 'personal',
        })
      });

      const result = await response.json();

      if (result.success) {
        toast.success(`已添加 "${file.name}"`);
        // 添加到个人知识库并自动选中
        setPersonalKnowledgeIds(prev => new Set(prev).add(result.knowledge_id));
        loadCoursesAndKnowledge();
        if (fileInputRef.current) {
          fileInputRef.current.value = '';
        }
      } else {
        toast.error(result.error || '上传失败');
      }
    } catch (error) {
      console.error('上传文件失败:', error);
      toast.error('上传失败，请检查网络连接');
    } finally {
      setUploadingFile(false);
    }
  };

  const fileToBase64 = (file: File): Promise<string> => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onloadend = () => resolve(reader.result as string);
      reader.onerror = reject;
      reader.readAsDataURL(file);
    });
  };

  const handleDeleteKnowledge = async (knowledgeId: string, knowledgeName: string) => {
    if (!confirm(`确定要删除 "${knowledgeName}" 吗？`)) {
      return;
    }

    try {
      const response = await fetch(`${AI_RAG_URL}/knowledge/${knowledgeId}`, {
        method: 'DELETE',
        headers: {
          'x-user-id': studentId,
        }
      });

      const result = await response.json();
      if (result.success) {
        toast.success('删除成功');
        setPersonalKnowledgeIds(prev => {
          const newSet = new Set(prev);
          newSet.delete(knowledgeId);
          return newSet;
        });
        loadCoursesAndKnowledge();
      } else {
        toast.error(result.error || '删除失败');
      }
    } catch (error) {
      console.error('删除失败:', error);
      toast.error('删除失败，请检查网络连接');
    }
  };

  // 发送消息
  const handleSendMessage = async () => {
    if (!inputMessage.trim()) {
      toast.error('请输入消息');
      return;
    }

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: inputMessage,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      // 构建历史消息
      const history = messages
        .filter(m => m.id !== '1')
        .slice(-6)
        .map(m => ({
          role: m.role,
          content: m.content
        }));

      // 获取课程资源ID + 选中的个人资源ID
      const courseKnowledgeIds = knowledgeList
        .filter(k => k.source_type === 'course')
        .map(k => k.id);
      const selectedIds = [...courseKnowledgeIds, ...Array.from(personalKnowledgeIds)];

      const response = await fetch(`${AI_RAG_URL}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'x-user-id': studentId,
        },
        body: JSON.stringify({
          message: inputMessage,
          knowledge_ids: selectedIds,
          history
        })
      });

      const result = await response.json();

      if (result.success) {
        const assistantMessage: Message = {
          id: (Date.now() + 1).toString(),
          role: 'assistant',
          content: result.message,
          timestamp: new Date(),
          sources: result.sources
        };
        setMessages(prev => [...prev, assistantMessage]);
      } else {
        toast.error(result.error || '获取回答失败');
        const errorMessage: Message = {
          id: (Date.now() + 1).toString(),
          role: 'assistant',
          content: `抱歉，出现了一些问题：${result.error || '未知错误'}`,
          timestamp: new Date(),
        };
        setMessages(prev => [...prev, errorMessage]);
      }
    } catch (error) {
      console.error('发送消息失败:', error);
      toast.error('发送消息失败，请检查网络连接');
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: '抱歉，无法连接到AI服务，请确保RAG服务已启动。',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  // 快捷问题
  const quickQuestions = [
    '你好，你能帮我做什么？',
    '请总结一下重点知识点',
    '有哪些需要注意的难点？',
    '能给我出几道练习题吗？',
  ];

  const handleQuickQuestion = (question: string) => {
    setInputMessage(question);
  };

  // 获取知识库统计
  const courseCount = knowledgeList.filter(k => k.source_type === 'course').length;
  const personalCount = knowledgeList.filter(k => k.source_type === 'personal').length;

  return (
    <div className="h-full flex flex-col bg-white rounded-lg shadow-sm border border-gray-200">
      {/* 头部 */}
      <div className="p-4 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-br from-purple-600 to-blue-600 rounded-full flex items-center justify-center">
              <Sparkles size={20} className="text-white" />
            </div>
            <div>
              <h2 className="text-gray-800 text-lg">AI 学习助手</h2>
              <p className="text-gray-500 text-xs">基于课程资料的智能问答</p>
            </div>
          </div>
          {/* 知识库状态 */}
          <div className="flex items-center gap-2 text-sm">
            {courseCount > 0 && (
              <span className="px-2 py-1 bg-green-100 text-green-700 rounded-full text-xs">
                课程资料 {courseCount}
              </span>
            )}
            {personalCount > 0 && (
              <span className="px-2 py-1 bg-blue-100 text-blue-700 rounded-full text-xs">
                个人资料 {personalCount}
              </span>
            )}
          </div>
        </div>
      </div>

      {/* 消息列表 */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 1 && (
          <div className="mb-4">
            <p className="text-gray-600 text-sm mb-2">💡 试试问我这些问题：</p>
            <div className="grid grid-cols-2 gap-2">
              {quickQuestions.map((question, index) => (
                <button
                  key={index}
                  onClick={() => handleQuickQuestion(question)}
                  className="px-3 py-2 bg-blue-50 text-blue-600 rounded-lg hover:bg-blue-100 transition text-sm text-left"
                >
                  {question}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map(message => (
          <div
            key={message.id}
            className={`flex gap-3 ${message.role === 'user' ? 'flex-row-reverse' : ''}`}
          >
            {/* 头像 */}
            <div
              className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
                message.role === 'user'
                  ? 'bg-gradient-to-br from-blue-500 to-cyan-600'
                  : 'bg-gradient-to-br from-purple-600 to-blue-600'
              }`}
            >
              {message.role === 'user' ? (
                <User size={16} className="text-white" />
              ) : (
                <Bot size={16} className="text-white" />
              )}
            </div>

            {/* 消息内容 */}
            <div className={`flex-1 ${message.role === 'user' ? 'flex justify-end' : ''}`}>
              <div
                className={`inline-block max-w-[85%] px-4 py-3 rounded-lg ${
                  message.role === 'user'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-800'
                }`}
              >
                <MessageContent content={message.content} sources={message.sources} />
                <p
                  className={`text-xs mt-1 ${
                    message.role === 'user' ? 'text-blue-100' : 'text-gray-500'
                  }`}
                >
                  {message.timestamp.toLocaleTimeString('zh-CN', {
                    hour: '2-digit',
                    minute: '2-digit',
                  })}
                </p>
              </div>
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="flex gap-3">
            <div className="w-8 h-8 bg-gradient-to-br from-purple-600 to-blue-600 rounded-full flex items-center justify-center flex-shrink-0">
              <Bot size={16} className="text-white" />
            </div>
            <div className="inline-block px-4 py-3 bg-gray-100 rounded-lg">
              <div className="flex items-center gap-2">
                <Loader size={16} className="text-gray-500 animate-spin" />
                <span className="text-gray-500 text-sm">正在思考...</span>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* 输入框区域 */}
      <div className="p-4 border-t border-gray-200">
        {/* 知识库状态 */}
        <div className="mb-3 flex items-center justify-between">
          <div className="flex items-center gap-2 text-sm text-gray-600">
            <Database size={16} />
            <span>
              使用课程资料 ({courseCount}) + 已选个人资料 ({personalKnowledgeIds.size})
            </span>
          </div>
          <button
            onClick={() => setShowKnowledgeModal(true)}
            className="text-sm text-blue-600 hover:text-blue-700"
          >
            资料管理
          </button>
        </div>

        {/* 输入框 */}
        <div className="flex gap-2">
          <input
            type="text"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSendMessage();
              }
            }}
            placeholder="输入你的问题..."
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            disabled={isLoading}
          />
          <button
            onClick={handleSendMessage}
            disabled={isLoading || !inputMessage.trim()}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
          >
            <Send size={18} />
            <span>发送</span>
          </button>
        </div>
        <p className="text-gray-400 text-xs mt-2">
          回答基于你所在课程的资料，可添加个人资料获得更精准的回答
        </p>
      </div>

      {/* 资料管理弹窗 */}
      {showKnowledgeModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4 max-h-[80vh] flex flex-col">
            {/* 弹窗头部 */}
            <div className="p-4 border-b border-gray-200 flex items-center justify-between">
              <h2 className="text-lg font-semibold text-gray-800">个人资料管理</h2>
              <button
                onClick={() => setShowKnowledgeModal(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <X size={20} />
              </button>
            </div>

            {/* 弹窗内容 */}
            <div className="flex-1 overflow-y-auto p-4">
              {/* 上传区域 */}
              <div className="mb-4 p-4 bg-gray-50 rounded-lg">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  上传个人资料
                </label>
                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".pdf,.docx,.txt,.md"
                  onChange={handleFileSelect}
                  disabled={uploadingFile}
                  className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100 disabled:opacity-50"
                />
                <p className="text-xs text-gray-500 mt-2">支持 PDF、DOCX、TXT、MD，最大 10MB</p>

                {uploadingFile && (
                  <div className="flex items-center gap-2 text-sm text-gray-600 mt-2">
                    <Loader size={16} className="animate-spin" />
                    <span>正在上传并处理文件...</span>
                  </div>
                )}
              </div>

              {/* 个人资料列表 */}
              <div>
                <h3 className="text-sm font-medium text-gray-700 mb-2">我的资料</h3>

                {knowledgeList.filter(k => k.source_type === 'personal').length === 0 ? (
                  <p className="text-sm text-gray-500 text-center py-4">暂无个人资料</p>
                ) : (
                  <div className="space-y-2">
                    {knowledgeList
                      .filter(k => k.source_type === 'personal')
                      .map(knowledge => {
                        const isSelected = personalKnowledgeIds.has(knowledge.id);
                        return (
                          <div
                            key={knowledge.id}
                            className={`p-3 rounded-lg border transition ${
                              isSelected ? 'border-blue-500 bg-blue-50' : 'border-gray-200'
                            }`}
                          >
                            <div className="flex items-start gap-3">
                              <input
                                type="checkbox"
                                checked={isSelected}
                                onChange={() => handleTogglePersonalKnowledge(knowledge.id)}
                                className="w-4 h-4 text-blue-600 rounded focus:ring-2 focus:ring-blue-500 mt-1"
                              />
                              <div className="flex-1 min-w-0">
                                <div className="flex items-center gap-2">
                                  <FileText size={14} className="text-gray-400" />
                                  <span className="text-sm text-gray-800 truncate">{knowledge.name}</span>
                                </div>
                                <p className="text-xs text-gray-500 mt-1">{knowledge.chunks_count} 片段</p>
                              </div>
                              <button
                                onClick={() => handleDeleteKnowledge(knowledge.id, knowledge.name)}
                                className="text-red-500 hover:bg-red-50 rounded p-1"
                                title="删除"
                              >
                                <Trash2 size={14} />
                              </button>
                            </div>
                          </div>
                        );
                      })}
                  </div>
                )}
              </div>

              {/* 课程资料统计 */}
              <div className="mt-4 pt-4 border-t border-gray-200">
                <h3 className="text-sm font-medium text-gray-700 mb-2">课程资料（自动使用）</h3>
                <div className="flex flex-wrap gap-2">
                  {knowledgeList
                    .filter(k => k.source_type === 'course')
                    .map(knowledge => (
                      <span
                        key={knowledge.id}
                        className="inline-flex items-center gap-1 px-2 py-1 bg-green-50 text-green-700 rounded text-xs"
                      >
                        <FileText size={12} />
                        {knowledge.name.length > 15 ? knowledge.name.slice(0, 15) + '...' : knowledge.name}
                      </span>
                    ))}
                </div>
                {courseCount === 0 && (
                  <p className="text-sm text-gray-500">暂无课程资料</p>
                )}
              </div>
            </div>

            {/* 底部操作按钮 */}
            <div className="p-4 border-t border-gray-200">
              <button
                onClick={() => setShowKnowledgeModal(false)}
                className="w-full px-4 py-2 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700"
              >
                确定
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
