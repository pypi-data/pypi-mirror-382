"""
Terminal MCP Server - 精简版
单文件包含所有 MCP 功能，无需 Web 服务器依赖
"""

import asyncio
import json
import os
import platform
import subprocess
import sys
import threading
import time
import webbrowser
from collections import deque
from typing import Dict, List, Optional, Tuple
import psutil
from mcp.server import Server
from mcp.types import Tool, TextContent
import mcp.server.stdio

# 简单的 Web 服务器
try:
    from http.server import HTTPServer, SimpleHTTPRequestHandler
    import urllib.parse
    HAS_HTTP = True
except ImportError:
    HAS_HTTP = False


# ============================================================================
# 终端会话类
# ============================================================================

def detect_shell():
    """检测系统最佳终端"""
    system = platform.system()
    
    if system == "Windows":
        # Windows: Git Bash > PowerShell > cmd
        git_bash_paths = [
            r"C:\Program Files\Git\bin\bash.exe",
            r"C:\Program Files (x86)\Git\bin\bash.exe",
        ]
        for path in git_bash_paths:
            if os.path.exists(path):
                return path
        
        # PowerShell
        pwsh_paths = [
            r"C:\Program Files\PowerShell\7\pwsh.exe",
            r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe",
        ]
        for path in pwsh_paths:
            if os.path.exists(path):
                return path
        
        # 默认 cmd
        return "cmd.exe"
    else:
        # Linux/Mac: 使用默认 shell
        return os.environ.get("SHELL", "/bin/bash")


class TerminalSession:
    """单个终端会话"""
    
    def __init__(self, session_id: str, name: str, max_output_lines: int = 10000):
        self.session_id = session_id
        self.name = name
        self.created_at = time.time()
        self.last_activity = time.time()
        self.last_output = time.time()
        self.current_command = None
        self.output_buffer = deque(maxlen=max_output_lines)
        self.is_running = False
        self.process = None
        self.lock = threading.Lock()
        self.is_windows = platform.system() == "Windows"
        self.shell_type = detect_shell()
        
    def start(self):
        """启动终端进程"""
        shell_cmd = self.shell_type
        
        # 设置环境变量强制 UTF-8
        env = os.environ.copy()
        if self.is_windows:
            env['PYTHONIOENCODING'] = 'utf-8'
            env['LANG'] = 'en_US.UTF-8'
        
        if self.is_windows:
            if "bash.exe" in shell_cmd:
                # Git Bash
                self.process = subprocess.Popen(
                    [shell_cmd, "--login", "-i"],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    encoding='utf-8',
                    errors='replace',  # 替换无法解码的字符
                    bufsize=1,
                    env=env,
                    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
                )
            elif "powershell" in shell_cmd.lower() or "pwsh" in shell_cmd.lower():
                # PowerShell - 设置 UTF-8
                self.process = subprocess.Popen(
                    [shell_cmd, "-NoLogo", "-NoExit", "-Command", "[Console]::OutputEncoding=[System.Text.Encoding]::UTF8"],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    encoding='utf-8',
                    errors='replace',
                    bufsize=1,
                    env=env,
                    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
                )
            else:
                # cmd - 设置代码页 65001 (UTF-8)
                self.process = subprocess.Popen(
                    [shell_cmd, "/K", "chcp 65001 >nul"],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    encoding='utf-8',
                    errors='replace',
                    bufsize=1,
                    env=env,
                    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
                )
        else:
            # Linux/Mac
            env['LANG'] = 'en_US.UTF-8'
            env['LC_ALL'] = 'en_US.UTF-8'
            self.process = subprocess.Popen(
                [shell_cmd],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding='utf-8',
                errors='replace',
                bufsize=1,
                env=env
            )
        
        self.is_running = True
        threading.Thread(target=self._read_output, daemon=True).start()
        
    def _read_output(self):
        """持续读取进程输出"""
        try:
            while self.is_running and self.process:
                line = self.process.stdout.readline()
                if not line:
                    break
                    
                with self.lock:
                    self.output_buffer.append({
                        "timestamp": time.time(),
                        "content": line.rstrip('\n\r')
                    })
                    self.last_output = time.time()
                    self.last_activity = time.time()
        except:
            pass
        finally:
            self.is_running = False
            
    def execute(self, command: str) -> bool:
        """执行命令"""
        if not self.process or not self.is_running:
            return False
            
        try:
            with self.lock:
                self.current_command = command
                self.last_activity = time.time()
                
            self.process.stdin.write(command + "\n")
            self.process.stdin.flush()
            return True
        except:
            return False
            
    def get_output(self, lines: int = 100) -> List[Dict]:
        """获取最近的输出"""
        with self.lock:
            return list(self.output_buffer)[-lines:]
            
    def get_status(self) -> Dict:
        """获取会话状态"""
        is_idle = time.time() - self.last_activity > 60
        
        process_status = "stopped"
        if self.process and self.is_running:
            try:
                proc = psutil.Process(self.process.pid)
                cpu_percent = proc.cpu_percent(interval=0.1)
                process_status = "running" if cpu_percent > 1 else "idle"
            except:
                process_status = "stopped"
                
        return {
            "session_id": self.session_id,
            "name": self.name,
            "status": process_status,
            "is_idle": is_idle,
            "current_command": self.current_command,
            "created_at": self.created_at,
            "last_activity": self.last_activity,
            "last_output": self.last_output,
            "uptime": time.time() - self.created_at,
            "output_lines": len(self.output_buffer)
        }
        
    def kill(self):
        """终止会话"""
        self.is_running = False
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=3)
            except:
                self.process.kill()
            finally:
                self.process = None


# ============================================================================
# 会话管理器
# ============================================================================

class SessionManager:
    """终端会话管理器"""
    
    def __init__(self, config: dict):
        self.max_sessions = config.get("max_sessions", 64)
        self.idle_timeout = config.get("idle_timeout", 300)
        self.auto_cleanup_interval = config.get("auto_cleanup_interval", 60)
        self.max_output_lines = config.get("max_output_lines", 10000)
        self.web_port = config.get("web_port", 18888)
        self.auto_open_browser = config.get("auto_open_browser", True)
        
        self.sessions: Dict[str, TerminalSession] = {}
        self.session_counter = 0
        self.lock = threading.Lock()
        self.web_server_started = False
        
        # 启动自动清理线程
        threading.Thread(target=self._auto_cleanup, daemon=True).start()
        
        # 启动 Web 服务器
        if HAS_HTTP and not self.web_server_started:
            threading.Thread(target=self._start_web_server, daemon=True).start()
            self.web_server_started = True
        
    def _auto_cleanup(self):
        """自动清理空闲会话"""
        while True:
            time.sleep(self.auto_cleanup_interval)
            self.cleanup_idle_sessions(self.idle_timeout)
    
    def get_system_info(self):
        """获取系统信息"""
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            
            # 尝试获取 GPU 信息（如果可用）
            gpu_info = "N/A"
            try:
                import subprocess
                if platform.system() == "Windows":
                    result = subprocess.run(
                        ['wmic', 'path', 'win32_VideoController', 'get', 'name'],
                        capture_output=True, text=True, timeout=1
                    )
                    if result.returncode == 0:
                        lines = result.stdout.strip().split('\n')
                        if len(lines) > 1:
                            gpu_info = lines[1].strip()
            except:
                pass
            
            return {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_used_gb": memory.used / (1024**3),
                "memory_total_gb": memory.total / (1024**3),
                "gpu_info": gpu_info
            }
        except:
            return {
                "cpu_percent": 0,
                "memory_percent": 0,
                "memory_used_gb": 0,
                "memory_total_gb": 0,
                "gpu_info": "N/A"
            }
    
    def get_language(self):
        """默认英文，用户可切换"""
        return 'en'
    
    def _start_web_server(self):
        """启动简单的 Web 服务器"""
        try:
            manager_ref = self
            
            class RequestHandler(SimpleHTTPRequestHandler):
                def do_GET(self):
                    if self.path == '/' or self.path.startswith('/?lang='):
                        self.send_response(200)
                        self.send_header('Content-type', 'text/html; charset=utf-8')
                        self.end_headers()
                        html = self.get_index_html()
                        self.wfile.write(html.encode('utf-8'))
                    elif self.path.startswith('/api/system'):
                        self.send_response(200)
                        self.send_header('Content-type', 'application/json')
                        self.end_headers()
                        sys_info = manager_ref.get_system_info()
                        self.wfile.write(json.dumps(sys_info).encode())
                    elif self.path.startswith('/api/sessions'):
                        self.send_response(200)
                        self.send_header('Content-type', 'application/json')
                        self.end_headers()
                        sessions = manager_ref.get_all_sessions()
                        stats = manager_ref.get_stats()
                        sys_info = manager_ref.get_system_info()
                        data = {"sessions": sessions, "stats": stats, "system": sys_info}
                        self.wfile.write(json.dumps(data).encode())
                    elif self.path.startswith('/api/output/'):
                        session_id = self.path.split('/')[-1]
                        self.send_response(200)
                        self.send_header('Content-type', 'application/json')
                        self.end_headers()
                        output = manager_ref.get_output(session_id, 1000) or []
                        self.wfile.write(json.dumps({"output": output}).encode())
                    else:
                        self.send_error(404)
                
                def do_POST(self):
                    content_length = int(self.headers['Content-Length'])
                    body = self.rfile.read(content_length)
                    data = json.loads(body.decode())
                    
                    success, msg = manager_ref.execute_command(data['session_id'], data['command'])
                    
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({"success": success, "message": msg}).encode())
                
                def do_DELETE(self):
                    content_length = int(self.headers.get('Content-Length', 0))
                    if content_length > 0:
                        body = self.rfile.read(content_length)
                        data = json.loads(body.decode())
                        
                        # 检查是否是关闭服务器请求
                        if data.get('shutdown'):
                            success, msg = True, "服务器即将关闭"
                            self.send_response(200)
                            self.send_header('Content-type', 'application/json')
                            self.end_headers()
                            self.wfile.write(json.dumps({"success": success, "message": msg}).encode())
                            # 关闭服务器
                            manager_ref.shutdown()
                        else:
                            success, msg = manager_ref.kill_session(data['session_id'])
                            self.send_response(200)
                            self.send_header('Content-type', 'application/json')
                            self.end_headers()
                            self.wfile.write(json.dumps({"success": success, "message": msg}).encode())
                    else:
                        success, msg = False, "No data provided"
                        self.send_response(400)
                        self.send_header('Content-type', 'application/json')
                        self.end_headers()
                        self.wfile.write(json.dumps({"success": success, "message": msg}).encode())
                
                def get_index_html(self):
                    try:
                        # 检测语言
                        lang = manager_ref.get_language()
                        if '?lang=zh' in self.path:
                            lang = 'zh'
                        elif '?lang=en' in self.path:
                            lang = 'en'
                        
                        # 多语言文本
                        texts = {
                            'en': {
                            'title': 'Terminal MCP Manager',
                            'cpu': 'CPU',
                            'memory': 'Memory',
                            'total': 'Total',
                            'running': 'Running',
                            'terminals': 'Running Terminals',
                            'overview': 'Overview',
                            'clear': 'Clear',
                            'terminate': 'Terminate',
                            'shutdown': 'Shutdown Server',
                            'shutdown_confirm': '⚠️ Are you sure to shutdown the server?\\nThis will terminate all sessions.',
                            'server_closed': 'Server Closed',
                            'resources_released': 'All sessions terminated, resources released',
                            'close_window': 'You can close this window',
                            'select_terminal': 'Click a terminal on the left to view details',
                            'no_sessions': 'No sessions',
                            'enter_command': 'Enter command after selecting a terminal...',
                            'send': 'Send',
                            'terminal_prefix': 'Terminal: ',
                            'confirm_terminate': 'Are you sure to terminate this session?',
                            'session_terminated': 'Session Terminated',
                            'switch_lang': '中文',
                            'minutes': 'm',
                            'lines': ' lines'
                            },
                            'zh': {
                            'title': '终端管理器',
                            'cpu': 'CPU',
                            'memory': '内存',
                            'total': '总会话',
                            'running': '运行中',
                            'terminals': '运行中的终端',
                            'overview': '总览',
                            'clear': '清空',
                            'terminate': '终止',
                            'shutdown': '关闭服务器',
                            'shutdown_confirm': '⚠️ 确定要关闭服务器吗？\\n这将终止所有会话。',
                            'server_closed': '服务器已关闭',
                            'resources_released': '所有会话已终止，资源已释放',
                            'close_window': '可以关闭此窗口',
                            'select_terminal': '点击左侧终端查看详情',
                            'no_sessions': '暂无会话',
                            'enter_command': '选择终端后输入命令...',
                            'send': '发送',
                            'terminal_prefix': '终端: ',
                            'confirm_terminate': '确定终止会话？',
                            'session_terminated': '会话已终止',
                            'switch_lang': 'English',
                            'minutes': '分钟',
                            'lines': ' 行'
                            }
                        }
                        t = texts[lang]
                        next_lang = 'en' if lang == 'zh' else 'zh'
                        
                        # 提取所有文本变量
                        title = t['title']
                        cpu = t['cpu']
                        memory = t['memory']
                        total = t['total']
                        running = t['running']
                        terminals = t['terminals']
                        overview = t['overview']
                        clear_btn = t['clear']
                        terminate = t['terminate']
                        shutdown = t['shutdown']
                        shutdown_confirm = t['shutdown_confirm']
                        server_closed = t['server_closed']
                        resources_released = t['resources_released']
                        close_window = t['close_window']
                        select_terminal = t['select_terminal']
                        no_sessions = t['no_sessions']
                        enter_command = t['enter_command']
                        send = t['send']
                        terminal_prefix = t['terminal_prefix']
                        confirm_terminate = t['confirm_terminate']
                        session_terminated = t['session_terminated']
                        switch_lang = t['switch_lang']
                        minutes = t['minutes']
                        lines = t['lines']
                        
                        # 使用 format() 而不是 f-string 避免 JavaScript {{}} 冲突
                        html = """<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/xterm@5.3.0/css/xterm.css"/>
<script src="https://cdn.jsdelivr.net/npm/xterm@5.3.0/lib/xterm.js"></script>
<script src="https://cdn.jsdelivr.net/npm/xterm-addon-fit@0.8.0/lib/xterm-addon-fit.js"></script>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:'Segoe UI',sans-serif;background:#0a0a0a;color:#fff;overflow:hidden;height:100vh}}
.container{{display:flex;flex-direction:column;height:100vh}}
.header{{background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);padding:15px 20px;box-shadow:0 2px 10px rgba(0,0,0,0.5)}}
.header h1{{font-size:1.5em;margin-bottom:10px}}
.system-stats{{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:15px;margin-top:10px}}
.stat-card{{background:rgba(255,255,255,0.1);padding:12px;border-radius:6px;text-align:center}}
.stat-value{{font-size:1.8em;font-weight:bold;margin-bottom:5px}}
.stat-label{{font-size:0.85em;opacity:0.9}}
.main{{flex:1;display:flex;overflow:hidden}}
.sidebar{{width:280px;background:#1a1a1a;border-right:1px solid#333;display:flex;flex-direction:column}}
.sidebar-header{{padding:15px;background:#252525;border-bottom:1px solid#333;font-weight:bold}}
.sessions-list{{flex:1;overflow-y:auto;padding:10px}}
.session-item{{background:#252525;padding:12px;margin-bottom:8px;border-radius:6px;cursor:pointer;transition:all 0.2s;border-left:3px solid transparent}}
.session-item:hover{{background:#2d2d2d}}
.session-item.active{{border-left-color:#667eea;background:#2d2d2d}}
.session-name{{font-weight:bold;margin-bottom:5px}}
.session-info{{font-size:0.85em;color:#999}}
.status{{display:inline-block;width:8px;height:8px;border-radius:50%;margin-right:5px}}
.status-running{{background:#4caf50}}
.status-idle{{background:#ff9800}}
.status-stopped{{background:#f44336}}
.terminal-area{{flex:1;display:flex;flex-direction:column;background:#0a0a0a}}
.terminal-header{{background:#1a1a1a;padding:12px 20px;border-bottom:1px solid#333;display:flex;justify-content:space-between;align-items:center}}
.terminal-title{{font-weight:bold;font-size:1.1em}}
.terminal-controls button{{background:#555;color:#fff;border:none;padding:6px 15px;margin-left:8px;border-radius:4px;cursor:pointer}}
.terminal-controls button:hover{{background:#666}}
.terminal-container{{flex:1;position:relative}}
#terminal{{position:absolute;top:0;left:0;right:0;bottom:0;padding:10px}}
.placeholder{{display:flex;flex-direction:column;align-items:center;justify-content:center;height:100%;color:#555}}
.placeholder-icon{{font-size:5em;margin-bottom:20px}}
.input-area{{background:#1a1a1a;padding:12px 20px;border-top:1px solid#333;display:flex;gap:10px}}
#cmdInput{{flex:1;background:#0a0a0a;border:1px solid#333;border-radius:4px;padding:8px 12px;color:#fff;font-family:monospace}}
#cmdInput:focus{{outline:none;border-color:#667eea}}
.btn-send{{background:#4caf50;color:#fff;border:none;padding:8px 20px;border-radius:4px;cursor:pointer;font-weight:bold}}
.btn-send:hover{{background:#45a049}}
.btn-send:disabled{{background:#333;cursor:not-allowed}}
::-webkit-scrollbar{{width:8px}}
::-webkit-scrollbar-track{{background:#0a0a0a}}
::-webkit-scrollbar-thumb{{background:#333;border-radius:4px}}
::-webkit-scrollbar-thumb:hover{{background:#444}}
</style>
</head>
<body>
<div class="container">
<div class="header">
<div style="display:flex;justify-content:space-between;align-items:center">
<h1>🖥️ {title}</h1>
<div style="display:flex;gap:10px">
<button onclick="switchLang()" style="background:#667eea;color:#fff;border:none;padding:10px 16px;border-radius:6px;cursor:pointer;font-weight:bold">
🌐 {switch_lang}
</button>
<button onclick="shutdownServer()" style="background:#f44336;color:#fff;border:none;padding:10px 20px;border-radius:6px;cursor:pointer;font-weight:bold">
🛑 {shutdown}
</button>
</div>
</div>
<div class="system-stats">
<div class="stat-card"><div class="stat-value" id="cpu">-</div><div class="stat-label">{cpu}</div></div>
<div class="stat-card"><div class="stat-value" id="mem">-</div><div class="stat-label">{memory}</div></div>
<div class="stat-card"><div class="stat-value" id="total">0</div><div class="stat-label">{total}</div></div>
<div class="stat-card"><div class="stat-value" id="running">0</div><div class="stat-label">{running}</div></div>
</div>
</div>
<div class="main">
<div class="sidebar">
<div class="sidebar-header">{terminals}</div>
<div class="sessions-list" id="sessions"></div>
</div>
<div class="terminal-area">
<div class="terminal-header">
<div class="terminal-title" id="title">{overview}</div>
<div class="terminal-controls">
<button onclick="clearTerm()" id="btnClear" disabled>{clear_btn}</button>
<button onclick="killSess()" id="btnKill" disabled style="background:#f44336">{terminate}</button>
</div>
</div>
<div class="terminal-container" id="termContainer">
<div class="placeholder">
<div class="placeholder-icon">🖥️</div>
<h2>{title}</h2>
<p style="margin-top:10px">{select_terminal}</p>
</div>
</div>
<div class="input-area">
<input type="text" id="cmdInput" placeholder="{enter_command}" disabled onkeypress="if(event.key==='Enter')sendCmd()">
<button class="btn-send" id="btnSend" onclick="sendCmd()" disabled>{send}</button>
</div>
</div>
</div>
</div>
<script>
let currentSid=null,term=null,fitAddon=null,pollTimer=null;
async function load(){{
try{{
const r=await fetch('/api/sessions');
const d=await r.json();
document.getElementById('cpu').textContent=d.system.cpu_percent.toFixed(1)+'%';
document.getElementById('mem').textContent=d.system.memory_percent.toFixed(1)+'%';
document.getElementById('total').textContent=d.stats.total_sessions;
document.getElementById('running').textContent=d.stats.running_sessions;
const sessionsList=document.getElementById('sessions');
if(!d.sessions.length){{
sessionsList.innerHTML='<div style="text-align:center;padding:40px;color:#555"><div style="font-size:3em">📭</div><p>{no_sessions}</p></div>';
return;
}}
sessionsList.innerHTML=d.sessions.map(s=>{{
const uptime=Math.floor(s.uptime/60);
return`<div class="session-item ${{currentSid===s.session_id?'active':''}}\" onclick="selectSess('${{s.session_id}}')">
<div class="session-name"><span class="status status-${{s.status}}"></span>${{s.name}}</div>
<div class="session-info">${{uptime}}{minutes} | ${{s.output_lines}}{lines}</div>
</div>`;
}}).join('');
}}catch(e){{console.error(e)}}
}}
async function selectSess(sid){{
currentSid=sid;
if(!term){{
term=new Terminal({{cursorBlink:true,fontSize:14,theme:{{background:'#0a0a0a',foreground:'#00ff00'}}}});
fitAddon=new FitAddon.FitAddon();
term.loadAddon(fitAddon);
}}
const c=document.getElementById('termContainer');
c.innerHTML='<div id="terminal" style="width:100%;height:100%"></div>';
term.open(document.getElementById('terminal'));
fitAddon.fit();
window.addEventListener('resize',()=>fitAddon.fit());
const r=await fetch('/api/output/'+sid);
const d=await r.json();
term.clear();
d.output.forEach(l=>term.writeln(l.content));
document.getElementById('title').textContent='{terminal_prefix}'+sid;
document.getElementById('btnClear').disabled=false;
document.getElementById('btnKill').disabled=false;
document.getElementById('cmdInput').disabled=false;
document.getElementById('btnSend').disabled=false;
load();
if(pollTimer)clearInterval(pollTimer);
pollTimer=setInterval(async()=>{{
const r=await fetch('/api/output/'+currentSid);
const d=await r.json();
const oldLen=term.buffer.active.length;
if(d.output.length>oldLen){{
d.output.slice(oldLen).forEach(l=>term.writeln(l.content));
}}
}},1000);
}}
async function sendCmd(){{
if(!currentSid)return;
const input=document.getElementById('cmdInput');
const cmd=input.value.trim();
if(!cmd)return;
term.writeln('\\x1b[36m$ '+cmd+'\\x1b[0m');
await fetch('/api/sessions',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{session_id:currentSid,command:cmd}})}});
input.value='';
}}
function clearTerm(){{if(term)term.clear()}}
async function killSess(){{
if(!currentSid||!confirm('{confirm_terminate}'))return;
await fetch('/api/sessions',{{method:'DELETE',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{session_id:currentSid}})}});
currentSid=null;
document.getElementById('termContainer').innerHTML='<div class="placeholder"><div class="placeholder-icon">✓</div><h2>{session_terminated}</h2></div>';
load();
}}
async function shutdownServer(){{
if(!confirm('{shutdown_confirm}'))return;
try{{
await fetch('/api/sessions',{{method:'DELETE',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{shutdown:true}})}});
document.body.innerHTML='<div style="display:flex;align-items:center;justify-content:center;height:100vh;flex-direction:column;background:#0a0a0a;color:#fff"><div style="font-size:5em;margin-bottom:20px">✓</div><h1>{server_closed}</h1><p style="color:#888;margin-top:10px">{resources_released}</p><p style="color:#666;margin-top:20px">{close_window}</p></div>';
}}catch(e){{alert(e)}}
}}
function switchLang(){{
window.location.href='/?lang={next_lang}';
}}
setInterval(load,2000);
load();
</script>
</body></html>""".format(
    lang=lang,
    title=title,
    cpu=cpu,
    memory=memory,
    total=total,
    running=running,
    terminals=terminals,
    overview=overview,
    clear_btn=clear_btn,
    terminate=terminate,
    shutdown=shutdown,
    switch_lang=switch_lang,
    select_terminal=select_terminal,
    enter_command=enter_command,
    send=send,
    no_sessions=no_sessions,
    minutes=minutes,
    lines=lines,
    terminal_prefix=terminal_prefix,
    confirm_terminate=confirm_terminate,
    session_terminated=session_terminated,
    shutdown_confirm=shutdown_confirm,
    server_closed=server_closed,
    resources_released=resources_released,
    close_window=close_window,
    next_lang=next_lang
)
                        return html
                    except Exception as e:
                        # 如果生成失败，返回简单错误页面
                        return f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>Error</title></head>
<body><h1>Error generating page</h1><p>{str(e)}</p></body></html>"""
                
                def log_message(self, format, *args):
                    pass
            
            server = HTTPServer(('localhost', self.web_port), RequestHandler)
            print(f"✅ Web 服务器已启动: http://localhost:{self.web_port}", file=sys.stderr)
            server.serve_forever()
        except Exception as e:
            print(f"⚠️ Web 服务器启动失败: {e}", file=sys.stderr)
            
    def create_session(self, name: Optional[str] = None) -> Tuple[bool, str, str]:
        """创建新会话"""
        with self.lock:
            if len(self.sessions) >= self.max_sessions:
                return False, "", f"已达到最大会话数限制 ({self.max_sessions})"
                
            self.session_counter += 1
            session_id = f"session_{self.session_counter}"
            session_name = name or f"terminal_{self.session_counter}"
            
            try:
                session = TerminalSession(session_id, session_name, self.max_output_lines)
                session.start()
                self.sessions[session_id] = session
                
                # 自动打开浏览器（仅第一次）
                if self.auto_open_browser and self.session_counter == 1 and HAS_HTTP:
                    web_url = f"http://localhost:{self.web_port}"
                    threading.Thread(target=lambda: webbrowser.open(web_url), daemon=True).start()
                    time.sleep(0.5)  # 给浏览器启动时间
                
                return True, session_id, f"会话创建成功: {session_name}"
            except Exception as e:
                return False, "", f"创建会话失败: {str(e)}"
                
    def execute_command(self, session_id: str, command: str) -> Tuple[bool, str]:
        """在指定会话中执行命令"""
        with self.lock:
            if session_id not in self.sessions:
                return False, f"会话不存在: {session_id}"
            session = self.sessions[session_id]
            
        success = session.execute(command)
        return (True, f"命令已发送到 {session.name}") if success else (False, "命令执行失败")
            
    def broadcast_command(self, command: str, session_ids: Optional[List[str]] = None) -> Dict[str, bool]:
        """向多个会话并发执行命令"""
        results = {}
        
        with self.lock:
            target_sessions = session_ids if session_ids else list(self.sessions.keys())
            
        def execute_single(sid):
            success, _ = self.execute_command(sid, command)
            results[sid] = success
            
        threads = [threading.Thread(target=execute_single, args=(sid,)) for sid in target_sessions]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
            
        return results
        
    def get_session_status(self, session_id: str) -> Optional[Dict]:
        """获取会话状态"""
        with self.lock:
            if session_id not in self.sessions:
                return None
            return self.sessions[session_id].get_status()
        
    def get_all_sessions(self) -> List[Dict]:
        """获取所有会话状态"""
        with self.lock:
            return [s.get_status() for s in self.sessions.values()]
        
    def get_output(self, session_id: str, lines: int = 100) -> Optional[List[Dict]]:
        """获取会话输出"""
        with self.lock:
            if session_id not in self.sessions:
                return None
            return self.sessions[session_id].get_output(lines)
        
    def kill_session(self, session_id: str) -> Tuple[bool, str]:
        """终止会话"""
        with self.lock:
            if session_id not in self.sessions:
                return False, f"会话不存在: {session_id}"
            session = self.sessions[session_id]
            session.kill()
            del self.sessions[session_id]
        return True, f"会话已终止: {session.name}"
        
    def cleanup_idle_sessions(self, idle_timeout: Optional[int] = None) -> List[str]:
        """清理空闲会话"""
        timeout = idle_timeout or self.idle_timeout
        cleaned = []
        
        with self.lock:
            current_time = time.time()
            to_remove = [
                sid for sid, session in self.sessions.items()
                if current_time - session.last_activity > timeout and session.current_command is None
            ]
            
            for session_id in to_remove:
                self.sessions[session_id].kill()
                del self.sessions[session_id]
                cleaned.append(session_id)
                
        return cleaned
        
    def get_stats(self) -> Dict:
        """获取统计信息"""
        with self.lock:
            total = len(self.sessions)
            running = sum(1 for s in self.sessions.values() if s.is_running)
            
        return {
            "total_sessions": total,
            "running_sessions": running,
            "max_sessions": self.max_sessions,
            "usage_percent": (total / self.max_sessions) * 100
        }
    
    def shutdown(self):
        """关闭所有会话并退出"""
        with self.lock:
            session_ids = list(self.sessions.keys())
        
        for session_id in session_ids:
            self.kill_session(session_id)
        
        print("🛑 所有会话已终止，服务器即将关闭...", file=sys.stderr)
        # 延迟退出，让响应返回
        threading.Timer(1.0, lambda: os._exit(0)).start()


# ============================================================================
# MCP 服务器
# ============================================================================

class TerminalMCPServer:
    """Terminal MCP 服务器"""
    
    def __init__(self, config_path: str = "config.json"):
        self.app = Server("terminal-manager")
        
        # 加载配置
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
        else:
            config = {"max_sessions": 64, "idle_timeout": 300}
            
        self.session_manager = SessionManager(config)
        self._register_tools()
        
    def _register_tools(self):
        """注册 MCP 工具"""
        
        @self.app.list_tools()
        async def list_tools() -> list[Tool]:
            return [
                Tool(
                    name="create_session",
                    description="创建新的终端会话。最多支持 64 个并发会话。",
                    inputSchema={
                        "type": "object",
                        "properties": {"name": {"type": "string", "description": "会话名称（可选）"}}
                    }
                ),
                Tool(
                    name="execute_command",
                    description="在指定的终端会话中执行命令。命令会在后台异步执行。",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "session_id": {"type": "string", "description": "会话 ID"},
                            "command": {"type": "string", "description": "要执行的命令"}
                        },
                        "required": ["session_id", "command"]
                    }
                ),
                Tool(
                    name="broadcast_command",
                    description="向多个终端会话并发执行相同的命令。",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "command": {"type": "string", "description": "要执行的命令"},
                            "session_ids": {"type": "array", "items": {"type": "string"}, "description": "会话 ID 列表（可选）"}
                        },
                        "required": ["command"]
                    }
                ),
                Tool(
                    name="get_session_status",
                    description="获取指定会话的详细状态信息。",
                    inputSchema={
                        "type": "object",
                        "properties": {"session_id": {"type": "string"}},
                        "required": ["session_id"]
                    }
                ),
                Tool(
                    name="get_all_sessions",
                    description="列出所有终端会话的状态信息。",
                    inputSchema={"type": "object", "properties": {}}
                ),
                Tool(
                    name="get_output",
                    description="获取会话的输出内容。",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "session_id": {"type": "string"},
                            "lines": {"type": "number", "description": "返回的行数，默认 100"}
                        },
                        "required": ["session_id"]
                    }
                ),
                Tool(
                    name="kill_session",
                    description="强制终止指定的会话。",
                    inputSchema={
                        "type": "object",
                        "properties": {"session_id": {"type": "string"}},
                        "required": ["session_id"]
                    }
                ),
                Tool(
                    name="cleanup_idle_sessions",
                    description="清理空闲超时的会话。",
                    inputSchema={
                        "type": "object",
                        "properties": {"idle_timeout": {"type": "number", "description": "超时时间（秒）"}}
                    }
                ),
                Tool(
                    name="get_stats",
                    description="获取终端管理器的统计信息。",
                    inputSchema={"type": "object", "properties": {}}
                ),
            ]
            
        @self.app.call_tool()
        async def call_tool(name: str, arguments: dict) -> list[TextContent]:
            """处理工具调用"""
            try:
                if name == "create_session":
                    success, sid, msg = self.session_manager.create_session(arguments.get("name"))
                    web_url = f"http://localhost:{self.session_manager.web_port}"
                    return [TextContent(type="text", text=json.dumps({
                        "success": success,
                        "session_id": sid,
                        "message": msg,
                        "web_url": web_url,
                        "tip": f"💡 打开浏览器访问 {web_url} 查看实时输出"
                    }, ensure_ascii=False, indent=2))]
                    
                elif name == "execute_command":
                    success, msg = self.session_manager.execute_command(
                        arguments["session_id"], arguments["command"]
                    )
                    return [TextContent(type="text", text=json.dumps({
                        "success": success, "message": msg
                    }, ensure_ascii=False, indent=2))]
                    
                elif name == "broadcast_command":
                    results = self.session_manager.broadcast_command(
                        arguments["command"], arguments.get("session_ids")
                    )
                    return [TextContent(type="text", text=json.dumps({
                        "total": len(results),
                        "successful": sum(1 for v in results.values() if v),
                        "results": results
                    }, ensure_ascii=False, indent=2))]
                    
                elif name == "get_session_status":
                    status = self.session_manager.get_session_status(arguments["session_id"])
                    return [TextContent(type="text", text=json.dumps(
                        status or {"error": "会话不存在"}, ensure_ascii=False, indent=2
                    ))]
                    
                elif name == "get_all_sessions":
                    sessions = self.session_manager.get_all_sessions()
                    stats = self.session_manager.get_stats()
                    return [TextContent(type="text", text=json.dumps({
                        "stats": stats, "sessions": sessions
                    }, ensure_ascii=False, indent=2))]
                    
                elif name == "get_output":
                    output = self.session_manager.get_output(
                        arguments["session_id"], arguments.get("lines", 100)
                    )
                    return [TextContent(type="text", text=json.dumps({
                        "output": output or []
                    }, ensure_ascii=False, indent=2))]
                    
                elif name == "kill_session":
                    success, msg = self.session_manager.kill_session(arguments["session_id"])
                    return [TextContent(type="text", text=json.dumps({
                        "success": success, "message": msg
                    }, ensure_ascii=False, indent=2))]
                    
                elif name == "cleanup_idle_sessions":
                    cleaned = self.session_manager.cleanup_idle_sessions(
                        arguments.get("idle_timeout")
                    )
                    return [TextContent(type="text", text=json.dumps({
                        "cleaned_count": len(cleaned), "cleaned_sessions": cleaned
                    }, ensure_ascii=False, indent=2))]
                    
                elif name == "get_stats":
                    stats = self.session_manager.get_stats()
                    return [TextContent(type="text", text=json.dumps(
                        stats, ensure_ascii=False, indent=2
                    ))]
                    
            except Exception as e:
                return [TextContent(type="text", text=json.dumps({
                    "error": str(e)
                }, ensure_ascii=False))]
    
    async def run(self):
        """启动 MCP 服务器"""
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await self.app.run(read_stream, write_stream, self.app.create_initialization_options())


async def async_main():
    """异步主函数"""
    # 尝试在当前目录或用户目录查找配置文件
    config_paths = [
        "config.json",
        os.path.join(os.path.expanduser("~"), ".terminal-mcp", "config.json"),
        os.path.join(os.path.dirname(__file__), "config.json"),
    ]
    
    config_path = None
    for path in config_paths:
        if os.path.exists(path):
            config_path = path
            break
    
    server = TerminalMCPServer(config_path or "config.json")
    await server.run()


def main():
    """命令行入口点"""
    asyncio.run(async_main())


if __name__ == "__main__":
    main()

