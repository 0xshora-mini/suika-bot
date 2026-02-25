#!/usr/bin/env python3
"""
Arbitrum上のUSDC残高を確認（シンプル版）
"""
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

def main():
    wallet_address = "0x0165ca6E898c13DfF9d1DEBedb969863B6Ed0313"
    
    print(f"Wallet: {wallet_address}")
    
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
    contract_bridged = w3.eth.contract(address=Web3.to_checksum_address(USDC_BRIDGED), abi=ERC20_ABI)
    balance_bridged_wei = contract_bridged.functions.balanceOf(Web3.to_checksum_address(wallet_address)).call()
    balance_bridged = balance_bridged_wei / 10**6
    print(f"USDC.e (Bridged) 残高: ${balance_bridged:.6f}")
    
    # Native USDC 残高
    contract_native = w3.eth.contract(address=Web3.to_checksum_address(USDC_NATIVE), abi=ERC20_ABI)
    balance_native_wei = contract_native.functions.balanceOf(Web3.to_checksum_address(wallet_address)).call()
    balance_native = balance_native_wei / 10**6
    print(f"Native USDC 残高: ${balance_native:.6f}")
    
    total_usdc = balance_bridged + balance_native
    print(f"\n合計USDC: ${total_usdc:.6f}")

if __name__ == "__main__":
    main()
