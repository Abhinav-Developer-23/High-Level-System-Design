#!/usr/bin/env python3
"""Step 2 QA: render + lint SVGs with headless Windows Chrome (the SVG files must live under C:).
usage: python3 tools/svg-diagrams/svgcheck.py file1.svg [file2.svg ...]
 - writes out/<name>.png (gitignored) for visual review
 - prints JSON issues: text outside canvas, text overflowing its enclosing rect, text/text overlaps
"""
import sys, os, json, subprocess, re, html, pathlib
CHROME="/mnt/c/Program Files/Google/Chrome/Application/chrome.exe"
OUT=pathlib.Path(__file__).resolve().parent/"out"; OUT.mkdir(exist_ok=True)
WORK=OUT
def win(p):
    p=str(pathlib.Path(p).resolve())
    assert p.startswith("/mnt/c/"), p
    return "C:\\"+p[7:].replace("/","\\")
JS=r"""
<script>
window.onload=()=>{
 const res={};
 document.querySelectorAll('.case').forEach(c=>{
  const svg=c.querySelector('svg'); const sb=svg.getBoundingClientRect(); const issues=[];
  const texts=[...svg.querySelectorAll('text')].filter(t=>t.textContent.trim());
  const rects=[...svg.querySelectorAll('rect')].map(r=>({el:r,b:r.getBoundingClientRect()})).filter(r=>r.b.width<sb.width-4||r.b.height<sb.height-4);
  const tb=texts.map(t=>({t, b:t.getBoundingClientRect(), s:t.textContent.trim().slice(0,40)}));
  for(const x of tb){
    const b=x.b;
    if(b.left<sb.left-0.5||b.right>sb.right+0.5||b.top<sb.top-0.5||b.bottom>sb.bottom+0.5) issues.push('OUTSIDE CANVAS: "'+x.s+'"');
    // enclosing rect = smallest rect containing text center
    const cx=(b.left+b.right)/2, cy=(b.top+b.bottom)/2;
    const enc=rects.filter(r=>cx>r.b.left&&cx<r.b.right&&cy>r.b.top&&cy<r.b.bottom).sort((p,q)=>p.b.width*p.b.height-q.b.width*q.b.height)[0];
    if(enc && !x.t.closest('[data-nocheck]')){
      const e=enc.b, pad=2;
      if(b.left<e.left+pad||b.right>e.right-pad||b.top<e.top||b.bottom>e.bottom) issues.push('OVERFLOWS BOX: "'+x.s+'" ('+Math.round(Math.max(e.left+pad-b.left,b.right-(e.right-pad)))+'px)');
    }
  }
  for(let i=0;i<tb.length;i++)for(let j=i+1;j<tb.length;j++){
    const a=tb[i].b,b=tb[j].b; const ox=Math.min(a.right,b.right)-Math.max(a.left,b.left), oy=Math.min(a.bottom,b.bottom)-Math.max(a.top,b.top);
    if(ox>2&&oy>3) issues.push('TEXT OVERLAP: "'+tb[i].s+'" <> "'+tb[j].s+'"');
  }
  res[c.dataset.name]={w:Math.round(sb.width),h:Math.round(sb.height),issues};
 });
 document.body.innerHTML='<pre id="out">'+JSON.stringify(res)+'</pre>';
};
</script>"""
files=sys.argv[1:]
parts=[]
for f in files:
    s=open(f,encoding='utf-8').read()
    s=re.sub(r'<\?xml[^>]*\?>','',s)
    parts.append(f'<div class="case" data-name="{html.escape(os.path.basename(f))}">{s}</div>')
page=WORK/f"_lint_{os.getpid()}.html"
page.write_text('<!doctype html><html><body style="margin:0;background:#0d1117">'+''.join(parts)+JS+'</body></html>',encoding='utf-8')
r=subprocess.run([CHROME,"--headless=new","--disable-gpu","--virtual-time-budget=3000","--dump-dom","file:///"+win(page).replace("\\","/")],capture_output=True,text=True,timeout=120)
m=re.search(r'<pre id="out">(.*?)</pre>',r.stdout,re.S)
data=json.loads(html.unescape(m.group(1))) if m else {"error":r.stdout[-500:]+r.stderr[-500:]}
# screenshots
for f in files:
    s=open(f,encoding='utf-8').read()
    w=re.search(r'<svg[^>]*\swidth="([\d.]+)"',s); h=re.search(r'<svg[^>]*\sheight="([\d.]+)"',s)
    if not(w and h): continue
    W,H=int(float(w.group(1)))+16,int(float(h.group(1)))+16
    hp=WORK/f"_shot_{os.getpid()}.html"
    hp.write_text(f'<!doctype html><html><body style="margin:8px;background:#0d1117">{re.sub(r"<[?]xml[^>]*[?]>","",s)}</body></html>',encoding='utf-8')
    png=OUT/(pathlib.Path(f).stem+".png")
    subprocess.run([CHROME,"--headless=new","--disable-gpu","--hide-scrollbars",f"--window-size={W},{H}",f"--screenshot={win(png)}","file:///"+win(hp).replace("\\","/")],capture_output=True,timeout=120)
    if isinstance(data,dict) and os.path.basename(f) in data: data[os.path.basename(f)]["png"]=str(png)
for f in OUT.glob(f"_*_{os.getpid()}.html"): f.unlink()
print(json.dumps(data,indent=1,ensure_ascii=False))
