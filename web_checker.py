#!/usr/bin/env python3
"""
图片自动审核工具 - Web 版本 (弹窗交互)
"""
import os, io, base64
from flask import Flask, request, render_template_string
from PIL import Image

app = Flask(__name__)

HTML = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>www.autocheckimg.dyy.com - 图片自动审核</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;background:#f5f5f7;color:#1d1d1f;min-height:100vh;display:flex;flex-direction:column;align-items:center}
.container{max-width:720px;width:100%;padding:40px 24px}
h1{font-size:28px;font-weight:700;margin-bottom:8px}
.subtitle{color:#6e6e73;font-size:14px;margin-bottom:32px}
.card{background:#fff;border-radius:12px;padding:28px;margin-bottom:20px;box-shadow:0 1px 3px rgba(0,0,0,.08)}
.instruction-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin-bottom:16px}
.instruction-btn{border:2px solid #e8e8ed;border-radius:10px;padding:12px 8px;background:#fff;cursor:pointer;text-align:center;transition:all .15s;font-size:13px;-webkit-user-select:none;user-select:none}
.instruction-btn:hover{border-color:#0071e3}
.instruction-btn.active{border-color:#0071e3;background:#e8f0fe;font-weight:600}
.instruction-btn .name{font-size:15px;font-weight:600}
.instruction-btn .size{color:#6e6e73;font-size:12px;margin-top:2px}
.upload-zone{border:2px dashed #c7c7cc;border-radius:10px;padding:40px 20px;text-align:center;cursor:pointer;transition:all .15s;margin-bottom:4px}
.upload-zone:hover,.upload-zone.dragover{border-color:#0071e3;background:#e8f0fe}
.upload-zone.has-image{border-style:solid;border-color:#34c759;padding:16px}
.upload-zone img{max-width:100%;max-height:260px;border-radius:6px;display:block;margin:0 auto}
.upload-zone p{color:#6e6e73;font-size:14px;margin-top:8px}
.paste-hint{display:inline-block;background:#f0f0f5;color:#6e6e73;font-size:11px;padding:2px 8px;border-radius:4px;margin-top:6px}
.preview-actions{display:flex;gap:8px;margin-top:12px;justify-content:center}
.delete-btn{background:#fff;border:1px solid #e8e8ed;border-radius:8px;padding:8px 24px;font-size:13px;font-weight:600;cursor:pointer;color:#ff3b30;transition:all .15s}
.delete-btn:hover{background:#ff3b30;color:#fff;border-color:#ff3b30}
.paste-btn{background:#fff;border:1px solid #e8e8ed;border-radius:8px;padding:8px 16px;font-size:13px;cursor:pointer;color:#1d1d1f;transition:all .15s;display:inline-flex;align-items:center;gap:4px}
.paste-btn:hover{border-color:#0071e3;color:#0071e3}
.btn{display:inline-block;background:#0071e3;color:#fff;border:none;border-radius:8px;padding:12px 32px;font-size:15px;font-weight:600;cursor:pointer;width:100%;transition:background .15s}
.btn:hover{background:#0060c8}
.btn:disabled{background:#c7c7cc;cursor:not-allowed}
.file-input{position:absolute;width:0.1px;height:0.1px;opacity:0.01;z-index:-1}
.info-row{display:flex;justify-content:space-between;font-size:13px;color:#6e6e73;margin:8px 0}
.info-row span:last-child{font-weight:600;color:#1d1d1f}
#loading{display:none;text-align:center;margin-top:16px}
#loading p{color:#6e6e73}
#modalOverlay{display:none;position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,.4);z-index:1000;align-items:center;justify-content:center}
#modalBox{background:#fff;border-radius:14px;padding:32px 28px 24px;max-width:380px;width:90%;text-align:center;box-shadow:0 8px 30px rgba(0,0,0,.15);animation:fadeIn .2s ease}
#modalIcon{font-size:48px;margin-bottom:12px}
#modalTitle{font-size:20px;font-weight:700;margin-bottom:8px}
#modalMsg{font-size:14px;color:#6e6e73;margin-bottom:8px;line-height:1.5}
#modalDetail{font-size:13px;color:#999;margin-bottom:20px;line-height:1.4}
#modalButtons{display:flex;gap:10px;justify-content:center}
@keyframes fadeIn{from{opacity:0;transform:scale(.92)}to{opacity:1;transform:scale(1)}}
@media(max-width:600px){
.container{padding:24px 16px}
h1{font-size:22px}
.card{padding:20px 16px}
.instruction-grid{grid-template-columns:repeat(3,1fr);gap:6px}
.instruction-btn{padding:10px 4px;font-size:12px}
.instruction-btn .name{font-size:13px}
.instruction-btn .size{font-size:11px}
.upload-zone{padding:24px 16px}
.upload-zone img{max-height:180px}
.btn{padding:14px 24px;font-size:16px}
#modalBox{margin:0 16px;padding:24px 20px}
#modalBox #modalTitle{font-size:18px}
#modalButtons button{padding:12px 24px;font-size:16px;flex:1}
.info-row{font-size:12px}
}
</style>
</head>
<body>
<div class="container">
<h1>📷 <span style="color:#0071e3">autocheckimg.dyy.com</span></h1>
<p class="subtitle">上传图片 → 选择指令 → 自动检查或调整尺寸</p>
<div class="card">
<p style="font-size:13px;color:#6e6e73;margin-bottom:10px;font-weight:600">选择指令</p>
<div class="instruction-grid">
<div class="instruction-btn" data-value="1" onclick="selectInstruction(this)"><div class="name">2号门</div><div class="size">1440 × 1080</div></div>
<div class="instruction-btn" data-value="2" onclick="selectInstruction(this)"><div class="name">8号门</div><div class="size">1032 × 1720</div></div>
<div class="instruction-btn" data-value="3" onclick="selectInstruction(this)"><div class="name">广告机</div><div class="size">2160 × 3840</div></div>
</div>
<label for="fileInput" class="upload-zone" id="dropZone">
<div id="uploadPrompt"><p style="font-size:32px;margin-bottom:8px">📤</p><p>点击或拖拽图片到此处</p><p style="font-size:12px;color:#999;margin-top:4px">支持 JPG / PNG / WebP</p><span class="paste-hint">👆 点击选择 / ⌘V 粘贴</span></div>
<div id="previewArea" style="display:none">
<img id="previewImg" alt="预览">
<div class="info-row"><span>文件名</span><span id="fileName">-</span></div>
<div class="info-row"><span>图片尺寸</span><span id="fileDims">-</span></div>
<div class="preview-actions">
<button class="delete-btn" onclick="clearImage()">✕ 删除</button>
</div>
</div>
</label>
<input type="file" id="fileInput" class="file-input" accept="image/*" onchange="handleFile(this)">
<button class="btn" id="submitBtn" disabled onclick="submitImage()">开始审核</button>
<div id="loading"><p>⏳ 处理中...</p></div>
</div>
</div>

<div id="modalOverlay" onclick="closeModal(event)">
<div id="modalBox" onclick="event.stopPropagation()">
<div id="modalIcon"></div>
<div id="modalTitle"></div>
<div id="modalMsg"></div>
<div id="modalDetail"></div>
<div id="modalButtons"></div>
</div>
</div>

<script>
let selectedInstruction = null;
let currentFile = null;
let downloadData = null;

function selectInstruction(el) {
  document.querySelectorAll('.instruction-btn').forEach(i => i.classList.remove('active'));
  el.classList.add('active');
  selectedInstruction = el.dataset.value;
  updateSubmit();
}

function showModal(icon, title, msg, detail, buttons) {
  document.getElementById('modalIcon').textContent = icon;
  document.getElementById('modalTitle').textContent = title;
  document.getElementById('modalMsg').textContent = msg;
  document.getElementById('modalDetail').textContent = detail || '';
  const c = document.getElementById('modalButtons');
  c.innerHTML = '';
  buttons.forEach(b => {
    const btn = document.createElement('button');
    btn.textContent = b.label;
    Object.assign(btn.style, {
      padding: '10px 28px', borderRadius: '8px', border: 'none',
      fontSize: '14px', fontWeight: '600', cursor: 'pointer',
      background: b.primary ? '#0071e3' : '#e8e8ed',
      color: b.primary ? '#fff' : '#1d1d1f'
    });
    btn.onclick = function() {
      document.getElementById('modalOverlay').style.display = 'none';
      if (b.action) b.action();
    };
    c.appendChild(btn);
  });
  document.getElementById('modalOverlay').style.display = 'flex';
}

function closeModal(e) {
  if (e && e.target !== e.currentTarget) return;
  document.getElementById('modalOverlay').style.display = 'none';
}

function triggerDownload(url, filename) {
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
}

function handleFile(i) {
  const f = i.files[0];
  if (!f) return;
  loadFile(f);
}

document.getElementById('dropZone').addEventListener('dragover', function(e) {
  e.preventDefault();
  document.getElementById('dropZone').classList.add('dragover');
});
document.getElementById('dropZone').addEventListener('dragleave', function(e) {
  e.preventDefault();
  document.getElementById('dropZone').classList.remove('dragover');
});
document.getElementById('dropZone').addEventListener('drop', function(e) {
  e.preventDefault();
  document.getElementById('dropZone').classList.remove('dragover');
  const f = e.dataTransfer.files[0];
  if (!f || !f.type.startsWith('image/')) return;
  document.getElementById('fileInput').files = e.dataTransfer.files;
  loadFile(e.dataTransfer.files[0]);
});

// ===== 粘贴上传图片 =====
document.addEventListener('paste', function(e) {
  if (document.activeElement && document.activeElement.tagName === 'INPUT') return;
  const items = e.clipboardData && e.clipboardData.items;
  if (!items) return;
  for (let i = 0; i < items.length; i++) {
    if (items[i].type.startsWith('image/')) {
      const file = items[i].getAsFile();
      if (file) {
        // Clipboard files don't have a meaningful name
        const renamed = new File([file], 'pasted_image.png', { type: file.type });
        document.getElementById('fileInput').files = (function() {
          const dt = new DataTransfer();
          dt.items.add(renamed);
          return dt.files;
        })();
        loadFile(renamed);
      }
      break;
    }
  }
});

function loadFile(f) {
  currentFile = f;
  const r = new FileReader();
  r.onload = function(e) {
    const img = new Image();
    img.onload = function() {
      document.getElementById('uploadPrompt').style.display = 'none';
      document.getElementById('previewArea').style.display = 'block';
      document.getElementById('previewImg').src = e.target.result;
      document.getElementById('fileName').textContent = f.name;
      document.getElementById('fileDims').textContent = img.width + ' \u00d7 ' + img.height;
      document.getElementById('dropZone').classList.add('has-image');
      updateSubmit();
    };
    img.src = e.target.result;
  };
  r.readAsDataURL(f);
}

// iOS Safari touch support - 确保点击上传区域能打开文件选择器
document.getElementById('dropZone').addEventListener('touchstart', function(e) {
  // 不阻止默认行为，让 label 正常触发文件输入
  // 这只确保 iOS 上 touch 事件能正确传递
});

function updateSubmit() {
  document.getElementById('submitBtn').disabled = !(selectedInstruction && currentFile);
}

function clearImage() {
  currentFile = null;
  selectedInstruction = null;
  document.querySelectorAll('.instruction-btn').forEach(i => i.classList.remove('active'));
  document.getElementById('fileInput').value = '';
  document.getElementById('uploadPrompt').style.display = 'block';
  document.getElementById('previewArea').style.display = 'none';
  document.getElementById('previewImg').src = '';
  document.getElementById('fileName').textContent = '-';
  document.getElementById('fileDims').textContent = '-';
  document.getElementById('dropZone').classList.remove('has-image');
  updateSubmit();
}

async function submitImage() {
  if (!selectedInstruction || !currentFile) return;
  const btn = document.getElementById('submitBtn');
  const loading = document.getElementById('loading');
  btn.disabled = true;
  loading.style.display = 'block';

  const fd = new FormData();
  fd.append('image', currentFile);
  fd.append('instruction', selectedInstruction);

  // Abort after 60 seconds (Render冷启动可能需要30s)
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 60000);

  try {
    const resp = await fetch('/check', { method: 'POST', body: fd, signal: controller.signal });
    clearTimeout(timeout);
    const data = await resp.json();
    loading.style.display = 'none';

    if (data.status === 'correct') {
      alert('✅ 尺寸正确
' + data.message);
    } else if (data.status === 'resized') {
      const url = data.download_url;
      const name = data.filename;
      if (confirm('✏️ 已将图片调整为 ' + data.new_size + '
是否下载修改后的图像？')) {
        triggerDownload(url, name);
      }
    } else {
      alert('❌ 处理失败
' + data.message);
    }
  } catch (e) {
    clearTimeout(timeout);
    loading.style.display = 'none';
    if (e.name === 'AbortError') {
      alert('⏳ 请求超时
服务器可能正在唤醒，请稍候再试');
    } else {
      alert('❌ 网络错误
' + e.message);
    }
  }

  btn.disabled = false;
}
</script>
</body>
</html>
"""

INSTRUCTIONS = {"1": {"name": "2号门", "width": 1440, "height": 1080},
                "2": {"name": "8号门", "width": 1032, "height": 1720},
                "3": {"name": "广告机", "width": 2160, "height": 3840}}

@app.route("/")
def index():
    return render_template_string(HTML)

@app.route("/check", methods=["POST"])
def check():
    if "image" not in request.files:
        return {"status": "error", "message": "未上传图片"}, 400
    file = request.files["image"]
    instruction = request.form.get("instruction", "").strip()
    if instruction not in INSTRUCTIONS:
        return {"status": "error", "message": f"无效指令: {instruction}"}, 400
    target = INSTRUCTIONS[instruction]
    target_w, target_h = target["width"], target["height"]
    target_name = target["name"]
    try:
        img = Image.open(file.stream)
        w, h = img.size
        if w == target_w and h == target_h:
            return {"status": "correct",
                    "message": f"图片尺寸为 {w}\u00d7{h}，符合\u300c{target_name}\u300f要求 ({target_w}\u00d7{target_h})"}
        resized = img.resize((target_w, target_h), Image.LANCZOS)
        buf = io.BytesIO()
        fmt = "PNG"
        if "." in file.filename:
            e = file.filename.rsplit(".", 1)[-1].upper()
            if e in ("JPG", "JPEG"): fmt = "JPEG"
            elif e in ("PNG", "WEBP", "GIF"): fmt = e
        resized.save(buf, format=fmt)
        buf.seek(0)
        b64 = base64.b64encode(buf.getvalue()).decode()
        ext = fmt.lower()
        name = f"{os.path.splitext(file.filename)[0]}_{target_name}_{target_w}x{target_h}.{ext}"
        return {"status": "resized",
                "message": f"原始尺寸: {w}\u00d7{h} \u2192 {target_w}\u00d7{target_h}",
                "new_size": f"{target_w}\u00d7{target_h}",
                "download_url": f"data:image/{ext};base64,{b64}",
                "filename": name}
    except Exception as e:
        return {"status": "error", "message": f"处理图片时出错: {str(e)}"}, 500

if __name__ == "__main__":
    print("=" * 50)
    print("  autocheckimg.dyy.com - 图片自动审核工具")
    port = int(os.environ.get("PORT", 5001))
    host = os.environ.get("HOST", "0.0.0.0")
    print(f"  启动地址: http://{host}:{port}")
    print("=" * 50)
    app.run(debug=False, host=host, port=port)
