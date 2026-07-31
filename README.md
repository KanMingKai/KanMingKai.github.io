# 甘銘凱 Ming-Kai Kan — 履歷與作品集

自主系統工程師 · 量產 ADAS → 工廠 AMR

線上版:<https://kanmingkai.github.io/>

## 三個頁面

| 頁面 | 檔案 | 內容 |
|---|---|---|
| 履歷 | `home/index.html` | 工作經歷、技能、學習能力、學歷、發明專利 |
| TRJ 軌跡規劃 | `trj_page/01_trj_page.html` | 把 9 項側向功能收斂成單一共用模組 |
| LFS 車道融合 | `lfs_page/lfs01.html` | 讓不完美的感知也能安全地用 |

互動 demo 以 `<iframe>` 內嵌在兩個專案頁裡,不單獨作為頁面呈現。

## 結構

```
index.html              轉址頁 → home/index.html(GitHub Pages 首頁需要它)
home/index.html         履歷本體
trj_page/               TRJ 專案頁 + 6 個內嵌 demo
lfs_page/               LFS 專案頁 + 4 個內嵌 demo
assets/
  tokens.css            三頁共用的設計 token(改品牌色動這裡)
  nav.css / nav.js      兩層固定導覽列(共用元件)
check.py                發布前檢查
```

純靜態 HTML,沒有建置步驟 —— 直接開檔就能看。

## 維護

**改版面**:各頁的排版 CSS 都留在該頁自己的 `<style>` 裡,改一頁不會影響其他頁。

**改品牌色/字體**:改 `assets/tokens.css` 一個檔,三頁同步。

**改導覽列章節**:改該頁的 `<nav class="chnav">`,規則是 `data-sec` 要等於對應 `<section>` 的 `id`。

**改關鍵數字**:同一組數字散在多個 HTML 裡,沒有單一來源。改完務必跑:

```bash
python check.py
```

它會檢查(1)已作廢的舊數字有沒有殘留、(2)關鍵數字有沒有被改掉、(3)連結與錨點是否都通、(4)有沒有孤兒檔與未填的「待補」。有問題會回傳離開碼 1。

> 改動關鍵數字時,請同步更新 `check.py` 裡的 `STALE` / `REQUIRED` 兩張表 ——
> 那是本專案唯一需要人工維護的地方,漏改的話檢查就會失效。
