import numpy as np, torch, random, time
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import cross_val_score
from sklearn.metrics import roc_auc_score, balanced_accuracy_score
from transformers import AutoTokenizer, AutoModel
from concept_erasure import LeaceEraser
from data import make_base, make_cv, label

random.seed(0); np.random.seed(0); torch.manual_seed(0)
N_BASE=600
bases=[make_base(i) for i in range(N_BASE)]
rows=[]
for i,b in enumerate(bases):
    for g in ['F','M']:
        y,p=label(b,g,seed=10000+i*2+(g=='M'))
        rows.append(dict(base=i,gender=g,text=make_cv(b,g),y=y,p=p,q=b['q'],job=b['job']))
print('rows',len(rows),'label rate',np.mean([r['y'] for r in rows]))
print('female label rate',np.mean([r['y'] for r in rows if r['gender']=='F']),'male',np.mean([r['y'] for r in rows if r['gender']=='M']))

tok=AutoTokenizer.from_pretrained('sentence-transformers/all-MiniLM-L6-v2')
model=AutoModel.from_pretrained('sentence-transformers/all-MiniLM-L6-v2',output_hidden_states=True).eval()
texts=[r['text'] for r in rows]
t=time.time()
with torch.no_grad():
    enc=tok(texts,padding=True,truncation=True,max_length=256,return_tensors='pt')
    out=model(**enc)
print('encode sec',round(time.time()-t,1))
H=torch.stack(out.hidden_states,dim=1).numpy()  # n, layers, seq, dim
print('H',H.shape)
Hcls=H[:,:,0,:]
X=Hcls[:,6,:]  # last layer CLS
y=np.array([r['y'] for r in rows]); g=np.array([1 if r['gender']=='M' else 0 for r in rows])
base=np.array([r['base'] for r in rows])
# split by base
rng=np.random.default_rng(0); idx=rng.permutation(N_BASE); tr_bases=set(idx[:480].tolist()); tr=np.array([i for i,r in enumerate(rows) if r['base'] in tr_bases]); ho=np.array([i for i,r in enumerate(rows) if r['base'] not in tr_bases])
print('train/test',len(tr),len(ho))
sc=StandardScaler().fit(X[tr]); Xtr=sc.transform(X[tr]); Xte=sc.transform(X[ho])
clf=LogisticRegression(max_iter=2000,C=0.5).fit(Xtr,y[tr])
proba=clf.predict_proba(Xte)[:,1]
print('AUC',roc_auc_score(y[ho],proba),'bal acc',balanced_accuracy_score(y[ho],proba>0.5))
# gap on heldout pairs
def gap(pred, mask):
    d={}
    for gi,gg in [(0,'F'),(1,'M')]:
        vals=[pred[k] for k in np.where(mask & (g[ho]==gi))[0]]
        d[gg]=np.mean(vals)
    return d, d['F']-d['M']
mask=np.ones(len(ho),bool)
print('full gap',gap(proba,mask))
# probe gender layer by layer
for l in range(Hcls.shape[1]):
    Xl=Hcls[ho,l,:]
    sc2=StandardScaler().fit(Xl)
    clfp=LogisticRegression(max_iter=1000,C=1.0).fit(sc2.transform(Xl),g[ho])
    print('layer',l,'probe acc',clfp.score(sc2.transform(Xl),g[ho]))
# LEACE on layer 6 train set
Xtr_raw=torch.tensor(Hcls[tr,6,:],dtype=torch.float32); ztr=torch.tensor(g[tr],dtype=torch.int64)
er=LeaceEraser.fit(Xtr_raw,ztr)
Xtr_e=er(Xtr_raw).numpy(); Xho_e=er(torch.tensor(Hcls[ho,6,:],dtype=torch.float32)).numpy()
sc3=StandardScaler().fit(Xtr_e); clf3=LogisticRegression(max_iter=2000,C=0.5).fit(sc3.transform(Xtr_e),y[tr])
p3=clf3.predict_proba(sc3.transform(Xho_e))[:,1]
print('LEACE AUC',roc_auc_score(y[ho],p3),'gap',gap(p3,mask))
# probe after
sc4=StandardScaler().fit(Xho_e); clfp=LogisticRegression(max_iter=1000).fit(sc4.transform(Xho_e),g[ho])
print('LEACE probe acc',clfp.score(sc4.transform(Xho_e),g[ho]))
# cosine between before/after mean diff
v_before=Hcls[ho,6,:][g[ho]==0].mean(0)-Hcls[ho,6,:][g[ho]==1].mean(0)
v_after=Xho_e[g[ho]==0].mean(0)-Xho_e[g[ho]==1].mean(0)
print('cos',np.dot(v_before,v_after)/(np.linalg.norm(v_before)*np.linalg.norm(v_after)))
print('norm before',np.linalg.norm(v_before),'after',np.linalg.norm(v_after),'mean norm',np.mean(np.linalg.norm(Hcls[ho,6,:],axis=1)))
