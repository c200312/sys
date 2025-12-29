import { useState, useEffect } from 'react';
import { RefreshCw, User, GraduationCap, Database } from 'lucide-react';
import { toast } from 'sonner@2.0.3';
import api from '../utils/api-client';

interface LoginPageProps {
  onLoginSuccess: (role: string, username: string, accessToken: string, userId: string) => void;
}

export function LoginPage({ onLoginSuccess }: LoginPageProps) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [captchaInput, setCaptchaInput] = useState('');
  const [captchaCode, setCaptchaCode] = useState('');
  const [loading, setLoading] = useState(false);
  const [showRegister, setShowRegister] = useState(false);
  const [role, setRole] = useState<'teacher' | 'student'>('student');
  const [showResetConfirm, setShowResetConfirm] = useState(false);

  // 生成随机验证码
  const generateCaptcha = () => {
    const chars = 'ABCDEFGHJKMNPQRSTWXYZabcdefhijkmnprstwxyz2345678';
    let code = '';
    for (let i = 0; i < 4; i++) {
      code += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    return code;
  };

  // 重置所有数据 - 后端会自动初始化数据，这里只需要提示用户
  const handleResetData = () => {
    toast.info('请联系管理员重置数据，或重启后端服务');
    setShowResetConfirm(false);
  };

  // 初始化验证码
  useEffect(() => {
    setCaptchaCode(generateCaptcha());
  }, []);

  // 刷新验证码
  const handleRefreshCaptcha = () => {
    setCaptchaCode(generateCaptcha());
    setCaptchaInput('');
  };

  // 处理登录
  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!username || !password || !captchaInput) {
      toast.error('请填写所有字段');
      return;
    }

    if (captchaInput.toLowerCase() !== captchaCode.toLowerCase()) {
      toast.error('验证码错误，请重新输入');
      handleRefreshCaptcha();
      return;
    }

    setLoading(true);

    try {
      const result = await api.login(username, password);
      if (result.success && result.data) {
        toast.success('登录成功！正在跳转...');
        setTimeout(() => {
          onLoginSuccess(
            result.data!.user.role,
            result.data!.user.username,
            result.data!.access_token,
            result.data!.user.id
          );
        }, 500);
      } else {
        toast.error(result.error || '登录失败');
        handleRefreshCaptcha();
      }
    } catch (error) {
      console.error('登录失败:', error);
      toast.error(error instanceof Error ? error.message : '登录失败');
      handleRefreshCaptcha();
    } finally {
      setLoading(false);
    }
  };

  // 处理注册
  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!username || !password || !captchaInput) {
      toast.error('请填写所有字段');
      return;
    }

    if (username.length < 3) {
      toast.error('用户名长度不能少于3位');
      return;
    }

    if (password.length < 6) {
      toast.error('密码长度不能少于6位');
      return;
    }

    if (captchaInput.toLowerCase() !== captchaCode.toLowerCase()) {
      toast.error('验证码错误，请重新输入');
      handleRefreshCaptcha();
      return;
    }

    setLoading(true);

    try {
      const result = await api.signup(username, password, role);
      if (result.success) {
        toast.success(`注册成功！欢迎${role === 'teacher' ? '老师' : '同学'}，请登录`);
        setTimeout(() => {
          setShowRegister(false);
          setPassword('');
          setCaptchaInput('');
          handleRefreshCaptcha();
        }, 1000);
      } else {
        toast.error(result.error || '注册失败');
      }
    } catch (error) {
      console.error('注册失败:', error);
      toast.error(error instanceof Error ? error.message : '注册失败');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      {/* 开发者工具 - 重置数据按钮 */}
      <button
        onClick={() => {
          setShowResetConfirm(true);
        }}
        className="fixed bottom-4 right-4 flex items-center gap-2 px-3 py-2 bg-gray-800 text-white rounded-lg hover:bg-gray-700 transition text-sm shadow-lg"
        title="重置所有数据并重新生成100个学生和5个老师"
      >
        <Database size={16} />
        <span>重置数据</span>
      </button>

      {/* 重置数据确认对话框 */}
      {showResetConfirm && (
        <div className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50 z-50">
          <div className="bg-white p-8 rounded-lg shadow-xl max-w-md">
            <h2 className="text-gray-800 mb-4">确认重置数据</h2>
            <div className="text-gray-600 mb-6 space-y-2">
              <p>⚠️ <strong>确定要重置所有数据吗？</strong></p>
              <p className="text-sm">这将清空所有课程、学员、作业等数据，并重新生成：</p>
              <ul className="text-sm list-disc list-inside ml-4 space-y-1">
                <li><strong>5 个教师账号</strong>（teacher1 - teacher5）</li>
                <li><strong>100 个学生账号</strong>（student1 - student100）</li>
                <li>学生分为 3 个班级：
                  <ul className="ml-6 mt-1 space-y-0.5">
                    <li>student1-40: 一班</li>
                    <li>student41-80: 二班</li>
                    <li>student81-100: 三班</li>
                  </ul>
                </li>
              </ul>
              <p className="text-sm mt-2">所有账号密码均为：<strong>123456</strong></p>
            </div>
            <div className="flex gap-3 justify-end">
              <button
                onClick={() => setShowResetConfirm(false)}
                className="px-6 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition"
              >
                取消
              </button>
              <button
                onClick={handleResetData}
                className="px-6 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition"
              >
                确认重置
              </button>
            </div>
          </div>
        </div>
      )}

      <div className="w-full max-w-md bg-white rounded-2xl shadow-xl p-8">
        <div className="text-center mb-8">
          <h1 className="text-gray-800 mb-2">
            {showRegister ? '用户注册' : '欢迎登录'}
          </h1>
          <p className="text-gray-500">
            {showRegister ? '创建您的新账号' : '请输入您的账号信息'}
          </p>
          {!showRegister && (
            <div className="mt-3 p-3 bg-blue-50 rounded-lg text-sm text-gray-600">
              <p className="mb-1">📝 测试账号（密码：123456）</p>
              <p className="text-xs">
                教师：teacher1-5 | 学生：student1-100
              </p>
            </div>
          )}
        </div>

        <form onSubmit={showRegister ? handleRegister : handleLogin} className="space-y-6">
          {/* 用户名 */}
          <div>
            <label htmlFor="username" className="block text-gray-700 mb-2">
              用户名
            </label>
            <input
              id="username"
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="请输入用户名"
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
              disabled={loading}
            />
          </div>

          {/* 密码 */}
          <div>
            <label htmlFor="password" className="block text-gray-700 mb-2">
              密码
            </label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder={showRegister ? '请设置密码（至少6位）' : '请输入密码'}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
              disabled={loading}
            />
          </div>

          {/* 角色选择 - 仅在注册时显示 */}
          {showRegister && (
            <div>
              <label className="block text-gray-700 mb-2">
                选择角色
              </label>
              <div className="grid grid-cols-2 gap-3">
                <button
                  type="button"
                  onClick={() => setRole('student')}
                  className={`flex flex-col items-center justify-center p-4 border-2 rounded-lg transition ${
                    role === 'student'
                      ? 'border-blue-500 bg-blue-50 text-blue-700'
                      : 'border-gray-300 hover:border-gray-400'
                  }`}
                  disabled={loading}
                >
                  <GraduationCap size={32} className="mb-2" />
                  <span>学生</span>
                </button>
                <button
                  type="button"
                  onClick={() => setRole('teacher')}
                  className={`flex flex-col items-center justify-center p-4 border-2 rounded-lg transition ${
                    role === 'teacher'
                      ? 'border-blue-500 bg-blue-50 text-blue-700'
                      : 'border-gray-300 hover:border-gray-400'
                  }`}
                  disabled={loading}
                >
                  <User size={32} className="mb-2" />
                  <span>教师</span>
                </button>
              </div>
            </div>
          )}

          {/* 验证码 */}
          <div>
            <label htmlFor="captcha" className="block text-gray-700 mb-2">
              验证码
            </label>
            <div className="flex gap-3">
              <input
                id="captcha"
                type="text"
                value={captchaInput}
                onChange={(e) => setCaptchaInput(e.target.value)}
                placeholder="请输入验证码"
                className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
                disabled={loading}
              />
              <div className="flex items-center gap-2">
                <div className="bg-gradient-to-r from-blue-500 to-indigo-600 px-4 py-3 rounded-lg select-none flex items-center justify-center min-w-[100px]">
                  <span className="text-white tracking-wider" style={{ fontFamily: 'monospace' }}>
                    {captchaCode}
                  </span>
                </div>
                <button
                  type="button"
                  onClick={handleRefreshCaptcha}
                  className="p-3 text-gray-600 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition"
                  title="刷新验证码"
                  disabled={loading}
                >
                  <RefreshCw size={20} />
                </button>
              </div>
            </div>
          </div>

          {/* 提交按钮 */}
          <button
            type="submit"
            className="w-full bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed"
            disabled={loading}
          >
            {loading ? '处理中...' : (showRegister ? '注册' : '登录')}
          </button>

          {/* 切换登录/注册 */}
          <div className="text-center">
            <button
              type="button"
              onClick={() => {
                setShowRegister(!showRegister);
                setPassword('');
                setCaptchaInput('');
                handleRefreshCaptcha();
              }}
              className="text-blue-600 hover:text-blue-700 transition-colors"
              disabled={loading}
            >
              {showRegister ? '已有账号？去登录' : '没有账号？去注册'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}