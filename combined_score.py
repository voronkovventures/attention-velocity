import os, time, requests, math

# On-chain + X social velocity combined

BEARER=os.getenv('X_BEARER_TOKEN')
if not BEARER:
    raise SystemExit('Missing X_BEARER_TOKEN')
HEADERS={'Authorization': f'Bearer {BEARER}'}


def fetch_trending():
    url='https://api.geckoterminal.com/api/v2/networks/solana/trending_pools'
    js=requests.get(url,params={'include':'base_token,quote_token'},timeout=20).json()
    inc={}
    for item in js.get('included',[]):
        if item.get('type')=='token':
            inc[item['id']]=item['attributes']
    rows=[]
    for p in js['data']:
        attr=p['attributes']
        rel=p.get('relationships',{}).get('base_token',{}).get('data',{})
        token=inc.get(rel.get('id'),{})
        sym=token.get('symbol') or attr.get('name')
        vol=attr.get('volume_usd',{})
        tx=attr.get('transactions',{})
        v5=float(vol.get('m5',0) or 0)
        v15=float(vol.get('m15',0) or 0)
        v1=float(vol.get('h1',0) or 0)
        tx1=tx.get('h1',{}).get('buys',0)+tx.get('h1',{}).get('sells',0)
        pc1=float(attr.get('price_change_percentage',{}).get('h1',0) or 0)
        vel_vol=(v5*12 + v15*4)/2
        accel=(vel_vol+1)/(v1+1)
        onchain = math.log1p(v1)+math.log1p(tx1)+0.6*math.log1p(accel)+0.15*abs(pc1)
        rows.append((sym,onchain))
    rows.sort(key=lambda x:x[1], reverse=True)
    return rows[:10]


def count_recent(query):
    url='https://api.twitter.com/2/tweets/counts/recent'
    params={'query':query,'granularity':'minute'}
    r=requests.get(url,headers=HEADERS,params=params,timeout=20)
    r.raise_for_status()
    data=r.json().get('data',[])
    total=sum(c.get('tweet_count',0) for c in data)
    return total


def main():
    top=fetch_trending()
    out=[]
    for sym,onchain in top:
        q=f'${sym} OR {sym} lang:en -is:retweet'
        try:
            social=count_recent(q)
        except Exception:
            social=0
        combined=onchain + 0.4*math.log1p(social)
        out.append((combined,sym,onchain,social))
        time.sleep(60)
    out.sort(reverse=True)
    for c,s,on,sv in out:
        print(f"{s}\tcombined={c:.2f}\tonchain={on:.2f}\tsocial={sv}")

if __name__=='__main__':
    main()
