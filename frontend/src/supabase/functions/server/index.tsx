import { Hono } from 'npm:hono';
import { cors } from 'npm:hono/cors';
import { logger } from 'npm:hono/logger';
import { createClient } from 'npm:@supabase/supabase-js@2';

const app = new Hono();

app.use('*', cors());
app.use('*', logger(console.log));

const supabaseAdmin = createClient(
  Deno.env.get('SUPABASE_URL') ?? '',
  Deno.env.get('SUPABASE_SERVICE_ROLE_KEY') ?? '',
);

// 注册接口
app.post('/make-server-0dd9fd5d/signup', async (c) => {
  try {
    const { username, password, role } = await c.req.json();

    if (!username || !password || !role) {
      return c.json({ error: '用户名、密码和角色不能为空' }, 400);
    }

    if (role !== 'teacher' && role !== 'student') {
      return c.json({ error: '角色必须是教师或学生' }, 400);
    }

    // 使用用户名作为邮箱（加上域名后缀）
    const email = `${username}@demo.local`;

    const { data, error } = await supabaseAdmin.auth.admin.createUser({
      email: email,
      password: password,
      user_metadata: { username: username, role: role },
      // 自动确认用户邮箱，因为未配置邮件服务器
      email_confirm: true
    });

    if (error) {
      console.log('注册错误:', error);
      return c.json({ error: error.message || '注册失败' }, 400);
    }

    return c.json({ 
      success: true, 
      message: '注册成功',
      user: {
        id: data.user?.id,
        username: username,
        role: role
      }
    });
  } catch (error) {
    console.log('注册异常:', error);
    return c.json({ error: '服务器错误' }, 500);
  }
});

// 登录接口
app.post('/make-server-0dd9fd5d/login', async (c) => {
  try {
    const { username, password } = await c.req.json();

    if (!username || !password) {
      return c.json({ error: '用户名和密码不能为空' }, 400);
    }

    const supabase = createClient(
      Deno.env.get('SUPABASE_URL') ?? '',
      Deno.env.get('SUPABASE_ANON_KEY') ?? '',
    );

    // 使用用户名作为邮箱（加上域名后缀）
    const email = `${username}@demo.local`;

    const { data, error } = await supabase.auth.signInWithPassword({
      email: email,
      password: password,
    });

    if (error) {
      console.log('登录错误:', error);
      return c.json({ error: '用户名或密码错误' }, 401);
    }

    return c.json({ 
      success: true, 
      message: '登录成功',
      access_token: data.session?.access_token,
      user: {
        id: data.user?.id,
        username: data.user?.user_metadata?.username || username,
        role: data.user?.user_metadata?.role || 'student'
      }
    });
  } catch (error) {
    console.log('登录异常:', error);
    return c.json({ error: '服务器错误' }, 500);
  }
});

// 验证会话接口
app.get('/make-server-0dd9fd5d/verify', async (c) => {
  try {
    const accessToken = c.req.header('Authorization')?.split(' ')[1];
    
    if (!accessToken) {
      return c.json({ error: '未提供访问令牌' }, 401);
    }

    const { data: { user }, error } = await supabaseAdmin.auth.getUser(accessToken);

    if (error || !user) {
      return c.json({ error: '无效的访问令牌' }, 401);
    }

    return c.json({ 
      success: true,
      user: {
        id: user.id,
        username: user.user_metadata?.username,
        role: user.user_metadata?.role || 'student'
      }
    });
  } catch (error) {
    console.log('验证异常:', error);
    return c.json({ error: '服务器错误' }, 500);
  }
});

Deno.serve(app.fetch);
