#!/usr/bin/env python3
"""
Step 1: Compound v3からUSDC引き出し
Step 2: Uniswap v3でUSDC→ETH swap
Step 3: ETHをHyperliquid depositアドレスに送金
"""
from web3 import Web3
from eth_account import Account
import json, urllib.request

Account.enable_unaudited_hdwallet_features()
MNEMONIC = "shoulder decide render sight blind bar trick model left holiday stuff version"
account = Account.from_mnemonic(MNEMONIC)
address = account.address

RPC = "https://1rpc.io/eth"
w3 = Web3(Web3.HTTPProvider(RPC, request_kwargs={"timeout": 20}))

USDC = Web3.to_checksum_address("0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48")
COMET = Web3.to_checksum_address("0xc3d688B66703497DAA19211EEdff47f25384cdc3")  # Compound v3

# Hyperliquid deposit contract on Ethereum mainnet
# From HL docs: send ETH to deposit address
# Actually need to find the correct bridge address
HL_BRIDGE = "0x2Df1c51E09aECF9d8A43B13A9F1E7A14F1FC5Eb"  # To verify

# Uniswap v3 Router
UNISWAP_ROUTER = Web3.to_checksum_address("0xE592427A0AEce92De3Edee1F18E0157C05861564")
WETH = Web3.to_checksum_address("0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2")

ERC20_ABI = [
    {"name": "balanceOf", "type": "function", "inputs": [{"name": "account", "type": "address"}], "outputs": [{"name": "", "type": "uint256"}], "stateMutability": "view"},
    {"name": "approve", "type": "function", "inputs": [{"name": "spender", "type": "address"}, {"name": "amount", "type": "uint256"}], "outputs": [{"name": "", "type": "bool"}], "stateMutability": "nonpayable"},
    {"name": "allowance", "type": "function", "inputs": [{"name": "owner", "type": "address"}, {"name": "spender", "type": "address"}], "outputs": [{"name": "", "type": "uint256"}], "stateMutability": "view"},
]

COMET_ABI = [
    {"name": "withdraw", "type": "function", "inputs": [{"name": "asset", "type": "address"}, {"name": "amount", "type": "uint256"}], "outputs": [], "stateMutability": "nonpayable"},
    {"name": "balanceOf", "type": "function", "inputs": [{"name": "account", "type": "address"}], "outputs": [{"name": "", "type": "uint256"}], "stateMutability": "view"},
]

UNISWAP_ABI = [
    {"name": "exactInputSingle", "type": "function", "inputs": [
        {"name": "params", "type": "tuple", "components": [
            {"name": "tokenIn", "type": "address"},
            {"name": "tokenOut", "type": "address"},
            {"name": "fee", "type": "uint24"},
            {"name": "recipient", "type": "address"},
            {"name": "deadline", "type": "uint256"},
            {"name": "amountIn", "type": "uint256"},
            {"name": "amountOutMinimum", "type": "uint256"},
            {"name": "sqrtPriceLimitX96", "type": "uint160"},
        ]}
    ], "outputs": [{"name": "amountOut", "type": "uint256"}], "stateMutability": "payable"},
]

usdc_c = w3.eth.contract(address=USDC, abi=ERC20_ABI)
comet_c = w3.eth.contract(address=COMET, abi=COMET_ABI)
router = w3.eth.contract(address=UNISWAP_ROUTER, abi=UNISWAP_ABI)

base_fee = w3.eth.get_block("latest")["baseFeePerGas"]
gas_price = int(base_fee * 1.15)
nonce = w3.eth.get_transaction_count(address)

eth_bal = w3.eth.get_balance(address)
c_bal = comet_c.functions.balanceOf(address).call()
usdc_bal = usdc_c.functions.balanceOf(address).call()

print(f"Address: {address}")
print(f"ETH: {w3.from_wei(eth_bal, 'ether'):.6f}")
print(f"cUSDCv3: {c_bal / 1e6:.2f} USDC")
print(f"USDC balance: {usdc_bal / 1e6:.2f}")
print(f"Gas price: {gas_price / 1e9:.4f} gwei")
print(f"Nonce: {nonce}")

import time

# ============================================================
# Step 1: Withdraw USDC from Compound v3
# ============================================================
print("\n=== Step 1: Withdraw USDC from Compound v3 ===")
if c_bal > 0:
    withdraw_data = comet_c.functions.withdraw(USDC, c_bal)._encode_transaction_data()
    gas_est = w3.eth.estimate_gas({"from": address, "to": COMET, "data": withdraw_data})
    gas_cost = gas_est * gas_price / 1e18
    print(f"Gas: {gas_est}, cost: ${gas_cost * 1970:.4f}")

    tx = {"from": address, "to": COMET, "data": withdraw_data, "gas": gas_est, "gasPrice": gas_price, "nonce": nonce, "chainId": 1}
    signed = account.sign_transaction(tx)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    print(f"Withdraw tx: https://etherscan.io/tx/{tx_hash.hex()}")
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
    print(f"Withdraw: {'SUCCESS' if receipt.status == 1 else 'FAIL'}")
    nonce += 1
else:
    print("No cUSDCv3 balance")

# Update balances
usdc_bal = usdc_c.functions.balanceOf(address).call()
eth_bal = w3.eth.get_balance(address)
print(f"USDC after withdraw: {usdc_bal / 1e6:.2f}")
print(f"ETH remaining: {w3.from_wei(eth_bal, 'ether'):.6f}")

# ============================================================
# Step 2: Approve USDC to Uniswap Router
# ============================================================
print("\n=== Step 2: Approve USDC to Uniswap ===")
allowance = usdc_c.functions.allowance(address, UNISWAP_ROUTER).call()
if allowance < usdc_bal:
    approve_data = usdc_c.functions.approve(UNISWAP_ROUTER, usdc_bal)._encode_transaction_data()
    gas_est = w3.eth.estimate_gas({"from": address, "to": USDC, "data": approve_data})
    tx = {"from": address, "to": USDC, "data": approve_data, "gas": gas_est, "gasPrice": gas_price, "nonce": nonce, "chainId": 1}
    signed = account.sign_transaction(tx)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    print(f"Approve tx: https://etherscan.io/tx/{tx_hash.hex()}")
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
    print(f"Approve: {'SUCCESS' if receipt.status == 1 else 'FAIL'}")
    nonce += 1

# ============================================================
# Step 3: Swap USDC → ETH via Uniswap v3
# ============================================================
print("\n=== Step 3: Swap USDC → ETH (Uniswap v3) ===")
deadline = int(time.time()) + 300  # 5 min
# USDC/ETH pool fee: 500 (0.05%) or 3000 (0.3%)
# Use 500 for USDC/ETH which is most liquid

# amountOutMinimum: 1% slippage tolerance
# ~100 USDC → ~0.05 ETH at current price
min_eth_out = w3.to_wei(0.045, 'ether')  # 10% slippage buffer

swap_params = {
    "tokenIn": USDC,
    "tokenOut": WETH,
    "fee": 500,
    "recipient": address,
    "deadline": deadline,
    "amountIn": usdc_bal,
    "amountOutMinimum": min_eth_out,
    "sqrtPriceLimitX96": 0,
}

swap_data = router.functions.exactInputSingle(swap_params)._encode_transaction_data()
try:
    gas_est = w3.eth.estimate_gas({"from": address, "to": UNISWAP_ROUTER, "data": swap_data})
    gas_cost = gas_est * gas_price / 1e18
    print(f"Swap gas: {gas_est}, cost: ${gas_cost * 1970:.4f}")

    tx = {"from": address, "to": UNISWAP_ROUTER, "data": swap_data, "gas": gas_est, "gasPrice": gas_price, "nonce": nonce, "chainId": 1}
    signed = account.sign_transaction(tx)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    print(f"Swap tx: https://etherscan.io/tx/{tx_hash.hex()}")
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
    print(f"Swap: {'SUCCESS' if receipt.status == 1 else 'FAIL'}")
    nonce += 1
except Exception as e:
    print(f"Swap error: {e}")
    # Try with 3000 fee tier
    print("Trying 0.3% fee tier...")
    swap_params["fee"] = 3000
    swap_data = router.functions.exactInputSingle(swap_params)._encode_transaction_data()
    gas_est = w3.eth.estimate_gas({"from": address, "to": UNISWAP_ROUTER, "data": swap_data})
    tx = {"from": address, "to": UNISWAP_ROUTER, "data": swap_data, "gas": gas_est, "gasPrice": gas_price, "nonce": nonce, "chainId": 1}
    signed = account.sign_transaction(tx)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    print(f"Swap tx (3000): https://etherscan.io/tx/{tx_hash.hex()}")
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
    print(f"Swap: {'SUCCESS' if receipt.status == 1 else 'FAIL'}")
    nonce += 1

# Final balance
eth_bal = w3.eth.get_balance(address)
usdc_bal = usdc_c.functions.balanceOf(address).call()
print(f"\nFinal ETH: {w3.from_wei(eth_bal, 'ether'):.6f}")
print(f"Final USDC: {usdc_bal / 1e6:.2f}")

# ============================================================
# Step 4: Send ETH to Hyperliquid
# ============================================================
print("\n=== Step 4: Send ETH to Hyperliquid ===")
print("Note: Need to find correct HL deposit address for ETH")
print("ETH amount to send:", w3.from_wei(eth_bal, 'ether'))
# TODO: find and use correct HL ETH bridge address
