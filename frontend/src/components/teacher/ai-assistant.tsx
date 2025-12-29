import { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Loader, Sparkles } from 'lucide-react';
import { toast } from 'sonner@2.0.3';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

interface AIAssistantProps {
  courseId: string;
  courseName: string;
}

export function AIAssistant({ courseId, courseName }: AIAssistantProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      role: 'assistant',
      content: `你好！我是《${courseName}》课程的AI助手。我可以帮助你：\n\n📚 解答课程相关问题\n✍️ 提供作业设计建议\n📊 分析学生学习情况\n💡 提供教学方法建议\n\n请问有什么我可以帮助你的吗？`,
      timestamp: new Date(),
    },
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // 自动滚动到底部
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // 发送消息
  const handleSend = async () => {
    if (!inputValue.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: inputValue.trim(),
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    // 模拟AI回复（这里可以接入真实的AI API）
    setTimeout(() => {
      const aiResponse: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: generateAIResponse(userMessage.content),
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, aiResponse]);
      setIsLoading(false);
    }, 1000 + Math.random() * 1000);
  };

  // 生成AI回复（模拟）
  const generateAIResponse = (userInput: string): string => {
    const input = userInput.toLowerCase();

    // 作业相关
    if (input.includes('作业') || input.includes('布置')) {
      return `关于作业布置，我有以下建议：\n\n1. **明确目标**：确保作业与课程学习目标对齐\n2. **难度适中**：考虑学生的实际水平，既有挑战性又可完成\n3. **形式多样**：可以结合理论题、实践题、小组项目等\n4. **及时反馈**：设置合理的截止时间，并及时批改反馈\n\n你具体想了解作业的哪个方面呢？`;
    }

    // 学生管理相关
    if (input.includes('学生') || input.includes('学员')) {
      return `关于学生管理，建议关注以下几点：\n\n📊 **学习数据分析**：定期查看作业提交率、成绩分布\n💬 **互动沟通**：通过作业批语、课程资源等加强互动\n🎯 **分层教学**：根据学生表现提供个性化指导\n⚡ **及时激励**：对表现优秀的学生给予肯定\n\n需要我详细说明某一方面吗？`;
    }

    // 教学方法相关
    if (input.includes('教学') || input.includes('方法') || input.includes('如何')) {
      return `关于教学方法，这里有一些实用建议：\n\n🎓 **案例教学**：用实际案例帮助学生理解理论\n🤝 **互动式学习**：鼓励学生提问和讨论\n📱 **数字化工具**：善用在线资源、视频等辅助教学\n📝 **过程性评价**：注重学习过程而非单次考试\n\n你想深入了解哪种教学方法？`;
    }

    // 课程资源相关
    if (input.includes('资源') || input.includes('材料') || input.includes('课件')) {
      return `关于课程资源建设：\n\n📚 **系统化组织**：按章节或主题分类整理资料\n📄 **多种格式**：提供PDF、视频、PPT等多种格式\n🔄 **定期更新**：及时补充最新的教学资源\n💾 **云端存储**：使用课程资源功能方便学生随时访问\n\n需要帮你整理特定类型的资源吗？`;
    }

    // 评分相关
    if (input.includes('评分') || input.includes('批改') || input.includes('打分')) {
      return `关于作业批改和评分：\n\n✅ **标准明确**：提前告知评分标准，让学生有清晰预期\n📊 **等级评价**：可以采用优秀/良好/及格等等级制\n💬 **反馈详细**：不只给分数，更要给出改进建议\n⏰ **及时批改**：尽量在一周内完成批改\n\n你想了解如何制定评分标准吗？`;
    }

    // 默认回复
    return `感谢你的问题！作为《${courseName}》的AI助手，我会尽力帮助你。\n\n你可以问我关于：\n• 作业设计与布置\n• 学生管理技巧\n• 教学方法建议\n• 课程资源整理\n• 评分标准制定\n\n请告诉我你具体想了解什么？`;
  };

  // 快捷问题
  const quickQuestions = [
    '如何设计有效的作业？',
    '怎样提高学生参与度？',
    '如何组织课程资源？',
    '评分标准怎么制定？',
  ];

  return (
    <div className="flex flex-col h-[calc(100vh-280px)]">
      {/* 头部 */}
      <div className="flex items-center gap-3 mb-4 pb-4 border-b border-gray-200">
        <div className="w-10 h-10 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-full flex items-center justify-center">
          <Sparkles size={20} className="text-white" />
        </div>
        <div>
          <h3 className="text-gray-800">AI 教学助手</h3>
          <p className="text-gray-500 text-sm">为《{courseName}》课程提供智能支持</p>
        </div>
      </div>

      {/* 快捷问题 */}
      {messages.length === 1 && (
        <div className="mb-4">
          <p className="text-gray-600 text-sm mb-3">💡 快捷提问：</p>
          <div className="grid grid-cols-2 gap-2">
            {quickQuestions.map((question, index) => (
              <button
                key={index}
                onClick={() => {
                  setInputValue(question);
                  inputRef.current?.focus();
                }}
                className="p-3 text-left bg-gray-50 hover:bg-gray-100 rounded-lg transition text-sm text-gray-700 border border-gray-200"
              >
                {question}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* 消息列表 */}
      <div className="flex-1 overflow-y-auto mb-4 space-y-4">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex gap-3 ${
              message.role === 'user' ? 'flex-row-reverse' : 'flex-row'
            }`}
          >
            {/* 头像 */}
            <div
              className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
                message.role === 'user'
                  ? 'bg-indigo-600'
                  : 'bg-gradient-to-br from-indigo-500 to-purple-600'
              }`}
            >
              {message.role === 'user' ? (
                <User size={16} className="text-white" />
              ) : (
                <Bot size={16} className="text-white" />
              )}
            </div>

            {/* 消息内容 */}
            <div
              className={`max-w-[70%] ${
                message.role === 'user' ? 'items-end' : 'items-start'
              }`}
            >
              <div
                className={`px-4 py-3 rounded-2xl ${
                  message.role === 'user'
                    ? 'bg-indigo-600 text-white'
                    : 'bg-gray-100 text-gray-800'
                }`}
              >
                <p className="text-sm whitespace-pre-wrap">{message.content}</p>
              </div>
              <p className="text-xs text-gray-500 mt-1 px-2">
                {message.timestamp.toLocaleTimeString('zh-CN', {
                  hour: '2-digit',
                  minute: '2-digit',
                })}
              </p>
            </div>
          </div>
        ))}

        {/* 加载中 */}
        {isLoading && (
          <div className="flex gap-3">
            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center flex-shrink-0">
              <Bot size={16} className="text-white" />
            </div>
            <div className="px-4 py-3 bg-gray-100 rounded-2xl">
              <div className="flex items-center gap-2">
                <Loader size={16} className="text-gray-600 animate-spin" />
                <span className="text-sm text-gray-600">AI正在思考...</span>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* 输入框 */}
      <div className="border-t border-gray-200 pt-4">
        <div className="flex items-center gap-3">
          <input
            ref={inputRef}
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSend();
              }
            }}
            placeholder="输入你的问题..."
            className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
            disabled={isLoading}
          />
          <button
            onClick={handleSend}
            disabled={!inputValue.trim() || isLoading}
            className="px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
          >
            <Send size={18} />
            <span>发送</span>
          </button>
        </div>
        <p className="text-xs text-gray-500 mt-2">
          💡 提示：按 Enter 发送，Shift + Enter 换行
        </p>
      </div>
    </div>
  );
}
