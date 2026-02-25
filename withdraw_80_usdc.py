#!/usr/bin/env python3
"""
Hyperliquidから$80をArbitrumに出金するスクリプト
"""
import json
from eth_account import Account
from hyperliquid.exchange import Exchange
from hyperliquid.info import Info
from hyperliquid.utils import constants

def main():
    # Mnemonicを読み込み
    with open('/Users/shora-mini/shora-bot/suika-bot/wallet/.wallet_secret', 'r') as f:
        content = f.read().strip()
    
    # mnemonic行を抽出
    for line in content.split('\n'):
        if line.startswith('mnemonic:'):
            mnemonic = line.split('mnemonic:')[1].strip()
            break
    
    # Mnemonicからアカウントを復元
    Account.enable_unaudited_hdwallet_features()
    account = Account.from_mnemonic(mnemonic)
    address = account.address
    
    print(f"Wallet address: {address}")
    
    # Mainnet API URL
    api_url = constants.MAINNET_API_URL
    
    # Infoオブジェクトで現在の状態を確認
    info = Info(api_url, skip_ws=True)
    user_state = info.user_state(address)
    
    print(f"\n現在の状態:")
    print(f"Account value: ${user_state.get('marginSummary', {}).get('accountValue', 'N/A')}")
    print(f"Withdrawable: ${user_state.get('withdrawable', 'N/A')}")
    
    # Exchangeオブジェクトを作成
    exchange = Exchange(
        account,
        api_url,
        account_address=address
    )
    
    # メインウォレットであることを確認
    if exchange.account_address != exchange.wallet.address:
        raise Exception("API Walletでは出金できません。メインウォレットが必要です。")
    
    # $80を出金（USDCとして）
    withdraw_amount = 80.0
    print(f"\n{withdraw_amount} USDCをArbitrumに出金中...")
    
    # 出金実行（destinationは同じアドレス）
    withdraw_result = exchange.withdraw_from_bridge(withdraw_amount, address)
    
    print(f"\n出金結果:")
    print(json.dumps(withdraw_result, indent=2))
    
    if withdraw_result.get('status') == 'ok':
        print(f"\n✅ 出金リクエスト成功！")
        print(f"出金額: ${withdraw_amount}")
        print(f"宛先: {address} (Arbitrum)")
    else:
        print(f"\n❌ 出金失敗: {withdraw_result}")
    
    return withdraw_result

if __name__ == "__main__":
    main()
