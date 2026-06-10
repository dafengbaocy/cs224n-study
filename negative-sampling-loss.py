#!/usr/bin/env python3
"""
CS224N L01 Word Vectors - Code Capsule: negative-sampling-loss (WP05)
Concept: Negative Sampling (SGNS) vs Full Softmax
Anchor: Notes 3.5 (Eq.14-15); R02 paper Section 3
"""
import math, random, json, os, copy

random.seed(42)
VOCAB = ["bank","river","money","loan","stock","market","cat","dog","car","book"]
VS = len(VOCAB); D = 4
w2i = {w:i for i,w in enumerate(VOCAB)}
i2w = {i:w for w,i in w2i.items()}

def mkvec(vs, d, s=42):
    random.seed(s)
    return [[random.gauss(0,0.1) for _ in range(d)] for _ in range(vs)]

V = mkvec(VS, D, 42); U = mkvec(VS, D, 99)

def dot(a,b): return sum(x*y for x,y in zip(a,b))
def sig(x):
    if x>=0: return 1.0/(1.0+math.exp(-x))
    e=math.exp(x); return e/(1.0+e)
def sfx(scores):
    m=max(scores); e=[math.exp(s-m) for s in scores]; t=sum(e); return [x/t for x in e]
def vsub(a,b): return [x-y for x,y in zip(a,b)]
def vadd(a,b): return [x+y for x,y in zip(a,b)]
def vscl(a,c): return [x*c for x in a]
def vnorm(a): return math.sqrt(sum(x*x for x in a))
def cosim(a,b):
    na,nb=vnorm(a),vnorm(b)
    return dot(a,b)/(na*nb) if na and nb else 0.0

cw="bank"; pw="river"; ci=w2i[cw]; pi=w2i[pw]
K=5
negs=random.sample([i for i in range(VS) if i!=pi], K)
nw=[i2w[i] for i in negs]

print("="*70)
print("CS224N L01 Code Capsule: Negative Sampling Loss vs Full Softmax")
print("="*70)
print(f"\nVocabulary |V|={VS}, dim d={D}")
print(f"Center: {cw} (idx={ci}), Positive: {pw} (idx={pi})")
print(f"Negatives k={K}: {nw} (indices={negs})\n")

print("-"*70)
print("[Part A] Full Softmax Loss (Notes 3.2 Eq.4-5)")
print("-"*70+"\n")
vc=V[ci]
scores=[dot(vc,U[j]) for j in range(VS)]
probs=sfx(scores)
L_sm=-math.log(probs[pi])

print(f"{'Word':<10}{'Score':>12}{'P(w|c)':>12}  Label")
print("-"*50)
for j in range(VS):
    lb=""
    if j==pi: lb="<- positive"
    elif i2w[j] in nw: lb="<- negative"
    print(f"{i2w[j]:<10}{scores[j]:>12.6f}{probs[j]:>12.6f}  {lb}")
print(f"\nFull Softmax loss = -log P({pw}|{cw}) = -log({probs[pi]:.6f}) = {L_sm:.6f}")
print(f"Cost: O(|V|) = O({VS})\n")

print("-"*70)
print("[Part B] Negative Sampling Loss (Notes 3.5 Eq.15)")
print("-"*70+"\n")
sp=dot(vc,U[pi]); Lp=-math.log(sig(sp))
nscores=[dot(vc,U[k]) for k in negs]
Lnt=[-math.log(sig(-s)) for s in nscores]
Ln=sum(Lnt); Lsgns=Lp+Ln

print(f"Positive: -log sigma({sp:.6f}) = {Lp:.6f}\n")
print(f"{'Neg':<10}{'u^Tv':>10}{'sigma(-u^Tv)':>14}{'-log sig':>12}")
print("-"*48)
for ki,s in zip(negs,nscores):
    print(f"{i2w[ki]:<10}{s:>10.6f}{sig(-s):>14.6f}{-math.log(sig(-s)):>12.6f}")
print(f"{'Sum':<10}{'':>10}{'':>14}{Ln:>12.6f}")
print(f"\nSGNS loss = {Lp:.6f} + {Ln:.6f} = {Lsgns:.6f}")
print(f"Cost: O(k) = O({K+1})\n")

print("-"*70)
print("[Part C] Loss Comparison")
print("-"*70+"\n")
print(f"{'Method':<20}{'Loss':>12}{'Terms':>8}  Complexity")
print("-"*55)
print(f"{'Full Softmax':<20}{L_sm:>12.6f}{VS:>8}  O(|V|)=O({VS})")
print(f"{'Neg. Sampling':<20}{Lsgns:>12.6f}{K+1:>8}  O(k)=O({K+1})")
print(f"\nSpeedup: |V|/k = {VS/K:.1f}x; at |V|=100k: 20,000x\n")

print("-"*70)
print("[Part D] Gradient Analysis")
print("-"*70+"\n")
eu=[0.0]*D
for j in range(VS):
    for d in range(D): eu[d]+=probs[j]*U[j][d]
g_sm=vsub(eu,U[pi])
sp_sig=sig(sp)
g_sg=vscl(U[pi],sp_sig-1.0)
for i in range(K):
    g_sg=vadd(g_sg,vscl(U[negs[i]],sig(-nscores[i])))

print(f"Full Softmax grad: [{', '.join(f'{g:.6f}' for g in g_sm)}]  norm={vnorm(g_sm):.6f}")
print(f"  touches {VS} outside vectors (ALL)\n")
print(f"SGNS grad: [{', '.join(f'{g:.6f}' for g in g_sg)}]  norm={vnorm(g_sg):.6f}")
print(f"  touches {K+1} outside vectors\n")
u_sm=vscl(g_sm,-1); u_sg=vscl(g_sg,-1)
print(f"Update (-grad):")
print(f"  Softmax: [{', '.join(f'{g:.6f}' for g in u_sm)}]")
print(f"  SGNS:    [{', '.join(f'{g:.6f}' for g in u_sg)}]\n")

print("-"*70)
print("[Part E] Training: Pull Positive, Push Negatives")
print("-"*70+"\n")
Vt=copy.deepcopy(V); Ut=copy.deepcopy(U)
lr=0.05; N=100
hist={"step":[],"pos":[],"neg":[]}
for step in range(N+1):
    pc=cosim(Vt[ci],Ut[pi])
    nc=[cosim(Vt[ci],Ut[k]) for k in negs]
    an=sum(nc)/len(nc)
    if step%20==0 or step==N:
        hist["step"].append(step); hist["pos"].append(round(pc,4)); hist["neg"].append(round(an,4))
    if step==N: break
    vcs=list(Vt[ci])
    sp_d=dot(vcs,Ut[pi]); sg_p=sig(sp_d)
    Ut[pi]=vsub(Ut[pi],vscl(vcs,sg_p-1.0,lr) if False else vscl(vscl(vcs,sg_p-1.0),lr))
    for ki in negs:
        sk=dot(vcs,Ut[ki]); sg_k=sig(sk)
        Ut[ki]=vsub(Ut[ki],vscl(vscl(vcs,1.0-sg_k),lr))

fpc=cosim(Vt[ci],Ut[pi])
fnc=[cosim(Vt[ci],Ut[k]) for k in negs]
fan=sum(fnc)/len(fnc)
print(f"Config: lr={lr}, steps={N}, k={K}\n")
print(f"{'Step':<8}{'cos(pos)':<16}{'avg cos(neg)'}")
print("-"*40)
for i in range(len(hist["step"])):
    print(f"{hist['step'][i]:<8}{hist['pos'][i]:<16.4f}{hist['neg'][i]:.4f}")
pd="UP (closer)" if fpc>hist["pos"][0] else "DOWN"
nd="DOWN (apart)" if fan<hist["neg"][0] else "UP"
print(f"\nPositive cos: {hist['pos'][0]:.4f} -> {fpc:.4f} ({pd})")
print(f"Negative avg cos: {hist['neg'][0]:.4f} -> {fan:.4f} ({nd})")

odir=os.path.join(os.path.dirname(os.path.abspath(__file__)),"outputs")
os.makedirs(odir,exist_ok=True)
res={"vocab_size":VS,"embedding_dim":D,"center_word":cw,"positive_word":pw,
     "negative_words":nw,"negative_k":K,
     "full_softmax":{"loss":round(L_sm,6),"positive_prob":round(probs[pi],6),
                     "terms":VS,"complexity":f"O(|V|)=O({VS})"},
     "negative_sampling":{"loss":round(Lsgns,6),"positive_loss":round(Lp,6),
                          "negative_loss":round(Ln,6),"positive_sigmoid":round(sig(sp),6),
                          "terms":K+1,"complexity":f"O(k)=O({K+1})"},
     "training":{"lr":lr,"steps":N,"init_pos_cos":hist["pos"][0],
                 "final_pos_cos":round(fpc,4),"init_neg_cos":hist["neg"][0],
                 "final_neg_cos":round(fan,4),"history":hist}}
jp=os.path.join(odir,"negative-sampling-loss-results.json")
with open(jp,"w") as f: json.dump(res,f,indent=2,ensure_ascii=False)
print(f"\nSaved: {jp}")

try:
    import matplotlib; matplotlib.use('Agg')
    import matplotlib.pyplot as plt; import numpy as np
    fig,axes=plt.subplots(1,3,figsize=(18,5))
    fig.suptitle('Negative Sampling vs Full Softmax (CS224N L01 WP05)',fontsize=14,fontweight='bold')
    cols=['#e74c3c' if j==pi else '#3498db' if i2w[j] in nw else '#95a5a6' for j in range(VS)]
    axes[0].bar(range(VS),probs,color=cols)
    axes[0].set_xticks(range(VS)); axes[0].set_xticklabels(VOCAB,rotation=45,ha='right',fontsize=8)
    axes[0].set_ylabel('P(w|c)'); axes[0].set_title('Full Softmax probabilities')
    axes[0].axhline(1/VS,color='k',ls='--',alpha=.5)
    cats=['Full SM','SGNS pos','SGNS neg','SGNS total']
    vals=[L_sm,Lp,Ln,Lsgns]; bcols=['#e74c3c','#2ecc71','#3498db','#9b59b6']
    bars=axes[1].bar(cats,vals,color=bcols)
    axes[1].set_ylabel('Loss'); axes[1].set_title('Loss Comparison')
    for b,v in zip(bars,vals): axes[1].text(b.get_x()+b.get_width()/2,v+.02,f'{v:.3f}',ha='center',fontsize=9)
    axes[2].plot(hist["step"],hist["pos"],'o-',color='#e74c3c',label='cos(pos)',lw=2)
    axes[2].plot(hist["step"],hist["neg"],'s-',color='#3498db',label='avg cos(neg)',lw=2)
    axes[2].set_xlabel('Step'); axes[2].set_ylabel('Cosine'); axes[2].set_title('Training dynamics')
    axes[2].legend(); axes[2].grid(True,alpha=.3)
    plt.tight_layout()
    fp=os.path.join(odir,"negative-sampling-loss-comparison.png")
    plt.savefig(fp,dpi=150,bbox_inches='tight'); plt.close()
    print(f"Plot: {fp}")
    fig2,(a4,a5)=plt.subplots(1,2,figsize=(12,5))
    fig2.suptitle('Gradient: Softmax vs SGNS',fontsize=13,fontweight='bold')
    x=np.arange(D); w=.35; dims=[f'd{i}' for i in range(D)]
    a4.bar(x-w/2,g_sm,w,label='Softmax',color='#e74c3c',alpha=.8)
    a4.bar(x+w/2,g_sg,w,label='SGNS',color='#3498db',alpha=.8)
    a4.set_xticks(x); a4.set_xticklabels(dims); a4.set_ylabel('Gradient'); a4.legend(); a4.grid(True,alpha=.3,axis='y')
    a5.bar(x-w/2,u_sm,w,label='Softmax',color='#e74c3c',alpha=.8)
    a5.bar(x+w/2,u_sg,w,label='SGNS',color='#3498db',alpha=.8)
    a5.set_xticks(x); a5.set_xticklabels(dims); a5.set_ylabel('Update (-grad)'); a5.legend(); a5.grid(True,alpha=.3,axis='y')
    plt.tight_layout()
    fp2=os.path.join(odir,"negative-sampling-loss-gradient.png")
    plt.savefig(fp2,dpi=150,bbox_inches='tight'); plt.close()
    print(f"Gradient plot: {fp2}")
except ImportError as e:
    print(f"[WARN] no matplotlib: {e}")
print("\nDONE")
