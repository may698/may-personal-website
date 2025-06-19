from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import re

app = Flask(__name__)
CORS(app)

# 使用绝对路径确保文件位置正确
COMMENTS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "comments.txt")

def sanitize_input(text):
    """清理和验证输入数据"""
    if not text:
        return ""
    # 移除潜在的恶意字符，保留基本的中文、英文、数字和标点
    cleaned = re.sub(r'[<>"\']', '', str(text).strip())
    return cleaned[:500]  # 限制长度

@app.route("/api/comment", methods=["POST"])
def save_comment():
    try:
        if request.is_json:
            data = request.get_json()
            name = data.get("name", "名無し")
            message = data.get("message", "")
        else:
            name = request.form.get("name", "名無し")
            message = request.form.get("message", "")

        # 清理和验证输入
        name = sanitize_input(name)
        message = sanitize_input(message)

        if not message.strip():
            return jsonify({"error": "メッセージが空です"}), 400

        # 确保目录存在
        os.makedirs(os.path.dirname(COMMENTS_FILE), exist_ok=True)

        with open(COMMENTS_FILE, "a", encoding="utf-8") as f:
            f.write(f"{name}: {message}\n")

        return jsonify({"status": "ok"})
    
    except Exception as e:
        return jsonify({"error": f"保存留言时发生错误: {str(e)}"}), 500

# ✅ 新增：取得留言列表
@app.route("/api/comments", methods=["GET"])
def get_comments():
    try:
        if not os.path.exists(COMMENTS_FILE):
            return jsonify([])

        with open(COMMENTS_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()

        comments = []
        for line in lines:
            line = line.strip()
            if ": " in line:
                try:
                    name, message = line.split(": ", 1)
                    comments.append({"name": name, "message": message})
                except ValueError:
                    # 跳过格式不正确的行
                    continue
        return jsonify(comments)
    
    except Exception as e:
        return jsonify({"error": f"读取留言时发生错误: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True, port=8080, host='0.0.0.0')