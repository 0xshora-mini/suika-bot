#!/usr/bin/env python3
"""
Gemini APIを使って音声ファイルを分析
"""
import os
import google.generativeai as genai

# APIキーを設定（環境変数から取得）
api_key = os.environ.get('GEMINI_API_KEY') or os.environ.get('GOOGLE_GENERATIVE_AI_API_KEY') or os.environ.get('GOOGLE_API_KEY')

if not api_key:
    print("ERROR: Gemini API keyが設定されていません")
    print("環境変数 GEMINI_API_KEY, GOOGLE_GENERATIVE_AI_API_KEY, または GOOGLE_API_KEY を設定してください")
    exit(1)

genai.configure(api_key=api_key)

print("音声ファイルをアップロード中...")
audio_file = genai.upload_file(path="temp_audio.m4a")
print(f"アップロード完了: {audio_file.name}")

# モデルを初期化
model = genai.GenerativeModel('gemini-2.0-flash-exp')

prompt = """この音楽を聴いて、以下を詳しく分析してください：

1. **リズムとテンポ**: BPM、グルーブ感、リズムパターンの特徴
2. **ハイハット**: どのように使われているか、刻み方の特徴
3. **音色と音響**: 全体的な音色、ミックスの特徴
4. **楽曲構成**: セクション構成、展開の仕方
5. **雰囲気**: 音楽全体から感じる印象、エネルギーレベル
6. **印象に残る要素**: 特に耳に残る音やパート

音楽的な専門用語を使いながら、具体的に説明してください。"""

print("\nGeminiが音楽を分析中...")
response = model.generate_content([prompt, audio_file])

print("\n" + "="*50)
print("Geminiによる音楽分析結果:")
print("="*50)
print(response.text)
