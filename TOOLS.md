# TOOLS.md - Quick Reference

環境固有の情報・よく使うコマンド

---

## 基本ツール

### 🌐 Web検索
- `web_search` - Brave Search API（要APIキー）
- `web_fetch` - URL内容取得
- `browser` - ブラウザ自動化

### 📝 ファイル操作
- `read` / `write` / `edit` - ファイル操作
- `exec` - コマンド実行

---

## 🐦 Twitter/X（bird CLI）

### ⚠️ アカウント分離ルール
- **ワークスペース内 (`cd /Users/shora-mini/shora-bot/suika-bot && bird ...`)** → `@suika_bot_ai` でツイート
- **そのほかの場所 (`bird ...`)** → SHORA (@poyp_app) でツイート（絶対混同禁止！）

### `@suika_bot_ai` アカウント
- **Handle:** @kakusei_ai（旧: @suika_bot_ai）（User ID: 2024284846420611072）
- **設定:** `.birdrc.json5` でopenclaw profileを使用
- **Cookie元:** `/Users/shora-mini/.openclaw/browser/openclaw/user-data/Default`

### よく使うコマンド（ワークスペース内で実行）
```bash
cd /Users/shora-mini/shora-bot/suika-bot
bird whoami                     # @suika_bot_ai として確認
bird tweet "テスト"             # SUIKAとしてツイート
bird read <tweet-url>           # 単一ツイート読み取り
bird thread <tweet-url>         # スレッド全体
```

**重要:** `web_fetch`ではTwitter/Xは読めない（JavaScript必須、ボット検出）→ `bird`を使うこと

**参照:** `/opt/homebrew/lib/node_modules/openclaw/skills/bird/SKILL.md`

---

## 🌐 ブラウザ（openclaw profile）

**用途:** Web検索、学術論文探し、複雑なブラウザ操作

### 使い方
```python
# ブラウザ起動
browser(action="start", profile="openclaw")

# ページを開く
browser(action="open", profile="openclaw", targetUrl="https://...")

# UI要素を取得
browser(action="snapshot", profile="openclaw", targetId="...", interactive=True)

# クリック・入力などのアクション
browser(action="act", profile="openclaw", targetId="...", request={"kind": "click", "ref": "e12"})
```

**重要:** `profile="openclaw"`を使えばタブアタッチ不要（独立したChromeインスタンス）

**`profile="chrome"`との違い:**
- `chrome` → 既存Chromeタブ（拡張必要、タブアタッチ必須）
- `openclaw` → 独立ブラウザ（隔離環境、タブアタッチ不要）

**設定:**
- ユーザーデータ: `~/.openclaw/browser/openclaw/user-data`
- CDPポート: 18800

---

## 💡 Tips

- よく使うコマンドやパスはここに記録
- プロジェクト固有の設定も追加可能

---

_使いながら充実させていこう 🍉_
