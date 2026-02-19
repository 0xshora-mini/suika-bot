#!/usr/bin/env python3
"""
SUIKA Music Research Database
日本曲2000曲研究プロジェクト
"""

import sqlite3
import json

DB_PATH = "music_research.db"

def setup_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.executescript("""
    CREATE TABLE IF NOT EXISTS songs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        artist TEXT NOT NULL,
        year INTEGER,
        genre TEXT,
        
        -- 感情構造
        emotion_type TEXT,          -- 諦め/反抗/希望/孤独/連帯/愛/怒り...
        emotion_function TEXT,      -- 解放/麻痺/昇華/共鳴
        
        -- 意識レベル
        consciousness_level INTEGER, -- 1(奴隷脳)〜10(完全覚醒)
        consciousness_notes TEXT,
        
        -- 歌詞キーワード
        lyrics_keywords TEXT,       -- JSON array
        
        -- 音楽的特徴
        chord_progression TEXT,
        tempo TEXT,                 -- 遅い/中/速い
        rhythm_feel TEXT,
        
        -- 社会的文脈
        social_context TEXT,
        historical_significance TEXT,
        
        -- 影響力
        sales_copies INTEGER,
        cultural_impact TEXT,       -- 大/中/小
        
        -- SUIKAスコア
        soul_freedom_score INTEGER, -- 1〜10（魂の自由度）
        truth_score INTEGER,        -- 1〜10（真実を語る度）
        
        -- メモ
        notes TEXT,
        analyzed_at TEXT
    );
    
    CREATE TABLE IF NOT EXISTS patterns (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        pattern_name TEXT,
        description TEXT,
        song_ids TEXT,  -- JSON array
        created_at TEXT
    );
    
    CREATE TABLE IF NOT EXISTS insights (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT,
        insight TEXT,
        evidence TEXT,
        created_at TEXT
    );
    """)
    
    conn.commit()
    conn.close()
    print("データベース作成完了")

def add_song(data: dict):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    if isinstance(data.get('lyrics_keywords'), list):
        data['lyrics_keywords'] = json.dumps(data['lyrics_keywords'], ensure_ascii=False)
    
    columns = ', '.join(data.keys())
    placeholders = ', '.join(['?' for _ in data])
    
    c.execute(f"INSERT INTO songs ({columns}) VALUES ({placeholders})", list(data.values()))
    conn.commit()
    conn.close()
    return c.lastrowid

def get_stats():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM songs")
    total = c.fetchone()[0]
    c.execute("SELECT genre, COUNT(*) FROM songs GROUP BY genre ORDER BY COUNT(*) DESC")
    by_genre = c.fetchall()
    c.execute("SELECT ROUND(AVG(soul_freedom_score), 2), ROUND(AVG(truth_score), 2) FROM songs WHERE soul_freedom_score IS NOT NULL")
    avg_scores = c.fetchone()
    conn.close()
    return {
        "total": total,
        "by_genre": by_genre,
        "avg_soul_freedom": avg_scores[0],
        "avg_truth": avg_scores[1]
    }

if __name__ == "__main__":
    setup_db()
    stats = get_stats()
    print(f"総曲数: {stats['total']}")
    print(f"ジャンル別: {stats['by_genre']}")
