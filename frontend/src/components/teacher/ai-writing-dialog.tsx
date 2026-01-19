import { useState, useRef, useEffect, ChangeEvent, MouseEvent } from 'react';
import { X, Sparkles, Upload, Loader, FileText, Check, Undo } from 'lucide-react';
import { toast } from 'sonner@2.0.3';

const WRITING_API_BASE = import.meta.env.VITE_WRITING_API_URL || 'http://localhost:8003';

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

interface UploadedFile {
  name: string;
  content: string;
}

// 资源类型选项
const RESOURCE_TYPES = [
  { value: 'lesson_plan', label: '教案', description: '包含教学目标、重难点、教学过程等' },
  { value: 'exercises', label: '习题/试卷', description: '选择题、填空题、简答题等，含答案' },
  { value: 'courseware', label: '课件大纲', description: '适合制作PPT的结构化大纲' },
  { value: 'summary', label: '知识总结', description: '知识点整理、重点归纳' },
  { value: 'activity', label: '教学活动设计', description: '互动活动方案、实施步骤' },
  { value: 'custom', label: '自定义', description: '按照您的要求自由创作' },
];

// 每种资源类型的示例模板
const RESOURCE_TEMPLATES_EXAMPLES: Record<string, string> = {
  lesson_plan: `请生成一份关于"基于eBPF劫持CUDA Driver API实现GPU细粒度虚拟化"的完整教案，要求如下：

【课程基本信息】
- 面向云原生/AI基础设施方向的研究生或高年级本科生
- 课程时长：90分钟（含实验演示）
- 先修知识：Linux内核基础、容器技术、CUDA编程基础

【教学目标】
1. 理解云原生时代GPU算力困境：资源利用率低、传统虚拟化方案局限性
2. 掌握eBPF核心技术：Uprobes机制、BPF Map、内核态Hook原理
3. 理解CUDA Driver API与Runtime API的关系及拦截策略
4. 掌握GPU虚拟化架构：控制面(HAMi-Scheduler、Webhook)与数据面(Device Plugin、eBPF Agent)
5. 理解关键实现：显存虚拟化(cuMemAlloc拦截)、算力虚拟化(时间片轮转)、故障隔离

【教学内容要点】
1. 背景与动机（15分钟）
   - GPU资源碎片化问题：单个Jupyter占用整张A100
   - 传统方案对比：PCIe Passthrough、vGPU、MIG、LD_PRELOAD的优缺点

2. eBPF技术原理（20分钟）
   - eBPF架构：验证器、JIT编译、Map数据结构
   - Uprobe机制：用户态函数Hook原理
   - 与传统LD_PRELOAD方案的对比优势

3. CUDA驱动模型（15分钟）
   - Runtime API vs Driver API层次关系
   - 为什么必须Hook libcuda.so
   - 关键API：cuMemAlloc、cuLaunchKernel

4. 系统架构设计（20分钟）
   - 控制面：HAMi-Scheduler调度策略、Mutating Webhook
   - 数据面：Device Plugin资源上报、eBPF Agent拦截
   - 显存虚拟化：配额检查、欺骗查询
   - 算力虚拟化：Token桶限流、时间片轮转

5. 生产实践（15分钟）
   - Kubernetes部署：Helm安装HAMi
   - Pod资源申请：nvidia.com/gpumem、nvidia.com/gpucores
   - 性能评估：约1-2%损耗

6. 实验演示（5分钟）
   - 演示多容器共享GPU场景

【教学方法】
- 理论讲授结合架构图解析
- 代码走读：eBPF程序示例
- 实际演示：Kubernetes环境部署`,

  exercises: `请生成一套关于"eBPF GPU虚拟化技术"的习题，要求如下：

【题目设置】
- 题目总数：10道
- 题型分布：选择题5道、填空题3道、简答题2道
- 难度分级：基础题60%、提高题30%、拓展题10%

【考察知识点】
1. eBPF基础：验证器、JIT、Map类型、Uprobe机制
2. CUDA架构：Runtime API与Driver API关系、关键API功能
3. 虚拟化原理：显存虚拟化、算力虚拟化、故障隔离
4. 系统架构：HAMi组件、Device Plugin、调度策略
5. 生产实践：Kubernetes资源配置、性能指标

【题目示例方向】
- 选择题：eBPF相比LD_PRELOAD的优势、cuMemAlloc拦截的目的
- 填空题：BPF Map类型、HAMi调度策略名称
- 简答题：解释显存"欺骗查询"的必要性、描述Token桶限流算法

【答案要求】
- 每道题目需标注考察知识点
- 提供完整的参考答案和详细解析
- 预估完成时间：45分钟`,

  courseware: `请生成关于"基于eBPF的GPU细粒度虚拟化"课件大纲，要求如下：

【整体结构】
- 总页数控制在25-30页
- 每页包含标题和3-5个要点
- 需要配图建议的页面请标注[配图：图片描述]

【内容大纲】
第一部分：背景与动机（5页）
- 封面：标题、副标题、讲师信息
- GPU算力困境：利用率数据、成本问题
- 传统虚拟化方案对比表：Passthrough/vGPU/MIG/LD_PRELOAD
- eBPF方案优势：透明性、安全性、高性能
- [配图：虚拟化架构层次图]

第二部分：eBPF技术原理（6页）
- eBPF架构总览 [配图：eBPF内部架构图]
- 验证器与JIT编译
- BPF Map数据结构
- Uprobe机制详解
- Hook流程示意 [配图：Uprobe Hook流程图]
- 代码示例：基础eBPF程序

第三部分：CUDA驱动模型（4页）
- CUDA软件栈层次 [配图：CUDA架构图]
- Runtime API vs Driver API
- 关键API：cuMemAlloc、cuLaunchKernel
- 为什么Hook Driver API

第四部分：系统架构设计（8页）
- 整体架构图 [配图：HAMi架构示意图]
- 控制面组件：Scheduler、Webhook
- 数据面组件：Device Plugin、eBPF Agent
- 显存虚拟化实现
- 算力虚拟化实现
- 故障隔离机制
- 拓扑感知调度 [配图：NVLink拓扑图]
- eBPF代码示例：cuMemAlloc拦截

第五部分：生产实践（5页）
- Kubernetes部署步骤
- Pod资源配置示例
- 监控指标与Grafana面板
- 性能评估数据
- 常见问题排查

第六部分：总结（2页）
- 核心优势总结
- 未来展望与Q&A`,

  summary: `请生成关于"eBPF GPU虚拟化技术"的知识总结，要求如下：

【结构要求】
- 采用思维导图式的层级结构
- 核心概念需要给出准确定义
- 列出知识点之间的关联关系
- 标注重点和易混淆点

【知识点覆盖】
1. eBPF核心概念
   - 定义：extended Berkeley Packet Filter
   - 组件：验证器、JIT编译器、Map、Helper函数
   - Uprobe：用户态函数探针
   - 与传统方案对比

2. CUDA架构
   - Runtime API (libcudart.so)：高级封装
   - Driver API (libcuda.so)：底层接口
   - 关键API功能说明

3. GPU虚拟化技术
   - 显存虚拟化：配额检查、欺骗查询、地址映射
   - 算力虚拟化：Token桶、时间片轮转
   - 故障隔离：XID错误处理

4. HAMi系统架构
   - 控制面：Scheduler扩展、Webhook注入
   - 数据面：Device Plugin、eBPF Agent
   - 调度策略：Binpack、Spread、拓扑感知

【记忆要点】
- 关键数值：性能损耗约1-2%
- 易混淆点：Runtime API vs Driver API
- 核心优势：细粒度、硬隔离、零侵入、生态兼容`,

  activity: `请设计关于"eBPF GPU虚拟化"的教学活动方案，要求如下：

【活动基本信息】
- 活动时长：30分钟
- 参与形式：小组协作（3-4人一组）
- 所需环境：每组一台配置好Kubernetes和GPU的实验机器

【活动目标】
1. 理解GPU资源碎片化问题
2. 掌握HAMi部署和配置方法
3. 验证GPU虚拟化效果

【活动步骤】

第一阶段：环境准备（5分钟）
- 检查Kubernetes集群状态
- 确认GPU节点标签
- 验证NVIDIA驱动版本

第二阶段：HAMi部署（10分钟）
- 添加Helm仓库
- 执行helm install命令
- 检查Pod运行状态
- 验证Device Plugin注册

第三阶段：资源验证（10分钟）
- 创建申请vGPU的测试Pod
- 配置显存限制(nvidia.com/gpumem)
- 配置算力限制(nvidia.com/gpucores)
- 在容器内运行nvidia-smi验证
- 运行简单CUDA程序测试限制效果

第四阶段：结果讨论（5分钟）
- 各组分享实验结果
- 讨论遇到的问题
- 对比物理卡与虚拟化后的差异

【评价标准】
- HAMi部署成功：40分
- Pod正确申请vGPU资源：30分
- 验证限制生效：20分
- 问题分析与讨论：10分

【注意事项】
- 确保集群有足够的GPU资源
- 提前准备好测试用的CUDA程序镜像
- 准备常见错误的排查指南`,

  custom: `请按照您的需求自由创作，您可以描述：
- 目标受众和教学场景
- 内容主题和核心要点
- 期望的格式和结构
- 特殊要求或注意事项`,
};

export function AIWritingDialog({ onClose, onSave }: AIWritingDialogProps) {
  const [step, setStep] = useState<'input' | 'editing'>('input');

  // 输入阶段状态
  const [resourceTitle, setResourceTitle] = useState('');
  const [resourceType, setResourceType] = useState('lesson_plan');
  const [requirements, setRequirements] = useState(RESOURCE_TEMPLATES_EXAMPLES['lesson_plan']);
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([]);
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
  const editInputRef = useRef<HTMLInputElement>(null);

  // 处理参考资料上传
  const handleFileChange = async (e: ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []);
    if (files.length === 0) return;

    for (const file of files) {
      try {
        // 读取文件为 base64
        const reader = new FileReader();
        const base64Content = await new Promise<string>((resolve, reject) => {
          reader.onload = () => resolve(reader.result as string);
          reader.onerror = reject;
          reader.readAsDataURL(file);
        });

        // 调用后端解析接口
        const response = await fetch(`${WRITING_API_BASE}/parse`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            filename: file.name,
            content_base64: base64Content,
          }),
        });

        const result = await response.json();

        if (result.success) {
          setUploadedFiles(prev => [...prev, {
            name: file.name,
            content: result.text_content
          }]);
          toast.success(`已解析：${file.name}`);
        } else {
          toast.error(result.error || `解析失败：${file.name}`);
        }
      } catch (error) {
        console.error('File upload error:', error);
        toast.error(`上传失败：${file.name}`);
      }
    }

    // 重置 input
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
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

    try {
      console.log('[AI Writing] Generating with type:', resourceType);
      const response = await fetch(`${WRITING_API_BASE}/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          title: resourceTitle.trim(),
          resource_type: resourceType,
          requirements: requirements.trim(),
          reference_contents: uploadedFiles.map(f => f.content),
          reference_names: uploadedFiles.map(f => f.name),
        }),
      });

      const result = await response.json();

      if (result.success && result.content) {
        setGeneratedContent(result.content);
        setStep('editing');
        toast.success('教学资源已生成！选中文本可进行AI二改');
      } else {
        toast.error(result.error || '生成失败，请重试');
      }
    } catch (error) {
      console.error('Generate error:', error);
      toast.error('生成失败，请检查后端服务是否启动');
    } finally {
      setIsGenerating(false);
    }
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

  // 点击外部关闭浮窗（但点击浮窗内部的输入框不关闭）
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      // 如果点击在浮窗内部，不关闭
      if (popupRef.current && popupRef.current.contains(event.target as Node)) {
        return;
      }
      // 如果点击在 textarea 内部，不关闭（允许重新选择）
      if (textareaRef.current && textareaRef.current.contains(event.target as Node)) {
        return;
      }
      // 其他情况关闭浮窗
      setShowEditPopup(false);
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

    try {
      const response = await fetch(`${WRITING_API_BASE}/rewrite`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          selected_text: selectedText,
          rewrite_type: type,
          custom_requirement: type === 'custom' ? editRequirement : undefined,
          context: generatedContent.substring(
            Math.max(0, selectionStart - 200),
            Math.min(generatedContent.length, selectionEnd + 200)
          ),
        }),
      });

      const result = await response.json();

      if (result.success && result.content) {
        setAIEditResult({
          originalText: selectedText,
          generatedText: result.content,
          startIndex: selectionStart,
          endIndex: selectionEnd
        });
        toast.success('AI处理完成！您可以选择保留或还原');
      } else {
        toast.error(result.error || '改写失败，请重试');
      }
    } catch (error) {
      console.error('Rewrite error:', error);
      toast.error('改写失败，请检查后端服务是否启动');
    } finally {
      setIsEditing(false);
    }
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

                  {/* 资源类型选择 */}
                  <div>
                    <label className="block text-gray-700 text-sm mb-2">
                      <span className="text-red-500">*</span> 资源类型
                    </label>
                    <select
                      value={resourceType}
                      onChange={(e) => {
                        const newType = e.target.value;
                        setResourceType(newType);
                        // 切换类型时自动填充对应的示例模板
                        setRequirements(RESOURCE_TEMPLATES_EXAMPLES[newType] || '');
                      }}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-white"
                    >
                      {RESOURCE_TYPES.map((type) => (
                        <option key={type.value} value={type.value}>
                          {type.label} - {type.description}
                        </option>
                      ))}
                    </select>
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
              ref={editInputRef}
              type="text"
              value={editRequirement}
              onChange={(e) => setEditRequirement(e.target.value)}
              placeholder="例如：改为更口语化的表达"
              className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 mb-2"
              onMouseDown={(e: MouseEvent) => e.stopPropagation()}
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