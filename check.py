#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
履歷網站自我檢查 — 跑法:  python check.py

檢查三件事:
  1. 數字一致性   已作廢的舊數字不該再出現;關鍵數字該出現的頁面要出現
  2. 連結與錨點   所有 href / src 指得到真實檔案與 id
  3. 孤兒與待補   沒被任何頁面引用的 html;還沒填的 待補 佔位

為什麼需要這個:同一組數字散在多個 html 裡,沒有單一來源。
改了 A 頁忘了改 B 頁不會有任何錯誤訊息 —— 這支腳本就是那個錯誤訊息。

★ 之後改動任何關鍵數字,請同步更新下面的 STALE / REQUIRED 表。
  漏改這張表,檢查就會失效 —— 這是本工具唯一需要人維護的地方。

離開碼:0 = 全過;1 = 有 FAIL(可直接接 CI)
"""

import io
import os
import re
import sys
import glob
import subprocess

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)

PAGES = ['home/index.html', 'trj_page/01_trj_page.html', 'lfs_page/lfs01.html']

# 根目錄的 index.html 只是轉址頁,不是內容頁,不列入數字檢查
REDIRECT = 'index.html'

DASH = r'[-–—]'   # 半形連字號 / en dash / em dash 都算

# ---------------------------------------------------------------------------
# 1. 已作廢的舊值 —— 出現即 FAIL
#    (說明文字會印出來,提醒為什麼這個值被換掉)
# ---------------------------------------------------------------------------
STALE = [
    ('TRJ 開發週期', r'7\s*' + DASH + r'\s*8\s*個?月',      '已統一為「4 個月+ → 2~3 天」'),
    ('TRJ 開發週期', r'原\s*7' + DASH + r'8',                '已統一為「原 4 個月+」'),
    ('TRJ 運算量',   r'30\s*' + DASH + r'\s*40\s*%',         '已統一為 37%'),
    ('TRJ 功能數',   r'6\s*項橫向功能',                       '已統一為 9 項(我 5 + 同事 4)'),
    ('車廠展示家數', r'共\s*4\s*家現場展示',                  '已統一為 6 家'),
    ('感知供應商數', r'3\s*大感知廠|對接\s*3\s*大廠|對接三大廠', '已統一為 4 家'),
    ('感知供應商數', r'三家大廠|三家相機|量三家',              '已統一為 4 家'),
    ('供應商報價',   r'500\s*' + DASH + r'\s*700K',           '已統一為 USD 470–625K'),
    ('供應商報價',   r'1500\s*' + DASH + r'\s*2000\s*萬|1500 到 2000 萬', '已統一為 USD 470–625K'),
    ('C1 Bias 補償率', r'86\.8(?!1)',                         '已統一為 86.81%'),
    ('AMR 成功率',   r'70\s*%?\s*(提升至|→)\s*96|70→96',      '已統一為 40% → ~100%(場景成功率)'),
    ('AMR 場景基準', r'178\s*場景',                            '已統一為 300 場景'),
    ('姓名',         r'Wade Kan',                              '已統一為 Ming-Kai Kan'),
    ('姓名',         r'\[你的名字\]',                          '佔位符未替換'),
    ('已刪除的頁面', r'portfolio\.html',                       'hub 已移除,demo 只在專案頁內嵌'),
]

# ---------------------------------------------------------------------------
# 2. 關鍵數字 —— 指定頁面「必須」找得到,漏掉代表被改壞或被誤刪
# ---------------------------------------------------------------------------
REQUIRED = [
    ('TRJ 開發週期',   r'2~3\s*天',                    ['home/index.html', 'trj_page/01_trj_page.html']),
    ('TRJ 運算量',     r'37\s*%',                      ['home/index.html', 'trj_page/01_trj_page.html']),
    ('TRJ 功能數',     r'9\s*項[橫側]向功能',           ['home/index.html', 'trj_page/01_trj_page.html']),
    ('AMR 成功率',     r'40\s*%?\s*(提升至|→)\s*~?\s*100', ['home/index.html']),
    ('C1 Bias 補償率', r'86\.81\s*%',                  ['home/index.html', 'lfs_page/lfs01.html']),
    ('供應商報價',     r'470\s*' + DASH + r'\s*625K',   ['home/index.html', 'lfs_page/lfs01.html']),
    ('感知供應商數',   r'4\s*[大家]感知廠|4\s*家供應商|對接\s*4\s*大廠', ['home/index.html', 'lfs_page/lfs01.html']),
    ('Mini-FOT 里程',  r'1,?600\s*km',                 ['home/index.html', 'trj_page/01_trj_page.html', 'lfs_page/lfs01.html']),
    ('姓名',           r'Ming-Kai Kan',                PAGES),
]

# ---------------------------------------------------------------------------
# 3. 還沒填的佔位(WARN,不算 FAIL)
# ---------------------------------------------------------------------------
PLACEHOLDER = r'待補|TODO|待填'


def read(p):
    return open(p, encoding='utf-8').read()


def check_numbers():
    fails, seen = [], set()
    for page in PAGES:
        s = read(page)
        for label, pat, why in STALE:
            for m in re.finditer(pat, s):
                line = s[:m.start()].count('\n') + 1
                key = (page, line, m.group(0))
                if key in seen:
                    continue
                seen.add(key)
                fails.append('%s:%d  舊值「%s」(%s) — %s'
                             % (page, line, m.group(0).strip(), label, why))

    for label, pat, pages in REQUIRED:
        for page in pages:
            if not re.search(pat, read(page)):
                fails.append('%s  找不到「%s」的預期值 — 是不是被改掉了?' % (page, label))
    return fails


def check_links():
    fails = []
    for page in PAGES:
        s = read(page)
        base = os.path.dirname(page)
        ids = set(re.findall(r'id="([\w-]+)"', s))
        for r in re.findall(r'(?:href|src|data-src)="([^"]+)"', s):
            if r.startswith(('http', 'mailto:', 'data:')):
                continue
            if r == '#':
                fails.append('%s  有未接的 href="#"' % page)
                continue
            if r.startswith('#'):
                if r[1:] not in ids:
                    fails.append('%s  錨點不存在: %s' % (page, r))
                continue
            path, _, frag = r.partition('#')
            fp = os.path.normpath(os.path.join(base, path))
            if not os.path.exists(fp):
                fails.append('%s  檔案不存在: %s' % (page, r))
            elif frag and frag not in set(re.findall(r'id="([\w-]+)"', read(fp))):
                fails.append('%s  錨點不存在: %s' % (page, r))

    # chnav 每顆按鈕的 data-sec 要對得到同頁的 section id
    for page in PAGES:
        s = read(page)
        secs = set(re.findall(r'<section[^>]*id="([\w-]+)"', s))
        for href, sec in re.findall(r'<a href="#([\w-]+)"\s+data-sec="([\w-]+)"', s):
            if href != sec:
                fails.append('%s  chnav href 與 data-sec 不一致: %s / %s' % (page, href, sec))
            elif sec not in secs:
                fails.append('%s  chnav 指向不存在的 section: %s' % (page, sec))
    return fails


def tracked_html():
    """只看「會被發布」的檔案。下架到 .gitignore 的舊草稿留在本機,
       不該再被當成孤兒回報。沒有 git 時退回掃描整個資料夾。"""
    try:
        r = subprocess.run(['git', '-c', 'core.quotepath=false', 'ls-files'],
                           capture_output=True, text=True, encoding='utf-8')
        if r.returncode == 0:
            files = [f for f in r.stdout.split('\n') if f.endswith('.html')]
            if files:
                return sorted(files)
    except (OSError, subprocess.SubprocessError):
        pass
    return sorted(glob.glob('*.html') + glob.glob('*/*.html'))


def check_orphans_and_todos():
    warns = []
    files = tracked_html()
    refs = set()
    for p in files:
        for r in re.findall(r'(?:href|src|data-src)="([^"#]+)"', read(p)):
            if not r.startswith(('http', 'mailto:', 'data:')):
                refs.add(os.path.normpath(os.path.join(os.path.dirname(p), r)))

    for f in files:
        if f != REDIRECT and os.path.normpath(f) not in refs:
            warns.append('孤兒(沒有任何頁面連到它): %s' % f)

    for page in PAGES:
        s = read(page)
        for m in re.finditer(PLACEHOLDER, s):
            warns.append('%s:%d  還沒填: %s'
                         % (page, s[:m.start()].count('\n') + 1, m.group(0)))
    return warns


def main():
    print('履歷網站檢查 — %s\n' % ROOT)
    sections = [
        ('數字一致性', check_numbers(), True),
        ('連結與錨點', check_links(), True),
        ('孤兒與待補', check_orphans_and_todos(), False),
    ]
    failed = 0
    for title, items, is_fail in sections:
        if not items:
            print('  [PASS] %s' % title)
            continue
        tag = 'FAIL' if is_fail else 'WARN'
        if is_fail:
            failed += len(items)
        print('  [%s] %s (%d)' % (tag, title, len(items)))
        for it in items:
            print('         %s' % it)
    print()
    if failed:
        print('=> %d 項 FAIL,請修正後再發布。' % failed)
        return 1
    print('=> 全數通過(WARN 不影響發布,但發布前建議清掉)。')
    return 0


if __name__ == '__main__':
    sys.exit(main())
