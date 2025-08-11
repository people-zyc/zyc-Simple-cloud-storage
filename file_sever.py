import os
import argparse
import shutil
from flask import Flask, request, jsonify, abort, make_response
from flask_cors import CORS
app = Flask(__name__)
CORS(app)  # 允许所有来源的跨域请求
WORK_PATH = None
API_PASSWORD = None  # 密码将在启动时设置
def secure_path(user_path):
    abs_path = os.path.abspath(os.path.join(WORK_PATH, user_path.lstrip('/')))
    if not abs_path.startswith(WORK_PATH):
        abort(403, description="Path traversal attempt detected")
    return abs_path
@app.before_request
def check_password():
    if request.method == 'OPTIONS':
        return

    if request.endpoint in ['list_directory', 'create_file', 'write_file', 'read_file', 'delete_path']:
        if 'passwd' not in request.args or request.args.get('passwd') != API_PASSWORD:
            return make_response(jsonify({"error": "Unauthorized"}), 401)

@app.route('/files', methods=['GET', 'OPTIONS'])
def list_directory():
    if request.method == 'OPTIONS':
        # 预检请求处理
        response = make_response()
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response
    path = request.args.get('path', '')
    abs_path = secure_path(path)
    if not os.path.exists(abs_path):
        return jsonify({"error": "Directory not found"}), 404
    if not os.path.isdir(abs_path):
        return jsonify({"error": "Not a directory"}), 400
    contents = []
    for item in os.listdir(abs_path):
        item_path = os.path.join(abs_path, item)
        rel_path = os.path.join(path, item).replace('\\', '/').lstrip('/')
        item_type = 'directory' if os.path.isdir(item_path) else 'file'
        contents.append({
            "name": item,
            "type": item_type,
            "path": rel_path,
            "size": os.path.getsize(item_path) if item_type == 'file' else 0
        })
    return jsonify({"path": path, "contents": contents})
@app.route('/files', methods=['POST', 'OPTIONS'])
def create_file():
    if request.method == 'OPTIONS':
        response = make_response()
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response
    data = request.json
    file_path = data.get('path')
    if not file_path:
        return jsonify({"error": "Missing file path"}), 400
    abs_path = secure_path(file_path)
    os.makedirs(os.path.dirname(abs_path), exist_ok=True)
    open(abs_path, 'w').close()
    return jsonify({"message": f"File created: {file_path}"}), 201
@app.route('/files/content', methods=['PUT', 'OPTIONS'])
def write_file():
    if request.method == 'OPTIONS':
        response = make_response()
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response
    data = request.json
    file_path = data.get('path')
    content = data.get('content', '')
    if not file_path:
        return jsonify({"error": "Missing file path"}), 400
    abs_path = secure_path(file_path)
    if os.path.exists(abs_path) and os.path.isdir(abs_path):
        return jsonify({"error": "Cannot write to a directory"}), 400
    with open(abs_path, 'w') as f:
        f.write(content)
    return jsonify({"message": f"Content written to {file_path}"})
@app.route('/files/content', methods=['GET', 'OPTIONS'])
def read_file():
    if request.method == 'OPTIONS':
        # 预检请求处理
        response = make_response()
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response
    file_path = request.args.get('path')
    if not file_path:
        return jsonify({"error": "Missing file path"}), 400
    abs_path = secure_path(file_path)
    if not os.path.exists(abs_path):
        return jsonify({"error": "File not found"}), 404
    if os.path.isdir(abs_path):
        return jsonify({"error": "Cannot read directory content"}), 400
    with open(abs_path, 'r') as f:
        content = f.read()
    return jsonify({
        "path": file_path,
        "content": content
    })
@app.route('/files', methods=['DELETE', 'OPTIONS'])
def delete_path():
    if request.method == 'OPTIONS':
        response = make_response()
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response
    path = request.json.get('path')
    if not path:
        return jsonify({"error": "Missing path"}), 400
    abs_path = secure_path(path)
    if not os.path.exists(abs_path):
        return jsonify({"error": "Path not found"}), 404
    if os.path.isdir(abs_path):
        shutil.rmtree(abs_path)
        return jsonify({"message": f"Directory deleted: {path}"})
    else:
        os.remove(abs_path)
        return jsonify({"message": f"File deleted: {path}"})
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='File Management API')
    parser.add_argument('-workpath', required=True, help='Working directory path')
    parser.add_argument('-passwd', required=True, help='API access password')
    parser.add_argument('-host', default='127.0.0.1', help='Host to bind')
    parser.add_argument('-port', default=5000, type=int, help='Port to listen')
    args = parser.parse_args()
    WORK_PATH = os.path.abspath(args.workpath)
    API_PASSWORD = args.passwd
    os.makedirs(WORK_PATH, exist_ok=True)
    print(f"Starting API server on {args.host}:{args.port}")
    print(f"Working directory: {WORK_PATH}")
    app.run(host=args.host, port=args.port)
