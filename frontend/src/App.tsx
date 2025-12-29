import { useState, useEffect } from 'react';
import { LoginPage } from './components/login-page';
import { TeacherPage } from './components/teacher-page';
import { StudentPage } from './components/student-page';
import { Toaster } from 'sonner@2.0.3';

export default function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [userRole, setUserRole] = useState<'teacher' | 'student'>('student');
  const [username, setUsername] = useState('');
  const [userId, setUserId] = useState('');
  const [accessToken, setAccessToken] = useState('');

  // 检查本地存储的登录信息
  useEffect(() => {
    const savedToken = localStorage.getItem('access_token');
    const savedUsername = localStorage.getItem('username');
    const savedUserId = localStorage.getItem('user_id');
    const savedRole = localStorage.getItem('role') as 'teacher' | 'student';

    if (savedToken && savedUsername && savedUserId && savedRole) {
      setAccessToken(savedToken);
      setUsername(savedUsername);
      setUserId(savedUserId);
      setUserRole(savedRole);
      setIsLoggedIn(true);
    }
  }, []);

  // 登录成功处理
  const handleLoginSuccess = (role: string, username: string, token: string, userId: string) => {
    setUserRole(role as 'teacher' | 'student');
    setUsername(username);
    setUserId(userId);
    setAccessToken(token);
    setIsLoggedIn(true);

    // 保存到本地存储
    localStorage.setItem('access_token', token);
    localStorage.setItem('username', username);
    localStorage.setItem('user_id', userId);
    localStorage.setItem('role', role);
  };

  // 退出登录处理
  const handleLogout = () => {
    setIsLoggedIn(false);
    setUserRole('student');
    setUsername('');
    setUserId('');
    setAccessToken('');

    // 清除本地存储
    localStorage.removeItem('access_token');
    localStorage.removeItem('username');
    localStorage.removeItem('user_id');
    localStorage.removeItem('role');
  };

  // 根据登录状态和角色显示不同页面
  return (
    <>
      <Toaster position="top-center" richColors />
      
      {!isLoggedIn ? (
        <LoginPage onLoginSuccess={handleLoginSuccess} />
      ) : userRole === 'teacher' ? (
        <TeacherPage username={username} userId={userId} onLogout={handleLogout} />
      ) : (
        <StudentPage username={username} userId={userId} onLogout={handleLogout} />
      )}
    </>
  );
}