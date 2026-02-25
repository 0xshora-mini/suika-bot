#!/usr/bin/env python3
"""
Arbitrum上のUSDC残高を確認するスクリプト
"""
import time
from web3 import Web3

# Arbitrum One RPC
ARBITRUM_RPC = "https://arb1.arbitrum.io/rpc"

# USDC contract addresses on Arbitrum
USDC_BRIDGED = "0xFF970A61A04b1cA14834A43f5dE4533eBDDB5CC8"  # USDC.e (bridged)
USDC_NATIVE = "0xaf88d065e77c8cC2239327C5EDb3A432268e5831"   # Native USDC

# ERC20 ABI (balanceOf)
ERC20_ABI = [
    {
        "constant": True,
        "inputs": [{"name": "_owner", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "balance", "type": "uint256"}],
        "type": "function",
    }
]

def check_balance(w3, token_address, wallet_address, token_name):
    """指定されたトークンの残高を確認"""
    contract = w3.eth.contract(address=Web3.to_checksum_address(token_address), abi=ERC20_ABI)
    balance_wei = contract.functions.balanceOf(Web3.to_checksum_address(wallet_address)).call()
    balance = balance_wei / 10**6  # USDCは6 decimals
    return balance

def main():
    wallet_address = "0x0165ca6E898c13DfF9d1DEBedb969863B6Ed0313"
    
    print(f"Wallet: {wallet_address}")
    print(f"Arbitrum RPCに接続中...")
    
    w3 = Web3(Web3.HTTPProvider(ARBITRUM_RPC))
    
    if not w3.is_connected():
        print("❌ Arbitrumに接続できませんでした")
        return
    
    print("✅ 接続成功\n")
    
    # ETH残高
    eth_balance = w3.eth.get_balance(wallet_address)
    eth_balance_ether = w3.from_wei(eth_balance, 'ether')
    print(f"ETH残高: {eth_balance_ether} ETH")
    
    # USDC.e (bridged) 残高
    usdc_bridged_balance = check_balance(w3, USDC_BRIDGED, wallet_address, "USDC.e")
    print(f"USDC.e (Bridged) 残高: ${usdc_bridged_balance:.2f}")
    
    # Native USDC 残高
    usdc_native_balance = check_balance(w3, USDC_NATIVE, wallet_address, "Native USDC")
    print(f"Native USDC 残高: ${usdc_native_balance:.2f}")
    
    total_usdc = usdc_bridged_balance + usdc_native_balance
    print(f"\n合計USDC: ${total_usdc:.2f}")
    
    return {
        'eth': float(eth_balance_ether),
        'usdc_bridged': usdc_bridged_balance,
        'usdc_native': usdc_native_balance,
        'total_usdc': total_usdc
    }

if __name__ == "__main__":
    print("Arbitrum残高確認中...\n")
    result = main()
    
    # 着金待ちループ（最大5分）
    print("\n着金を待機中...")
    for i in range(10):  # 30秒ごとに10回チェック（5分間）
        time.sleep(30)
        print(f"\n[{i+1}/10] 再確認中...")
        result = main()
        if result and result['total_usdc'] >= 79:  # 手数料を考慮して79ドル以上
            print("\n✅ 着金確認！")
            break
    else:
        print("\n⏰ タイムアウト。手動で確認してください。")
