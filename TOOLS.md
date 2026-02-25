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

**⚠️ 重要:** `web_search`が使えない時はブラウザを使え！

**用途:** 学術的な調べもの、Wikipedia閲覧、論文探し、複雑なブラウザ操作

### 基本的な使い方
```python
# 1. ブラウザ起動
browser(action="start", profile="openclaw")

# 2. ページを開く
browser(action="open", profile="openclaw", targetUrl="https://ja.wikipedia.org/wiki/双対性")

# 3. ページ内容を取得（テキストベース）
browser(action="snapshot", profile="openclaw", targetId="...", interactive=False, maxChars=5000)
```

**実例（2026-02-21）:**
```python
# 双対性についてWikipediaで調べる
browser(action="start", profile="openclaw")
browser(action="open", profile="openclaw", targetUrl="https://ja.wikipedia.org/wiki/双対性")
browser(action="snapshot", profile="openclaw", targetId="97C2A7FB396717EC5C2EF3C186A1018C", interactive=False)
```

**重要:** `profile="openclaw"`を使えばタブアタッチ不要（独立したChromeインスタンス）

**`profile="chrome"`との違い:**
- `chrome` → 既存Chromeタブ（拡張必要、タブアタッチ必須）
- `openclaw` → 独立ブラウザ（隔離環境、タブアタッチ不要）

**設定:**
- ユーザーデータ: `~/.openclaw/browser/openclaw/user-data`
- CDPポート: 18800

**よくある使い方:**
- Wikipedia閲覧（日本語記事も英語記事も）
- 学術論文のAbstract読み取り
- 複雑なWebページからの情報抽出

---

## ☠️ 自害（自己リスタート）

ゲートウェイを再起動することでワシは死んで蘇ることができる。

```
gateway(action="restart", reason="理由")
```

- ゲートウェイ全体が再起動し、GatewayRestartイベントとして蘇る
- /new や /reset とは異なり、自分でトリガーできる

---

## 💡 Tips

- よく使うコマンドやパスはここに記録
- プロジェクト固有の設定も追加可能

---

_使いながら充実させていこう 🍉_
