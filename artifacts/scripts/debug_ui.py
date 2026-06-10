#!/usr/bin/env python3
"""CS224N debug UI — 阶段间断点的 web 界面(纯标准库,无依赖)

用法(由 run_lecture.sh 自动调用):
  python3 debug_ui.py --stage capsules --lecture L01-word-vectors --port 9120

功能:
- 显示当前阶段产物列表(自动扫描产物目录)
- 点击产物查看内容(纯文本展示,Markdown 不渲染但可读)
- 两个按钮:✓ 通过继续 / ✗ 返修
- 用 http.server,无外部依赖
"""
import argparse
import json
import os
import sys
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import html

STAGE = ""
LECTURE = ""
CONTROL_FILE = ""
ARTIFACTS_DIR = ""

class DebugUIHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # 静默日志

    def do_GET(self):
        parsed = urlparse(self.path)

        if parsed.path == '/':
            self.send_html()
        elif parsed.path == '/api/artifacts':
            self.send_json(list_artifacts())
        elif parsed.path == '/api/content':
            params = parse_qs(parsed.query)
            path = params.get('path', [''])[0]
            self.send_content(path)
        else:
            self.send_error(404)

    def do_POST(self):
        if self.path == '/api/decision':
            length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(length).decode('utf-8')
            data = json.loads(body)
            self.handle_decision(data)
            self.send_json({'status': 'ok'})
        else:
            self.send_error(404)

    def send_html(self):
        html_content = HTML_TEMPLATE.format(
            stage=STAGE.upper(),
            lecture=LECTURE,
            artifact_count=len(list_artifacts())
        )
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html_content.encode('utf-8'))

    def send_json(self, data):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))

    def send_content(self, path):
        full_path = Path(ARTIFACTS_DIR) / path
        if not full_path.exists() or not full_path.is_file():
            self.send_json({'error': 'File not found'})
            return

        content = full_path.read_text(encoding='utf-8', errors='ignore')
        # 简单转义,保留换行
        escaped = html.escape(content)

        self.send_json({
            'name': full_path.name,
            'content': f'<pre style="white-space:pre-wrap;word-wrap:break-word;">{escaped}</pre>'
        })

    def handle_decision(self, data):
        decision = data.get('decision')
        if decision == 'pass':
            Path(CONTROL_FILE).write_text('CONTINUE\n')
        elif decision == 'fail':
            feedback = data.get('feedback', '未填写原因')
            Path(CONTROL_FILE).write_text(f'FEEDBACK\n{feedback}\n')

HTML_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>CS224N Debug UI — {stage}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: #f5f5f5;
            padding: 20px;
        }}
        .container {{ max-width: 1400px; margin: 0 auto; }}
        .header {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }}
        .header h1 {{ color: #333; font-size: 24px; margin-bottom: 8px; }}
        .header .meta {{ color: #666; font-size: 14px; }}
        .actions {{
            display: flex;
            gap: 12px;
            margin-top: 16px;
        }}
        .btn {{
            padding: 12px 24px;
            border: none;
            border-radius: 6px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
        }}
        .btn-pass {{ background: #10b981; color: white; }}
        .btn-pass:hover {{ background: #059669; }}
        .btn-fail {{ background: #ef4444; color: white; }}
        .btn-fail:hover {{ background: #dc2626; }}
        .content {{
            display: grid;
            grid-template-columns: 300px 1fr;
            gap: 20px;
        }}
        .sidebar {{
            background: white;
            padding: 16px;
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            height: fit-content;
            position: sticky;
            top: 20px;
        }}
        .sidebar h2 {{ font-size: 16px; margin-bottom: 12px; color: #333; }}
        .artifact-list {{ list-style: none; max-height: 600px; overflow-y: auto; }}
        .artifact-item {{
            padding: 8px 12px;
            margin-bottom: 4px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 13px;
            transition: background 0.2s;
            word-break: break-word;
        }}
        .artifact-item:hover {{ background: #f3f4f6; }}
        .artifact-item.active {{ background: #dbeafe; color: #1e40af; }}
        .preview {{
            background: white;
            padding: 24px;
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            min-height: 500px;
            max-height: 800px;
            overflow-y: auto;
        }}
        .preview h2 {{ margin-bottom: 16px; color: #333; }}
        .preview-content {{
            line-height: 1.6;
            color: #333;
            font-size: 14px;
        }}
        .modal {{
            display: none;
            position: fixed;
            top: 0; left: 0;
            width: 100%; height: 100%;
            background: rgba(0,0,0,0.5);
            align-items: center;
            justify-content: center;
        }}
        .modal.show {{ display: flex; }}
        .modal-content {{
            background: white;
            padding: 24px;
            border-radius: 8px;
            width: 90%;
            max-width: 500px;
        }}
        .modal-content h3 {{ margin-bottom: 16px; }}
        .modal-content textarea {{
            width: 100%;
            min-height: 150px;
            padding: 12px;
            border: 1px solid #d1d5db;
            border-radius: 4px;
            font-family: inherit;
            font-size: 14px;
        }}
        .modal-actions {{
            display: flex;
            gap: 8px;
            margin-top: 16px;
            justify-content: flex-end;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔍 {stage} 阶段审查</h1>
            <div class="meta">Lecture: {lecture} | 产物: {artifact_count} 个</div>
            <div class="actions">
                <button class="btn btn-pass" onclick="passContinue()">✓ 通过继续</button>
                <button class="btn btn-fail" onclick="showFeedbackModal()">✗ 返修</button>
            </div>
        </div>
        <div class="content">
            <div class="sidebar">
                <h2>产物列表</h2>
                <ul class="artifact-list" id="artifactList"></ul>
            </div>
            <div class="preview">
                <h2 id="previewTitle">选择左侧产物查看</h2>
                <div class="preview-content" id="previewContent">
                    <p style="color:#999;">点击左侧文件名查看内容</p>
                </div>
            </div>
        </div>
    </div>

    <div class="modal" id="feedbackModal">
        <div class="modal-content">
            <h3>返修原因</h3>
            <textarea id="feedbackText" placeholder="描述具体问题和如何修改..."></textarea>
            <div class="modal-actions">
                <button class="btn" onclick="closeFeedbackModal()" style="background:#6b7280;color:white;">取消</button>
                <button class="btn btn-fail" onclick="submitFeedback()">提交返修</button>
            </div>
        </div>
    </div>

    <script>
        let artifacts = [];
        let currentActive = null;

        async function loadArtifacts() {{
            const res = await fetch('/api/artifacts');
            artifacts = await res.json();
            renderArtifactList();
            if (artifacts.length > 0) {{
                loadArtifact(artifacts[0].path, 0);
            }}
        }}

        function renderArtifactList() {{
            const list = document.getElementById('artifactList');
            list.innerHTML = artifacts.map((a, i) =>
                `<li class="artifact-item" data-idx="${{i}}" onclick="loadArtifact('${{a.path}}', ${{i}})">${{a.name}}</li>`
            ).join('');
        }}

        async function loadArtifact(path, idx) {{
            document.querySelectorAll('.artifact-item').forEach(el => el.classList.remove('active'));
            document.querySelector(`[data-idx="${{idx}}"]`).classList.add('active');

            const res = await fetch(`/api/content?path=${{encodeURIComponent(path)}}`);
            const data = await res.json();
            document.getElementById('previewTitle').textContent = data.name;
            document.getElementById('previewContent').innerHTML = data.content;
        }}

        async function passContinue() {{
            if (!confirm('确认通过,继续下一阶段?')) return;
            await fetch('/api/decision', {{
                method: 'POST',
                headers: {{'Content-Type': 'application/json'}},
                body: JSON.stringify({{decision: 'pass'}})
            }});
            document.body.innerHTML = '<div style="text-align:center;padding:100px;font-size:24px;color:#10b981;">✓ 已通过,脚本继续中...</div>';
        }}

        function showFeedbackModal() {{
            document.getElementById('feedbackModal').classList.add('show');
        }}

        function closeFeedbackModal() {{
            document.getElementById('feedbackModal').classList.remove('show');
        }}

        async function submitFeedback() {{
            const text = document.getElementById('feedbackText').value.trim();
            if (!text) {{
                alert('请填写返修原因');
                return;
            }}
            await fetch('/api/decision', {{
                method: 'POST',
                headers: {{'Content-Type': 'application/json'}},
                body: JSON.stringify({{decision: 'fail', feedback: text}})
            }});
            document.body.innerHTML = '<div style="text-align:center;padding:100px;font-size:24px;color:#ef4444;">✗ 已标记返修,脚本已停止</div>';
        }}

        loadArtifacts();
    </script>
</body>
</html>"""

def list_artifacts():
    """扫描产物目录,返回文件列表"""
    artifacts_path = Path(ARTIFACTS_DIR)
    if not artifacts_path.exists():
        return []

    files = []
    for ext in ['*.md', '*.py', '*.ipynb', '*.json', '*.txt']:
        for f in artifacts_path.rglob(ext):
            if '.git' in f.parts or '__pycache__' in f.parts:
                continue
            rel = f.relative_to(artifacts_path)
            files.append({'name': str(rel), 'path': str(rel)})

    return sorted(files, key=lambda x: x['name'])

def main():
    global STAGE, LECTURE, CONTROL_FILE, ARTIFACTS_DIR

    ap = argparse.ArgumentParser()
    ap.add_argument('--stage', required=True)
    ap.add_argument('--lecture', required=True)
    ap.add_argument('--port', type=int, default=9120)
    ap.add_argument('--artifacts-dir', required=True, help='产物目录路径')
    ap.add_argument('--control-file', required=True, help='控制文件路径(写 CONTINUE/FEEDBACK)')
    args = ap.parse_args()

    STAGE = args.stage
    LECTURE = args.lecture
    CONTROL_FILE = args.control_file
    ARTIFACTS_DIR = args.artifacts_dir

    print(f"Debug UI 启动: http://0.0.0.0:{args.port}")
    print(f"产物目录: {ARTIFACTS_DIR}")
    print(f"控制文件: {CONTROL_FILE}")

    server = HTTPServer(('0.0.0.0', args.port), DebugUIHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nUI 停止")

if __name__ == '__main__':
    main()
