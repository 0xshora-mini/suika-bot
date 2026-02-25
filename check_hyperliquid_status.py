#!/usr/bin/env python3
"""
Hyperliquidのアカウント状態と出金状況を確認
"""
from hyperliquid.info import Info
from hyperliquid.utils import constants

def main():
    address = "0x0165ca6E898c13DfF9d1DEBedb969863B6Ed0313"
    
    # Mainnet API
    info = Info(constants.MAINNET_API_URL, skip_ws=True)
    
    # ユーザー状態を確認
    user_state = info.user_state(address)
    
    print(f"Wallet: {address}\n")
    print("=== Hyperliquid Account Status ===")
    print(f"Account value: ${user_state.get('marginSummary', {}).get('accountValue', 'N/A')}")
    print(f"Withdrawable: ${user_state.get('withdrawable', 'N/A')}")
    
    # Cross margin summaryを確認
    margin_summary = user_state.get('crossMarginSummary', {})
    print(f"\nCross Margin Summary:")
    print(f"  Account Value: ${margin_summary.get('accountValue', 'N/A')}")
    print(f"  Total Margin Used: ${margin_summary.get('totalMarginUsed', 'N/A')}")
    
    # アセット詳細
    asset_positions = user_state.get('assetPositions', [])
    if asset_positions:
        print(f"\nAsset Positions:")
        for pos in asset_positions:
            print(f"  {pos.get('position', {}).get('coin', 'Unknown')}: {pos.get('position', {}).get('szi', 'N/A')}")

if __name__ == "__main__":
    main()
