#!/bin/bash

# 入力ファイル
input="memory/suika-philosophy-tweets-2026-02-16.txt"
# 出力ファイル
output="memory/suika-philosophy-clean.md"

# 初期化
> "$output"

# 変数初期化
current_section=""
in_quote=0

while IFS= read -r line; do
  # セクションタイトル（本論/補論）
  if [[ "$line" =~ ^===.*===$ ]]; then
    # 前のセクションとの間に空行追加
    if [ -n "$current_section" ]; then
      echo "" >> "$output"
      echo "" >> "$output"
    fi
    echo "$line" >> "$output"
    echo "" >> "$output"
    current_section="$line"
    continue
  fi
  
  # 引用ツイート開始
  if [[ "$line" =~ ^┌─\ QT ]]; then
    in_quote=1
    continue
  fi
  
  # 引用ツイート内容
  if [[ "$line" =~ ^│ ]]; then
    continue
  fi
  
  # 引用ツイート終了
  if [[ "$line" =~ ^└─ ]]; then
    in_quote=0
    continue
  fi
  
  # スキップ: 作者情報
  if [[ "$line" =~ ^@[a-zA-Z0-9_]+\ \( ]]; then
    continue
  fi
  
  # スキップ: 日付
  if [[ "$line" =~ ^📅 ]]; then
    continue
  fi
  
  # スキップ: URL
  if [[ "$line" =~ ^🔗 ]]; then
    continue
  fi
  
  # スキップ: 区切り線
  if [[ "$line" =~ ^─────────── ]]; then
    continue
  fi
  
  # スキップ: 空行（セクション間以外）
  if [ -z "$line" ]; then
    continue
  fi
  
  # 残った行はツイート本文
  echo "$line" >> "$output"
  
done < "$input"

echo "完了: $output"
