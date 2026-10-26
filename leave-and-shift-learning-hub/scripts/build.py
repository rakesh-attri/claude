#!/usr/bin/env python3
"""Builds an offline-friendly, sanitized static course bundle from source Markdown."""
import json,re,html,sys,shutil,urllib.request,os
from pathlib import Path
from urllib.parse import quote
ROOT=Path(__file__).resolve().parents[1]
CONTENT=ROOT/'content'
DATA=ROOT/'data'
try:
 from markdown_it import MarkdownIt
 import bleach
except ImportError:
 sys.exit('Install build dependencies: pip install -r requirements.txt')
md=MarkdownIt('commonmark',{'html':False,'linkify':True}).enable('table')
ALLOWED=set(bleach.sanitizer.ALLOWED_TAGS)|{'h1','h2','h3','h4','h5','h6','p','pre','code','img','hr','div','span','table','thead','tbody','tr','th','td','input','del','sup','sub'}
ATTR={'a':['href','title','target','rel'],'img':['src','alt','title','loading'],'code':['class'],'pre':['class'],'th':['align'],'td':['align'],'input':['type','checked','disabled'],'div':['class'],'span':['class']}
BRANCH='claude/bold-gauss-6bzbzk'
BASE='https://raw.githubusercontent.com/swapravo/leave_and_shift_management_system/'+BRANCH+'/content/'
FILES=['README.md','build-plan.md']+[f'day-{i}.md' for i in range(1,6)]
def hydrate():
 """Opt-in source sync. Never edit a local Markdown file unless --refresh is passed."""
 CONTENT.mkdir(exist_ok=True)
 for name in FILES:
  target=CONTENT/name
  if target.exists() and '--refresh' not in sys.argv: continue
  req=urllib.request.Request(BASE+quote(name),headers={'User-Agent':'learning-hub-content-builder'})
  try:
   with urllib.request.urlopen(req,timeout=20) as response: blob=response.read()
   target.write_bytes(blob)
   print('Fetched',name,len(blob),'bytes')
  except Exception as exc: print('Unable to fetch',name,':',exc,file=sys.stderr)
def clean_url(value):
 v=value.strip()
 if v.lower().startswith(('javascript:','data:','vbscript:')):return '#'
 return v

def render(source):
 raw=md.render(source)
 clean=bleach.clean(raw,tags=ALLOWED,attributes=ATTR,protocols=['http','https','mailto'],strip=True)
 # Resolve Markdown-relative source links from the site's root.
 clean=re.sub(r'(href|src)=([\"\'])(?!https?://|mailto:|#|/)([^\"\']+)\2',lambda m:m.group(1)+'='+m.group(2)+'content/'+m.group(3)+m.group(2),clean)
 return clean

def quiz_extract(source,lesson_id):
 # Multiple-choice material is preserved in lesson reading view. Auto-scoring is enabled
 # only when the original source explicitly marks correct answers with ✅.
 lines=source.splitlines(); quizzes=[]; q=None; options=[]
 def finish():
  nonlocal q,options
  if q and len(options)>=2 and any(x['correct'] for x in options):
   quizzes.append({'id':lesson_id+'-q'+str(len(quizzes)+1),'question':q,'options':options})
  q=None;options=[]
 for line in lines:
  s=line.strip()
  qm=re.match(r'^(?:\*\*)?Q(?:uestion)?\s*\d+\s*[.:)](?:\*\*)?\s*(.+)$',s,re.I)
  opt=re.match(r'^(?:[-*]\s*)?(?:\*\*)?([A-D])[).:]\s*(.+)$',s,re.I)
  if qm and '?' in s:
   finish();q=re.sub(r'\*','',qm.group(1)).strip()
  elif opt and q:
   val=opt.group(2).strip();correct='✅' in val
   options.append({'label':re.sub(r'\s*✅.*$','',val).strip(' *'),'correct':correct})
  elif q and s=='' :
   # tolerate a blank line before answer choices
   pass
  elif q and options and (s.startswith('#') or s.startswith('---')):finish()
 finish();return quizzes

def main():
 if '--sync' in sys.argv or '--refresh' in sys.argv:hydrate()
 DATA.mkdir(exist_ok=True)
 lessons=[]
 for i in range(1,6):
  path=CONTENT/f'day-{i}.md'
  if not path.exists(): continue
  source=path.read_text(encoding='utf-8')
  title=re.search(r'^#\s+(.+)',source,re.M)
  headings=[{'level':len(m.group(1)),'text':re.sub(r'[`*]','',m.group(2)).strip()} for m in re.finditer(r'^(#{2,4})\s+(.+)$',source,re.M)]
  plain=re.sub(r'[`*_#>\[\]()|]',' ',source)
  entry={'id':f'day-{i}','day':i,'title':title.group(1).strip() if title else f'Day {i}',
         'description':next((x.strip(' *') for x in source.splitlines() if x.startswith('*Day 0')),''),
         'source':f'content/day-{i}.md','html':render(source),'text':plain,'headings':headings,
         'quizzes':quiz_extract(source,f'day-{i}'),'wordCount':len(plain.split())}
  lessons.append(entry)
 manifest={'id':'claude-code-upskilling','title':'Claude Code Upskilling','description':'A five-day course by Swapravo Sinha Roy, based on the original Markdown learning material.','author':'Swapravo Sinha Roy','sourceBranch':BRANCH,'lessons':lessons,
 'resources':[{'title':n,'path':'content/'+n} for n in ['README.md','build-plan.md'] if (CONTENT/n).exists()]}
 (DATA/'course.json').write_text(json.dumps(manifest,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
 print('Generated',len(lessons),'lessons,',sum(len(x['quizzes']) for x in lessons),'source-marked quizzes')
 if len(lessons)!=5:sys.exit('Build incomplete: expected five original course days. Run python scripts/build.py --sync with internet access.')
 for l in lessons:
  for match in re.findall(r'(?<!!)\]\(([^)]+)\)',(CONTENT/f"{l['id']}.md").read_text(encoding="utf-8")):
   link=match.strip().split(' ')[0]
   if link.startswith(('http:','https:','#','mailto:')):continue
   if link.lower().endswith('.html'):continue # legacy source pages, referenced as authored
   if not (CONTENT/link).exists() and not (ROOT/link).exists():print('WARNING unresolved source link:',l['id'],link)
 print('Built data/course.json')
if __name__=='__main__':main()
