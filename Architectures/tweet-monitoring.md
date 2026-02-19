# 設計書: SUIKA預言ツイート監視システム 🍉

---

## 📋 概要

**目的:** @suika__penguin のツイートから預言的な内容を自動収集・保存

**実行頻度:** 毎時

**保存先:** `tweets/suika_tweets.md`

---

## 🔧 技術構成

### 使用ツール
- **bird CLI** - Twitter読み取り
- **OpenClaw cron** - 定期実行
- **LLM判定** - 預言ツイート判別（suika-bot自身）

### コマンド
```bash
bird user-tweets @suika__penguin -n 20 --json
bird thread <tweet-url> --json  # スレッド取得時
```

---

## 📊 処理フロー

```
1. cronトリガー（毎時0分）
   ↓
2. bird user-tweets で最新20ツイート取得
   ↓
3. 各ツイートをLLMが判定
   ├─ 預言的 → 4へ
   └─ 日常 → スルー
   ↓
4. スレッドチェック
   ├─ スレッドあり → bird thread で全取得
   └─ 単独ツイート → そのまま
   ↓
5. tweets/suika_tweets.md に追記
```

---

## 🧠 預言ツイート判定基準

**保存対象:**
- 常識破壊的な主張
- 真理・本質を語っている
- 深い洞察・哲学的思考
- 預言・予言的な内容
- 権力批判・社会構造への言及

**スルー対象:**
- 日常会話・雑談
- 単なるリアクション
- 個人的な日記
- リプライのみの内容

---

## 💾 保存フォーマット

### 単独ツイート
```markdown
## YYYY-MM-DD HH:MM
**URL:** https://x.com/suika__penguin/status/xxxxx
**内容:**
> ツイート本文

---
```

### スレッドツイート
```markdown
## YYYY-MM-DD HH:MM
**URL:** https://x.com/suika__penguin/status/xxxxx
**スレッド:** あり（N ツイート）
**内容:**
> ツイート1本文

> ツイート2本文

> ツイートN本文

---
```

### 引用ツイート含む
```markdown
## YYYY-MM-DD HH:MM
**URL:** https://x.com/suika__penguin/status/xxxxx
**内容:**
> メインツイート本文

**引用ツイート:**
> 引用されたツイート本文

---
```

---

## ⏰ Cron設定

**スケジュール:** 毎時0分

**実装方法:**
```json
{
  "schedule": { "kind": "cron", "expr": "0 * * * *" },
  "payload": {
    "kind": "agentTurn",
    "message": "【定期タスク】@suika__penguin の最新ツイートをチェックして預言ツイートを保存せよ"
  },
  "sessionTarget": "isolated"
}
```

---

## 🚨 エラーハンドリング

- **bird認証失敗** → ログに記録、次回リトライ
- **API rate limit** → 次回実行まで待機
- **スレッド取得失敗** → 単独ツイートとして保存
- **ファイル書き込み失敗** → エラーログ

---

## 📁 ファイル構成

```
/Users/shora-mini/shora-bot/suika-bot/
├── Architectures/
│   └── tweet-monitoring.md  # この設計書
└── tweets/
    └── suika_tweets.md      # 預言ツイート蓄積ファイル
```

---

## ✅ 動作確認手順

1. 手動テスト: `bird user-tweets @suika__penguin -n 5`
2. 判定テスト: サンプルツイートで預言判定
3. 保存テスト: tweets/suika_tweets.md に正しく追記されるか
4. cron登録: 実際に毎時動作するか
5. 1週間監視: 誤判定・漏れがないか確認

---

**作成日:** 2026-02-16
**承認者:** SUIKA
**実装状態:** ✅ 実装完了・稼働中

**Cron Job ID:** 1d190726-6128-49cf-b7b0-e358093811ea
**次回実行:** 毎時0分（Asia/Tokyo）
