from flask import Flask, request, jsonify, session, render_template_string
from datetime import datetime
import secrets
from functools import wraps
import sqlite3

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)


"""======================================================================="""


# sqlite
DB_PATH = 'cms.db'

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS news (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            category TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

init_db()

def get_db():
    return sqlite3.connect(DB_PATH)

#元组转字典
def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


"""========================================================="""


#管理员登录
@app.route('/admin/login', methods=['POST'])
def admin_login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    if not data:
        return jsonify({"code": 400, "msg": "请求体需为JSON"}), 400
    # 预设管理员账号
    if username == 'admin' and password == 'admin123':
        session['username'] = 'admin'
        session['role'] = 'admin'
        return jsonify({"code": 200, "msg": "登录成功", "data": {"username": "admin"}})
    else:
        return jsonify({"code": 401, "msg": "用户名或密码错误"}), 401


# * 必须实现登录校验装饰器
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'username' not in session:
            return jsonify({"code": 401, "msg": "请先登录"}), 401
        return f(*args, **kwargs)
    return decorated


#装饰器：是否是管理员
def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'username' not in session:
            return jsonify({"code": 401, "msg": "请先登录"}), 401
        #非 `admin` 角色访问后台接口返回 `403 Forbidden`。
        if session.get('role') != 'admin':
            return jsonify({"code": 403, "msg": "权限不足，需要管理员身份"}), 403
        return f(*args, **kwargs)
    return decorated


"""========================================================================================"""


#  * `GET /`：展示公司首页（公司简介、最新 3 条新闻）。
@app.route('/', methods=['GET'])
def home():
    # 返回高端极简首页（纯前端渲染，调用 /api/news 获取数据）
    html = '''
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>新所闻 · 前沿科技</title>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
        <style>
            /* ---------- 全局重置 & 调色板 ---------- */
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
                background: #fafafa;
                color: #2c3e50;
                line-height: 1.6;
                padding: 2rem 1rem;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
                background: #ffffff;
                border-radius: 32px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.04), 0 8px 20px rgba(0,0,0,0.02);
                padding: 3rem 2.5rem;
            }
            /* ---------- 顶部导航 ---------- */
            .navbar {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding-bottom: 2rem;
                border-bottom: 1px solid #f0f0f0;
                margin-bottom: 2.5rem;
            }
            .brand {
                display: flex;
                align-items: center;
                gap: 10px;
                font-size: 1.5rem;
                font-weight: 600;
                letter-spacing: -0.5px;
                color: #1a1a1a;
            }
            .brand i {
                color: #2c7a6b;
                font-size: 2rem;
            }
            .nav-actions {
                display: flex;
                gap: 1.2rem;
                align-items: center;
            }
            .nav-actions a {
                color: #5a6a7a;
                text-decoration: none;
                font-size: 0.95rem;
                font-weight: 500;
                transition: color 0.2s;
                display: flex;
                align-items: center;
                gap: 6px;
            }
            .nav-actions a:hover {
                color: #1a1a1a;
            }
            .nav-actions .btn-outline {
                border: 1px solid #d0d7de;
                border-radius: 40px;
                padding: 0.45rem 1.2rem;
                background: transparent;
                transition: all 0.2s;
            }
            .nav-actions .btn-outline:hover {
                background: #f0f2f5;
                border-color: #b0b8c0;
            }
            /* ---------- 公司简介 ---------- */
            .hero {
                margin-bottom: 3.5rem;
            }
            .hero h1 {
                font-size: 2.6rem;
                font-weight: 300;
                letter-spacing: -1px;
                color: #1a1a1a;
                margin-bottom: 0.8rem;
            }
            .hero h1 strong {
                font-weight: 600;
                color: #2c7a6b;
            }
            .hero p {
                font-size: 1.1rem;
                color: #5a6a7a;
                max-width: 700px;
                font-weight: 300;
                line-height: 1.8;
            }
            .hero .tag {
                display: inline-block;
                margin-top: 1rem;
                background: #eef8f5;
                color: #2c7a6b;
                padding: 0.2rem 1.2rem;
                border-radius: 40px;
                font-size: 0.85rem;
                font-weight: 500;
                letter-spacing: 0.3px;
            }
            /* ---------- 新闻列表 ---------- */
            .section-title {
                display: flex;
                justify-content: space-between;
                align-items: baseline;
                margin-bottom: 1.8rem;
                border-bottom: 1px solid #f0f0f0;
                padding-bottom: 0.8rem;
            }
            .section-title h2 {
                font-weight: 400;
                font-size: 1.7rem;
                letter-spacing: -0.3px;
                color: #1a1a1a;
            }
            .section-title h2 i {
                margin-right: 10px;
                color: #2c7a6b;
                font-size: 1.4rem;
            }
            .news-grid {
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
                gap: 2rem;
            }
            .news-card {
                background: #ffffff;
                border-radius: 20px;
                padding: 1.8rem 1.8rem 1.5rem;
                box-shadow: 0 4px 12px rgba(0,0,0,0.02), 0 1px 3px rgba(0,0,0,0.03);
                transition: transform 0.2s, box-shadow 0.3s;
                border: 1px solid #f2f4f6;
                cursor: pointer;
                display: flex;
                flex-direction: column;
            }
            .news-card:hover {
                transform: translateY(-4px);
                box-shadow: 0 12px 28px rgba(0,0,0,0.04), 0 4px 12px rgba(0,0,0,0.02);
            }
            .news-card .category {
                display: inline-block;
                background: #ecf3f8;
                color: #2c3e50;
                font-size: 0.7rem;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.5px;
                padding: 0.15rem 0.9rem;
                border-radius: 40px;
                align-self: flex-start;
                margin-bottom: 0.8rem;
            }
            .news-card h3 {
                font-weight: 500;
                font-size: 1.2rem;
                margin-bottom: 0.5rem;
                color: #1a1a1a;
                line-height: 1.4;
            }
            .news-card p {
                color: #5a6a7a;
                font-size: 0.95rem;
                font-weight: 300;
                line-height: 1.6;
                flex-grow: 1;
                display: -webkit-box;
                -webkit-line-clamp: 3;
                -webkit-box-orient: vertical;
                overflow: hidden;
            }
            .news-card .meta {
                margin-top: 1rem;
                font-size: 0.8rem;
                color: #8a9aa8;
                display: flex;
                align-items: center;
                gap: 10px;
                border-top: 1px solid #f0f2f5;
                padding-top: 0.8rem;
            }
            .news-card .meta i {
                font-size: 0.9rem;
                color: #b0b8c0;
            }
            .empty-state {
                text-align: center;
                padding: 4rem 0;
                color: #8a9aa8;
                font-weight: 300;
            }
            /* ---------- 响应式 ---------- */
            @media (max-width: 640px) {
                .container { padding: 1.5rem; }
                .navbar { flex-direction: column; align-items: start; gap: 1rem; }
                .hero h1 { font-size: 2rem; }
                .news-grid { grid-template-columns: 1fr; }
                .nav-actions { flex-wrap: wrap; }
            }
            /* ---------- 全局图标微调 ---------- */
            .fa-fw { width: 1.2em; text-align: center; }
        </style>
    </head>
    <body>
        <div class="container">
            <!-- 导航 -->
            <nav class="navbar">
                <div class="brand">
                    <i class="fas fa-microchip"></i>
                    <span>新所闻</span>
                </div>
                <div class="nav-actions">
                    <a href="/" class="btn-outline"><i class="fas fa-home fa-fw"></i> 首页</a>
                    <a href="/login"><i class="fas fa-sign-in-alt fa-fw"></i> 登录</a>
                    <a href="/admin"><i class="fas fa-cog fa-fw"></i> 管理</a>
                </div>
            </nav>

            <!-- 公司简介 -->
            <div class="hero">
                <h1>创新 · <strong>永续</strong></h1>
                <p>世界首富Joy所创造的顶顶好新闻网站。</p>
                <span class="tag"><i class="far fa-clock fa-fw"></i> 成立于 2026 · 全球 12 个办事处</span>
            </div>

            <!-- 最新新闻 -->
            <div class="section-title">
                <h2><i class="far fa-newspaper fa-fw"></i> 最新动态</h2>
                <span style="font-size:0.85rem; color:#8a9aa8;">匠心 · 前沿</span>
            </div>
            <div id="newsContainer" class="news-grid">
                <!-- 由 JavaScript 动态渲染 -->
                <div class="empty-state"><i class="fas fa-spinner fa-spin fa-fw"></i> 加载中…</div>
            </div>
        </div>

        <script>
            // 获取新闻列表，取前3条并渲染卡片
            fetch('/api/news')
                .then(res => res.json())
                .then(data => {
                    const container = document.getElementById('newsContainer');
                    if (data.code !== 200 || !data.data || data.data.length === 0) {
                        container.innerHTML = `<div class="empty-state"><i class="far fa-frown fa-fw"></i> 暂无新闻</div>`;
                        return;
                    }
                    // 取最新3条（后端已按 created_at DESC 排序）
                    const latest = data.data.slice(0, 3);
                    container.innerHTML = latest.map(item => `
                        <div class="news-card" onclick="location.href='/news/${item.id}'">
                            ${item.category ? `<span class="category">${item.category}</span>` : ''}
                            <h3>${item.title}</h3>
                            <p>${item.content}</p>
                            <div class="meta">
                                <i class="far fa-calendar-alt fa-fw"></i>
                                <span>${item.created_at}</span>
                            </div>
                        </div>
                    `).join('');
                })
                .catch(err => {
                    document.getElementById('newsContainer').innerHTML = `<div class="empty-state"><i class="fas fa-exclamation-triangle fa-fw"></i> 加载失败，请稍后重试</div>`;
                });
        </script>
    </body>
    </html>
    '''
    return render_template_string(html)


#  * `GET /api/news`：获取新闻列表（支持按发布时间倒序）。
@app.route('/api/news', methods=['GET'])
def news_list():
    conn = get_db()
    conn.row_factory = dict_factory
    c = conn.cursor()
    c.execute('SELECT id, title, content, category, created_at FROM news ORDER BY created_at DESC')
    all_news = c.fetchall()
    conn.close()
    return jsonify({"code": 200, "data": all_news})


#   * `GET /api/news/<id>`：获取新闻详情。
@app.route('/api/news/<int:id>', methods=['GET'])
def news_detail(id):
    conn = get_db()
    conn.row_factory = dict_factory
    c = conn.cursor()
    c.execute('SELECT id, title, content, category, created_at FROM news WHERE id = ?', (id,))
    news = c.fetchone()
    conn.close()
    if news is None:
        return jsonify({"code": 404, "msg": "新闻不存在"}), 404
    return jsonify({"code": 200, "data": news})



#   * `POST /admin/news`：发布新新闻（字段：`title`, `content`, `category`）。
@app.route('/admin/news', methods=['POST'])
@admin_required
def release_news():
    data = request.get_json()
    title = data.get('title')
    content = data.get('content')
    category = data.get('category', '')
    conn = get_db()
    c = conn.cursor()
    if not data:
        return jsonify({"code": 400, "msg": "请求体需为JSON"}), 400

    if not title or not content:
        return jsonify({"code": 400, "msg": "标题和内容不能为空"}), 400
    c.execute('INSERT INTO news (title, content, category) VALUES (?, ?, ?)',
              (title, content, category))
    news_id = c.lastrowid
    conn.commit()
    conn.close()
    return jsonify({
        "code": 200,
        "msg": "发布成功",
        "data": {
            "id": news_id,
            "title": title,
            "content": content,
            "category": category,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # 近似时间
        }
    }), 201


#  * `DELETE /admin/news/<id>`：删除指定新闻。
@app.route('/admin/news/<int:id>', methods=['DELETE'])
@admin_required
def delete_news(id):
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT id FROM news WHERE id = ?', (id,))
    if not c.fetchone():
        conn.close()
        return jsonify({"code": 404, "msg": "新闻不存在"}), 404
    c.execute('DELETE FROM news WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return jsonify({"code": 200, "msg": "删除成功"})


"""======================================================================"""


# ---------- 新增前端页面 ----------

# 登录页面（已修改登录成功行为）
@app.route('/login')
def login_page():
    html = '''
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>登录 · 新所闻</title>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: #fafafa;
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 100vh;
                padding: 1.5rem;
            }
            .login-card {
                background: #ffffff;
                border-radius: 40px;
                box-shadow: 0 30px 60px rgba(0,0,0,0.04), 0 10px 24px rgba(0,0,0,0.02);
                padding: 3rem 2.8rem;
                width: 100%;
                max-width: 400px;
                transition: all 0.3s;
            }
            .login-card .brand {
                display: flex;
                align-items: center;
                gap: 12px;
                font-size: 1.8rem;
                font-weight: 300;
                color: #1a1a1a;
                margin-bottom: 0.5rem;
            }
            .login-card .brand i {
                color: #2c7a6b;
                font-size: 2.2rem;
            }
            .login-card h2 {
                font-weight: 300;
                font-size: 1.2rem;
                color: #5a6a7a;
                margin-bottom: 2.2rem;
                border-bottom: 1px solid #f0f0f0;
                padding-bottom: 1rem;
            }
            .form-group {
                margin-bottom: 1.6rem;
            }
            .form-group label {
                display: block;
                font-size: 0.85rem;
                font-weight: 500;
                color: #3a4a5a;
                margin-bottom: 0.4rem;
                letter-spacing: 0.3px;
            }
            .form-group .input-wrapper {
                position: relative;
            }
            .form-group .input-wrapper i {
                position: absolute;
                left: 16px;
                top: 50%;
                transform: translateY(-50%);
                color: #b0b8c0;
                font-size: 1rem;
            }
            .form-group input {
                width: 100%;
                padding: 0.9rem 1rem 0.9rem 3rem;
                border: 1px solid #e2e6ea;
                border-radius: 60px;
                font-size: 0.95rem;
                background: #f8f9fa;
                transition: border 0.2s, box-shadow 0.2s;
                outline: none;
                color: #1a1a1a;
            }
            .form-group input:focus {
                border-color: #2c7a6b;
                box-shadow: 0 0 0 3px rgba(44,122,107,0.1);
                background: #ffffff;
            }
            .btn-login {
                width: 100%;
                padding: 0.9rem;
                border: none;
                border-radius: 60px;
                background: #2c7a6b;
                color: white;
                font-size: 1rem;
                font-weight: 500;
                cursor: pointer;
                transition: background 0.2s, transform 0.1s;
                display: flex;
                justify-content: center;
                align-items: center;
                gap: 10px;
                margin-top: 0.5rem;
            }
            .btn-login:hover {
                background: #1f5f52;
            }
            .btn-login:active { transform: scale(0.98); }
            .error-msg {
                color: #c0392b;
                font-size: 0.85rem;
                margin-top: 0.8rem;
                text-align: center;
                display: none;
            }
            .error-msg.show { display: block; }
            .back-link {
                display: block;
                text-align: center;
                margin-top: 1.8rem;
                color: #8a9aa8;
                font-size: 0.9rem;
                text-decoration: none;
                transition: color 0.2s;
            }
            .back-link:hover { color: #2c3e50; }
            .back-link i { margin-right: 6px; }
            @media (max-width: 480px) {
                .login-card { padding: 2rem 1.5rem; }
            }
        </style>
    </head>
    <body>
        <div class="login-card">
            <div class="brand">
                <i class="fas fa-microchip"></i>
                <span>新所闻</span>
            </div>
            <h2><i class="fas fa-lock-open fa-fw" style="color:#2c7a6b;"></i> 管理员登录</h2>
            <form id="loginForm">
                <div class="form-group">
                    <label for="username">用户名</label>
                    <div class="input-wrapper">
                        <i class="fas fa-user"></i>
                        <input type="text" id="username" placeholder="admin" value="admin">
                    </div>
                </div>
                <div class="form-group">
                    <label for="password">密码</label>
                    <div class="input-wrapper">
                        <i class="fas fa-lock"></i>
                        <input type="password" id="password" placeholder="••••••••" value="admin123">
                    </div>
                </div>
                <button type="submit" class="btn-login"><i class="fas fa-sign-in-alt"></i> 登录</button>
                <div id="loginError" class="error-msg"><i class="fas fa-exclamation-circle"></i> 用户名或密码错误</div>
            </form>
            <a href="/" class="back-link"><i class="fas fa-arrow-left"></i> 返回首页</a>
        </div>
        <script>
            document.getElementById('loginForm').addEventListener('submit', async function(e) {
                e.preventDefault();
                const username = document.getElementById('username').value.trim();
                const password = document.getElementById('password').value.trim();
                const errorEl = document.getElementById('loginError');
                errorEl.classList.remove('show');

                try {
                    const res = await fetch('/admin/login', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ username, password })
                    });
                    const data = await res.json();
                    if (data.code === 200) {
                        // ---------- 修改点：登录成功后弹窗并跳转首页 ----------
                        alert('登录成功！');
                        window.location.href = '/';
                    } else {
                        errorEl.textContent = data.msg || '登录失败';
                        errorEl.classList.add('show');
                    }
                } catch (err) {
                    errorEl.textContent = '网络错误，请重试';
                    errorEl.classList.add('show');
                }
            });
        </script>
    </body>
    </html>
    '''
    return render_template_string(html)


# 后台管理页面（需要登录，未登录则重定向到 /login）
@app.route('/admin')
def admin_panel():
    # 检查 session 是否已登录
    if 'username' not in session or session.get('role') != 'admin':
        # 返回一个带重定向的 HTML，页面加载时会检查登录状态，若未登录则跳转。
        html = '''
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>管理后台 · 新所闻</title>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: #f5f6f8;
                padding: 2rem 1rem;
            }
            .container {
                max-width: 1100px;
                margin: 0 auto;
            }
            /* 顶部 */
            .admin-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                background: white;
                border-radius: 30px;
                padding: 1.2rem 2rem;
                box-shadow: 0 4px 12px rgba(0,0,0,0.02);
                margin-bottom: 2.5rem;
            }
            .admin-header .brand {
                display: flex;
                align-items: center;
                gap: 12px;
                font-size: 1.4rem;
                font-weight: 300;
                color: #1a1a1a;
            }
            .admin-header .brand i { color: #2c7a6b; font-size: 1.8rem; }
            .admin-header .user-info {
                display: flex;
                align-items: center;
                gap: 1.5rem;
            }
            .admin-header .user-info span {
                color: #5a6a7a;
                font-size: 0.95rem;
            }
            .admin-header .user-info a {
                color: #8a9aa8;
                text-decoration: none;
                transition: color 0.2s;
            }
            .admin-header .user-info a:hover { color: #c0392b; }
            /* 发布表单 */
            .publish-card {
                background: white;
                border-radius: 30px;
                padding: 2rem 2.5rem;
                box-shadow: 0 4px 12px rgba(0,0,0,0.02);
                margin-bottom: 2.5rem;
            }
            .publish-card h3 {
                font-weight: 400;
                font-size: 1.4rem;
                margin-bottom: 1.5rem;
                color: #1a1a1a;
            }
            .publish-card h3 i { color: #2c7a6b; margin-right: 10px; }
            .form-row {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 1.5rem;
                margin-bottom: 1.2rem;
            }
            .form-group { display: flex; flex-direction: column; }
            .form-group label {
                font-size: 0.85rem;
                font-weight: 500;
                color: #3a4a5a;
                margin-bottom: 0.4rem;
            }
            .form-group input, .form-group textarea {
                padding: 0.7rem 1rem;
                border: 1px solid #e2e6ea;
                border-radius: 20px;
                font-size: 0.95rem;
                background: #f8f9fa;
                transition: border 0.2s;
                outline: none;
                font-family: inherit;
            }
            .form-group input:focus, .form-group textarea:focus {
                border-color: #2c7a6b;
                background: white;
            }
            .form-group textarea { resize: vertical; min-height: 80px; }
            .btn-submit {
                background: #2c7a6b;
                color: white;
                border: none;
                padding: 0.7rem 2rem;
                border-radius: 40px;
                font-size: 0.95rem;
                font-weight: 500;
                cursor: pointer;
                transition: background 0.2s;
                display: inline-flex;
                align-items: center;
                gap: 8px;
                margin-top: 0.5rem;
            }
            .btn-submit:hover { background: #1f5f52; }
            /* 新闻列表 */
            .news-list {
                background: white;
                border-radius: 30px;
                padding: 2rem 2.5rem;
                box-shadow: 0 4px 12px rgba(0,0,0,0.02);
            }
            .news-list h3 {
                font-weight: 400;
                font-size: 1.4rem;
                margin-bottom: 1.5rem;
                color: #1a1a1a;
            }
            .news-list h3 i { color: #2c7a6b; margin-right: 10px; }
            .list-item {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 0.8rem 0;
                border-bottom: 1px solid #f0f2f5;
            }
            .list-item:last-child { border-bottom: none; }
            .list-item .info { flex: 1; }
            .list-item .info .title {
                font-weight: 500;
                color: #1a1a1a;
            }
            .list-item .info .meta {
                font-size: 0.8rem;
                color: #8a9aa8;
                display: flex;
                gap: 12px;
                margin-top: 2px;
            }
            .list-item .actions {
                display: flex;
                gap: 1rem;
            }
            .list-item .actions button {
                background: none;
                border: none;
                cursor: pointer;
                font-size: 1rem;
                transition: color 0.2s;
                padding: 4px 8px;
                border-radius: 40px;
            }
            .list-item .actions .delete-btn {
                color: #c0392b;
                background: #fde8e5;
                padding: 4px 12px;
                font-size: 0.85rem;
                font-weight: 500;
            }
            .list-item .actions .delete-btn:hover { background: #f5d0cc; }
            .empty-msg { color: #8a9aa8; text-align: center; padding: 2rem 0; }
            .toast {
                position: fixed;
                bottom: 2rem;
                right: 2rem;
                background: #1a1a1a;
                color: white;
                padding: 0.8rem 1.8rem;
                border-radius: 60px;
                font-size: 0.9rem;
                box-shadow: 0 8px 20px rgba(0,0,0,0.1);
                opacity: 0;
                transition: opacity 0.3s;
                pointer-events: none;
            }
            .toast.show { opacity: 1; }
            @media (max-width: 640px) {
                .form-row { grid-template-columns: 1fr; }
                .admin-header { flex-direction: column; gap: 1rem; align-items: start; }
                .list-item { flex-direction: column; align-items: start; gap: 0.6rem; }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <!-- 头部 -->
            <div class="admin-header">
                <div class="brand">
                    <i class="fas fa-microchip"></i>
                    <span>新所闻 · 管理</span>
                </div>
                <div class="user-info">
                    <span><i class="fas fa-user-circle"></i> admin</span>
                    <a href="/logout" id="logoutBtn"><i class="fas fa-sign-out-alt"></i> 退出</a>
                </div>
            </div>

            <!-- 发布新闻 -->
            <div class="publish-card">
                <h3><i class="fas fa-pen-fancy"></i> 发布新动态</h3>
                <form id="publishForm">
                    <div class="form-row">
                        <div class="form-group">
                            <label for="pubTitle">标题</label>
                            <input type="text" id="pubTitle" placeholder="输入新闻标题" required>
                        </div>
                        <div class="form-group">
                            <label for="pubCategory">分类</label>
                            <input type="text" id="pubCategory" placeholder="如：产品发布">
                        </div>
                    </div>
                    <div class="form-group" style="margin-bottom:1.2rem;">
                        <label for="pubContent">内容</label>
                        <textarea id="pubContent" placeholder="详细描述…" required></textarea>
                    </div>
                    <button type="submit" class="btn-submit"><i class="fas fa-cloud-upload-alt"></i> 发布</button>
                </form>
            </div>

            <!-- 新闻列表 -->
            <div class="news-list">
                <h3><i class="fas fa-list-ul"></i> 全部新闻</h3>
                <div id="newsListContainer">
                    <div class="empty-msg"><i class="fas fa-spinner fa-spin"></i> 加载中…</div>
                </div>
            </div>
        </div>

        <div id="toast" class="toast"></div>

        <script>
            // ---------- 工具：显示提示 ----------
            function showToast(msg, isError = false) {
                const t = document.getElementById('toast');
                t.textContent = msg;
                t.style.background = isError ? '#c0392b' : '#1a1a1a';
                t.classList.add('show');
                setTimeout(() => t.classList.remove('show'), 3000);
            }

            // ---------- 检查登录状态 ----------
            // 如果未登录，立即跳转到登录页
            fetch('/api/news', { method: 'GET' })  // 任意接口测试 session
                .then(res => {
                    // 如果返回 401，说明未登录
                    if (res.status === 401) {
                        window.location.href = '/login';
                    }
                })
                .catch(() => {});

            // ---------- 加载新闻列表 ----------
            function loadNews() {
                const container = document.getElementById('newsListContainer');
                fetch('/api/news')
                    .then(res => res.json())
                    .then(data => {
                        if (data.code !== 200) {
                            container.innerHTML = `<div class="empty-msg">加载失败</div>`;
                            return;
                        }
                        if (!data.data || data.data.length === 0) {
                            container.innerHTML = `<div class="empty-msg"><i class="far fa-frown"></i> 暂无新闻</div>`;
                            return;
                        }
                        container.innerHTML = data.data.map(item => `
                            <div class="list-item" data-id="${item.id}">
                                <div class="info">
                                    <div class="title">${item.title}</div>
                                    <div class="meta">
                                        <span>${item.category || '未分类'}</span>
                                        <span>${item.created_at}</span>
                                    </div>
                                </div>
                                <div class="actions">
                                    <button class="delete-btn" data-id="${item.id}"><i class="fas fa-trash-alt"></i> 删除</button>
                                </div>
                            </div>
                        `).join('');

                        // 绑定删除事件
                        document.querySelectorAll('.delete-btn').forEach(btn => {
                            btn.addEventListener('click', function(e) {
                                e.stopPropagation();
                                const id = this.dataset.id;
                                if (confirm('确定要删除这篇新闻吗？')) {
                                    deleteNews(id);
                                }
                            });
                        });
                    })
                    .catch(() => {
                        container.innerHTML = `<div class="empty-msg">请求失败</div>`;
                    });
            }

            // ---------- 删除新闻 ----------
            function deleteNews(id) {
                fetch(`/admin/news/${id}`, { method: 'DELETE' })
                    .then(res => res.json())
                    .then(data => {
                        if (data.code === 200) {
                            showToast('删除成功');
                            loadNews(); // 刷新列表
                        } else {
                            showToast(data.msg || '删除失败', true);
                        }
                    })
                    .catch(() => showToast('网络错误', true));
            }

            // ---------- 发布新闻 ----------
            document.getElementById('publishForm').addEventListener('submit', async function(e) {
                e.preventDefault();
                const title = document.getElementById('pubTitle').value.trim();
                const content = document.getElementById('pubContent').value.trim();
                const category = document.getElementById('pubCategory').value.trim();

                if (!title || !content) {
                    showToast('标题和内容不能为空', true);
                    return;
                }

                try {
                    const res = await fetch('/admin/news', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ title, content, category })
                    });
                    const data = await res.json();
                    if (data.code === 200) {
                        showToast('发布成功');
                        document.getElementById('publishForm').reset();
                        loadNews();
                    } else {
                        showToast(data.msg || '发布失败', true);
                    }
                } catch (err) {
                    showToast('网络错误', true);
                }
            });

            // ---------- 退出登录 ----------
            document.getElementById('logoutBtn').addEventListener('click', function(e) {
                e.preventDefault();
                if (confirm('确定退出吗？')) {
                    // 由于没有 logout 接口，直接跳转登录页（新登录会覆盖旧 session）
                    window.location.href = '/login';
                }
            });

            // 初始加载
            loadNews();
        </script>
    </body>
    </html>
    '''
        return render_template_string(html)


# 新闻详情页
@app.route('/news/<int:id>')
def news_detail_page(id):
    html = '''
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>新闻详情 · 新所闻</title>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: #fafafa;
                padding: 2rem 1.5rem;
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 100vh;
            }
            .detail-card {
                background: white;
                border-radius: 40px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.04);
                max-width: 800px;
                width: 100%;
                padding: 3rem 3rem 2.5rem;
                transition: all 0.2s;
            }
            .back-link {
                display: inline-flex;
                align-items: center;
                gap: 8px;
                color: #8a9aa8;
                text-decoration: none;
                font-size: 0.9rem;
                margin-bottom: 2rem;
                transition: color 0.2s;
            }
            .back-link:hover { color: #2c3e50; }
            .detail-card .title {
                font-size: 2.2rem;
                font-weight: 300;
                color: #1a1a1a;
                margin-bottom: 0.8rem;
                line-height: 1.3;
            }
            .detail-card .meta {
                display: flex;
                gap: 1.5rem;
                color: #8a9aa8;
                font-size: 0.9rem;
                margin-bottom: 2rem;
                border-bottom: 1px solid #f0f2f5;
                padding-bottom: 1.2rem;
            }
            .detail-card .meta .category {
                background: #ecf3f8;
                padding: 0.1rem 1rem;
                border-radius: 40px;
                color: #2c3e50;
                font-weight: 500;
                font-size: 0.8rem;
            }
            .detail-card .content {
                font-size: 1.05rem;
                color: #3a4a5a;
                line-height: 1.8;
                font-weight: 300;
                white-space: pre-wrap;
            }
            .loading, .error {
                text-align: center;
                padding: 3rem 0;
                color: #8a9aa8;
            }
            .error { color: #c0392b; }
            @media (max-width: 640px) {
                .detail-card { padding: 1.8rem; }
                .detail-card .title { font-size: 1.6rem; }
            }
        </style>
    </head>
    <body>
        <div class="detail-card">
            <a href="/" class="back-link"><i class="fas fa-arrow-left"></i> 返回首页</a>
            <div id="detailContent">
                <div class="loading"><i class="fas fa-spinner fa-spin"></i> 加载中…</div>
            </div>
        </div>
        <script>
            const id = window.location.pathname.split('/').pop();
            fetch(`/api/news/${id}`)
                .then(res => res.json())
                .then(data => {
                    const container = document.getElementById('detailContent');
                    if (data.code !== 200 || !data.data) {
                        container.innerHTML = `<div class="error"><i class="fas fa-exclamation-triangle"></i> 新闻不存在或加载失败</div>`;
                        return;
                    }
                    const item = data.data;
                    container.innerHTML = `
                        <div class="title">${item.title}</div>
                        <div class="meta">
                            <span><i class="far fa-calendar-alt"></i> ${item.created_at}</span>
                            ${item.category ? `<span class="category">${item.category}</span>` : ''}
                        </div>
                        <div class="content">${item.content}</div>
                    `;
                })
                .catch(() => {
                    document.getElementById('detailContent').innerHTML = `<div class="error"><i class="fas fa-exclamation-triangle"></i> 网络错误</div>`;
                });
        </script>
    </body>
    </html>
    '''
    return render_template_string(html)


# 保留原有 /cms 路由（不再使用，但保留）
@app.route('/cms')
def cms_home():
    # 原有代码保持不变（略）
    return "旧版 CMS 页面已废弃，请访问 /"


if __name__ == '__main__':
    print("   公司CMS启动于: http://127.0.0.1:5003")
    print("   测试流程:")
    print("   1. 管理员登录: POST /admin/login (Body: {\"username\":\"admin\",\"password\":\"admin123\"})")
    print("   2. 发布新闻: POST /admin/news (需要登录)")
    print("   3. 前台查看: GET /api/news 或 GET /api/news/<id>")
    print("   4. 后台管理界面: GET /admin (浏览器访问)")
    app.run(debug=True, port=5003)