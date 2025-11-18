import io
import re
from typing import Optional

from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.responses import Response, JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from rembg import remove, new_session
from PIL import Image

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
_session = new_session("isnet-general-use")

def _hex_to_rgb(value: str):
    m = re.fullmatch(r"#?([0-9a-fA-F]{6})", value)
    if not m:
        raise ValueError("invalid hex color")
    h = m.group(1)
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

@app.get("/health")
def health():
    return JSONResponse({"status": "ok"})

@app.post("/remove-bg")
async def remove_bg(request: Request, file: Optional[UploadFile] = File(None), format: Optional[str] = "png", background: Optional[str] = None):
    data: bytes
    if file is not None:
        if not file.content_type or not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="invalid image file")
        data = await file.read()
    else:
        ct = request.headers.get("content-type", "")
        if not ct.startswith("image/"):
            raise HTTPException(status_code=400, detail="missing image: use multipart field 'file' or raw image body")
        data = await request.body()
    out_bytes = remove(data, session=_session)
    img = Image.open(io.BytesIO(out_bytes))
    fmt = (format or "png").lower()
    if fmt == "png":
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return Response(content=buf.getvalue(), media_type="image/png")
    if fmt in ("jpg", "jpeg"):
        bg = _hex_to_rgb(background or "#FFFFFF")
        base = Image.new("RGB", img.size, bg)
        if img.mode != "RGBA":
            img = img.convert("RGBA")
        base.paste(img, mask=img.split()[3])
        buf = io.BytesIO()
        base.save(buf, format="JPEG", quality=95)
        return Response(content=buf.getvalue(), media_type="image/jpeg")
    raise HTTPException(status_code=400, detail="unsupported format")

@app.get("/demo")
def demo():
    return HTMLResponse(
        """
        <!doctype html>
        <html lang=\"zh-CN\">
        <head>
          <meta charset=\"utf-8\" />
          <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
          <title>快速抠图</title>
          <style>
            :root { --bg:#0b0c10; --card:#111218; --muted:#a9b1bd; --text:#e6edf3; --brand:#6ea8fe; --accent:#10b981; }
            * { box-sizing: border-box; }
            body { margin:0; font-family: ui-sans-serif, system-ui, -apple-system, \"Segoe UI\", Roboto; background: var(--bg); color: var(--text); }
            .container { max-width: 1024px; margin: 0 auto; padding: 24px; }
            header { display:flex; align-items:center; justify-content:space-between; margin-bottom: 16px; }
            header h1 { font-size: 20px; margin:0; }
            header .badge { font-size:12px; color: var(--muted); }
            .grid { display:grid; grid-template-columns:1fr 1fr; gap:16px; }
            .card { background: var(--card); border: 1px solid #1f2330; border-radius: 12px; padding: 16px; }
            .card h2 { margin:0 0 12px; font-size:16px; color:#c9d1d9; }
            .uploader { border:2px dashed #2a2f3a; border-radius:12px; padding:24px; text-align:center; cursor:pointer; }
            .uploader:hover { border-color:#3b4253; }
            .uploader input { display:none; }
            .btn { appearance:none; border:none; border-radius:8px; padding:10px 14px; font-weight:600; cursor:pointer; }
            .btn-primary { background: var(--brand); color:#0b0c10; }
            .btn { transition: transform .05s ease; }
            .btn:active { transform: translateY(1px); }
            .row { display:flex; gap:8px; align-items:center; margin-top:12px; }
            .select, .text { background:#0b0d13; border:1px solid #232838; color: var(--text); border-radius:8px; padding:8px 10px; }
            .meta { font-size:12px; color: var(--muted); margin-top:8px; }
            .preview-wrap { background: repeating-conic-gradient(#444 0% 25%, transparent 0% 50%) 50% / 20px 20px; border-radius: 12px; overflow:hidden; min-height: 240px; display:flex; align-items:center; justify-content:center; }
            img.preview { max-width: 100%; height:auto; display:block; }
            .status { font-size:13px; margin-top:8px; color: var(--muted); }
            .row.space { justify-content: space-between; }
            .link { color: var(--accent); text-decoration:none; }
          </style>
        </head>
        <body>
          <div class=\"container\">
            <header>
              <h1>快速抠图</h1>
              <span class=\"badge\">前景保留 · 背景透明或自定义颜色</span>
            </header>
            <div class=\"grid\">
              <div class=\"card\">
                <h2>选择图片</h2>
                <label class=\"uploader\" id=\"drop\">
                  <input id=\"file\" type=\"file\" accept=\"image/*\" />
                  <div>拖拽图片到此或点击选择</div>
                  <div class=\"meta\" id=\"meta\"></div>
                </label>
                <div class=\"row\">
                  <label>输出格式</label>
                  <select id=\"fmt\" class=\"select\"><option value=\"png\">PNG(透明)</option><option value=\"jpeg\">JPEG(合成背景)</option></select>
                  <input id=\"bg\" class=\"text\" type=\"text\" value=\"#FFFFFF\" placeholder=\"#RRGGBB\" />
                  <button id=\"run\" class=\"btn btn-primary\">开始抠图</button>
                </div>
                <div class=\"status\" id=\"status\"></div>
                <div class=\"meta\">建议上传清晰主体图片，支持常见格式</div>
              </div>
              <div class=\"card\">
                <h2>预览</h2>
                <div class=\"preview-wrap\">
                  <img id=\"inPreview\" class=\"preview\" alt=\"原图预览\" />
                </div>
                <div class=\"row space\" style=\"margin-top:12px\">
                  <span class=\"meta\">原图预览</span>
                </div>
              </div>
            </div>
            <div class=\"card\" style=\"margin-top:16px\">
              <h2>输出结果</h2>
              <div class=\"preview-wrap\">
                <img id=\"outPreview\" class=\"preview\" alt=\"输出预览\" />
              </div>
              <div class=\"row space\" style=\"margin-top:12px\">
                <span class=\"meta\" id=\"outMeta\"></span>
                <a id=\"download\" class=\"link\" href=\"#\" download>下载结果</a>
              </div>
            </div>
          </div>
          <script>
          const fileEl = document.getElementById('file');
          const metaEl = document.getElementById('meta');
          const inPreview = document.getElementById('inPreview');
          const outPreview = document.getElementById('outPreview');
          const outMeta = document.getElementById('outMeta');
          const downloadEl = document.getElementById('download');
          const fmtEl = document.getElementById('fmt');
          const bgEl = document.getElementById('bg');
          const statusEl = document.getElementById('status');
          const drop = document.getElementById('drop');
          function human(n){ if(n<1024) return n+' B'; if(n<1024*1024) return (n/1024).toFixed(1)+' KB'; return (n/1024/1024).toFixed(1)+' MB'; }
          function resetOut(){ outPreview.src=''; outMeta.textContent=''; downloadEl.href='#'; }
          function setStatus(t){ statusEl.textContent=t; }
          function onFile(f){ if(!f) return; const url = URL.createObjectURL(f); inPreview.src = url; metaEl.textContent = f.name + ' · ' + human(f.size); resetOut(); }
          fileEl.addEventListener('change', e => onFile(e.target.files[0]));
          drop.addEventListener('dragover', e => { e.preventDefault(); drop.style.borderColor = '#6ea8fe'; });
          drop.addEventListener('dragleave', e => { drop.style.borderColor = '#2a2f3a'; });
          drop.addEventListener('drop', e => { e.preventDefault(); drop.style.borderColor = '#2a2f3a'; const f = e.dataTransfer.files[0]; if(f){ fileEl.files = e.dataTransfer.files; onFile(f); }});
          fmtEl.addEventListener('change', () => { const v = fmtEl.value; bgEl.disabled = v !== 'jpeg'; });
          bgEl.disabled = fmtEl.value !== 'jpeg';
          async function run(){ const f = fileEl.files[0]; if(!f){ setStatus('请先选择图片文件'); return; } setStatus('处理中...'); const fd = new FormData(); fd.append('file', f); const q = new URLSearchParams({ format: fmtEl.value, background: bgEl.value }); const resp = await fetch('/remove-bg?' + q.toString(), { method: 'POST', body: fd }); if(!resp.ok){ const text = await resp.text(); setStatus('错误: ' + resp.status + ' ' + text); return; } const blob = await resp.blob(); const url = URL.createObjectURL(blob); outPreview.src = url; downloadEl.href = url; downloadEl.download = fmtEl.value === 'png' ? 'output.png' : 'output.jpg'; setStatus('完成'); const sz = blob.size; outMeta.textContent = '大小 ' + human(sz) + ' · 类型 ' + blob.type; }
          document.getElementById('run').addEventListener('click', run);
          </script>
        </body>
        </html>
        """
    )