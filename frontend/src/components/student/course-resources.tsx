import { useState, useEffect } from 'react';
import { Folder, FileText, Download, ChevronDown, ChevronRight } from 'lucide-react';
import { toast } from 'sonner@2.0.3';
import api, { CourseFolder, CourseFile } from '../../utils/api-client';

interface FolderWithFiles extends CourseFolder {
  file_count: number;
}

interface CourseResourcesProps {
  courseId: string;
}

export function CourseResources({ courseId }: CourseResourcesProps) {
  const [folders, setFolders] = useState<FolderWithFiles[]>([]);
  const [loading, setLoading] = useState(true);
  const [expandedFolders, setExpandedFolders] = useState<Set<string>>(new Set());

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

        // 默认展开所有文件夹
        const allFolderIds = new Set(result.data.folders.map((f: any) => f.id));
        setExpandedFolders(allFolderIds);
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

  // 下载文件
  const handleDownloadFile = async (fileId: string) => {
    try {
      const result = await api.getFile(fileId);
      if (result.success && result.data) {
        const file = result.data;
        // 创建下载链接
        const link = document.createElement('a');
        link.href = file.content || '';
        link.download = file.name;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);

        toast.success('文件下载成功');
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

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-gray-400">加载中...</div>
      </div>
    );
  }

  if (folders.length === 0) {
    return (
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-12">
        <div className="text-center">
          <Folder size={64} className="text-gray-300 mx-auto mb-4" />
          <p className="text-gray-500 mb-2">暂无课程资源</p>
          <p className="text-gray-400 text-sm">
            教师暂未上传课程资料
          </p>
        </div>
      </div>
    );
  }

  return (
    <div>
      <div className="mb-6">
        <h3 className="text-gray-800">课程资源</h3>
        <p className="text-gray-500 text-sm mt-1">
          {folders.length} 个文件夹
        </p>
      </div>

      <div className="space-y-4">
        {folders.map((folder) => (
          <div
            key={folder.id}
            className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden"
          >
            {/* 文件夹头部 */}
            <button
              onClick={() => toggleFolder(folder.id)}
              className="w-full p-4 flex items-center gap-3 bg-gray-50 border-b border-gray-200 hover:bg-gray-100 transition"
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
                        <div className="flex items-center gap-3 flex-1 min-w-0">
                          <FileText size={20} className="text-blue-500" />
                          <div className="flex-1 min-w-0">
                            <p className="text-gray-800 truncate">{file.name}</p>
                            <p className="text-gray-500 text-xs">
                              {formatFileSize(file.size)} · {new Date(file.created_at).toLocaleDateString('zh-CN')}
                            </p>
                          </div>
                        </div>

                        <button
                          onClick={() => handleDownloadFile(file.id)}
                          className="flex items-center gap-2 px-3 py-2 text-indigo-600 hover:bg-indigo-50 rounded-lg transition flex-shrink-0"
                        >
                          <Download size={16} />
                          <span className="text-sm">下载</span>
                        </button>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
