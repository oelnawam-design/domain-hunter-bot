import random
import socket
import time
import requests
import re
import json
import os
from telegram import Bot

BOT_TOKEN = "PUT_TOKEN"
CHAT_ID = "PUT_CHAT_ID"

bot = Bot(token=BOT_TOKEN)

MEM = "sent.json"

# =====================
# MEMORY
# =====================

def load():
    if not os.path.exists(MEM):
        return []
    return json.load(open(MEM))

def save(d):
    json.dump(d, open(MEM,"w"))

sent = load()

# =====================
# WORD LIST
# =====================

prefix = [
"nova","flux","orbit","luma","neon","atlas",
"vector","quant","zen","meta","hyper",
"nexus","vertex","astra","pilot","stack"
]

suffix = [
"ai","labs","agent","brain","core",
"flow","cloud","data","forge","node"
]

trend_keywords = [
"ai","agent","copilot","gpt",
"labs","cloud","data","automation"
]

tlds_check = [".ai",".io",".co",".dev",".xyz"]

# =====================
# DOMAIN CHECK
# =====================

def available(domain):
    try:
        socket.gethostbyname(domain)
        return False
    except:
        return True

# =====================
# EXTENSION COUNT
# =====================

def extension_score(name):
    count = 0

    for t in tlds_check:
        try:
            socket.gethostbyname(name+t)
            count += 1
        except:
            pass

    if count >= 3:
        return 20
    elif count >=1:
        return 10

    return 0

# =====================
# AI SITE CHECK
# =====================

def ai_site_score(name):
    try:
        r = requests.get(f"http://{name}.ai",timeout=2)
        txt = r.text.lower()

        if "ai" in txt or "saas" in txt:
            return 20

        return 8

    except:
        return 0

# =====================
# TREND SCORE
# =====================

def trend_score(name):

    s = 0

    for k in trend_keywords:
        if k in name:
            s += 5

    return min(s,20)

# =====================
# BRAND SCORE
# =====================

def brand_score(name):

    l = len(name)
    score = 0

    if l <= 6:
        score += 20
    elif l <= 8:
        score += 15
    elif l <= 10:
        score += 5

    vowels = sum(1 for c in name if c in "aeiou")

    if vowels >= 2:
        score += 5

    return score

# =====================
# PRODUCT HUNT
# =====================

def producthunt():

    try:
        r = requests.get("https://www.producthunt.com/",timeout=5)
        html = r.text

        names = re.findall(r'"name":"(.*?)"', html)

        clean = []

        for n in names:
            n = n.lower()
            n = re.sub(r'[^a-z]', '', n)

            if 4 <= len(n) <= 10:
                clean.append(n)

        return list(set(clean))

    except:
        return []

# =====================
# GITHUB TRENDING
# =====================

def github():

    try:
        r = requests.get("https://github.com/trending",timeout=5)
        html = r.text

        repos = re.findall(r'href="/(.*?)"', html)

        clean = []

        for r in repos:
            name = r.split("/")[0]
            name = name.lower()
            name = re.sub(r'[^a-z]', '', name)

            if 4 <= len(name) <= 10:
                clean.append(name)

        return list(set(clean))

    except:
        return []

# =====================
# GENERATOR
# =====================

def generate():
    return random.choice(prefix)+random.choice(suffix)

# =====================
# EVALUATE
# =====================

def evaluate(name):

    score = 0

    score += extension_score(name)
    score += ai_site_score(name)
    score += trend_score(name)
    score += brand_score(name)

    return score

# =====================
# SCAN STARTUPS
# =====================

def scan_startups():

    names = producthunt() + github()

    for name in names:

        domain = name + ".com"

        if domain in sent:
            continue

        if not available(domain):
            continue

        sc = evaluate(name)

        if sc >= 80:
            return domain, sc

    return None,0

# =====================
# SCAN GENERATED
# =====================

def scan_generated():

    for _ in range(4000):

        name = generate()
        domain = name + ".com"

        if domain in sent:
            continue

        if not available(domain):
            continue

        sc = evaluate(name)

        if sc >= 85:
            return domain, sc

    return None,0

# =====================
# SEND
# =====================

def send(domain, score):

    msg = f"""
🔥 ELITE DOMAIN OPPORTUNITY

{domain}

Score: {score}

Check:
https://www.godaddy.com/domainsearch/find?domainToCheck={domain}
"""

    bot.send_message(chat_id=CHAT_ID,text=msg)

    sent.append(domain)
    save(sent)

# =====================
# LOOP
# =====================

print("PRO DOMAIN ENGINE RUNNING...")

while True:

    d,s = scan_startups()

    if not d:
        d,s = scan_generated()

    if d:
        send(d,s)

    time.sleep(60)
