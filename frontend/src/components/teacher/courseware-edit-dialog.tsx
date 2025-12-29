import { useState, useRef, useEffect } from 'react';
import { X, Sparkles, Loader, Check, Undo } from 'lucide-react';
import { toast } from 'sonner@2.0.3';

interface CoursewareEditDialogProps {
  onClose: () => void;
  onSave: (content: string) => void;
  fileName: string;
  content: string;
}

interface AIEditResult {
  originalText: string;
  generatedText: string;
  startIndex: number;
  endIndex: number;
}

export function CoursewareEditDialog({ onClose, onSave, fileName, content: initialContent }: CoursewareEditDialogProps) {
  const [courseware, setCourseware] = useState('');
  const [selectedText, setSelectedText] = useState('');
  const [selectionStart, setSelectionStart] = useState(0);
  const [selectionEnd, setSelectionEnd] = useState(0);
  const [showEditPopup, setShowEditPopup] = useState(false);
  const [popupPosition, setPopupPosition] = useState({ top: 0, left: 0 });
  const [editRequirement, setEditRequirement] = useState('');
  const [isEditing, setIsEditing] = useState(false);
  const [aiEditResult, setAIEditResult] = useState<AIEditResult | null>(null);
  
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const popupRef = useRef<HTMLDivElement>(null);

  // 初始化课件内容
  useEffect(() => {
    // 从 base64 解码内容
    try {
      if (initialContent.startsWith('data:')) {
        // 如果是 data URL 格式
        const base64Content = initialContent.split('base64,')[1];
        if (base64Content) {
          const decodedContent = decodeURIComponent(escape(atob(base64Content)));
          setCourseware(decodedContent);
        } else {
          setCourseware('');
        }
      } else {
        // 如果是普通文本
        setCourseware(initialContent);
      }
    } catch (error) {
      console.error('解码失败:', error);
      // 尝试直接使用
      setCourseware(initialContent);
    }
  }, [initialContent]);

  // 处理文本选择
  const handleTextSelect = () => {
    if (!textareaRef.current) return;
    
    const start = textareaRef.current.selectionStart;
    const end = textareaRef.current.selectionEnd;
    const selected = courseware.substring(start, end);
    
    if (selected && selected.trim().length > 0) {
      setSelectedText(selected);
      setSelectionStart(start);
      setSelectionEnd(end);
      
      // 计算浮窗位置
      const textarea = textareaRef.current;
      const rect = textarea.getBoundingClientRect();
      
      // 简单计算：浮窗显示在textarea右侧中间位置
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
      courseware.substring(0, aiEditResult.startIndex) + 
      aiEditResult.generatedText + 
      courseware.substring(aiEditResult.endIndex);
    
    setCourseware(newContent);
    setAIEditResult(null);
    toast.success('已保留AI修改');
  };

  // 还原原文
  const handleRevertEdit = () => {
    setAIEditResult(null);
    toast.success('已还原原文');
  };

  // 渲染课件内容（带高亮）
  const renderCoursewareWithHighlight = () => {
    if (!aiEditResult) {
      return courseware;
    }

    const beforeText = courseware.substring(0, aiEditResult.startIndex);
    const afterText = courseware.substring(aiEditResult.endIndex);

    return (
      <>
        {beforeText}
        <span className="bg-gray-300 text-gray-500 line-through">{aiEditResult.originalText}</span>
        <span className="bg-yellow-200 text-gray-800">{aiEditResult.generatedText}</span>
        {afterText}
      </>
    );
  };

  // 保存课件
  const handleSaveCourseware = () => {
    if (aiEditResult) {
      toast.error('请先保留或还原AI修改后再保存');
      return;
    }
    
    if (!courseware.trim()) {
      toast.error('课件内容不能为空');
      return;
    }

    onSave(courseware);
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4 overflow-y-auto">
      <div className="bg-white rounded-lg w-full max-w-5xl my-8">
        {/* 头部 */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div>
            <h2 className="text-gray-800">编辑课件</h2>
            <p className="text-gray-500 text-sm mt-1">{fileName}</p>
          </div>
          <button
            onClick={onClose}
            className="p-2 text-gray-500 hover:bg-gray-100 rounded-lg transition"
          >
            <X size={20} />
          </button>
        </div>

        {/* 内容区 */}
        <div className="p-6 max-h-[60vh] overflow-y-auto">
          <div className="relative">
            <label className="block text-gray-700 text-sm mb-2">
              课件内容（选中文本进行AI二改）
            </label>
            
            {/* 如果有AI编辑结果，显示带高亮的预览 */}
            {aiEditResult ? (
              <div className="relative">
                <div className="w-full px-4 py-2 border-2 border-yellow-400 rounded-lg bg-gray-50 font-mono text-sm whitespace-pre-wrap max-h-[500px] overflow-y-auto">
                  {renderCoursewareWithHighlight()}
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
                  value={courseware}
                  onChange={(e) => setCourseware(e.target.value)}
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
        </div>

        {/* 底部按钮 */}
        <div className="p-6 border-t border-gray-200 flex items-center gap-3">
          {!aiEditResult && (
            <button
              onClick={handleSaveCourseware}
              className="flex-1 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition"
            >
              保存课件
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