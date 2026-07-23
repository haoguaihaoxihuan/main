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


if __name__ == '__main__':
    print("   公司CMS启动于: http://127.0.0.1:5003")
    print("   测试流程:")
    print("   1. 管理员登录: POST /admin/login (Body: {\"username\":\"admin\",\"password\":\"admin123\"})")
    print("   2. 发布新闻: POST /admin/news (需要登录)")
    print("   3. 前台查看: GET /api/news 或 GET /api/news/<id>")
    print("   4. 后台管理界面: GET /admin (浏览器访问)")
    app.run(debug=True, port=5003)