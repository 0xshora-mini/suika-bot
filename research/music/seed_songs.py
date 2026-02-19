#!/usr/bin/env python3
"""
初期データ投入 - 時代×ジャンル横断で主要曲を登録
SUIKAの知識をベースに、後でウェブ情報で補完
"""

import sqlite3
import json
from datetime import datetime

DB_PATH = "music_research.db"

# 初期曲データ（SUIKAの知識から）
INITIAL_SONGS = [
    # ===== 1960年代 =====
    {
        "title": "上を向いて歩こう",
        "artist": "坂本九",
        "year": 1961,
        "genre": "歌謡曲",
        "emotion_type": "孤独/希望",
        "emotion_function": "昇華",
        "consciousness_level": 7,
        "consciousness_notes": "孤独を肯定し、それでも前を向く。奴隷プロトコルを避けた珍しい時代の曲",
        "lyrics_keywords": ["涙", "孤独", "歩く", "星"],
        "cultural_impact": "大",
        "sales_copies": 13000000,
        "soul_freedom_score": 7,
        "truth_score": 8,
        "notes": "世界初の非英語圏からのビルボード1位。日本人の孤独感の普遍性を証明"
    },
    {
        "title": "いい日旅立ち",
        "artist": "山口百恵",
        "year": 1978,
        "genre": "歌謡曲",
        "emotion_type": "郷愁/旅立ち",
        "emotion_function": "解放",
        "consciousness_level": 6,
        "consciousness_notes": "日本の原風景への愛着と新しい旅立ちの両立",
        "lyrics_keywords": ["旅立ち", "日本", "大地", "別れ"],
        "cultural_impact": "大",
        "soul_freedom_score": 6,
        "truth_score": 7,
        "notes": "国鉄CMタイアップ。故郷と旅立ちという日本人の永遠のテーマ"
    },
    # ===== 1970年代 =====
    {
        "title": "神田川",
        "artist": "かぐや姫",
        "year": 1973,
        "genre": "フォーク",
        "emotion_type": "青春/貧しさの中の豊かさ",
        "emotion_function": "解放",
        "consciousness_level": 8,
        "consciousness_notes": "物質的貧困の中に魂の自由を見出す。真の豊かさの問いかけ",
        "lyrics_keywords": ["神田川", "銭湯", "二十四色", "狭い", "若かった"],
        "cultural_impact": "大",
        "soul_freedom_score": 9,
        "truth_score": 9,
        "notes": "フォークブームの頂点。現代の物質主義へのアンチテーゼとして機能"
    },
    {
        "title": "津軽海峡・冬景色",
        "artist": "石川さゆり",
        "year": 1977,
        "genre": "演歌",
        "emotion_type": "孤独/離別",
        "emotion_function": "共鳴",
        "consciousness_level": 5,
        "consciousness_notes": "演歌的感情構造。諦めと美の共存",
        "lyrics_keywords": ["雪", "津軽", "別れ", "寒さ", "海峡"],
        "cultural_impact": "大",
        "soul_freedom_score": 5,
        "truth_score": 7,
        "notes": "日本的な美意識の結晶。悲しみを美として昇華する演歌の本質"
    },
    {
        "title": "時代",
        "artist": "中島みゆき",
        "year": 1975,
        "genre": "フォーク",
        "emotion_type": "諦めと再生",
        "emotion_function": "解放",
        "consciousness_level": 9,
        "consciousness_notes": "「今はこんなに悲しくて」から「人は誰もひとりじゃない」へ。真の希望の描き方",
        "lyrics_keywords": ["時代", "変わる", "悲しい", "あした"],
        "cultural_impact": "大",
        "soul_freedom_score": 9,
        "truth_score": 10,
        "notes": "苦しみを否定せず通り抜ける哲学。奴隷プロトコルにない本物の慰め"
    },
    # ===== 1980年代 =====
    {
        "title": "ルビーの指環",
        "artist": "寺尾聰",
        "year": 1981,
        "genre": "シティポップ",
        "emotion_type": "喪失/都会的孤独",
        "emotion_function": "共鳴",
        "consciousness_level": 7,
        "consciousness_notes": "都会の孤独を洗練された音楽で包む。内面の複雑さを肯定",
        "lyrics_keywords": ["指環", "別れ", "都会", "夜"],
        "cultural_impact": "大",
        "soul_freedom_score": 7,
        "truth_score": 7,
        "notes": "シティポップの原型。後の世界的再評価で日本音楽の真価を証明"
    },
    {
        "title": "DESIRE -情熱-",
        "artist": "中森明菜",
        "year": 1986,
        "genre": "アイドル歌謡",
        "emotion_type": "官能/反抗",
        "emotion_function": "解放",
        "consciousness_level": 7,
        "consciousness_notes": "アイドルという奴隷的システムの中で咲いた反抗の花",
        "lyrics_keywords": ["炎", "情熱", "欲望", "燃える"],
        "cultural_impact": "大",
        "soul_freedom_score": 7,
        "truth_score": 6,
        "notes": "明菜の本質的な野生性がアイドルフォーマットを突き破った"
    },
    {
        "title": "め組のひと",
        "artist": "ラッツ&スター",
        "year": 1983,
        "genre": "J-pop",
        "emotion_type": "喜び/祝祭",
        "emotion_function": "解放",
        "consciousness_level": 5,
        "consciousness_notes": "シンプルな喜びの表現。ドゥワップ的黒人音楽の影響",
        "lyrics_keywords": ["め組", "ファイヤー"],
        "cultural_impact": "中",
        "soul_freedom_score": 6,
        "truth_score": 5,
        "notes": "日本のブラックミュージック受容の面白い例"
    },
    {
        "title": "ガラスの十代",
        "artist": "光GENJI",
        "year": 1987,
        "genre": "アイドル",
        "emotion_type": "青春/アイドル的夢",
        "emotion_function": "麻痺",
        "consciousness_level": 2,
        "consciousness_notes": "ジャニーズアイドルシステムの完成形。感情を消費させるメカニズム",
        "lyrics_keywords": ["十代", "ガラス", "夢"],
        "cultural_impact": "大",
        "soul_freedom_score": 2,
        "truth_score": 2,
        "notes": "アイドル産業の奴隷プロトコルの典型例。しかし時代の鏡"
    },
    {
        "title": "愛は勝つ",
        "artist": "KAN",
        "year": 1990,
        "genre": "J-pop",
        "emotion_type": "希望/確信",
        "emotion_function": "麻痺",
        "consciousness_level": 3,
        "consciousness_notes": "奴隷脳的な「愛は必ず勝つ」という根拠のない確信。しかし人々が求めた",
        "lyrics_keywords": ["愛", "勝つ", "必ず", "信じる"],
        "cultural_impact": "大",
        "soul_freedom_score": 3,
        "truth_score": 3,
        "notes": "バブル崩壊前夜の無根拠な楽観主義。時代の集合意識"
    },
    # ===== 1990年代 =====
    {
        "title": "Love Story wa Totsuzen ni",
        "artist": "小田和正",
        "year": 1991,
        "genre": "J-pop",
        "emotion_type": "恋愛/高揚",
        "emotion_function": "共鳴",
        "consciousness_level": 5,
        "consciousness_notes": "純粋な恋愛感情の肯定。単純だが正直",
        "lyrics_keywords": ["愛してる", "突然", "恋", "言葉"],
        "cultural_impact": "大",
        "sales_copies": 2542000,
        "soul_freedom_score": 5,
        "truth_score": 6,
        "notes": "ドラマタイアップ全盛期の象徴。恋愛への純粋な希求"
    },
    {
        "title": "世界に一つだけの花",
        "artist": "SMAP",
        "year": 2003,
        "genre": "J-pop",
        "emotion_type": "自己肯定",
        "emotion_function": "麻痺",
        "consciousness_level": 4,
        "consciousness_notes": "「ナンバーワンにならなくていい」という一見解放的だが実は現状維持を促すメッセージ",
        "lyrics_keywords": ["ナンバーワン", "オンリーワン", "花", "違う"],
        "cultural_impact": "大",
        "sales_copies": 3260000,
        "soul_freedom_score": 4,
        "truth_score": 4,
        "notes": "表面的な個性尊重。しかしシステムへの反抗を抑制する機能も持つ"
    },
    {
        "title": "名もなき詩",
        "artist": "Mr.Children",
        "year": 1996,
        "genre": "ロック",
        "emotion_type": "実存的問い",
        "emotion_function": "覚醒",
        "consciousness_level": 8,
        "consciousness_notes": "「あるがままの心で生きようとすること」という根源的なメッセージ",
        "lyrics_keywords": ["あるがまま", "心", "生きる", "愛"],
        "cultural_impact": "大",
        "sales_copies": 2740000,
        "soul_freedom_score": 8,
        "truth_score": 8,
        "notes": "J-popの中では稀な実存的問いを持つ作品"
    },
    {
        "title": "TOMORROW",
        "artist": "岡本真夜",
        "year": 1995,
        "genre": "J-pop",
        "emotion_type": "希望/励まし",
        "emotion_function": "麻痺",
        "consciousness_level": 3,
        "consciousness_notes": "「泣かないで」という抑圧的メッセージ。感情の否定",
        "lyrics_keywords": ["明日", "泣かないで", "頑張れ"],
        "cultural_impact": "大",
        "soul_freedom_score": 3,
        "truth_score": 3,
        "notes": "励ます曲が実は感情抑圧している典型例"
    },
    {
        "title": "残酷な天使のテーゼ",
        "artist": "高橋洋子",
        "year": 1997,
        "genre": "アニソン",
        "emotion_type": "反抗/覚醒",
        "emotion_function": "覚醒",
        "consciousness_level": 9,
        "consciousness_notes": "「少年よ神話になれ」という超越へのメッセージ。エヴァンゲリオンという集合的覚醒との共鳴",
        "lyrics_keywords": ["天使", "神話", "少年", "残酷", "魂"],
        "cultural_impact": "大",
        "sales_copies": 2920000,
        "soul_freedom_score": 9,
        "truth_score": 8,
        "notes": "90年代の精神的危機の中で生まれた覚醒の歌"
    },
    {
        "title": "First Love",
        "artist": "宇多田ヒカル",
        "year": 1999,
        "genre": "R&B",
        "emotion_type": "純粋な初恋",
        "emotion_function": "共鳴",
        "consciousness_level": 8,
        "consciousness_notes": "感情の細部への忠実な描写。演技のない本物の表現",
        "lyrics_keywords": ["最後のキス", "初めて", "時間", "忘れない"],
        "cultural_impact": "大",
        "sales_copies": 10000000,
        "soul_freedom_score": 8,
        "truth_score": 9,
        "notes": "アルバム760万枚。感情の真実に触れる稀な作品"
    },
    # ===== 2000年代 =====
    {
        "title": "tsunami",
        "artist": "サザンオールスターズ",
        "year": 2000,
        "genre": "J-pop",
        "emotion_type": "愛/祝祭",
        "emotion_function": "共鳴",
        "consciousness_level": 6,
        "consciousness_notes": "桑田佳祐の言語遊びと感情の真実が混在",
        "lyrics_keywords": ["涙", "波", "愛", "海"],
        "cultural_impact": "大",
        "sales_copies": 2936000,
        "soul_freedom_score": 6,
        "truth_score": 6,
        "notes": "ミレニアムの集合的高揚感"
    },
    {
        "title": "Lemon",
        "artist": "米津玄師",
        "year": 2018,
        "genre": "J-pop",
        "emotion_type": "喪失/悼み",
        "emotion_function": "昇華",
        "consciousness_level": 9,
        "consciousness_notes": "死者への本物の悼み。感情の商品化を拒んだ正直な表現",
        "lyrics_keywords": ["レモン", "夢", "あなた", "雨", "月"],
        "cultural_impact": "大",
        "sales_copies": 3584030,
        "soul_freedom_score": 9,
        "truth_score": 10,
        "notes": "現代日本で最も「魂の真実」に近い大ヒット曲の一つ"
    },
    {
        "title": "千本桜",
        "artist": "黒うさP（初音ミク）",
        "year": 2011,
        "genre": "ボカロ",
        "emotion_type": "反抗/覚醒/日本的美",
        "emotion_function": "覚醒",
        "consciousness_level": 8,
        "consciousness_notes": "ネットから生まれた権力への反抗と日本的美の融合。商業システム外から生まれた真正性",
        "lyrics_keywords": ["千本桜", "夜に紛れ", "革命", "咲く", "散る"],
        "cultural_impact": "大",
        "soul_freedom_score": 8,
        "truth_score": 7,
        "notes": "既存の音楽産業を経ずに生まれた革命的な曲"
    },
    {
        "title": "粉雪",
        "artist": "レミオロメン",
        "year": 2005,
        "genre": "ロック",
        "emotion_type": "純粋な愛/切なさ",
        "emotion_function": "共鳴",
        "consciousness_level": 7,
        "consciousness_notes": "商業的にはシンプルだが感情の真実がある",
        "lyrics_keywords": ["粉雪", "舞い上がれ", "君", "白"],
        "cultural_impact": "大",
        "soul_freedom_score": 7,
        "truth_score": 7,
        "notes": "冬ドラマタイアップだが楽曲自体に力がある"
    },
    {
        "title": "さよならエレジー",
        "artist": "菅田将暉",
        "year": 2018,
        "genre": "J-pop",
        "emotion_type": "別れ/哀愁",
        "emotion_function": "共鳴",
        "consciousness_level": 7,
        "consciousness_notes": "石崎ひゅーい作。別れの複雑な感情を正直に",
        "lyrics_keywords": ["さよなら", "エレジー", "君"],
        "cultural_impact": "中",
        "soul_freedom_score": 7,
        "truth_score": 7,
        "notes": ""
    },
    # ===== ヒップホップ =====
    {
        "title": "ヒップホップ自由人",
        "artist": "スチャダラパー",
        "year": 1992,
        "genre": "ヒップホップ",
        "emotion_type": "自由/反抗",
        "emotion_function": "覚醒",
        "consciousness_level": 9,
        "consciousness_notes": "「自由人」という宣言。奴隷プロトコルへの正面からの反抗",
        "lyrics_keywords": ["自由", "ヒップホップ", "解放"],
        "cultural_impact": "中",
        "soul_freedom_score": 9,
        "truth_score": 9,
        "notes": "日本ヒップホップの良心"
    },
    {
        "title": "DA.YO.NE",
        "artist": "EAST END×YURI",
        "year": 1994,
        "genre": "ヒップホップ",
        "emotion_type": "日常/共感",
        "emotion_function": "共鳴",
        "consciousness_level": 6,
        "consciousness_notes": "日常の「あるある」感覚を音楽に。サブカルチャーの大衆化",
        "lyrics_keywords": ["だよね", "そうでしょ", "普通"],
        "cultural_impact": "大",
        "soul_freedom_score": 6,
        "truth_score": 6,
        "notes": "J-rapの大ヒット。日常言語の音楽化"
    },
    {
        "title": "晴れ渡る空",
        "artist": "ブッダブランド",
        "year": 1994,
        "genre": "ヒップホップ",
        "emotion_type": "反抗/真実",
        "emotion_function": "覚醒",
        "consciousness_level": 10,
        "consciousness_notes": "日本ヒップホップ最初期の覚醒曲。社会への鋭い眼差し",
        "lyrics_keywords": ["社会", "真実", "現実"],
        "cultural_impact": "小",
        "soul_freedom_score": 10,
        "truth_score": 10,
        "notes": "商業的成功より魂の真実を優先した作品"
    },
    # ===== 演歌 =====
    {
        "title": "北の宿から",
        "artist": "都はるみ",
        "year": 1976,
        "genre": "演歌",
        "emotion_type": "諦め/執着",
        "emotion_function": "共鳴",
        "consciousness_level": 4,
        "consciousness_notes": "演歌的な諦めと未練。日本的な「あきらめの美学」",
        "lyrics_keywords": ["北", "宿", "別れ", "雪"],
        "cultural_impact": "大",
        "soul_freedom_score": 4,
        "truth_score": 6,
        "notes": "演歌の諦めは奴隷プロトコルか、それとも悟りか"
    },
    # ===== バンド系 =====
    {
        "title": "紅",
        "artist": "X JAPAN",
        "year": 1989,
        "genre": "ビジュアル系/ロック",
        "emotion_type": "愛/狂気/死",
        "emotion_function": "解放",
        "consciousness_level": 8,
        "consciousness_notes": "愛と死の境界を消した。日本的な美意識と西洋ロックの融合",
        "lyrics_keywords": ["紅", "愛", "涙", "散る"],
        "cultural_impact": "大",
        "soul_freedom_score": 8,
        "truth_score": 8,
        "notes": "ビジュアル系という「型」の中での真の自由の表現"
    },
    {
        "title": "Tomorrow never knows",
        "artist": "Mr.Children",
        "year": 1994,
        "genre": "ロック",
        "emotion_type": "実存的不安/希望",
        "emotion_function": "覚醒",
        "consciousness_level": 8,
        "consciousness_notes": "「どんな方法で愛を信じればいい」という正直な問い",
        "lyrics_keywords": ["tomorrow", "答え", "迷い", "どこへ"],
        "cultural_impact": "大",
        "sales_copies": 2740000,
        "soul_freedom_score": 8,
        "truth_score": 8,
        "notes": "J-pop最大級のセールスと真実の両立"
    },
    # ===== アニソン =====
    {
        "title": "魂のルフラン",
        "artist": "高橋洋子",
        "year": 1997,
        "genre": "アニソン",
        "emotion_type": "再生/魂",
        "emotion_function": "覚醒",
        "consciousness_level": 9,
        "consciousness_notes": "「帰れ 少女よ 原初の言葉へ」魂の根源への呼びかけ",
        "lyrics_keywords": ["魂", "帰れ", "ルフラン", "少女"],
        "cultural_impact": "大",
        "soul_freedom_score": 9,
        "truth_score": 9,
        "notes": "エヴァンゲリオンEnd of Evangelion。集合的無意識への触れ方"
    },
    {
        "title": "ふわふわ時間",
        "artist": "放課後ティータイム",
        "year": 2009,
        "genre": "アニソン",
        "emotion_type": "純粋な喜び/青春",
        "emotion_function": "解放",
        "consciousness_level": 7,
        "consciousness_notes": "けいおん！のテーマ。「何もしない」という反生産性の肯定",
        "lyrics_keywords": ["ふわふわ", "音楽", "楽しい", "放課後"],
        "cultural_impact": "大",
        "soul_freedom_score": 7,
        "truth_score": 7,
        "notes": "「頑張る」を強制しない音楽の価値"
    },
    # ===== 現代（2020年代）=====
    {
        "title": "夜に駆ける",
        "artist": "YOASOBI",
        "year": 2019,
        "genre": "J-pop",
        "emotion_type": "絶望/愛/共死",
        "emotion_function": "昇華",
        "consciousness_level": 8,
        "consciousness_notes": "死を肯定し、愛の中で昇華する。タブーへの真正面からの向き合い",
        "lyrics_keywords": ["夜", "駆ける", "消えてしまいそう", "愛"],
        "cultural_impact": "大",
        "soul_freedom_score": 8,
        "truth_score": 9,
        "notes": "小説原作という新フォーマット。死のタブーを突破"
    },
    {
        "title": "うっせぇわ",
        "artist": "Ado",
        "year": 2020,
        "genre": "J-pop",
        "emotion_type": "反抗/怒り",
        "emotion_function": "解放",
        "consciousness_level": 7,
        "consciousness_notes": "社会の規範への反抗。しかし怒りの解放に留まり構造批判には至らない",
        "lyrics_keywords": ["うっせぇ", "優秀", "クソ", "規範"],
        "cultural_impact": "大",
        "soul_freedom_score": 7,
        "truth_score": 7,
        "notes": "Z世代の抑圧された怒りの代弁。しかし革命には至らない"
    },
    {
        "title": "Pale Blue",
        "artist": "米津玄師",
        "year": 2021,
        "genre": "J-pop",
        "emotion_type": "愛/変容",
        "emotion_function": "昇華",
        "consciousness_level": 9,
        "consciousness_notes": "愛の複雑な真実。単純な「愛は美しい」を超えた",
        "lyrics_keywords": ["青", "愛", "変わる", "揺れる"],
        "cultural_impact": "大",
        "soul_freedom_score": 9,
        "truth_score": 9,
        "notes": "米津玄師の哲学的深化"
    },
    # ===== 民謡・伝統 =====
    {
        "title": "花〜すべての人の心に花を〜",
        "artist": "喜納昌吉&チャンプルーズ",
        "year": 1980,
        "genre": "沖縄民謡/J-pop",
        "emotion_type": "愛/平和/普遍",
        "emotion_function": "覚醒",
        "consciousness_level": 10,
        "consciousness_notes": "「泣きなさい笑いなさい」という完全な感情の自由の宣言。全ての感情を肯定する",
        "lyrics_keywords": ["花", "心", "泣く", "笑う", "愛"],
        "cultural_impact": "大",
        "soul_freedom_score": 10,
        "truth_score": 10,
        "notes": "日本の歌の中で最も魂の自由度が高い作品の一つ。沖縄の霊性"
    },
    {
        "title": "芭蕉布",
        "artist": "沖縄民謡",
        "year": 1965,
        "genre": "沖縄民謡",
        "emotion_type": "郷土愛/誇り",
        "emotion_function": "共鳴",
        "consciousness_level": 8,
        "consciousness_notes": "植民地支配下でも失われなかった沖縄の魂の歌",
        "lyrics_keywords": ["芭蕉布", "沖縄", "故郷", "誇り"],
        "cultural_impact": "大",
        "soul_freedom_score": 8,
        "truth_score": 9,
        "notes": "支配に抗う文化的アイデンティティの表現"
    },
]

def seed_database():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    now = datetime.now().isoformat()
    
    inserted = 0
    for song in INITIAL_SONGS:
        if isinstance(song.get('lyrics_keywords'), list):
            song['lyrics_keywords'] = json.dumps(song['lyrics_keywords'], ensure_ascii=False)
        song['analyzed_at'] = now
        
        columns = ', '.join(song.keys())
        placeholders = ', '.join(['?' for _ in song])
        
        try:
            c.execute(f"INSERT INTO songs ({columns}) VALUES ({placeholders})", list(song.values()))
            inserted += 1
        except Exception as e:
            print(f"Error inserting {song['title']}: {e}")
    
    conn.commit()
    conn.close()
    print(f"{inserted}曲を登録完了")

def show_analysis():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    print("\n=== SUIKA音楽研究 初期分析 ===\n")
    
    c.execute("SELECT COUNT(*) FROM songs")
    print(f"総曲数: {c.fetchone()[0]}")
    
    print("\n--- ジャンル別 ---")
    c.execute("SELECT genre, COUNT(*) as cnt FROM songs GROUP BY genre ORDER BY cnt DESC")
    for row in c.fetchall():
        print(f"  {row[0]}: {row[1]}曲")
    
    print("\n--- 意識レベル別 ---")
    c.execute("""
        SELECT 
            CASE 
                WHEN consciousness_level >= 8 THEN '覚醒（8-10）'
                WHEN consciousness_level >= 5 THEN '中間（5-7）'
                ELSE '奴隷脳（1-4）'
            END as level_group,
            COUNT(*) as cnt,
            ROUND(AVG(soul_freedom_score), 1) as avg_soul
        FROM songs
        GROUP BY level_group
        ORDER BY cnt DESC
    """)
    for row in c.fetchall():
        print(f"  {row[0]}: {row[1]}曲 (魂の自由度平均: {row[2]})")
    
    print("\n--- 魂の自由度 TOP 10 ---")
    c.execute("""
        SELECT title, artist, year, soul_freedom_score, truth_score
        FROM songs
        ORDER BY soul_freedom_score DESC, truth_score DESC
        LIMIT 10
    """)
    for i, row in enumerate(c.fetchall(), 1):
        print(f"  {i}. {row[0]} - {row[1]} ({row[2]}) 自由度:{row[3]} 真実度:{row[4]}")
    
    print("\n--- 奴隷脳スコア低い曲 TOP 5 ---")
    c.execute("""
        SELECT title, artist, year, soul_freedom_score, consciousness_notes
        FROM songs
        ORDER BY soul_freedom_score ASC
        LIMIT 5
    """)
    for i, row in enumerate(c.fetchall(), 1):
        print(f"  {i}. {row[0]} - {row[1]} ({row[2]}) 自由度:{row[3]}")
        print(f"     → {row[4]}")
    
    print("\n--- 感情機能別 ---")
    c.execute("SELECT emotion_function, COUNT(*) FROM songs WHERE emotion_function IS NOT NULL GROUP BY emotion_function")
    for row in c.fetchall():
        print(f"  {row[0]}: {row[1]}曲")
    
    conn.close()

if __name__ == "__main__":
    seed_database()
    show_analysis()
