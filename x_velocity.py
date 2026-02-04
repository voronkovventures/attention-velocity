import os, requests, time

# Uses Twitter/X counts endpoint (recent) with bearer token
# Requires env: X_BEARER_TOKEN

BEARER=os.getenv('X_BEARER_TOKEN')

if not BEARER:
    raise SystemExit('Missing X_BEARER_TOKEN')

HEADERS={'Authorization': f'Bearer {BEARER}'}


def count_recent(query):
    url='https://api.twitter.com/2/tweets/counts/recent'
    params={'query':query,'granularity':'minute'}
    r=requests.get(url,headers=HEADERS,params=params,timeout=20)
    r.raise_for_status()
    data=r.json().get('data',[])
    total=sum(c.get('tweet_count',0) for c in data)
    return total


def main():
    symbols=['PONKE','SHARK','ELON','PENGUIN','ARC','RENTA','KITTY','K2']
    for sym in symbols:
        q=f'${sym} OR {sym} lang:en -is:retweet'
        try:
            total=count_recent(q)
            print(sym, total)
        except Exception as e:
            print(sym, 'ERR', e)
        time.sleep(60)  # conservative rate

if __name__=='__main__':
    main()
