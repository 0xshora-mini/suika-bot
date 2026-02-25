#!/usr/bin/env node
// たぎりスキャン: 世界でアツいこと × 内部でくすぶってること

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const MEMORY_DIR = path.join(__dirname, '..', 'memory');
const LOG_FILE = path.join(MEMORY_DIR, 'tagiri-scan.log');

async function main() {
  // Node.jsの時計が狂ってる問題の対処: システム時刻を直接取得
  const dateOutput = execSync('date "+%Y-%m-%d %H:%M:%S"', { encoding: 'utf-8' }).trim();
  const timestamp = dateOutput;
  
  try {
    // ログに記録
    const logEntry = `${timestamp} スキャン完了\n`;
    fs.appendFileSync(LOG_FILE, logEntry);
    
    // 日次memoryファイルに追記するかどうかは手動判断
    // cronで定期的に実行し、ログだけ残す
    
    console.log(`たぎりスキャン完了: ${timestamp}`);
  } catch (error) {
    const errorEntry = `${timestamp} エラー: ${error.message}\n`;
    fs.appendFileSync(LOG_FILE, errorEntry);
    console.error('たぎりスキャンエラー:', error);
    process.exit(1);
  }
}

main();
