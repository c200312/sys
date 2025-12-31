import { useState, useEffect, useRef } from 'react';
import { FolderPlus, Upload, Folder, FileText, Download, Trash2, ChevronDown, ChevronRight, Sparkles, Edit2, Eye, Presentation } from 'lucide-react';
import { toast } from 'sonner@2.0.3';
import api, { CourseFolder, CourseFile } from '../../utils/api-client';
import { AIWritingDialog } from './ai-writing-dialog';
import { AIPPTDialog } from './ai-ppt-dialog';
import { CoursewareEditDialog } from './courseware-edit-dialog';
import { FilePreviewDialog } from './file-preview-dialog';

interface FolderWithFiles extends CourseFolder {
  file_count: number;
}

interface CourseResourcesProps {
  courseId: string;
}

export function CourseResources({ courseId }: CourseResourcesProps) {
  const [folders, setFolders] = useState<FolderWithFiles[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateFolderDialog, setShowCreateFolderDialog] = useState(false);
  const [newFolderName, setNewFolderName] = useState('');
  const [expandedFolders, setExpandedFolders] = useState<Set<string>>(new Set());
  const [uploadingFolder, setUploadingFolder] = useState<string | null>(null);
  const [aiWritingFolder, setAIWritingFolder] = useState<string | null>(null);
  const [aiPPTFolder, setAIPPTFolder] = useState<string | null>(null);
  const [editingFile, setEditingFile] = useState<CourseFile | null>(null);
  const [previewFile, setPreviewFile] = useState<CourseFile | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    loadResources();
  }, [courseId]);

  const loadResources = async () => {
    setLoading(true);
    try {
      const result = await api.getCourseResources(courseId);
      console.log('✅ 获取课程资源成功:', result);
      if (result.success && result.data) {
        const foldersWithCount = result.data.folders.map(folder => ({
          ...folder,
          file_count: folder.files?.length || 0,
        }));
        setFolders(foldersWithCount as FolderWithFiles[]);
      } else {
        toast.error(result.error || '获取课程资源失败');
      }
    } catch (error: any) {
      console.error('❌ 获取课程资源失败:', error);
      toast.error('获取课程资源失败');
    } finally {
      setLoading(false);
    }
  };

  // 创建文件夹
  const handleCreateFolder = async () => {
    if (!newFolderName.trim()) {
      toast.error('请输入文件夹名称');
      return;
    }

    try {
      const result = await api.createFolder(courseId, newFolderName.trim());
      if (result.success) {
        toast.success('文件夹创建成功');
        setNewFolderName('');
        setShowCreateFolderDialog(false);
        loadResources();
      } else {
        toast.error(result.error || '创建失败');
      }
    } catch (error: any) {
      toast.error(error.message || '创建失败');
    }
  };

  // 删除文件夹
  const handleDeleteFolder = async (folderId: string, folderName: string) => {
    if (!confirm(`确定要删除文件夹"${folderName}"吗？\n文件夹内的所有文件也会被删除。`)) {
      return;
    }

    try {
      const result = await api.deleteFolder(folderId);
      if (result.success) {
        toast.success('文件夹已删除');
        loadResources();
      } else {
        toast.error(result.error || '删除失败');
      }
    } catch (error: any) {
      toast.error(error.message || '删除失败');
    }
  };

  // 切换文件夹展开/折叠
  const toggleFolder = (folderId: string) => {
    const newExpanded = new Set(expandedFolders);
    if (newExpanded.has(folderId)) {
      newExpanded.delete(folderId);
    } else {
      newExpanded.add(folderId);
    }
    setExpandedFolders(newExpanded);
  };

  // 触发文件上传
  const handleUploadClick = (folderId: string) => {
    setUploadingFolder(folderId);
    fileInputRef.current?.click();
  };

  // 处理文件选择
  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file || !uploadingFolder) return;

    // 将文件转换为base64
    const reader = new FileReader();
    reader.onload = async () => {
      try {
        const base64Content = reader.result as string;
        const result = await api.uploadFile(uploadingFolder, {
          name: file.name,
          size: file.size,
          type: file.type,
          content: base64Content,
        });
        if (result.success) {
          toast.success('文件上传成功');
          loadResources();

          // 自动展开该文件夹
          const newExpanded = new Set(expandedFolders);
          newExpanded.add(uploadingFolder);
          setExpandedFolders(newExpanded);
        } else {
          toast.error(result.error || '上传失败');
        }
      } catch (error: any) {
        toast.error(error.message || '上传失败');
      } finally {
        setUploadingFolder(null);
        // 重置input，允许重复上传同一文件
        if (fileInputRef.current) {
          fileInputRef.current.value = '';
        }
      }
    };

    reader.onerror = () => {
      toast.error('文件读取失败');
      setUploadingFolder(null);
    };

    reader.readAsDataURL(file);
  };

  // 删除文件
  const handleDeleteFile = async (fileId: string, fileName: string) => {
    if (!confirm(`确定要删除文件"${fileName}"吗？`)) {
      return;
    }

    try {
      const result = await api.deleteFile(fileId);
      if (result.success) {
        toast.success('文件已删除');
        loadResources();
      } else {
        toast.error(result.error || '删除失败');
      }
    } catch (error: any) {
      toast.error(error.message || '删除失败');
    }
  };

  // 下载文件
  const handleDownloadFile = async (fileId: string) => {
    try {
      const result = await api.getFile(fileId);
      if (result.success && result.data) {
        const file = result.data;
        // 使用预签名 URL 下载
        if (file.url) {
          const link = document.createElement('a');
          link.href = file.url;
          link.download = file.name;
          link.target = '_blank';
          document.body.appendChild(link);
          link.click();
          document.body.removeChild(link);
          toast.success('文件下载成功');
        } else {
          // 回退到后端下载接口
          window.open(api.getFileDownloadUrl(fileId), '_blank');
        }
      } else {
        toast.error(result.error || '下载失败');
      }
    } catch (error: any) {
      toast.error(error.message || '下载失败');
    }
  };

  // 格式化文件大小
  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(2) + ' MB';
  };

  // AI写作完成后保存课件
  const handleAISave = async (fileName: string, content: string) => {
    if (!aiWritingFolder) return;

    try {
      // 将内容转换为 base64
      const blob = new Blob([content], { type: 'text/plain' });
      const reader = new FileReader();

      reader.onload = async () => {
        const base64Content = reader.result as string;
        const result = await api.uploadFile(aiWritingFolder, {
          name: fileName,
          size: blob.size,
          type: 'text/plain',
          content: base64Content,
        });
        if (result.success) {
          toast.success('课件已保存');
          loadResources();

          // 自动展开该文件夹
          const newExpanded = new Set(expandedFolders);
          newExpanded.add(aiWritingFolder);
          setExpandedFolders(newExpanded);

          setAIWritingFolder(null);
        } else {
          toast.error(result.error || '保存失败');
        }
      };

      reader.onerror = () => {
        toast.error('保存失败');
      };

      reader.readAsDataURL(blob);
    } catch (error: any) {
      toast.error(error.message || '保存失败');
    }
  };

  // AI生成PPT完成后保存课件
  const handleAIPPTSave = async (fileName: string, content: string) => {
    if (!aiPPTFolder) return;

    try {
      // content 已经是 base64 格式的数据（可能是图片或 PPTX）
      // 计算 base64 数据的大致大小
      const base64Data = content.split(',')[1] || content;
      const size = Math.ceil(base64Data.length * 0.75);

      // 根据文件名判断类型
      const isPptx = fileName.toLowerCase().endsWith('.pptx');
      const mimeType = isPptx
        ? 'application/vnd.openxmlformats-officedocument.presentationml.presentation'
        : 'image/png';

      const result = await api.uploadFile(aiPPTFolder, {
        name: fileName,
        size: size,
        type: mimeType,
        content: content,
      });

      if (result.success) {
        toast.success('课件已保存');
        loadResources();

        // 自动展开该文件夹
        const newExpanded = new Set(expandedFolders);
        newExpanded.add(aiPPTFolder);
        setExpandedFolders(newExpanded);

        setAIPPTFolder(null);
      } else {
        toast.error(result.error || '保存失败');
      }
    } catch (error: any) {
      toast.error(error.message || '保存失败');
    }
  };

  // 编辑文件
  const handleEditFile = (file: CourseFile) => {
    setEditingFile(file);
  };

  // 保存编辑后的文件
  const handleSaveEdit = async (content: string) => {
    if (!editingFile) return;

    try {
      // 将内容转换为 base64
      const blob = new Blob([content], { type: 'text/plain' });
      const reader = new FileReader();

      reader.onload = async () => {
        const base64Content = reader.result as string;
        const result = await api.updateFile(editingFile.id, { content: base64Content });
        if (result.success) {
          toast.success('文件已保存');
          loadResources();

          // 自动展开该文件夹
          const newExpanded = new Set(expandedFolders);
          newExpanded.add(editingFile.folder_id);
          setExpandedFolders(newExpanded);

          setEditingFile(null);
        } else {
          toast.error(result.error || '保存失败');
        }
      };

      reader.onerror = () => {
        toast.error('保存失败');
      };

      reader.readAsDataURL(blob);
    } catch (error: any) {
      toast.error(error.message || '保存失败');
    }
  };

  // 预览文件
  const handlePreviewFile = (file: CourseFile) => {
    setPreviewFile(file);
  };

  // 判断文件是否可编辑
  const isEditableFile = (fileName: string): boolean => {
    const ext = fileName.toLowerCase().split('.').pop();
    return ext === 'txt' || ext === 'md';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-gray-400">加载中...</div>
      </div>
    );
  }

  return (
    <div>
      {/* 隐藏的文件输入 */}
      <input
        ref={fileInputRef}
        type="file"
        className="hidden"
        onChange={handleFileChange}
        accept=".pdf,.doc,.docx,.ppt,.pptx,.xls,.xlsx,.txt,.jpg,.jpeg,.png,.gif,.zip,.rar"
      />

      {/* 头部 */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-gray-800">课程资源</h3>
          <p className="text-gray-500 text-sm mt-1">
            {folders.length} 个文件夹
          </p>
        </div>
        <button
          onClick={() => setShowCreateFolderDialog(true)}
          className="flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition"
        >
          <FolderPlus size={20} />
          <span>新建文件夹</span>
        </button>
      </div>

      {/* 文件夹列表 */}
      {folders.length === 0 ? (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-12">
          <div className="text-center">
            <Folder size={64} className="text-gray-300 mx-auto mb-4" />
            <p className="text-gray-500 mb-2">还没有创建文件夹</p>
            <p className="text-gray-400 text-sm">
              点击右上角按钮创建文件夹，然后上传课程资料
            </p>
          </div>
        </div>
      ) : (
        <div className="space-y-4">
          {folders.map((folder) => (
            <div
              key={folder.id}
              className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden"
            >
              {/* 文件夹头部 */}
              <div className="p-4 flex items-center justify-between bg-gray-50 border-b border-gray-200">
                <button
                  onClick={() => toggleFolder(folder.id)}
                  className="flex items-center gap-3 flex-1 text-left hover:text-indigo-600 transition"
                >
                  {expandedFolders.has(folder.id) ? (
                    <ChevronDown size={20} className="text-gray-400" />
                  ) : (
                    <ChevronRight size={20} className="text-gray-400" />
                  )}
                  <Folder size={20} className="text-yellow-500" />
                  <span className="text-gray-800">{folder.name}</span>
                  <span className="text-gray-400 text-sm">
                    ({folder.file_count} 个文件)
                  </span>
                </button>

                <div className="flex items-center gap-2">
                  <button
                    onClick={() => setAIWritingFolder(folder.id)}
                    className="flex items-center gap-2 px-3 py-1.5 bg-gradient-to-r from-purple-600 to-blue-600 text-white hover:from-purple-700 hover:to-blue-700 rounded-lg transition"
                  >
                    <Sparkles size={16} />
                    <span className="text-sm">AI写作</span>
                  </button>
                  <button
                    onClick={() => setAIPPTFolder(folder.id)}
                    className="flex items-center gap-2 px-3 py-1.5 bg-gradient-to-r from-orange-600 to-pink-600 text-white hover:from-orange-700 hover:to-pink-700 rounded-lg transition"
                  >
                    <Presentation size={16} />
                    <span className="text-sm">AI PPT</span>
                  </button>
                  <button
                    onClick={() => handleUploadClick(folder.id)}
                    className="flex items-center gap-2 px-3 py-1.5 text-indigo-600 hover:bg-indigo-50 rounded-lg transition"
                  >
                    <Upload size={16} />
                    <span className="text-sm">上传文件</span>
                  </button>
                  <button
                    onClick={() => handleDeleteFolder(folder.id, folder.name)}
                    className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition"
                  >
                    <Trash2 size={16} />
                  </button>
                </div>
              </div>

              {/* 文件列表 */}
              {expandedFolders.has(folder.id) && (
                <div className="p-4">
                  {folder.files.length === 0 ? (
                    <div className="text-center py-8">
                      <FileText size={48} className="text-gray-300 mx-auto mb-2" />
                      <p className="text-gray-400 text-sm">暂无文件</p>
                    </div>
                  ) : (
                    <div className="space-y-2">
                      {folder.files.map((file) => (
                        <div
                          key={file.id}
                          className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition"
                        >
                          <div className="flex items-center gap-3 flex-1">
                            <FileText size={20} className="text-blue-500" />
                            <div className="flex-1 min-w-0">
                              <p className="text-gray-800 truncate">{file.name}</p>
                              <p className="text-gray-500 text-xs">
                                {formatFileSize(file.size)} · {new Date(file.created_at).toLocaleDateString('zh-CN')}
                              </p>
                            </div>
                          </div>

                          <div className="flex items-center gap-2">
                            <button
                              onClick={() => handleDownloadFile(file.id)}
                              className="p-2 text-indigo-600 hover:bg-indigo-50 rounded-lg transition"
                              title="下载"
                            >
                              <Download size={16} />
                            </button>
                            <button
                              onClick={() => handleDeleteFile(file.id, file.name)}
                              className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition"
                              title="删除"
                            >
                              <Trash2 size={16} />
                            </button>
                            {isEditableFile(file.name) && (
                              <button
                                onClick={() => handleEditFile(file)}
                                className="p-2 text-gray-600 hover:bg-gray-50 rounded-lg transition"
                                title="编辑"
                              >
                                <Edit2 size={16} />
                              </button>
                            )}
                            <button
                              onClick={() => handlePreviewFile(file)}
                              className="p-2 text-gray-600 hover:bg-gray-50 rounded-lg transition"
                              title="预览"
                            >
                              <Eye size={16} />
                            </button>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* 创建文件夹对话框 */}
      {showCreateFolderDialog && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg w-full max-w-md p-6">
            <h3 className="text-gray-800 mb-4">新建文件夹</h3>
            
            <input
              type="text"
              value={newFolderName}
              onChange={(e) => setNewFolderName(e.target.value)}
              placeholder="例如：第一节课、第二节课"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 mb-4"
              autoFocus
              onKeyDown={(e) => {
                if (e.key === 'Enter') handleCreateFolder();
                if (e.key === 'Escape') setShowCreateFolderDialog(false);
              }}
            />

            <div className="flex items-center gap-3">
              <button
                onClick={handleCreateFolder}
                className="flex-1 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition"
              >
                创建
              </button>
              <button
                onClick={() => {
                  setShowCreateFolderDialog(false);
                  setNewFolderName('');
                }}
                className="flex-1 px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition"
              >
                取消
              </button>
            </div>
          </div>
        </div>
      )}

      {/* AI写作对话框 */}
      {aiWritingFolder && (
        <AIWritingDialog
          onClose={() => setAIWritingFolder(null)}
          onSave={handleAISave}
        />
      )}

      {/* AI生成PPT对话框 */}
      {aiPPTFolder && (
        <AIPPTDialog
          onClose={() => setAIPPTFolder(null)}
          onSave={handleAIPPTSave}
        />
      )}

      {/* 文件编辑对话框 */}
      {editingFile && (
        <CoursewareEditDialog
          onClose={() => setEditingFile(null)}
          onSave={handleSaveEdit}
          fileName={editingFile.name}
          content={editingFile.content}
        />
      )}

      {/* 文件预览对话框 */}
      {previewFile && (
        <FilePreviewDialog
          onClose={() => setPreviewFile(null)}
          file={previewFile}
        />
      )}
    </div>
  );
}