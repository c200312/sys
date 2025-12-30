import { useState } from 'react';
import { X, Sparkles, Loader, Download, ChevronLeft, ChevronRight, Image } from 'lucide-react';
import { toast } from 'sonner@2.0.3';

const PPT_API_BASE = import.meta.env.VITE_PPT_API_URL || 'http://localhost:8002';

interface AIPPTDialogProps {
  onClose: () => void;
  onSave: (fileName: string, content: string) => void;
}

interface SlideData {
  index: number;
  image_url: string;
  prompt: string;
}

interface GenerateResult {
  success: boolean;
  slides: SlideData[];
  session_id?: string;
  error?: string;
}

export function AIPPTDialog({ onClose, onSave }: AIPPTDialogProps) {
  const [pptTitle, setPPTTitle] = useState('');
  const [prompt, setPrompt] = useState('');
  const [pageCount, setPageCount] = useState(5);
  const [styleTemplate, setStyleTemplate] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [generatedSlides, setGeneratedSlides] = useState<SlideData[]>([]);
  const [sessionId, setSessionId] = useState<string>('');
  const [currentSlideIndex, setCurrentSlideIndex] = useState(0);
  const [showPreview, setShowPreview] = useState(false);
  const [generationProgress, setGenerationProgress] = useState(0);

  // 生成 PPT
  const generatePPT = async () => {
    if (!pptTitle.trim()) {
      toast.error('请输入PPT标题');
      return;
    }
    if (!prompt.trim()) {
      toast.error('请输入生成提示词');
      return;
    }

    setIsGenerating(true);
    setGenerationProgress(0);
    setGeneratedSlides([]);

    try {
      const response = await fetch(`${PPT_API_BASE}/ppt/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          prompt: `${pptTitle}\n\n${prompt}`,
          page_count: pageCount,
          style_template: styleTemplate || undefined,
        }),
      });

      const result: GenerateResult = await response.json();

      if (result.success && result.slides && result.slides.length > 0) {
        setGeneratedSlides(result.slides);
        setSessionId(result.session_id || '');
        setCurrentSlideIndex(0);
        setShowPreview(true);
        toast.success(`成功生成 ${result.slides.length} 张幻灯片！`);
      } else {
        toast.error(result.error || 'PPT生成失败');
      }
    } catch (error: any) {
      console.error('Generate PPT error:', error);
      toast.error('PPT生成失败，请检查后端服务是否启动');
    } finally {
      setIsGenerating(false);
    }
  };

  // 获取完整图片URL
  const getImageUrl = (path: string) => {
    if (path.startsWith('http')) return path;
    return `${PPT_API_BASE}${path}`;
  };

  // 切换幻灯片
  const goToPrevSlide = () => {
    if (currentSlideIndex > 0) {
      setCurrentSlideIndex(currentSlideIndex - 1);
    }
  };

  const goToNextSlide = () => {
    if (currentSlideIndex < generatedSlides.length - 1) {
      setCurrentSlideIndex(currentSlideIndex + 1);
    }
  };

  // 下载当前幻灯片图片
  const handleDownloadSlide = async () => {
    if (!generatedSlides[currentSlideIndex]) return;

    const slide = generatedSlides[currentSlideIndex];
    const imageUrl = getImageUrl(slide.image_url);

    try {
      const response = await fetch(imageUrl);
      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `${pptTitle}_slide_${currentSlideIndex + 1}.png`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
      toast.success('幻灯片已下载');
    } catch (error) {
      toast.error('下载失败');
    }
  };

  // 保存所有幻灯片到课程资源（导出为 PPTX）
  const handleSave = async () => {
    if (generatedSlides.length === 0) {
      toast.error('没有可保存的内容');
      return;
    }

    setIsSaving(true);

    try {
      // 调用导出接口，将所有幻灯片合并为 PPTX
      const imageUrls = generatedSlides.map((slide: SlideData) => slide.image_url);
      const title = pptTitle.trim() || `AI_PPT_${Date.now()}`;

      const response = await fetch(`${PPT_API_BASE}/ppt/export`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          session_id: sessionId,
          image_urls: imageUrls,
          title: title,
        }),
      });

      const result = await response.json();

      if (result.success && result.pptx_base64) {
        const fileName = result.filename || `${title}.pptx`;
        onSave(fileName, result.pptx_base64);
        toast.success('PPT已保存到课程资源');
      } else {
        toast.error(result.error || '导出PPT失败');
      }
    } catch (error) {
      console.error('Export PPT error:', error);
      toast.error('保存失败');
    } finally {
      setIsSaving(false);
    }
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
                      disabled={isGenerating}
                    />
                  </div>

                  {/* 生成提示词 */}
                  <div>
                    <label className="block text-gray-700 text-sm mb-2">
                      <span className="text-red-500">*</span> 生成提示词
                    </label>
                    <textarea
                      value={prompt}
                      onChange={(e) => setPrompt(e.target.value)}
                      rows={6}
                      placeholder="请详细描述PPT的内容要求，例如：&#10;- 面向本科二年级学生&#10;- 重点讲解useState和useEffect的使用&#10;- 包含代码示例和案例分析&#10;- 风格简洁专业"
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 resize-none"
                      disabled={isGenerating}
                    />
                  </div>

                  {/* 页数设置 */}
                  <div>
                    <label className="block text-gray-700 text-sm mb-2">
                      幻灯片页数
                    </label>
                    <div className="flex items-center gap-4">
                      <input
                        type="range"
                        min="3"
                        max="10"
                        value={pageCount}
                        onChange={(e) => setPageCount(Number(e.target.value))}
                        className="flex-1"
                        disabled={isGenerating}
                      />
                      <span className="text-gray-700 w-12 text-center">{pageCount} 页</span>
                    </div>
                  </div>

                  {/* 风格模板（可选） */}
                  <div>
                    <label className="block text-gray-700 text-sm mb-2">
                      风格模板 <span className="text-gray-400">(可选)</span>
                    </label>
                    <textarea
                      value={styleTemplate}
                      onChange={(e) => setStyleTemplate(e.target.value)}
                      rows={3}
                      placeholder="自定义风格描述，留空使用默认现代科技风格"
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 resize-none"
                      disabled={isGenerating}
                    />
                  </div>

                  {/* 提示信息 */}
                  <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
                    <p className="text-blue-800 text-sm">
                      💡 <strong>提示：</strong>AI 将根据您的描述生成图片格式的幻灯片，生成过程可能需要几分钟时间。
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
                        <span>AI 正在生成幻灯片...</span>
                      </>
                    ) : (
                      <>
                        <Sparkles size={18} />
                        <span>生成 PPT</span>
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

              {/* 幻灯片预览 */}
              <div className="bg-gray-900 rounded-lg p-4 relative">
                {/* 当前幻灯片 */}
                <div className="aspect-video bg-black rounded-lg overflow-hidden flex items-center justify-center">
                  {generatedSlides[currentSlideIndex] ? (
                    <img
                      src={getImageUrl(generatedSlides[currentSlideIndex].image_url)}
                      alt={`Slide ${currentSlideIndex + 1}`}
                      className="max-w-full max-h-full object-contain"
                    />
                  ) : (
                    <div className="text-gray-500 flex items-center gap-2">
                      <Image size={24} />
                      <span>加载中...</span>
                    </div>
                  )}
                </div>

                {/* 导航按钮 */}
                <button
                  onClick={goToPrevSlide}
                  disabled={currentSlideIndex === 0}
                  className="absolute left-6 top-1/2 -translate-y-1/2 p-2 bg-white/20 hover:bg-white/30 rounded-full text-white disabled:opacity-30 disabled:cursor-not-allowed transition"
                >
                  <ChevronLeft size={24} />
                </button>
                <button
                  onClick={goToNextSlide}
                  disabled={currentSlideIndex === generatedSlides.length - 1}
                  className="absolute right-6 top-1/2 -translate-y-1/2 p-2 bg-white/20 hover:bg-white/30 rounded-full text-white disabled:opacity-30 disabled:cursor-not-allowed transition"
                >
                  <ChevronRight size={24} />
                </button>

                {/* 页码指示 */}
                <div className="mt-4 flex items-center justify-center gap-2">
                  {generatedSlides.map((_, index) => (
                    <button
                      key={index}
                      onClick={() => setCurrentSlideIndex(index)}
                      className={`w-3 h-3 rounded-full transition ${
                        index === currentSlideIndex
                          ? 'bg-orange-500'
                          : 'bg-gray-600 hover:bg-gray-500'
                      }`}
                    />
                  ))}
                </div>

                {/* 页码文字 */}
                <div className="text-center text-gray-400 text-sm mt-2">
                  {currentSlideIndex + 1} / {generatedSlides.length}
                </div>
              </div>

              {/* 操作区 */}
              <div className="flex items-center justify-between">
                <p className="text-gray-600 text-sm">
                  <strong>{pptTitle}</strong> · 共 {generatedSlides.length} 页
                </p>
                <button
                  onClick={handleDownloadSlide}
                  className="flex items-center gap-2 px-3 py-1.5 text-indigo-600 hover:bg-indigo-50 rounded-lg transition text-sm"
                >
                  <Download size={16} />
                  <span>下载当前页</span>
                </button>
              </div>

              {/* 使用说明 */}
              <div className="bg-yellow-50 rounded-lg p-4 border border-yellow-200">
                <p className="text-yellow-800 text-sm">
                  📌 <strong>说明：</strong>点击"保存到课程资源"将所有幻灯片合并为 PPTX 文件保存。您也可以逐张下载幻灯片图片。
                </p>
              </div>
            </div>
          )}
        </div>

        {/* 底部按钮 */}
        <div className="p-6 border-t border-gray-200 flex items-center gap-3">
          {showPreview && generatedSlides.length > 0 && (
            <button
              onClick={handleSave}
              disabled={isSaving}
              className="flex-1 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {isSaving ? (
                <>
                  <Loader size={16} className="animate-spin" />
                  <span>正在导出...</span>
                </>
              ) : (
                <span>保存到课程资源</span>
              )}
            </button>
          )}
          <button
            onClick={onClose}
            className="flex-1 px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition"
          >
            {showPreview ? '关闭' : '取消'}
          </button>
        </div>
      </div>
    </div>
  );
}
