import { X } from 'lucide-react';
import { type CourseFile } from '../../utils/api-client';
import { useState, useEffect } from 'react';

interface FilePreviewDialogProps {
  onClose: () => void;
  file: CourseFile;
}

export function FilePreviewDialog({ onClose, file }: FilePreviewDialogProps) {
  const { name: fileName, type: fileType, content } = file;
  const [textContent, setTextContent] = useState('');
  
  // 判断文件类型
  const isImage = fileType.startsWith('image/') || /\.(jpg|jpeg|png|gif|bmp|svg|webp)$/i.test(fileName);
  const isPDF = fileType === 'application/pdf' || fileName.toLowerCase().endsWith('.pdf');
  const isText = fileType.startsWith('text/') || /\.(txt|md)$/i.test(fileName);

  // 解码文本内容
  useEffect(() => {
    if (isText) {
      try {
        if (content.startsWith('data:')) {
          const base64Content = content.split('base64,')[1];
          if (base64Content) {
            const decodedContent = decodeURIComponent(escape(atob(base64Content)));
            setTextContent(decodedContent);
          } else {
            setTextContent('');
          }
        } else {
          setTextContent(content);
        }
      } catch (error) {
        console.error('解码失败:', error);
        setTextContent('文件内容解码失败');
      }
    }
  }, [content, isText]);

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4 overflow-y-auto">
      <div className="bg-white rounded-lg w-full max-w-5xl my-8 max-h-[90vh] flex flex-col">
        {/* 头部 */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200 flex-shrink-0">
          <div>
            <h2 className="text-gray-800">文件预览</h2>
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
        <div className="p-6 overflow-auto flex-1">
          {isImage ? (
            <div className="flex items-center justify-center">
              <img
                src={content}
                alt={fileName}
                className="max-w-full max-h-[70vh] object-contain rounded-lg shadow-lg"
              />
            </div>
          ) : isPDF ? (
            <div className="w-full h-[70vh]">
              <iframe
                src={content}
                className="w-full h-full rounded-lg border border-gray-300"
                title={fileName}
              />
            </div>
          ) : isText ? (
            <div className="bg-gray-50 rounded-lg p-6 border border-gray-200">
              <pre className="text-gray-700 whitespace-pre-wrap text-left font-mono text-sm max-h-[70vh] overflow-auto">{textContent}</pre>
            </div>
          ) : (
            <div className="bg-gray-50 rounded-lg p-6 text-center">
              <p className="text-gray-500">暂不支持预览此类型文件</p>
              <p className="text-gray-400 text-sm mt-2">请下载后查看</p>
            </div>
          )}
        </div>

        {/* 底部按钮 */}
        <div className="p-6 border-t border-gray-200 flex-shrink-0">
          <button
            onClick={onClose}
            className="w-full px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition"
          >
            关闭
          </button>
        </div>
      </div>
    </div>
  );
}