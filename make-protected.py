#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
make-protected.py — Mã hoá một file HTML bằng mật khẩu (AES-256-GCM).
Cổng nhập mật khẩu nền ảnh thiên nhiên (Ken Burns) + thẻ kính mờ.

CÁCH DÙNG:
    python make-protected.py "MatKhau" masterclass-all-in-one.html index.html
Yêu cầu: pip install cryptography

ĐỔI ẢNH NỀN: sửa URL trong biến BG_URL ngay dưới đây.
"""
import sys, os, base64, json, gzip, re, getpass
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

ITER = 600_000

# Ảnh nền — núi hoàng hôn (Unsplash). Đổi link này để thay ảnh.
BG_URL = "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?auto=format&fit=crop&w=2000&q=72"

def main():
    if len(sys.argv) >= 2 and sys.argv[1]:
        password = sys.argv[1]
    else:
        password = getpass.getpass("Mật khẩu: ")
    if not password:
        print("Thiếu mật khẩu.\n  python make-protected.py \"MatKhau\" [input.html] [output.html]"); sys.exit(1)
    src = sys.argv[2] if len(sys.argv) > 2 else "masterclass-all-in-one.html"
    dst = sys.argv[3] if len(sys.argv) > 3 else "masterclass-protected.html"
    data = open(src, "rb").read()

    # Chip hiển thị trên trang khóa: đếm số masterclass từ meta-data của bản gộp (nếu có)
    chip = "Data Engineering"
    m = re.search(rb'<script id="meta-data" type="application/json">(.*?)</script>', data, re.S)
    if m:
        try:
            chip = "%d masterclass" % len(json.loads(m.group(1).decode("utf-8")))
        except Exception:
            pass

    raw_len = len(data)
    data = gzip.compress(data, 9)  # nén trước khi mã hóa -> file nhỏ hơn đáng kể
    salt, iv = os.urandom(16), os.urandom(12)
    key = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=ITER).derive(password.encode("utf-8"))
    ct = AESGCM(key).encrypt(iv, data, None)
    payload = {"salt": base64.b64encode(salt).decode(), "iv": base64.b64encode(iv).decode(),
               "ct": base64.b64encode(ct).decode(), "iter": ITER, "gz": 1}
    html = TEMPLATE.replace("__PAYLOAD__", json.dumps(payload)).replace("__BG_URL__", BG_URL).replace("__CHIP__", chip)
    open(dst, "w", encoding="utf-8").write(html)
    print("Đã tạo %s (%.1f MB, gốc %.1f MB) — gzip + AES-256-GCM, PBKDF2 %d vòng." %
          (dst, len(html.encode())/1048576, raw_len/1048576, ITER))

TEMPLATE = r"""<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Data Engineering Masterclass</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700&family=Space+Mono:wght@400;700&family=IBM+Plex+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
  :root{
    --orange:#e2691f; --orange-2:#d55a1b; --orange-dim:#b04510;
    --cyan:#39c5ad; --red:#ff9a90;
    --tx:#eef2f8; --tx-dim:rgba(238,242,248,.74); --tx-faint:rgba(238,242,248,.5);
    --mono:'JetBrains Mono',ui-monospace,monospace;
    --display:'Space Mono',monospace;
    --sans:'IBM Plex Sans',system-ui,sans-serif;
  }
  *{box-sizing:border-box}
  html,body{margin:0;height:100%}
  body{
    min-height:100vh; display:flex; align-items:center; justify-content:center;
    padding:24px; position:relative; overflow:hidden; color:var(--tx);
    font-family:var(--sans); -webkit-font-smoothing:antialiased; text-rendering:optimizeLegibility;
    background:linear-gradient(180deg,#2c2348,#6f4068 36%,#c76a45 72%,#e89a5f);
  }
  .bg{position:fixed; inset:-8%; z-index:0; background-size:cover; background-position:50% 50%;
    background-image:url('__BG_URL__'); transform:scale(1.08);
    animation:ken 34s ease-in-out infinite alternate; will-change:transform,background-position;}
  @keyframes ken{0%{transform:scale(1.08) translate(0,0)}100%{transform:scale(1.22) translate(-2.4%,-2%)}}
  .overlay{position:fixed; inset:0; z-index:1; pointer-events:none;
    background:linear-gradient(180deg,rgba(12,14,26,.30),rgba(12,14,26,.50) 55%,rgba(12,14,26,.76)),
      radial-gradient(circle at 50% 38%,transparent 38%,rgba(8,10,20,.5));}

  .box{position:relative; z-index:2; width:100%; max-width:404px;
    background:rgba(20,24,40,.46); -webkit-backdrop-filter:blur(22px) saturate(1.2); backdrop-filter:blur(22px) saturate(1.2);
    border:1px solid rgba(255,255,255,.16); border-radius:22px;
    padding:38px 36px 30px; text-align:center; overflow:hidden; isolation:isolate;
    box-shadow:0 30px 70px -28px rgba(0,0,0,.66), inset 0 1px 0 rgba(255,255,255,.14);
    animation:rise .65s cubic-bezier(.2,.8,.2,1) both;}
  .box::before{content:""; position:absolute; top:0; left:0; right:0; height:3px;
    background:linear-gradient(90deg,var(--orange),#e0883b,var(--cyan),#e0883b,var(--orange));
    background-size:200% 100%; animation:barFlow 6s linear infinite;}
  @keyframes barFlow{to{background-position:-200% 0}}
  @keyframes rise{from{opacity:0; transform:translateY(18px) scale(.985)} to{opacity:1; transform:none}}
  .box.shake{animation:shake .42s}
  @keyframes shake{0%,100%{transform:translateX(0)}20%{transform:translateX(-8px)}40%{transform:translateX(7px)}60%{transform:translateX(-5px)}80%{transform:translateX(3px)}}

  .shine{position:absolute; inset:0; z-index:-1; pointer-events:none; opacity:0; transition:opacity .35s;
    background:radial-gradient(200px circle at var(--mx,50%) var(--my,0%), rgba(255,255,255,.10), transparent 60%);}
  .box:hover .shine{opacity:1;}

  .badge,.brand,.tag,.chips,.form{opacity:0; animation:fadeUp .55s cubic-bezier(.2,.8,.2,1) both;}
  .badge{animation-delay:.10s} .brand{animation-delay:.17s} .tag{animation-delay:.23s}
  .chips{animation-delay:.29s} .form{animation-delay:.35s}
  @keyframes fadeUp{from{opacity:0; transform:translateY(10px)} to{opacity:1; transform:none}}

  .badge{position:relative; width:56px; height:56px; margin:2px auto 18px; border-radius:16px;
    display:grid; place-items:center; color:#ffb98a;
    background:rgba(255,255,255,.12); border:1px solid rgba(255,255,255,.22);
    box-shadow:inset 0 1px 0 rgba(255,255,255,.25), 0 8px 20px -10px rgba(0,0,0,.5);}
  .badge::after{content:""; position:absolute; inset:-32%; z-index:-1; border-radius:50%;
    background:radial-gradient(circle,rgba(226,105,31,.45),transparent 64%); animation:halo 3.6s ease-in-out infinite;}
  .badge svg{width:29px; height:29px; animation:floatY 4.6s ease-in-out 1s infinite;}
  @keyframes halo{0%,100%{opacity:.55; transform:scale(.92)}50%{opacity:1; transform:scale(1.1)}}
  @keyframes floatY{0%,100%{transform:translateY(0)}50%{transform:translateY(-3px)}}

  .brand{font-family:var(--display); font-weight:700; font-size:23px; letter-spacing:-.6px; margin:0 0 6px; color:#fff;}
  .brand .dot{color:#ff9242;}
  .caret{display:inline-block; width:2px; height:1.02em; margin-left:3px; vertical-align:-3px;
    background:#ff9242; border-radius:1px; animation:blink 1.15s steps(1) infinite;}
  @keyframes blink{50%{opacity:0}}
  .tag{margin:0 0 17px; font-size:13.5px; color:var(--tx-dim); line-height:1.5;}

  .chips{display:flex; gap:8px; justify-content:center; flex-wrap:wrap; margin-bottom:25px;}
  .chip{font-family:var(--mono); font-size:10.5px; letter-spacing:.5px; text-transform:uppercase;
    color:var(--tx-dim); background:rgba(255,255,255,.1); border:1px solid rgba(255,255,255,.18);
    border-radius:20px; padding:5px 11px; display:inline-flex; align-items:center; gap:6px;}
  .chip .cdot{width:6px; height:6px; border-radius:50%; background:var(--cyan); animation:dotPulse 2.2s ease-in-out infinite;}
  @keyframes dotPulse{0%,100%{box-shadow:0 0 0 3px rgba(57,197,173,.25)}50%{box-shadow:0 0 0 6px rgba(57,197,173,.05)}}

  .form{text-align:left;}
  .lbl{display:block; font-size:12px; font-weight:600; color:var(--tx-dim); margin:0 2px 7px;}
  .field{display:flex; align-items:center; gap:9px; height:50px; padding:0 7px 0 13px;
    background:rgba(255,255,255,.08); border:1.5px solid rgba(255,255,255,.2); border-radius:13px; transition:.18s;}
  .field:focus-within{border-color:var(--cyan); background:rgba(255,255,255,.13); box-shadow:0 0 0 4px rgba(57,197,173,.16);}
  .field .lock{color:var(--tx-faint); flex:0 0 auto; display:flex; transition:.18s;}
  .field .lock svg{width:18px; height:18px;}
  .field:focus-within .lock{color:var(--cyan);}
  #pw{flex:1; min-width:0; border:0; background:transparent; outline:none; color:var(--tx);
    font-family:var(--mono); font-size:14.5px; letter-spacing:.5px;}
  #pw::placeholder{color:var(--tx-faint); letter-spacing:0;}
  .reveal{flex:0 0 auto; width:34px; height:34px; border:0; background:transparent; cursor:pointer;
    color:var(--tx-faint); border-radius:9px; display:grid; place-items:center; transition:.15s;}
  .reveal:hover{color:var(--tx); background:rgba(255,255,255,.1);}
  .reveal.on{color:var(--cyan);}
  .reveal svg{width:18px; height:18px;}

  .submit{margin-top:14px; width:100%; height:50px; border:0; border-radius:13px; cursor:pointer;
    position:relative; overflow:hidden; display:flex; align-items:center; justify-content:center; gap:9px;
    color:#fff; font-family:var(--sans); font-weight:600; font-size:15px; letter-spacing:.2px;
    background:linear-gradient(135deg,#e2691f,var(--orange-2) 55%,var(--orange-dim));
    box-shadow:0 12px 26px -10px rgba(226,105,31,.7), inset 0 1px 0 rgba(255,255,255,.35); transition:.2s;}
  .submit:hover{transform:translateY(-1px); filter:brightness(1.06);}
  .submit:active{transform:translateY(0);}
  .submit .arr{font-size:17px; transition:transform .2s;}
  .submit:hover .arr{transform:translateX(4px);}
  .submit::before{content:""; position:absolute; top:0; left:-70%; width:45%; height:100%;
    transform:skewX(-22deg); background:linear-gradient(100deg,transparent,rgba(255,255,255,.5),transparent);
    animation:sheen 4.6s ease-in-out infinite;}
  @keyframes sheen{0%,68%{left:-70%}84%{left:155%}100%{left:155%}}
  .submit.loading{pointer-events:none;}
  .submit.loading .t,.submit.loading .arr{visibility:hidden;}
  .submit.loading::after{content:""; position:absolute; width:18px; height:18px;
    border:2px solid rgba(255,255,255,.55); border-top-color:#fff; border-radius:50%; animation:spin .7s linear infinite;}
  @keyframes spin{to{transform:rotate(360deg)}}

  .err{min-height:18px; margin:13px 2px 0; font-family:var(--mono); font-size:12px; color:var(--red);
    display:flex; align-items:center; gap:6px; opacity:0; transform:translateY(-2px); transition:.2s;}
  .err.show{opacity:1; transform:none;}

  .flash{position:fixed; inset:0; z-index:9; pointer-events:none; background:#f6f7f9; opacity:0;}
  .flash.go{animation:flash .45s ease forwards;}
  @keyframes flash{0%{opacity:0}70%{opacity:1}100%{opacity:1}}

  @media(max-width:440px){.box{padding:32px 22px 26px;}}
</style>
</head>
<body>
  <div class="bg" id="bg"></div>
  <div class="overlay"></div>

  <main class="box" id="box">
    <div class="shine"></div>
    <div class="badge" aria-hidden="true">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">
        <path d="M12 3 21 7.5 12 12 3 7.5 12 3Z"/>
        <path d="M3 12 12 16.5 21 12"/>
        <path d="M3 16.5 12 21 21 16.5"/>
      </svg>
    </div>
    <h1 class="brand">data<span class="dot">·</span>engineering<span class="dot">.</span><span class="caret"></span></h1>
    <p class="tag">Data Engineering · Masterclass</p>
    <div class="chips">
      <span class="chip"><span class="cdot"></span>__CHIP__</span>
    </div>

    <form class="form" id="form" autocomplete="off">
      <label class="lbl" for="pw">Mật khẩu truy cập</label>
      <div class="field">
        <span class="lock" aria-hidden="true">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">
            <rect x="4.5" y="10.5" width="15" height="10" rx="2.3"/>
            <path d="M8 10.5V7.5a4 4 0 0 1 8 0v3"/>
          </svg>
        </span>
        <input id="pw" type="password" placeholder="Nhập mật khẩu…" autocomplete="current-password" autofocus>
        <button class="reveal" type="button" id="reveal" aria-label="Hiện mật khẩu">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">
            <path d="M2.5 12S6 5.5 12 5.5 21.5 12 21.5 12 18 18.5 12 18.5 2.5 12 2.5 12Z"/>
            <circle cx="12" cy="12" r="3"/>
          </svg>
        </button>
      </div>
      <button class="submit" id="go" type="submit"><span class="t">Mở khoá</span><span class="arr">→</span></button>
      <div class="err" id="err" role="alert"></div>
    </form>
  </main>
  <div class="flash" id="flash"></div>
<script>
  var P = __PAYLOAD__;
  function b2u(b64){var s=atob(b64),a=new Uint8Array(s.length);for(var i=0;i<s.length;i++)a[i]=s.charCodeAt(i);return a;}
  var pw=document.getElementById('pw'), go=document.getElementById('go'), err=document.getElementById('err'),
      box=document.getElementById('box'), flash=document.getElementById('flash'),
      form=document.getElementById('form'), reveal=document.getElementById('reveal'), bg=document.getElementById('bg');

  // parallax nhẹ theo con trỏ (đổi vị trí ảnh nền, không đụng Ken Burns)
  window.addEventListener('mousemove',function(e){
    var dx=(e.clientX/window.innerWidth-0.5), dy=(e.clientY/window.innerHeight-0.5);
    bg.style.backgroundPosition=(50+dx*6).toFixed(2)+'% '+(50+dy*6).toFixed(2)+'%';
  });
  // glow theo con trỏ trên thẻ
  box.addEventListener('mousemove',function(e){
    var r=box.getBoundingClientRect();
    box.style.setProperty('--mx',((e.clientX-r.left)/r.width*100)+'%');
    box.style.setProperty('--my',((e.clientY-r.top)/r.height*100)+'%');
  });

  reveal.addEventListener('click',function(){
    var show=pw.type==='password';
    pw.type=show?'text':'password';
    reveal.classList.toggle('on',show);
    reveal.setAttribute('aria-label',show?'Ẩn mật khẩu':'Hiện mật khẩu');
    pw.focus();
  });

  function fail(msg){
    go.classList.remove('loading');
    box.classList.remove('shake'); void box.offsetWidth; box.classList.add('shake');
    err.textContent='✗ '+msg; err.classList.add('show');
  }

  async function unlock(){
    if(go.classList.contains('loading')) return;
    if(!pw.value){ fail('Vui lòng nhập mật khẩu.'); pw.focus(); return; }
    if(!window.crypto || !window.crypto.subtle){
      fail('WebCrypto không khả dụng — mở file trực tiếp (file://) hoặc qua HTTPS/localhost, không dùng HTTP thường.'); return;
    }
    if(P.gz && !window.DecompressionStream){
      fail('Trình duyệt quá cũ (thiếu DecompressionStream) — hãy cập nhật trình duyệt.'); return;
    }
    err.classList.remove('show'); err.textContent=''; go.classList.add('loading');
    await new Promise(function(r){setTimeout(r,30);});
    try{
      var enc=new TextEncoder();
      var km=await crypto.subtle.importKey('raw',enc.encode(pw.value),'PBKDF2',false,['deriveKey']);
      var key=await crypto.subtle.deriveKey({name:'PBKDF2',salt:b2u(P.salt),iterations:P.iter,hash:'SHA-256'},
        km,{name:'AES-GCM',length:256},false,['decrypt']);
      var plain=await crypto.subtle.decrypt({name:'AES-GCM',iv:b2u(P.iv)},key,b2u(P.ct));
      var html;
      if(P.gz){
        var ds=new Blob([plain]).stream().pipeThrough(new DecompressionStream('gzip'));
        html=await new Response(ds).text();
      }else{
        html=new TextDecoder().decode(plain);
      }
      flash.classList.add('go');
      setTimeout(function(){document.open();document.write(html);document.close();},300);
    }catch(e){
      if(e && e.name==='OperationError'){
        fail('Sai mật khẩu. Vui lòng thử lại.'); pw.select();
      }else{
        fail('Lỗi giải mã ('+(e&&e.name?e.name:'không rõ')+') — không phải do sai mật khẩu.');
      }
    }
  }

  form.addEventListener('submit',function(e){ e.preventDefault(); unlock(); });
</script>
</body>
</html>"""

if __name__ == "__main__":
    main()
