import { useState } from 'react';
import { X, Sparkles, Loader, Download } from 'lucide-react';
import { toast } from 'sonner@2.0.3';

interface AIPPTDialogProps {
  onClose: () => void;
  onSave: (fileName: string, content: string) => void;
}

export function AIPPTDialog({ onClose, onSave }: AIPPTDialogProps) {
  const [pptTitle, setPPTTitle] = useState('');
  const [requirements, setRequirements] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedPPT, setGeneratedPPT] = useState('');
  const [showPreview, setShowPreview] = useState(false);

  // AI生成PPT
  const generatePPT = async () => {
    if (!pptTitle.trim()) {
      toast.error('请输入PPT标题');
      return;
    }
    if (!requirements.trim()) {
      toast.error('请输入生成要求');
      return;
    }

    setIsGenerating(true);
    await new Promise(resolve => setTimeout(resolve, 2000 + Math.random() * 1500));

    // 生成PPT内容（Markdown格式）
    const pptContent = `---
marp: true
theme: default
paginate: true
---

# ${pptTitle}

---

## 课程概述

### 学习目标
- 理解${pptTitle}的核心概念
- 掌握相关理论和实践方法
- 能够应用知识解决实际问题

### 课程安排
- 理论讲解：30分钟
- 案例分析：15分钟
- 互动讨论：15分钟

---

## 第一部分：基础概念

### 核心定义
${pptTitle}是指...

### 主要特点
- 特点一：...
- 特点二：...
- 特点三：...

### 应用场景
在实际工作中的应用...

---

## 第二部分：理论框架

### 理论基础
- 理论来源
- 发展历程
- 核心思想

### 框架结构
1. 基本要素
2. 相互关系
3. 运作机制

---

## 第三部分：实践应用

### 应用方法
1. 问题识别
2. 方案设计
3. 实施步骤
4. 效果评估

### 成功案例
**案例一：某企业实践**
- 背景介绍
- 实施过程
- 取得成果

---

## 第四部分：深入探讨

### 难点分析
- 难点一及解决方案
- 难点二及解决方案
- 难点三及解决方案

### 注意事项
⚠️ 实施过程中需要注意的关键问题

---

## 第五部分：案例研究

### 综合案例分析
**项目背景**
描述实际项目情况...

**解决方案**
应用所学知识的具体方案...

**实施效果**
项目取得的成果和经验...

---

## 互动讨论

### 思考题
1. 如何将理论应用到实际工作中？
2. 在应用过程中可能遇到哪些挑战？
3. 如何创新性地解决这些挑战？

### 小组讨论
请大家分组讨论上述问题，5分钟后分享观点

---

## 重点回顾

### 核心知识点
✓ ${pptTitle}的基本概念
✓ 理论框架和方法论
✓ 实践应用和案例分析
✓ 难点问题及解决方案

### 关键要点
1. 理论与实践相结合
2. 注重问题分析能力
3. 培养创新思维

---

## 课后作业

### 本周任务
1. 完成课后练习题
2. 阅读推荐文献
3. 撰写学习心得（500字）
4. 准备下次课程讨论

### 提交方式
请在一周内提交到课程平台

---

## 推荐资源

### 必读材料
- 《${pptTitle}理论与实践》
- 相关学术论文集
- 在线课程资源

### 扩展阅读
- 前沿研究动态
- 行业应用案例
- 专家访谈视频

---

## Q&A 环节

### 常见问题
Q1: ${pptTitle}的核心是什么？
A1: ...

Q2: 如何快速掌握相关技能？
A2: ...

### 开放提问
欢迎大家提出问题，共同讨论

---

## 总结

### 课程收获
通过本次学习，我们：
- 理解了核心概念和理论
- 掌握了实践应用方法
- 提升了问题解决能力

### 下节预告
下节课我们将学习...

---

# 感谢聆听！

## 联系方式
- 邮箱：teacher@example.com
- 课程答疑时间：每周三 14:00-16:00

欢迎随时交流讨论！

---`;

    setGeneratedPPT(pptContent);
    setIsGenerating(false);
    setShowPreview(true);
    toast.success('PPT已生成！您可以预览或直接保存');
  };

  // 保存PPT
  const handleSave = () => {
    if (!generatedPPT.trim()) {
      toast.error('PPT内容不能为空');
      return;
    }

    const fileName = pptTitle.trim() ? `${pptTitle}.md` : `PPT_${Date.now()}.md`;
    onSave(fileName, generatedPPT);
  };

  // 下载PPT（Markdown格式）
  const handleDownload = () => {
    if (!generatedPPT.trim()) {
      toast.error('PPT内容不能为空');
      return;
    }

    const blob = new Blob([generatedPPT], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = pptTitle.trim() ? `${pptTitle}.md` : `PPT_${Date.now()}.md`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
    toast.success('PPT已下载');
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4 overflow-y-auto">
      <div className="bg-white rounded-lg w-full max-w-4xl my-8">
        {/* 头部 */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-br from-orange-600 to-pink-600 rounded-full flex items-center justify-center">
              <Sparkles size={20} className="text-white" />
            </div>
            <div>
              <h2 className="text-gray-800">AI PPT 生成</h2>
              <p className="text-gray-500 text-sm">智能生成教学演示文稿</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 text-gray-500 hover:bg-gray-100 rounded-lg transition"
          >
            <X size={20} />
          </button>
        </div>

        {/* 内容区 */}
        <div className="p-6 max-h-[70vh] overflow-y-auto">
          {!showPreview ? (
            /* 输入阶段 */
            <div className="space-y-6">
              <div>
                <h3 className="text-gray-800 mb-4">填写PPT信息</h3>
                
                <div className="space-y-4">
                  {/* PPT标题 */}
                  <div>
                    <label className="block text-gray-700 text-sm mb-2">
                      <span className="text-red-500">*</span> PPT标题
                    </label>
                    <input
                      type="text"
                      value={pptTitle}
                      onChange={(e) => setPPTTitle(e.target.value)}
                      placeholder="例如：React Hooks 进阶应用"
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
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
                      rows={8}
                      placeholder="请详细描述PPT的生成要求，例如：&#10;- 面向本科二年级学生&#10;- 总页数20页左右&#10;- 重点讲解useState和useEffect的使用&#10;- 包含3-5个代码示例&#10;- 包含案例分析和互动讨论环节&#10;- 风格简洁专业"
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 resize-none"
                    />
                  </div>

                  {/* 提示信息 */}
                  <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
                    <p className="text-blue-800 text-sm">
                      💡 <strong>提示：</strong>生成的PPT将采用Markdown格式（支持Marp），您可以使用Marp、reveal.js等工具将其转换为演示文稿。
                    </p>
                  </div>

                  {/* 生成按钮 */}
                  <button
                    onClick={generatePPT}
                    disabled={isGenerating}
                    className="w-full px-4 py-3 bg-gradient-to-r from-orange-600 to-pink-600 text-white rounded-lg hover:from-orange-700 hover:to-pink-700 transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                  >
                    {isGenerating ? (
                      <>
                        <Loader size={18} className="animate-spin" />
                        <span>AI生成PPT中...</span>
                      </>
                    ) : (
                      <>
                        <Sparkles size={18} />
                        <span>生成PPT</span>
                      </>
                    )}
                  </button>
                </div>
              </div>
            </div>
          ) : (
            /* 预览阶段 */
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-gray-800">PPT预览</h3>
                <button
                  onClick={() => setShowPreview(false)}
                  className="text-orange-600 hover:text-orange-700 text-sm"
                >
                  ← 返回重新生成
                </button>
              </div>

              <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
                <div className="flex items-center justify-between mb-3">
                  <p className="text-gray-700">
                    <strong>{pptTitle || '未命名PPT'}.md</strong> 
                    <span className="text-gray-500 text-sm ml-2">
                      (Markdown格式 · 共 {generatedPPT.split('---').length - 1} 页)
                    </span>
                  </p>
                  <button
                    onClick={handleDownload}
                    className="flex items-center gap-2 px-3 py-1.5 text-indigo-600 hover:bg-indigo-50 rounded-lg transition text-sm"
                  >
                    <Download size={16} />
                    <span>下载</span>
                  </button>
                </div>
                
                <div className="bg-white rounded-lg p-4 border border-gray-300 max-h-[400px] overflow-y-auto">
                  <pre className="text-sm text-gray-700 whitespace-pre-wrap font-mono">
                    {generatedPPT}
                  </pre>
                </div>
              </div>

              <div className="bg-yellow-50 rounded-lg p-4 border border-yellow-200">
                <p className="text-yellow-800 text-sm">
                  📌 <strong>使用说明：</strong>
                </p>
                <ul className="text-yellow-700 text-sm mt-2 space-y-1 ml-4 list-disc">
                  <li>此PPT采用Markdown格式，使用"---"分隔每一页</li>
                  <li>可以使用Marp、reveal.js、slidev等工具将其转换为演示文稿</li>
                  <li>您可以直接编辑内容，添加图片、代码、表格等元素</li>
                  <li>点击"保存到课程资源"将文件保存到当前文件夹</li>
                </ul>
              </div>
            </div>
          )}
        </div>

        {/* 底部按钮 */}
        <div className="p-6 border-t border-gray-200 flex items-center gap-3">
          {showPreview && generatedPPT && (
            <button
              onClick={handleSave}
              className="flex-1 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition"
            >
              保存到课程资源
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
    </div>
  );
}
