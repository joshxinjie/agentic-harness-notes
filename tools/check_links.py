# Usage: python3 tools/check_links.py .   (reports broken internal links/anchors and leftover Gmail redirect URLs)
import re,os,sys,glob
root=sys.argv[1]
def slug(h):
    h=h.strip().lower()
    h=re.sub(r'[^\w\- ]','',h)
    return h.replace(' ','-')
anchors={}
files=glob.glob(root+'/*.md')+glob.glob(root+'/weeks/*.md')
for f in files:
    s=set();cnt={}
    inc=False
    for line in open(f):
        if line.startswith('```'): inc=not inc
        if inc: continue
        m=re.match(r'#+ (.*)',line)
        if m:
            a=slug(m.group(1)); 
            if a in cnt: cnt[a]+=1; a=f"{a}-{cnt[a]}"
            else: cnt[a]=0
            s.add(a)
    anchors[os.path.abspath(f)]=s
bad=0
for f in files:
    txt=open(f).read()
    txt=re.sub(r'```.*?```','',txt,flags=re.S); txt=re.sub(r'`[^`\n]*`','',txt)
    for m in re.finditer(r'\]\(([^)\s]+)\)',txt):
        u=m.group(1)
        if u.startswith('http') or u.startswith('mailto'): 
            if 'google.com/url' in u: print('REDIRECT',f,u); bad+=1
            continue
        p,_,a=u.partition('#')
        t=os.path.abspath(os.path.join(os.path.dirname(f),p)) if p else os.path.abspath(f)
        if t not in anchors:
            if not p.endswith('.md') and os.path.exists(t): continue
            print('NOFILE',f,u); bad+=1; continue
        if a and a not in anchors[t]: print('NOANCHOR',os.path.basename(f),u); bad+=1
print('bad',bad)
