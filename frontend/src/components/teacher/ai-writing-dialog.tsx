import { useState, useRef, useEffect } from 'react';
import { X, Sparkles, Upload, Loader, FileText, Check, Undo } from 'lucide-react';
import { toast } from 'sonner@2.0.3';

interface AIWritingDialogProps {
  onClose: () => void;
  onSave: (fileName: string, content: string) => void;
}

interface AIEditResult {
  originalText: string;
  generatedText: string;
  startIndex: number;
  endIndex: number;
}

export function AIWritingDialog({ onClose, onSave }: AIWritingDialogProps) {
  const [step, setStep] = useState<'input' | 'editing'>('input');
  
  // 输入阶段状态
  const [resourceTitle, setResourceTitle] = useState('');
  const [requirements, setRequirements] = useState('');
  const [uploadedFiles, setUploadedFiles] = useState<Array<{name: string, content: string}>>([]);
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedContent, setGeneratedContent] = useState('');
  
  // 二改模式状态
  const [selectedText, setSelectedText] = useState('');
  const [selectionStart, setSelectionStart] = useState(0);
  const [selectionEnd, setSelectionEnd] = useState(0);
  const [showEditPopup, setShowEditPopup] = useState(false);
  const [popupPosition, setPopupPosition] = useState({ top: 0, left: 0 });
  const [editRequirement, setEditRequirement] = useState('');
  const [isEditing, setIsEditing] = useState(false);
  const [aiEditResult, setAIEditResult] = useState<AIEditResult | null>(null);
  
  const fileInputRef = useRef<HTMLInputElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const popupRef = useRef<HTMLDivElement>(null);

  // 处理参考资料上传
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []);
    if (files.length === 0) return;

    files.forEach(file => {
      const reader = new FileReader();
      reader.onload = () => {
        const content = reader.result as string;
        const text = content.includes('base64,') ? atob(content.split('base64,')[1]) : content;
        setUploadedFiles(prev => [...prev, { name: file.name, content: text }]);
        toast.success(`已上传：${file.name}`);
      };
      reader.onerror = () => {
        toast.error(`读取失败：${file.name}`);
      };
      reader.readAsText(file);
    });
  };

  // 删除已上传的文件
  const handleRemoveFile = (index: number) => {
    setUploadedFiles(prev => prev.filter((_, i) => i !== index));
    toast.success('已移除文件');
  };

  // AI生成教学资源
  const generateResource = async () => {
    if (!resourceTitle.trim()) {
      toast.error('请输入资源标题');
      return;
    }
    if (!requirements.trim()) {
      toast.error('请输入生成要求');
      return;
    }

    setIsGenerating(true);
    await new Promise(resolve => setTimeout(resolve, 2000 + Math.random() * 1500));

    // 组合参考资料内容
    const referenceContent = uploadedFiles.length > 0 
      ? `\n\n【参考资料】\n${uploadedFiles.map(f => `文件：${f.name}\n${f.content.substring(0, 200)}...`).join('\n\n')}`
      : '';

    const generated = `# ${resourceTitle}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## 教学资源说明

本教学资源根据以下要求生成：
${requirements}
${referenceContent ? '\n参考了 ' + uploadedFiles.length + ' 个文件作为素材' : ''}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## 一、课程概述

### 1.1 教学目标
通过本节课的学习，学生将能够：
• 理解${resourceTitle}的核心概念和基本原理
• 掌握相关的理论知识和实践技能
• 能够运用所学知识分析和解决实际问题
• 培养独立思考和创新能力

### 1.2 教学重点
• 核心概念的理解与应用
• 理论与实践的有机结合
• 问题分析与解决方法
• 知识迁移与拓展能力

### 1.3 教学难点
• 抽象概念的具体化理解
• 复杂问题的分析方法
• 理论知识的实际应用
• 批判性思维的培养

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## 二、教学内容

### 2.1 导入环节（5分钟）

**情境创设**
通过实际案例或生活实例引入本节课的主题，激发学生的学习兴趣和求知欲。

**问题导向**
提出与主题相关的核心问题，引导学生思考：
1. 为什么要学习这个内容？
2. 它与我们的生活有什么关系？
3. 学习它能解决什么问题？

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

### 2.2 核心知识讲解（20分钟）

**知识点一：基础理论**

📌 概念解析
• 定义：详细阐述核心概念的准确定义
• 特征：分析主要特征和关键要素
• 分类：介绍不同类型及其特点
• 联系：说明与其他概念的关联

💡 理解要点
在理解这一概念时，需要特别注意以下几个方面：
- 概念的本质属性和外延
- 概念形成的历史背景和发展脉络
- 概念在不同情境下的应用方式
- 概念与相关理论的内在联系

📖 案例说明
【案例1】典型应用场景
背景：描述具体情境
分析：运用概念进行分析
结论：总结关键启示

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**知识点二：深入探讨**

🔍 理论框架
1. 基本原理
   • 核心假设和前提条件
   • 逻辑推导过程
   • 理论的适用范围

2. 关键要素
   • 要素A：功能与作用
   • 要素B：相互关系
   • 要素C：影响因素

3. 应用方法
   步骤1：问题识别与分析
   步骤2：理论选择与应用
   步骤3：方案设计与实施
   步骤4：效果评估与改进

🎯 重点强调
特别需要掌握的核心要点：
✓ 理论的核心思想和精髓
✓ 应用的基本方法和技巧
✓ 常见误区和注意事项
✓ 理论创新和发展趋势

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**知识点三：综合应用**

🌟 实践应用
将理论知识转化为实践能力的关键路径：

1. 问题分析能力
   • 识别问题的本质
   • 分析问题的成因
   • 确定解决问题的方向

2. 方案设计能力
   • 制定解决方案
   • 优化方案细节
   • 评估方案可行性

3. 执行实施能力
   • 合理安排步骤
   • 有效配置资源
   • 及时调整策略

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

### 2.3 互动讨论（10分钟）

**小组讨论主题**
将学生分成小组，围绕以下问题展开讨论：
1. 如何将所学理论应用到实际情境中？
2. 在应用过程中可能遇到哪些困难？
3. 如何创新性地解决这些困难？

**成果展示**
每组派代表分享讨论成果，教师进行点评和总结。

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

### 2.4 实践操作（10分钟）

**动手环节**
学生根据所学知识，完成以下实践任务：

任务描述：${requirements.substring(0, 100)}...

操作步骤：
1. 理解任务要求
2. 分析问题关键
3. 制定解决方案
4. 实施并验证
5. 总结与反思

**教师指导**
巡视指导，针对学生的具体问题给予个别辅导，确保每位学生都能顺利完成任务。

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## 三、课堂总结（5分钟）

### 3.1 知识回顾
今天我们学习了${resourceTitle}的相关内容，主要包括：
✅ 核心概念和基本原理
✅ 理论框架和应用方法
✅ 实践操作和问题解决
✅ 批判性思维和创新能力

### 3.2 重点强调
再次强调本节课的核心要点：
• 要点1：${requirements.split('，')[0] || '理论与实践相结合'}
• 要点2：注重问题分析能力的培养
• 要点3：培养创新思维和实践能力

### 3.3 课后延伸
为了巩固所学知识，建议同学们：
1. 复习本节课的核心内容
2. 完成相关练习题
3. 尝试将知识应用到实际场景
4. 阅读推荐的扩展资料

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## 四、教学反思

### 4.1 教学效果评估
• 学生参与度：观察学生的课堂表现
• 知识掌握度：通过提问和练习检验
• 能力提升度：评估实践操作效果
• 创新思维度：鼓励创新性思考

### 4.2 改进方向
• 根据学生反馈调整教学策略
• 优化案例选择和讲解方式
• 增加互动环节和实践机会
• 关注个体差异，因材施教

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## 五、附录资源

### 5.1 推荐阅读
1. 相关理论经典著作
2. 最新研究成果和论文
3. 实践案例分析集
4. 在线学习资源

### 5.2 思考题
1. 如何深化对核心概念的理解？
2. 理论如何更好地指导实践？
3. 如何培养创新性思维？
4. 未来的发展方向是什么？

### 5.3 练习题
（根据教学内容设计相应的练习题）

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【资源生成完成】
本教学资源已根据您的要求生成，您可以选中任意文本进行AI二次改写。`;

    setGeneratedContent(generated);
    setIsGenerating(false);
    setStep('editing');
    toast.success('教学资源已生成！选中文本可进行AI二改');
  };

  // 处理文本选择
  const handleTextSelect = () => {
    if (!textareaRef.current) return;
    
    const start = textareaRef.current.selectionStart;
    const end = textareaRef.current.selectionEnd;
    const selected = generatedContent.substring(start, end);
    
    if (selected && selected.trim().length > 0) {
      setSelectedText(selected);
      setSelectionStart(start);
      setSelectionEnd(end);
      
      // 计算浮窗位置
      const textarea = textareaRef.current;
      const rect = textarea.getBoundingClientRect();
      
      // 浮窗显示在textarea右侧中间位置
      setPopupPosition({
        top: rect.top + rect.height / 2 - 100,
        left: rect.right + 20
      });
      
      setShowEditPopup(true);
      setEditRequirement('');
    } else {
      setShowEditPopup(false);
    }
  };

  // 点击外部关闭浮窗
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (popupRef.current && !popupRef.current.contains(event.target as Node)) {
        if (textareaRef.current && !textareaRef.current.contains(event.target as Node)) {
          setShowEditPopup(false);
        }
      }
    };

    if (showEditPopup) {
      document.addEventListener('mousedown', handleClickOutside);
    }
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [showEditPopup]);

  // AI改写
  const handleAIEdit = async (type: 'rewrite' | 'expand' | 'custom') => {
    if (!selectedText.trim()) {
      toast.error('请先选中要修改的文本');
      return;
    }

    if (type === 'custom' && !editRequirement.trim()) {
      toast.error('请输入修改要求');
      return;
    }

    setIsEditing(true);
    setShowEditPopup(false);
    
    await new Promise(resolve => setTimeout(resolve, 1500 + Math.random() * 1000));

    let generatedText = '';
    
    if (type === 'rewrite') {
      generatedText = `\n\n【AI改写】${selectedText.substring(0, 30)}...\n改写为：通过对原文的重新组织和表达，我们可以更清晰地理解：${selectedText.substring(0, 20)}的核心要点在于......（内容经过优化，表达更加简洁明了，逻辑性更强，便于理解和记忆）`;
    } else if (type === 'expand') {
      generatedText = `\n\n【AI扩写】${selectedText.substring(0, 30)}...\n扩写内容：\n\n进一步说明：\n• 详细解释：在这个概念中，我们需要特别注意......\n• 补充要点：除了上述内容外，还应当了解......\n• 实例说明：例如，在实际应用中，我们可以看到......\n• 深入分析：从理论角度来看，这一部分涉及到......\n\n通过以上扩展，我们对这部分内容有了更深入和全面的理解。`;
    } else {
      generatedText = `\n\n【AI定制修改】按照"${editRequirement}"的要求修改：\n${selectedText.substring(0, 30)}...\n修改后：根据您的要求"${editRequirement}"，我们对内容进行了针对性调整......（内容已按要求优化）`;
    }

    setAIEditResult({
      originalText: selectedText,
      generatedText: generatedText,
      startIndex: selectionStart,
      endIndex: selectionEnd
    });

    setIsEditing(false);
    toast.success('AI处理完成！您可以选择保留或还原');
  };

  // 保留AI修改
  const handleKeepEdit = () => {
    if (!aiEditResult) return;
    
    // 将原文替换为AI生成的内容
    const newContent = 
      generatedContent.substring(0, aiEditResult.startIndex) + 
      aiEditResult.generatedText + 
      generatedContent.substring(aiEditResult.endIndex);
    
    setGeneratedContent(newContent);
    setAIEditResult(null);
    toast.success('已保留AI修改');
  };

  // 还原原文
  const handleRevertEdit = () => {
    setAIEditResult(null);
    toast.success('已还原原文');
  };

  // 渲染内容（带高亮）
  const renderContentWithHighlight = () => {
    if (!aiEditResult) {
      return generatedContent;
    }

    const beforeText = generatedContent.substring(0, aiEditResult.startIndex);
    const afterText = generatedContent.substring(aiEditResult.endIndex);

    return (
      <>
        {beforeText}
        <span className="bg-gray-300 text-gray-500 line-through">{aiEditResult.originalText}</span>
        <span className="bg-yellow-200 text-gray-800">{aiEditResult.generatedText}</span>
        {afterText}
      </>
    );
  };

  // 保存资源
  const handleSaveResource = () => {
    if (aiEditResult) {
      toast.error('请先保留或还原AI修改后再保存');
      return;
    }
    
    if (!generatedContent.trim()) {
      toast.error('资源内容不能为空');
      return;
    }

    const fileName = resourceTitle.trim() ? `${resourceTitle}.txt` : `教学资源_${Date.now()}.txt`;
    onSave(fileName, generatedContent);
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4 overflow-y-auto">
      <div className="bg-white rounded-lg w-full max-w-5xl my-8">
        {/* 头部 */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-br from-purple-600 to-blue-600 rounded-full flex items-center justify-center">
              <Sparkles size={20} className="text-white" />
            </div>
            <div>
              <h2 className="text-gray-800">AI 写作助手</h2>
              <p className="text-gray-500 text-sm">智能创作课件和二次改写</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 text-gray-500 hover:bg-gray-100 rounded-lg transition"
          >
            <X size={20} />
          </button>
        </div>

        {/* 步骤指示 */}
        <div className="p-6 border-b border-gray-200">
          <div className="flex items-center gap-4">
            <div className={`flex items-center gap-2 ${step === 'input' ? 'text-indigo-600' : 'text-gray-400'}`}>
              <div className={`w-8 h-8 rounded-full flex items-center justify-center ${step === 'input' ? 'bg-indigo-600 text-white' : 'bg-gray-200'}`}>
                1
              </div>
              <span className="text-sm">填写生成信息</span>
            </div>
            <div className="flex-1 h-px bg-gray-200"></div>
            <div className={`flex items-center gap-2 ${step === 'editing' ? 'text-indigo-600' : 'text-gray-400'}`}>
              <div className={`w-8 h-8 rounded-full flex items-center justify-center ${step === 'editing' ? 'bg-indigo-600 text-white' : 'bg-gray-200'}`}>
                2
              </div>
              <span className="text-sm">编辑资源（选中文本可AI二改）</span>
            </div>
          </div>
        </div>

        {/* 内容区 */}
        <div className="p-6 max-h-[60vh] overflow-y-auto">
          {step === 'input' ? (
            /* 输入阶段 */
            <div className="space-y-6">
              <div>
                <h3 className="text-gray-800 mb-4">填写生成信息</h3>
                
                <div className="space-y-4">
                  {/* 资源标题 */}
                  <div>
                    <label className="block text-gray-700 text-sm mb-2">
                      <span className="text-red-500">*</span> 资源标题
                    </label>
                    <input
                      type="text"
                      value={resourceTitle}
                      onChange={(e) => setResourceTitle(e.target.value)}
                      placeholder="例如：React Hooks 进阶应用"
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    />
                  </div>

                  {/* 生成要求 */}
                  <div>
                    <label className="block text-gray-700 text-sm mb-2">
                      <span className="text-red-500">*</span> 生成要求/提示词
                    </label>
                    <textarea
                      value={requirements}
                      onChange={(e) => setRequirements(e.target.value)}
                      rows={6}
                      placeholder="请详细描述教学资源的生成要求，例如：&#10;- 面向本科二年级学生&#10;- 重点讲解useState和useEffect的使用&#10;- 包含3-5个实际案例&#10;- 课程时长45分钟&#10;- 包含课堂互动和练习环节"
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 resize-none"
                    />
                  </div>

                  {/* 上传参考资料 */}
                  <div>
                    <label className="block text-gray-700 text-sm mb-2">
                      上传参考资料/模板（可选）
                    </label>
                    <input
                      type="file"
                      ref={fileInputRef}
                      onChange={handleFileChange}
                      accept=".txt,.md,.doc,.docx"
                      multiple
                      className="hidden"
                    />
                    <button
                      onClick={() => fileInputRef.current?.click()}
                      className="w-full px-4 py-3 border-2 border-dashed border-indigo-300 text-indigo-600 rounded-lg hover:bg-indigo-50 transition flex items-center justify-center gap-2"
                    >
                      <Upload size={18} />
                      <span>点击上传参考资料/模板（支持多个文件）</span>
                    </button>
                    
                    {/* 已上传文件列表 */}
                    {uploadedFiles.length > 0 && (
                      <div className="mt-3 space-y-2">
                        {uploadedFiles.map((file, index) => (
                          <div
                            key={index}
                            className="flex items-center justify-between p-3 bg-gray-50 rounded-lg border border-gray-200"
                          >
                            <div className="flex items-center gap-2">
                              <FileText size={16} className="text-indigo-600" />
                              <span className="text-sm text-gray-700">{file.name}</span>
                            </div>
                            <button
                              onClick={() => handleRemoveFile(index)}
                              className="p-1 text-gray-500 hover:text-red-600 hover:bg-red-50 rounded transition"
                            >
                              <X size={16} />
                            </button>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>

                  {/* 生成按钮 */}
                  <button
                    onClick={generateResource}
                    disabled={isGenerating}
                    className="w-full px-4 py-3 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-lg hover:from-purple-700 hover:to-blue-700 transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                  >
                    {isGenerating ? (
                      <>
                        <Loader size={18} className="animate-spin" />
                        <span>AI生成教学资源中...</span>
                      </>
                    ) : (
                      <>
                        <Sparkles size={18} />
                        <span>生成教学资源</span>
                      </>
                    )}
                  </button>
                </div>
              </div>
            </div>
          ) : (
            /* 编辑阶段 */
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-gray-800">编辑教学资源</h3>
                <button
                  onClick={() => setStep('input')}
                  className="text-indigo-600 hover:text-indigo-700 text-sm"
                >
                  ← 返回重新生成
                </button>
              </div>

              {isGenerating ? (
                <div className="flex flex-col items-center justify-center py-12">
                  <Loader size={48} className="text-indigo-600 animate-spin mb-4" />
                  <p className="text-gray-600">AI正在生成教学资源...</p>
                  <p className="text-gray-500 text-sm mt-2">这可能需要几秒钟</p>
                </div>
              ) : generatedContent ? (
                <div className="relative">
                  <label className="block text-gray-700 text-sm mb-2">
                    生成的资源（可编辑，选中文本进行AI二改）
                  </label>
                  
                  {/* 如果有AI编辑结果，显示带高亮的预览 */}
                  {aiEditResult ? (
                    <div className="relative">
                      <div className="w-full px-4 py-2 border-2 border-yellow-400 rounded-lg bg-gray-50 font-mono text-sm whitespace-pre-wrap max-h-[500px] overflow-y-auto">
                        {renderContentWithHighlight()}
                      </div>
                      <div className="mt-4 p-4 bg-blue-50 rounded-lg border border-blue-200">
                        <p className="text-gray-700 text-sm mb-3">
                          <span className="bg-gray-300 text-gray-500 line-through px-1">灰色删除线</span> 表示原文，
                          <span className="bg-yellow-200 text-gray-800 px-1 ml-2">黄色高亮</span> 表示AI生成的内容
                        </p>
                        <div className="flex gap-3">
                          <button
                            onClick={handleKeepEdit}
                            className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition"
                          >
                            <Check size={16} />
                            <span>保留AI修改</span>
                          </button>
                          <button
                            onClick={handleRevertEdit}
                            className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition"
                          >
                            <Undo size={16} />
                            <span>还原原文</span>
                          </button>
                        </div>
                      </div>
                    </div>
                  ) : (
                    <>
                      <textarea
                        ref={textareaRef}
                        value={generatedContent}
                        onChange={(e) => setGeneratedContent(e.target.value)}
                        onSelect={handleTextSelect}
                        rows={20}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 font-mono text-sm"
                      />
                      <p className="text-gray-500 text-xs mt-2">
                        💡 提示：用鼠标选中文本后，会弹出AI二改选项
                      </p>
                    </>
                  )}
                </div>
              ) : null}
            </div>
          )}
        </div>

        {/* 底部按钮 */}
        <div className="p-6 border-t border-gray-200 flex items-center gap-3">
          {step === 'editing' && generatedContent && !aiEditResult && (
            <button
              onClick={handleSaveResource}
              className="flex-1 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition"
            >
              保存教学资源
            </button>
          )}
          <button
            onClick={onClose}
            className="flex-1 px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition"
          >
            取消
          </button>
        </div>
      </div>

      {/* AI二改浮窗 */}
      {showEditPopup && !isEditing && (
        <div
          ref={popupRef}
          className="fixed bg-white rounded-lg shadow-2xl border-2 border-indigo-300 p-4 z-[60]"
          style={{
            top: `${popupPosition.top}px`,
            left: `${popupPosition.left}px`,
            minWidth: '280px'
          }}
        >
          <div className="mb-3">
            <p className="text-gray-600 text-xs mb-2">已选中 {selectedText.length} 个字符</p>
            <div className="flex gap-2">
              <button
                onClick={() => handleAIEdit('rewrite')}
                className="flex-1 flex items-center justify-center gap-1 px-3 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition text-sm"
              >
                <Sparkles size={14} />
                <span>改写</span>
              </button>
              <button
                onClick={() => handleAIEdit('expand')}
                className="flex-1 flex items-center justify-center gap-1 px-3 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition text-sm"
              >
                <Sparkles size={14} />
                <span>扩写</span>
              </button>
            </div>
          </div>
          
          <div className="border-t border-gray-200 pt-3">
            <label className="block text-gray-600 text-xs mb-2">自定义修改要求</label>
            <input
              type="text"
              value={editRequirement}
              onChange={(e) => setEditRequirement(e.target.value)}
              placeholder="例如：改为更口语化的表达"
              className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 mb-2"
              onKeyDown={(e) => {
                if (e.key === 'Enter' && editRequirement.trim()) {
                  handleAIEdit('custom');
                }
              }}
            />
            <button
              onClick={() => handleAIEdit('custom')}
              disabled={!editRequirement.trim()}
              className="w-full flex items-center justify-center gap-1 px-3 py-2 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-lg hover:from-purple-700 hover:to-blue-700 transition text-sm disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Sparkles size={14} />
              <span>按要求修改</span>
            </button>
          </div>
        </div>
      )}

      {/* AI处理中提示 */}
      {isEditing && (
        <div className="fixed inset-0 bg-black/30 flex items-center justify-center z-[70]">
          <div className="bg-white rounded-lg p-6 shadow-2xl">
            <Loader size={48} className="text-indigo-600 animate-spin mx-auto mb-4" />
            <p className="text-gray-600">AI正在处理中...</p>
          </div>
        </div>
      )}
    </div>
  );
}