"""Build the static timeline from timeline-posts.json. Run with Python 3."""
from pathlib import Path
import json,html,re
from urllib.parse import quote,unquote
root=Path(__file__).resolve().parents[1]
data=json.loads((root/'timeline-posts.json').read_text())
data['posts']=[json.loads(f.read_text()) for f in sorted((root/'posts').glob('*.json'))]
posts=sorted(data['posts'],key=lambda p:p['date'],reverse=True)
seen=set()
for p in posts:
 path=Path(p['path'])
 if path.is_absolute() or '..' in path.parts or not re.fullmatch(r'\d{4}',path.parts[0]): raise ValueError('Invalid article path: '+p['path'])
 if p['path'] in seen: raise ValueError('Duplicate article path: '+p['path'])
 seen.add(p['path'])
 p.setdefault('categories',[]); p.setdefault('tags',[])
 if 'markdown' in p:
  import markdown
  p['body']=markdown.markdown(p['markdown'],extensions=['extra','sane_lists','nl2br'])
 p['excerpt']=re.sub(r'\s+',' ',html.unescape(re.sub('<[^>]+>',' ',p['body']))).strip()[:155]
 image=re.search(r'<img[^>]+src="([^"]+)"',p['body']); p['image']=image.group(1) if image else ''
# Remove only previously generated article pages whose sources were deleted.
for old in json.loads((root/'timeline-posts.json').read_text())['posts']:
 if old['path'] not in seen:
  target=root/old['path']/'index.html'
  if target.exists() and '/assets/timeline/style.css' in target.read_text(): target.unlink()
(root/'timeline-posts.json').write_text(json.dumps(data,ensure_ascii=False,indent=2))
# New dates and taxonomies get their own archive pages.
for p in posts:
 for directory in ['archives', 'archives/'+p['date'][:4], 'archives/'+p['date'][:4]+'/'+p['date'][5:7]]+[key+'/'+c['name'] for key in ['categories','tags'] for c in p[key]]:
  target=root/directory
  if '..' in Path(directory).parts: raise ValueError('Invalid archive path')
  target.mkdir(parents=True,exist_ok=True); (target/'index.html').touch()

e=lambda x:html.escape(str(x),quote=True)
def url(p):return '/'+quote(p['path'],safe='/')
def shell(title,body,home=False):
 return f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{e(title)} · 攸然自得</title><meta name="description" content="Tiney 的生活记录与成长日记"><link rel="stylesheet" href="/assets/timeline/style.css"><script defer src="/assets/timeline/app.js"></script></head><body><nav class="topnav"><a class="brand" href="/">TINEY / 攸然自得</a><div><a href="/">时间线</a><a href="/archives/">归档</a><a href="/photography/">摄影</a></div></nav>{'<header class="hero"><div class="diamond"></div><div class="hero-content"><span class="eyebrow">LIFE, ONE MOMENT AT A TIME</span><h1>攸然自得</h1><p>把日子写下来，让每一个平凡的瞬间有迹可循。</p><a class="start" href="#timeline">开始阅读 ↓</a></div><span class="hero-foot">TINEY’S JOURNAL · 记录生活</span></header>' if home else ''}{body}<footer>© Tiney · 攸然自得 <span>时间串起生活，文字留住记忆。</span></footer><dialog id="lightbox"><button aria-label="关闭图片">×</button><img alt="放大图片"></dialog></body></html>'''
def card(p):
 category=' · '.join(c['name'] for c in p['categories']) or '生活记录'
 return f'''<article class="card" data-date="{p['date']}" data-search="{e(p['title']+' '+p['excerpt'])}"><span class="dot"></span>{f'<a href="{url(p)}" class="card-image"><img loading="lazy" src="{e(p["image"])}" alt="{e(p["title"])}"></a>' if p['image'] else ''}<div class="card-content"><span class="category">{e(category)}</span><h2><a href="{url(p)}">{e(p['title'])}</a></h2><div class="meta">Tiney <span>·</span> <time>{p['date']}</time></div><p>{e(p['excerpt'])}…</p><a class="read" href="{url(p)}">阅读全文 <span>→</span></a></div></article>'''
def listing(title,selected,home=False):
 years=sorted({p['date'][:4] for p in selected},reverse=True)
 controls='<button class="year active" data-year="all">全部</button>'+''.join(f'<button class="year" data-year="{y}">{y}</button>' for y in years)
 content=f'<main id="timeline" class="timeline-main"><div class="section-title"><div><span class="eyebrow">THE TIMELINE</span><h2>{e(title)}</h2></div><p>{len(selected)} 篇记录 · 慢慢走，认真记</p></div><div class="toolbar"><div class="years">{controls}</div><label class="search"><span>⌕</span><input type="search" placeholder="搜索日记…" aria-label="搜索日记"></label></div><div class="timeline">'+''.join(card(p) for p in selected)+'</div><p class="empty" hidden>没有找到相关记录。</p><a class="back-top" href="#timeline">回到时间线顶部 ↑</a></main>'
 return shell(title,content,home)
# Preserve every existing article URL, with the original HTML body.
for i,p in enumerate(posts):
 links=''
 for label,j in [('较新的记录',i-1),('较早的记录',i+1)]:
  if 0<=j<len(posts): links+=f'<a href="{url(posts[j])}"><small>{label}</small>{e(posts[j]["title"])} →</a>'
 body=f'<main class="post-main"><a class="crumb" href="/">← 返回时间线</a><article class="post"><header><span class="category">生活记录 / JOURNAL</span><h1>{e(p["title"])}</h1><div class="meta">Tiney · <time>{p["date"]}</time></div></header><div class="post-body">{p["body"]}</div></article><nav class="post-nav">{links}</nav></main>'
 (root/p['path']).mkdir(parents=True,exist_ok=True)
 (root/p['path']/'index.html').write_text(shell(p['title'],body))
(root/'index.html').write_text(listing('生活的时间线',posts,True))
# Rebuild existing archives, categories, tags and paginated URLs.
for folder in ['archives','categories','tags','page']:
 for file in (root/folder).rglob('index.html'):
  parts=file.relative_to(root).parts; selected=posts; title='所有记录'
  if folder=='archives':
   digits=[x for x in parts[1:] if re.fullmatch(r'\d{4}|\d{2}',x)]
   if digits: selected=[p for p in posts if p['date'].startswith('-'.join(digits))]; title=' / '.join(digits)+' · 归档'
  if folder in ['categories','tags'] and len(parts)>2:
   name=unquote(parts[1]); key='categories' if folder=='categories' else 'tags'; selected=[p for p in posts if any(c['name']==name for c in p[key])]; title=name
  file.write_text(listing(title,selected))
for name,content in json.loads((root/'timeline-pages.json').read_text()).items():
 title='摄影' if name=='photography' else '关于'
 (root/name/'index.html').write_text(shell(title,f'<main class="post-main"><a class="crumb" href="/">← 返回时间线</a><article class="post"><h1>{title}</h1><div class="post-body">{content or "<p>这里留给镜头捕捉的生活瞬间。</p>"}</div></article></main>'))
