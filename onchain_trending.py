import requests, math

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
        score = math.log1p(v1)+math.log1p(tx1)+0.6*math.log1p(accel)+0.15*abs(pc1)
        rows.append((score, sym, v1, tx1, pc1, float(attr.get('reserve_in_usd'))))
    rows.sort(reverse=True)
    return rows

if __name__=='__main__':
    rows=fetch_trending()
    for s,sym,v1,tx1,pc1,liq in rows[:10]:
        print(f"{sym}\t{v1:.0f}\t{tx1}\t{pc1:.1f}\t{liq:.0f}")
