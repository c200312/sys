import { useState, useRef, useEffect } from 'react';
import { Sparkles, Send, Loader, User, Bot } from 'lucide-react';
import { toast } from 'sonner@2.0.3';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

interface StudentAIAssistantProps {
  studentId: string;
}

export function StudentAIAssistant({ studentId }: StudentAIAssistantProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // 初始化欢迎消息
  useEffect(() => {
    setMessages([
      {
        id: '1',
        role: 'assistant',
        content: '你好！我是你的AI学习助手。我可以帮助你：\n\n📚 解答学习问题\n💡 提供学习建议\n📝 辅导作业问题\n🎯 制定学习计划\n\n有什么我可以帮助你的吗？',
        timestamp: new Date(),
      },
    ]);
  }, []);

  // 自动滚动到底部
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

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

    // 模拟AI回复
    await new Promise(resolve => setTimeout(resolve, 1500 + Math.random() * 1000));

    const aiResponse = generateAIResponse(inputMessage);
    const assistantMessage: Message = {
      id: (Date.now() + 1).toString(),
      role: 'assistant',
      content: aiResponse,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, assistantMessage]);
    setIsLoading(false);
  };

  // 生成AI回复
  const generateAIResponse = (userInput: string): string => {
    const input = userInput.toLowerCase();

    // 学习相关
    if (input.includes('学习') || input.includes('怎么学')) {
      return '关于学习方法，我有以下建议：\n\n1. 制定学习计划：每天固定时间学习，保持规律\n2. 主动思考：不要只是被动接受知识，要主动提问\n3. 及时复习：遵循艾宾浩斯遗忘曲线，定期复习\n4. 做好笔记：记录重点和难点，方便回顾\n5. 实践应用：理论结合实践，加深理解\n\n你想了解哪方面的具体方法？';
    }

    // 作业相关
    if (input.includes('作业') || input.includes('题目')) {
      return '关于作业问题：\n\n📝 我可以帮你：\n• 理解题目要求\n• 提供解题思路\n• 讲解相关知识点\n• 检查答案逻辑\n\n💡 建议：\n• 先独立思考，再寻求帮助\n• 理解解题方法比答案更重要\n• 举一反三，掌握同类题型\n\n请告诉我具体的题目或问题！';
    }

    // 课程相关
    if (input.includes('课程') || input.includes('课堂')) {
      return '关于课程学习：\n\n✅ 课前准备：\n• 预习课程内容\n• 准备好学习材料\n• 思考可能的疑问\n\n✅ 课堂学习：\n• 认真听讲，做好笔记\n• 积极参与讨论\n• 及时提问\n\n✅ 课后巩固：\n• 整理笔记\n• 完成课后练习\n• 复习重点难点\n\n有什么具体问题吗？';
    }

    // 考试相关
    if (input.includes('考试') || input.includes('复习')) {
      return '考试复习建议：\n\n📚 复习策略：\n1. 梳理知识框架：建立完整的知识体系\n2. 重点突破：找出薄弱环节重点复习\n3. 真题练习：熟悉题型和考点\n4. 错题整理：总结易错点和解题方法\n\n⏰ 时间规划：\n• 提前制定复习计划\n• 合理分配各科时间\n• 劳逸结合，保证休息\n\n💪 心态调整：\n• 保持自信\n• 适度紧张\n• 规律作息\n\n加油！相信你一定能考好！';
    }

    // 时间管理
    if (input.includes('时间') || input.includes('计划')) {
      return '时间管理建议：\n\n⏰ 制定计划：\n• 使用番茄工作法（25分钟专注+5分钟休息）\n• 按优先级排列任务\n• 预留缓冲时间\n\n📋 执行技巧：\n• 消除干扰（关闭手机通知）\n• 一次只做一件事\n• 设置明确的deadline\n\n📊 效果评估：\n• 记录时间使用情况\n• 定期反思和调整\n• 奖励自己的进步\n\n坚持就是胜利！';
    }

    // 默认回复
    return `我理解你的问题："${userInput}"\n\n作为你的学习助手，我会尽力帮助你。你可以问我：\n\n• 学习方法和技巧\n• 课程内容相关问题\n• 作业辅导和答疑\n• 学习计划制定\n• 考试复习建议\n• 时间管理方法\n\n请告诉我更具体的问题，我会给你详细的建议！😊`;
  };

  // 快捷问题
  const quickQuestions = [
    '如何制定学习计划？',
    '怎样提高学习效率？',
    '作业遇到困难怎么办？',
    '如何准备考试？',
  ];

  const handleQuickQuestion = (question: string) => {
    setInputMessage(question);
  };

  return (
    <div className="h-full flex flex-col bg-white rounded-lg shadow-sm border border-gray-200">
      {/* 头部 */}
      <div className="p-6 border-b border-gray-200">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 bg-gradient-to-br from-purple-600 to-blue-600 rounded-full flex items-center justify-center">
            <Sparkles size={24} className="text-white" />
          </div>
          <div>
            <h2 className="text-gray-800">AI学习助手</h2>
            <p className="text-gray-500 text-sm">智能解答，助力学习</p>
          </div>
        </div>
      </div>

      {/* 消息列表 */}
      <div className="flex-1 overflow-y-auto p-6 space-y-4">
        {messages.length === 1 && (
          <div className="mb-6">
            <p className="text-gray-600 text-sm mb-3">💡 试试问我这些问题：</p>
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

        {messages.map((message) => (
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
                className={`inline-block max-w-[80%] px-4 py-3 rounded-lg ${
                  message.role === 'user'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-800'
                }`}
              >
                <p className="whitespace-pre-wrap text-sm">{message.content}</p>
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
              <Loader size={16} className="text-gray-500 animate-spin" />
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* 输入框 */}
      <div className="p-4 border-t border-gray-200">
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
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
          >
            <Send size={18} />
            <span>发送</span>
          </button>
        </div>
        <p className="text-gray-400 text-xs mt-2">按 Enter 发送消息</p>
      </div>
    </div>
  );
}
