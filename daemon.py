import requests
import json
import time

def load_config():
    try:
        with open("config.json") as f:
            return json.load(f)
    except:
        return

def load_cache():
    try:
        with open("cache.json") as f:
            return json.load(f)
    except:
        return

def setup():
    if load_config():
        return
    uid = input("Enter your akatsuki userID: ").strip()
    if not uid.isnumeric():
        print("Enter a valid number...")
        setup()
        return
    mode = input("Enter mode (STD: 0, Taiko: 1, Ctb: 2, Mania: 3): ")
    if not mode.isnumeric():
        print("Enter a valid number...")
        setup()
        return
    relax = input("Enter submode (vanilla: 0, relax: 1, autopilot: 2): ")
    if not relax.isnumeric():
        print("Enter a valid number...")
        setup()
        return
    with open(".\config.json", "w") as f:
        json.dump({'user_id': int(uid), 'mode': int(mode), 'relax': int(relax)}, f)

def get_stats(clears_page=0):
    config = load_config()
    if not clears_page:
        current_page = 0
        # 1st cycle, going by 10 pages (1000 clears)
        while True:
            time.sleep(0.5)
            current_page += 10
            req = requests.get(f"https://akatsuki.gg/api/v1/users/scores/best?mode={config['mode']}&p={current_page}&l=100&rx={config['relax']}&id={config['user_id']}").json()
            if not req['scores']:
                print(f"1st cycle done (<{current_page*100} clears), finding precise number")
                break
        while True:
            time.sleep(0.5)
            current_page -= 1
            req = requests.get(f"https://akatsuki.gg/api/v1/users/scores/best?mode={config['mode']}&p={current_page}&l=100&rx={config['relax']}&id={config['user_id']}").json()
            if not req['scores']:
                continue
            print(f"Found current ranked clears: {(current_page*100) + len(req['scores'])}")
            break
        clears_page = current_page
    stats = requests.get(f"https://akatsuki.gg/api/v1/users/full?id={config['user_id']}").json()
    clears = 0
    while True:
        time.sleep(0.5)
        req = requests.get(f"https://akatsuki.gg/api/v1/users/scores/best?mode={config['mode']}&p={clears_page}&l=100&rx={config['relax']}&id={config['user_id']}").json()
        if not req['scores']:
            req['scores'] = []
        if len(req['scores']) == 100:
            clears_page += 1
            continue
        clears = ((clears_page-1) * 100) + len(req['scores'])
        break
    first_places = requests.get(f"https://akatsuki.gg/api/v1/users/scores/first?mode={config['mode']}&p=0&l=1&rx={config['relax']}&id={config['user_id']}").json()['total']
    return {'api': stats['stats'], 'firsts': first_places, 'clears': clears, 'page' : clears_page}

def format(cache):
    config = load_config()
    mode_key = ['std', 'taiko', 'ctb', 'mania'][config['mode']]
    old_stats = cache[0]['api'][config['relax']][mode_key]
    new_stats = cache[-1]['api'][config['relax']][mode_key]
    current_pp = new_stats['pp']
    current_rscore = new_stats['ranked_score']
    current_clears = cache[-1]['clears']
    current_firsts = cache[-1]['firsts']
    if old_stats != new_stats:
        gain_pp = current_pp-old_stats['pp']
        gain_rscore = current_rscore-old_stats['ranked_score']
        gain_clears = current_clears-cache[0]['clears']
        gain_firsts = current_firsts-cache[0]['firsts']
    else:
        gain_pp = 0
        gain_rscore = 0
        gain_clears = 0
        gain_firsts = 0
    content = f"Ranked score: {current_rscore:,}"
    if gain_rscore:
        content += f" (+{gain_rscore:,})" if gain_rscore > 0 else f" ({gain_rscore:,})"
    content += f"\nClears: {current_clears:,}"
    if gain_clears:
        content += f" (+{gain_clears:,})" if gain_clears > 0 else f" ({gain_clears:,})"
    content += f"\n#1: {current_firsts:,}"
    if gain_firsts:
        content += f" (+{gain_firsts:,})" if gain_firsts > 0 else f" ({gain_firsts:,})"
    content += f"\nPP: {current_pp:,}"
    if gain_pp:
        content += f" (+{gain_pp:,})" if gain_pp > 0 else f" ({gain_pp:,})"
    with open("output.txt", "w") as f:
        f.write(content)

def main():
    print("Akatsuki stream tools | Keep this open!")
    setup()
    while True:
        print("Refreshing cache")
        cache = load_cache()
        if not cache:
            print("No cache found, This will take a while...")
            cache = [get_stats(0)]
            with open("cache.json", "w") as f:
                json.dump(cache, f, indent=4)
        else:
            cache = [cache[0], get_stats(cache[-1]['page'])]
            with open("cache.json", "w") as f:
                json.dump(cache, f, indent=4)
        format(cache)
        print("Done")
        time.sleep(30)

if __name__ == "__main__":
    main()