"""Align the script phrases (voice/slots.json) to the speech in voice/full-take.wav -> build/align.json."""
import json, re, wave, numpy as np, sys
import pathlib; R=str(pathlib.Path(__file__).parent)+'/'
w=wave.open(R+'voice/full-take.wav'); fs=w.getframerate(); x=np.frombuffer(w.readframes(w.getnframes()),'<i2')/32768.
# speech segments by 20ms energy
hop=int(.02*fs); fr=np.sqrt(np.add.reduceat(x**2,np.arange(0,len(x),hop))/hop); db=20*np.log10(fr+1e-9)
sp=db>-40
# close gaps < 0.22 s, drop blips < 0.12 s
segs=[];i=0;n=len(sp)
while i<n:
    if sp[i]:
        j=i
        while j<n and sp[j]: j+=1
        segs.append([i*.02,j*.02]); i=j
    else: i+=1
m=[]
for s in segs:
    if m and s[0]-m[-1][1]<.25: m[-1][1]=s[1]
    else: m.append(s)
segs=[s for s in m if s[1]-s[0]>.12]
slots=json.load(open(R+'voice/slots.json'))
ph=[]
for s in slots:
    parts=[p.strip() for p in re.split(r'(?<=[…؟.:])\s*',s['text']) if p.strip()]
    for p in parts: ph.append((s['id'],p))
strip=lambda t: re.sub(r'[ً-ْ\s….؟:،]','',t)
L=[len(strip(p)) for _,p in ph]
tot_sp=sum(b-a for a,b in segs); r=tot_sp/sum(L)
P,S=len(ph),len(segs)
INF=1e18
# dp[i][j]: first i phrases matched to first j segments. moves: k phrases->1 seg (k=1..4), 1 phrase->2 segs
dp=np.full((P+1,S+1),INF); bk={}
dp[0][0]=0
for i in range(P+1):
  for j in range(S+1):
    if dp[i][j]>=INF: continue
    for k in range(1,5):
      if i+k<=P and j+1<=S:
        exp=r*sum(L[i:i+k]); d=segs[j][1]-segs[j][0]
        gaps=k-1
        c=dp[i][j]+(d-exp-0.25*gaps)**2/(exp+.3)+0.15*gaps
        if c<dp[i+k][j+1]: dp[i+k][j+1]=c; bk[(i+k,j+1)]=(i,j)
    if i+1<=P and j+2<=S:
        exp=r*L[i]; d=segs[j+1][1]-segs[j][0]
        c=dp[i][j]+(d-exp-.4)**2/(exp+.3)+0.6
        if c<dp[i+1][j+2]: dp[i+1][j+2]=c; bk[(i+1,j+2)]=(i,j)
i,j=P,S; path=[]
while (i,j)!=(0,0):
    pi,pj=bk[(i,j)]; path.append((pi,i,pj,j)); i,j=pi,pj
path.reverse()
# pitch (autocorr) median per segment
def pitch(a,b):
    y=x[int(a*fs):int(b*fs)]; f=[]
    for k in range(0,len(y)-2048,1024):
        z=y[k:k+2048]; 
        if np.sqrt((z**2).mean())<.01: continue
        c=np.correlate(z,z,'full')[2047:]; lo,hi=int(fs/300),int(fs/70)
        l=lo+np.argmax(c[lo:hi]); f.append(fs/l)
    return np.median(f) if f else 0
out=[]
for pi,i2,pj,j2 in path:
    a,b=segs[pj][0],segs[j2-1][1]
    for q in range(pi,i2):
        pass
    ids=sorted(set(ph[q][0] for q in range(pi,i2)))
    txt=' '.join(ph[q][1] for q in range(pi,i2))
    print(f"{a:6.2f}-{b:6.2f} ({b-a:4.2f}s exp {r*sum(L[pi:i2]):4.2f}) f0 {pitch(a,b):5.0f}  {','.join(ids):8s} {txt}")
    out.append(dict(a=a,b=b,phr=list(range(pi,i2)),ids=ids))
json.dump(dict(ph=ph,al=out),open(R+'build/align.json','w'),ensure_ascii=False)
print('rate',round(1/r,1),'chars/s', 'segs',S,'phrases',P)
