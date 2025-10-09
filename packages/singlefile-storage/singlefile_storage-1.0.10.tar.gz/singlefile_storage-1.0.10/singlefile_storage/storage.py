#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: qicongsheng
import os
import sqlite3
import uuid
from math import ceil

from flask import Flask, request, jsonify, redirect, session, send_from_directory, render_template
from flask_httpauth import HTTPBasicAuth

from singlefile_storage import help

users = {
    "admin": "password"
}
DATA_PATH = './data'
API_KEY = 'your-api-key'
app = Flask(__name__)
auth = HTTPBasicAuth()
app.secret_key = str(uuid.uuid4())


def init_app():
    app.config.update({
        'UPLOAD_FOLDER': os.path.join(DATA_PATH, 'uploads'),  # 文件存储目录
        'DATABASE': os.path.join(DATA_PATH, 'storage.db'),  # SQLite数据库路径
        'MAX_CONTENT_LENGTH': 64 * 1024 * 1024,
        'ALLOWED_EXTENSIONS': {'html', 'htm'},
        'API_KEYS': {API_KEY},
        'ITEMS_PER_PAGE': 12  # 分页每页数量
    })
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    with sqlite3.connect(app.config['DATABASE']) as conn:
        conn.execute('''
                     CREATE TABLE IF NOT EXISTS uploads
                     (
                         id
                         INTEGER
                         PRIMARY
                         KEY
                         AUTOINCREMENT,
                         filename
                         TEXT
                         NOT
                         NULL
                         UNIQUE,
                         original_url
                         TEXT
                         NOT
                         NULL,
                         uploaded_at
                         DATETIME
                         DEFAULT
                         CURRENT_TIMESTAMP
                     )
                     ''')


# 验证用户
@auth.verify_password
def verify_password(username, password):
    if 'user_id' in session:
        return session['user_id']
    if username in users and users[username] == password:
        return username
    return None


@auth.error_handler
def auth_error(status):
    if status == 401:
        return redirect('/login')  # 重定向到登录页面的路由
    return "Authentication failed", status, {'X-Custom': 'Header', 'Content-Type': 'text/plain'}


@app.route('/', methods=['GET'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if verify_password(username, password):
            session['user_id'] = password
            session.permanent = True  # 启用超时设置
            return redirect('/list')
        return "无效的凭据", 401
    return render_template("login.html", version=help.get_version())


def get_unique_filename(filename):
    base, ext = os.path.splitext(filename)
    counter = 1
    new_name = filename
    while os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], new_name)):
        new_name = f"{base}({counter}){ext}"
        counter += 1
    return new_name


@app.route('/upload', methods=['POST'])
def upload_file():
    # Authentication
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'error': 'Invalid Authorization header'}), 401
    token = auth_header.split(' ')[1]
    if token not in app.config['API_KEYS']:
        return jsonify({'error': 'Invalid API key'}), 403

    # File validation
    if 'singlehtmlfile' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['singlehtmlfile']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if not ('.' in file.filename and
            file.filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']):
        return jsonify({'error': 'Invalid file type'}), 400

    # URL validation
    url = request.form.get('url', '').strip()
    if not url:
        return jsonify({'error': 'Missing URL'}), 400

    # Save file
    filename = get_unique_filename(file.filename)
    save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    try:
        file.save(save_path)
        # Database operation
        with sqlite3.connect(app.config['DATABASE']) as conn:
            conn.execute('''
                         INSERT INTO uploads (filename, original_url)
                         VALUES (?, ?)
                         ''', (filename, url))
    except Exception as e:
        if os.path.exists(save_path):
            os.remove(save_path)
        return jsonify({'error': str(e)}), 500

    return jsonify({
        'message': 'File uploaded successfully',
        'filename': filename,
        'original_url': url
    }), 200


@app.route('/delete/<filename>', methods=['DELETE', 'GET'])
@auth.login_required
def delete_file(filename):
    # Delete from database
    with sqlite3.connect(app.config['DATABASE']) as conn:
        cur = conn.execute('DELETE FROM uploads WHERE filename = ?', (filename,))
        if cur.rowcount == 0:
            return jsonify({'error': 'File not found'}), 404

    # Delete local file
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
        except Exception as e:
            return jsonify({'error': f'File deletion failed: {str(e)}'}), 500

    return jsonify({'message': 'File deleted successfully'}), 200


@app.route('/list')
@auth.login_required
def file_list():
    page = request.args.get('page', 1, type=int)
    per_page = app.config['ITEMS_PER_PAGE']

    with sqlite3.connect(app.config['DATABASE']) as conn:
        conn.row_factory = sqlite3.Row

        # Get total count
        total = conn.execute('SELECT COUNT(*) FROM uploads').fetchone()[0]
        total_pages = ceil(total / per_page) if total else 1

        # Validate page number
        page = max(1, min(page, total_pages))
        offset = (page - 1) * per_page

        # Get paginated data
        cur = conn.execute('''
                           SELECT filename,
                                  original_url,
                                  datetime(uploaded_at) as uploaded_at
                           FROM uploads
                           ORDER BY uploaded_at DESC LIMIT ?
                           OFFSET ?
                           ''', (per_page, offset))
        files = cur.fetchall()

    # Get file sizes
    files_with_size = []
    for item in files:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], item['filename'])
        size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
        files_with_size.append({
            'filename': item['filename'],
            'original_url': item['original_url'],
            'uploaded_at': item['uploaded_at'],
            'size': size
        })

    return render_template('content.html',
                           files=files_with_size,
                           pagination={
                               'page': page,
                               'total_pages': total_pages,
                               'has_prev': page > 1,
                               'has_next': page < total_pages
                           })


@app.route('/uploads/<filename>')
def serve_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.errorhandler(404)
def page_not_found(error):
    return "Leave me alone."


@app.route('/robots.txt', methods=['GET'])
def robots():
    return send_from_directory(app.static_folder, 'robots.txt')


def start(port=5000):
    init_app()
    app.run(host='0.0.0.0', port=port)


if __name__ == '__main__':
    start()
