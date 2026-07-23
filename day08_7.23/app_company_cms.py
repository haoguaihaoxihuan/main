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
    conn = get_db()
    conn.row_factory = dict_factory
    c = conn.cursor()
    # 最新三条新闻，倒序
    c.execute('SELECT id, title, content, category, created_at FROM news ORDER BY created_at DESC LIMIT 3')
    latest = c.fetchall()
    conn.close()
    # 公司简介
    company_info = "全球第一富有！！！！"
    return jsonify({
        "code": 200,
        "data": {
            "company": company_info,
            "latest_news": latest
        }
    })


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


# ---------- 新增前端页面（不修改已有代码） ----------

@app.route('/cms')
def cms_home():
    """
    公司官网首页（前端页面）
    展示公司简介和最新3条新闻，调用 /api/news 接口获取数据
    """
    html = '''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>科技公司官网</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; background: #f4f4f4; }
            .container { max-width: 900px; margin: auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
            h1 { color: #333; border-bottom: 2px solid #007BFF; padding-bottom: 10px; }
            .news-item { border-bottom: 1px solid #ddd; padding: 15px 0; }
            .news-item h3 { margin: 0 0 5px; color: #007BFF; }
            .news-item small { color: #888; }
            .news-item .category { background: #007BFF; color: white; padding: 2px 8px; border-radius: 12px; font-size: 12px; display: inline-block; }
            .btn { background: #007BFF; color: white; padding: 8px 16px; text-decoration: none; border-radius: 4px; }
            .btn:hover { background: #0056b3; }
            .admin-link { margin-top: 20px; display: inline-block; }
            #newsList { margin-top: 20px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 全球第一富有科技公司</h1>
            <p>我们致力于创新技术解决方案，引领行业未来。</p>
            <h2>📰 最新动态</h2>
            <div id="newsList">加载中...</div>
            <div style="margin-top: 20px;">
                <a href="/admin_panel" class="btn">后台管理</a>
            </div>
        </div>
        <script>
            fetch('/api/news')
                .then(res => res.json())
                .then(data => {
                    if (data.code === 200) {
                        const list = document.getElementById('newsList');
                        list.innerHTML = '';
                        if (data.data.length === 0) {
                            list.innerHTML = '<p>暂无新闻</p>';
                            return;
                        }
                        data.data.forEach(item => {
                            const div = document.createElement('div');
                            div.className = 'news-item';
                            div.innerHTML = `
                                <h3>${item.title}</h3>
                                <p>${item.content}</p>
                                <small>分类：<span class="category">${item.category || '未分类'}</span> 发布时间：${item.created_at}</small>
                                <hr>
                            `;
                            list.appendChild(div);
                        });
                    } else {
                        document.getElementById('newsList').innerHTML = '<p>加载失败</p>';
                    }
                })
                .catch(err => {
                    document.getElementById('newsList').innerHTML = '<p>请求出错</p>';
                });
        </script>
    </body>
    </html>
    '''
    return render_template_string(html)


@app.route('/admin_panel')
def admin_panel():
    """
    后台管理界面（前端页面）
    包含登录、发布新闻、新闻列表及删除功能
    """
    html = '''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>后台管理 - CMS</title>
        <style>
            body { font-family: Arial; margin: 20px; background: #f0f0f0; }
            .container { max-width: 800px; margin: auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
            input, textarea { width: 100%; padding: 8px; margin: 5px 0; border: 1px solid #ccc; border-radius: 4px; }
            button { padding: 8px 16px; background: #007BFF; color: white; border: none; border-radius: 4px; cursor: pointer; }
            button:hover { background: #0056b3; }
            .login-form { background: #f9f9f9; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
            .hidden { display: none; }
            .news-item { border: 1px solid #ddd; padding: 10px; margin: 10px 0; border-radius: 4px; }
            .delete-btn { background: #dc3545; margin-left: 10px; }
            .delete-btn:hover { background: #c82333; }
            .msg { color: green; margin-top: 5px; }
            .error { color: red; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🔐 后台管理</h1>
            <div id="loginSection" class="login-form">
                <h3>管理员登录</h3>
                <input type="text" id="username" placeholder="用户名" value="admin">
                <input type="password" id="password" placeholder="密码" value="admin123">
                <button onclick="login()">登录</button>
                <p id="loginMsg"></p>
            </div>
            <div id="adminSection" class="hidden">
                <h3>📝 发布新新闻</h3>
                <input type="text" id="title" placeholder="标题">
                <input type="text" id="category" placeholder="分类（可选）">
                <textarea id="content" rows="4" placeholder="内容"></textarea>
                <button onclick="publish()">发布</button>
                <p id="publishMsg"></p>
                <hr>
                <h3>📋 所有新闻</h3>
                <div id="newsList"></div>
                <button onclick="logout()" style="background:#6c757d;">退出登录</button>
            </div>
        </div>
        <script>
            // 检查是否已登录（尝试获取新闻列表需要登录，但我们可以通过调用一个需要登录的接口来判断）
            // 或者直接显示登录界面，用户手动登录
            function login() {
                const username = document.getElementById('username').value;
                const password = document.getElementById('password').value;
                fetch('/admin/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ username, password })
                })
                .then(res => res.json())
                .then(data => {
                    if (data.code === 200) {
                        document.getElementById('loginSection').classList.add('hidden');
                        document.getElementById('adminSection').classList.remove('hidden');
                        loadNews();
                        document.getElementById('loginMsg').innerText = '';
                    } else {
                        document.getElementById('loginMsg').innerText = '❌ ' + data.msg;
                        document.getElementById('loginMsg').className = 'error';
                    }
                })
                .catch(err => {
                    document.getElementById('loginMsg').innerText = '请求错误';
                });
            }

            function loadNews() {
                fetch('/api/news')
                    .then(res => res.json())
                    .then(data => {
                        if (data.code === 200) {
                            const list = document.getElementById('newsList');
                            list.innerHTML = '';
                            if (data.data.length === 0) {
                                list.innerHTML = '<p>暂无新闻</p>';
                                return;
                            }
                            data.data.forEach(item => {
                                const div = document.createElement('div');
                                div.className = 'news-item';
                                div.innerHTML = `
                                    <strong>${item.title}</strong>
                                    <p>${item.content}</p>
                                    <small>分类：${item.category || '无'} | 时间：${item.created_at}</small>
                                    <br>
                                    <button class="delete-btn" onclick="deleteNews(${item.id})">删除</button>
                                `;
                                list.appendChild(div);
                            });
                        } else {
                            document.getElementById('newsList').innerHTML = '<p>加载失败</p>';
                        }
                    });
            }

            function publish() {
                const title = document.getElementById('title').value.trim();
                const content = document.getElementById('content').value.trim();
                const category = document.getElementById('category').value.trim();
                if (!title || !content) {
                    document.getElementById('publishMsg').innerText = '标题和内容不能为空';
                    document.getElementById('publishMsg').className = 'error';
                    return;
                }
                fetch('/admin/news', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ title, content, category })
                })
                .then(res => res.json())
                .then(data => {
                    if (data.code === 200) {
                        document.getElementById('publishMsg').innerText = '✅ 发布成功！';
                        document.getElementById('publishMsg').className = 'msg';
                        document.getElementById('title').value = '';
                        document.getElementById('content').value = '';
                        document.getElementById('category').value = '';
                        loadNews();
                    } else {
                        document.getElementById('publishMsg').innerText = '❌ ' + data.msg;
                        document.getElementById('publishMsg').className = 'error';
                    }
                })
                .catch(err => {
                    document.getElementById('publishMsg').innerText = '请求错误';
                });
            }

            function deleteNews(id) {
                if (!confirm('确定删除该新闻吗？')) return;
                fetch('/admin/news/' + id, {
                    method: 'DELETE'
                })
                .then(res => res.json())
                .then(data => {
                    if (data.code === 200) {
                        alert('删除成功');
                        loadNews();
                    } else {
                        alert('删除失败: ' + data.msg);
                    }
                });
            }

            function logout() {
                fetch('/admin/logout', { method: 'POST' })
                    .then(res => res.json())
                    .then(data => {
                        alert(data.msg);
                        location.reload(); // 刷新页面回到登录状态
                    });
            }

            // 页面加载时检测登录状态：尝试调用一个需要登录的接口（比如获取新闻列表，但不需要登录，所以我们换成调用 /admin/news 的GET？我们没有提供。可以调用 /admin/news?xxx 但会返回404。更简单的是直接显示登录界面，用户自己登录。
            // 因为session可能持久，但前端无感知，这里默认显示登录，用户手动登录。
        </script>
    </body>
    </html>
    '''
    return render_template_string(html)


if __name__ == '__main__':
    print("   公司CMS启动于: http://127.0.0.1:5003")
    print("   测试流程:")
    print("   1. 管理员登录: POST /admin/login (Body: {\"username\":\"admin\",\"password\":\"admin123\"})")
    print("   2. 发布新闻: POST /admin/news (需要登录)")
    print("   3. 前台查看: GET /api/news 或 GET /api/news/<id>")
    print("   4. 后台管理界面: GET /admin (浏览器访问)")
    app.run(debug=True, port=5003)



