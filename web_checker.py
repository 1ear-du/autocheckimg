#!/usr/bin/env python3
"""图片自动审核工具 - 简洁版"""
import os, io, base64
from flask import Flask, render_template_string, request
from PIL import Image

app = Flask(__name__)

HTML = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>图片自动审核</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;background:#f5f5f7;color:#1d1d1f;padding:24px;display:flex;flex-direction:column;align-items:center}
.box{max-width:640px;width:100%}
h1{font-size:26px;margin-bottom:6px}
.sub{color:#6e6e73;font-size:14px;margin-bottom:28px}
.card{background:#fff;border-radius:12px;padding:28px;box-shadow:0 1px 3px rgba(0,0,0,.08);margin-bottom:20px}
.label{font-size:13px;font-weight:600;color:#6e6e73;margin-bottom:10px}
.btns{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin-bottom:20px}
.opt{border:2px solid #e8e8ed;border-radius:10px;padding:12px;text-align:center;cursor:pointer;font-size:13px;background:#fff;-webkit-user-select:none}
.opt:hover{border-color:#0071e3}
.opt.on{border-color:#0071e3;background:#e8f0fe;font-weight:600}
.opt .nm{font-size:15px;font-weight:600;margin-bottom:2px}
.opt .sz{color:#6e6e73;font-size:12px}
.upzone{border:2px dashed #c7c7cc;border-radius:10px;padding:40px;text-align:center;cursor:pointer;margin-bottom:16px;transition:.15s}
.upzone:hover{border-color:#0071e3;background:#e8f0fe}
.upzone.hasimg{border-style:solid;border-color:#34c759;padding:16px}
.upzone img{max-width:100%;max-height:260px;border-radius:6px;display:block;margin:0 auto}
.preview{display:none}
.inf{font-size:13px;color:#6e6e73;margin-top:8px}
.inf span{font-weight:600;color:#1d1d1f}
.fa{display:flex;gap:8px;margin-top:10px;justify-content:center}
.del{cursor:pointer;border:1px solid #e8e8ed;border-radius:8px;padding:8px 24px;font-size:13px;font-weight:600;color:#ff3b30;background:#fff}
.del:hover{background:#ff3b30;color:#fff;border-color:#ff3b30}
.btn{background:#0071e3;color:#fff;border:none;border-radius:8px;padding:12px;font-size:15px;font-weight:600;cursor:pointer;width:100%}
.btn:disabled{background:#c7c7cc;cursor:default}
#load{display:none;text-align:center;margin-top:16px;color:#6e6e73}
@media(max-width:600px){.box{padding:0}.card{padding:20px 16px}.opt{padding:10px}.upzone{padding:24px 16px}}
</style>
</head>
<body>
<div class="box">
<h1>图片自动审核</h1>
<p class="sub">上传图片 → 选择指令 → 自动检查或调整尺寸</p>

<div class="card">
<div class="label">选择指令</div>
<div class="btns" id="btnGroup">
<div class="opt" data-v="1"><div class="nm">2号门</div><div class="sz">1440 × 1080</div></div>
<div class="opt" data-v="2"><div class="nm">8号门</div><div class="sz">1032 × 1720</div></div>
<div class="opt" data-v="3"><div class="nm">广告机</div><div class="sz">2160 × 3840</div></div>
</div>

<div class="upzone" id="zone">
<div id="prompt">
<div style="font-size:32px;margin-bottom:8px">&#x1f4e4;</div>
<p>点击选择图片</p>
<p style="font-size:12px;color:#999;margin-top:4px">支持 JPG / PNG / WebP</p>
</div>
<div class="preview" id="prev">
<img id="prevImg" alt="">
<div class="inf">文件名: <span id="fname">-</span></div>
<div class="inf">尺寸: <span id="fdims">-</span></div>
<div class="fa"><button class="del" id="delBtn">&#x2715; 删除</button></div>
</div>
</div>

<input type="file" id="fileIn" accept="image/*" style="display:none">
<button class="btn" id="subBtn" disabled>开始审核</button>
<div id="load">处理中...</div>
</div>
</div>

<script>
var curFile = null;
var curInst = null;

// 指令按钮
document.getElementById('btnGroup').addEventListener('click', function(e) {
  var btn = e.target.closest('.opt');
  if (!btn) return;
  document.querySelectorAll('.opt').forEach(function(el) { el.classList.remove('on'); });
  btn.classList.add('on');
  curInst = btn.getAttribute('data-v');
  updateBtn();
});

// 上传区域点击
document.getElementById('zone').addEventListener('click', function() {
  document.getElementById('fileIn').click();
});

// 文件选择
document.getElementById('fileIn').addEventListener('change', function(e) {
  var file = e.target.files[0];
  if (!file) return;
  curFile = file;
  updateBtn();
  // 预览
  var reader = new FileReader();
  reader.onload = function(ev) {
    var img = new Image();
    img.onload = function() {
      document.getElementById('prompt').style.display = 'none';
      document.getElementById('prev').style.display = 'block';
      document.getElementById('prevImg').src = ev.target.result;
      document.getElementById('fname').textContent = file.name;
      document.getElementById('fdims').textContent = img.width + ' x ' + img.height;
      document.getElementById('zone').classList.add('hasimg');
    };
    img.src = ev.target.result;
  };
  reader.readAsDataURL(file);
});

// 删除按钮
document.getElementById('delBtn').addEventListener('click', function(e) {
  e.stopPropagation();
  clearAll();
});

function clearAll() {
  curFile = null;
  curInst = null;
  document.querySelectorAll('.opt').forEach(function(el) { el.classList.remove('on'); });
  document.getElementById('fileIn').value = '';
  document.getElementById('prompt').style.display = 'block';
  document.getElementById('prev').style.display = 'none';
  document.getElementById('zone').classList.remove('hasimg');
  updateBtn();
}

function updateBtn() {
  document.getElementById('subBtn').disabled = !(curInst && curFile);
}

// 提交
document.getElementById('subBtn').addEventListener('click', function() {
  if (!curInst || !curFile) return;
  var btn = this;
  var load = document.getElementById('load');
  btn.disabled = true;
  load.style.display = 'block';

  var fd = new FormData();
  fd.append('image', curFile);
  fd.append('instruction', curInst);

  fetch('/check', { method: 'POST', body: fd })
    .then(function(r) { return r.json(); })
    .then(function(data) {
      load.style.display = 'none';
      if (data.status === 'correct') {
        alert('\u2705 \u5c3a\u5bf8\u6b63\u786e\n' + data.message);
      } else if (data.status === 'resized') {
        if (confirm('\u270f\ufe0f \u5df2\u5c06\u56fe\u7247\u8c03\u6574\u4e3a ' + data.new_size + '\n\u662f\u5426\u4e0b\u8f7d\u4fee\u6539\u540e\u7684\u56fe\u50cf\uff1f')) {
          var a = document.createElement('a');
          a.href = data.download_url;
          a.download = data.filename;
          document.body.appendChild(a);
          a.click();
          document.body.removeChild(a);
        }
      } else {
        alert('\u274c \u5904\u7406\u5931\u8d25\n' + data.message);
      }
      btn.disabled = false;
    })
    .catch(function(err) {
      load.style.display = 'none';
      alert('\u274c \u7f51\u7edc\u9519\u8bef\n' + err.message);
      btn.disabled = false;
    });
});

// 删除按钮阻止冒泡已处理
</script>
</body>
</html>
"""

INSTRUCTIONS = {"1": {"name": "2号门", "w": 1440, "h": 1080},
                "2": {"name": "8号门", "w": 1032, "h": 1720},
                "3": {"name": "广告机", "w": 2160, "h": 3840}}

@app.route("/")
def index():
    return render_template_string(HTML)

@app.route("/check", methods=["POST"])
def check():
    f = request.files.get("image")
    if not f:
        return {"status": "error", "message": "未上传图片"}, 400
    inst = request.form.get("instruction", "").strip()
    if inst not in INSTRUCTIONS:
        return {"status": "error", "message": "无效指令"}, 400
    t = INSTRUCTIONS[inst]
    try:
        img = Image.open(f.stream)
        w, h = img.size
        if w == t["w"] and h == t["h"]:
            return {"status": "correct",
                    "message": "图片尺寸为 %d\u00d7%d，符合「%s」要求 (%d\u00d7%d)" % (w, h, t["name"], t["w"], t["h"])}
        resized = img.resize((t["w"], t["h"]), Image.LANCZOS)
        buf = io.BytesIO()
        ext = "PNG"
        if "." in f.filename:
            e = f.filename.rsplit(".", 1)[-1].upper()
            if e in ("JPG", "JPEG"): ext = "JPEG"
            elif e in ("PNG", "WEBP", "GIF"): ext = e
        resized.save(buf, format=ext)
        b64 = base64.b64encode(buf.getvalue()).decode()
        fn = "%s_%s_%dx%d.%s" % (os.path.splitext(f.filename)[0], t["name"], t["w"], t["h"], ext.lower())
        return {"status": "resized",
                "message": "原始: %d\u00d7%d \u2192 %d\u00d7%d" % (w, h, t["w"], t["h"]),
                "new_size": "%d\u00d7%d" % (t["w"], t["h"]),
                "download_url": "data:image/%s;base64,%s" % (ext.lower(), b64),
                "filename": fn}
    except Exception as e:
        return {"status": "error", "message": str(e)}, 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    print("http://0.0.0.0:%d" % port)
    app.run(debug=False, host="0.0.0.0", port=port)
