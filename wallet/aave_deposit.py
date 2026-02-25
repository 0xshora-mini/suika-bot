#!/usr/bin/env python3
"""
USDC を Aave v3 Ethereum mainnet に預けるスクリプト
"""

from web3 import Web3
from eth_account import Account
from mnemonic import Mnemonic
import json, time

# ============================================================
# Config
# ============================================================
MNEMONIC = "shoulder decide render sight blind bar trick model left holiday stuff version"
RPC_URL = "https://1rpc.io/eth"

# Aave v3 Ethereum mainnet
AAVE_POOL = "0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2"
USDC_ADDR = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"

# ABIs (minimal)
ERC20_ABI = [
    {"name": "balanceOf", "type": "function", "inputs": [{"name": "account", "type": "address"}], "outputs": [{"name": "", "type": "uint256"}], "stateMutability": "view"},
    {"name": "allowance", "type": "function", "inputs": [{"name": "owner", "type": "address"}, {"name": "spender", "type": "address"}], "outputs": [{"name": "", "type": "uint256"}], "stateMutability": "view"},
    {"name": "approve", "type": "function", "inputs": [{"name": "spender", "type": "address"}, {"name": "amount", "type": "uint256"}], "outputs": [{"name": "", "type": "bool"}], "stateMutability": "nonpayable"},
]

AAVE_POOL_ABI = [
    {"name": "supply", "type": "function", "inputs": [
        {"name": "asset", "type": "address"},
        {"name": "amount", "type": "uint256"},
        {"name": "onBehalfOf", "type": "address"},
        {"name": "referralCode", "type": "uint16"}
    ], "outputs": [], "stateMutability": "nonpayable"},
    {"name": "getReserveData", "type": "function", "inputs": [{"name": "asset", "type": "address"}], "outputs": [
        {"name": "configuration", "type": "tuple", "components": [{"name": "data", "type": "uint256"}]},
        {"name": "liquidityIndex", "type": "uint128"},
        {"name": "currentLiquidityRate", "type": "uint128"},
        {"name": "variableBorrowIndex", "type": "uint128"},
        {"name": "currentVariableBorrowRate", "type": "uint128"},
        {"name": "currentStableBorrowRate", "type": "uint128"},
        {"name": "lastUpdateTimestamp", "type": "uint40"},
        {"name": "id", "type": "uint16"},
        {"name": "aTokenAddress", "type": "address"},
        {"name": "stableDebtTokenAddress", "type": "address"},
        {"name": "variableDebtTokenAddress", "type": "address"},
        {"name": "interestRateStrategyAddress", "type": "address"},
        {"name": "accruedToTreasury", "type": "uint128"},
        {"name": "unbacked", "type": "uint128"},
        {"name": "isolationModeTotalDebt", "type": "uint128"},
    ], "stateMutability": "view"},
]

# ============================================================
# Main
# ============================================================
Account.enable_unaudited_hdwallet_features()
account = Account.from_mnemonic(MNEMONIC)
address = account.address
private_key = account.key

w3 = Web3(Web3.HTTPProvider(RPC_URL))
print(f"Connected: {w3.is_connected()}")
print(f"Wallet: {address}")

# ETH balance
eth_bal = w3.eth.get_balance(address)
print(f"ETH: {w3.from_wei(eth_bal, 'ether'):.6f}")

# USDC balance
usdc = w3.eth.contract(address=Web3.to_checksum_address(USDC_ADDR), abi=ERC20_ABI)
usdc_bal = usdc.functions.balanceOf(address).call()
print(f"USDC: {usdc_bal / 1e6:.2f}")

# Aave pool
pool = w3.eth.contract(address=Web3.to_checksum_address(AAVE_POOL), abi=AAVE_POOL_ABI)

# Check current APY
reserve = pool.functions.getReserveData(Web3.to_checksum_address(USDC_ADDR)).call()
liquidity_rate = reserve[2]  # currentLiquidityRate (RAY = 1e27)
apy = (liquidity_rate / 1e27) * 100
print(f"Aave USDC supply APY: {apy:.4f}%")

# Gas price
gas_price = w3.eth.gas_price
print(f"Gas price: {gas_price / 1e9:.4f} gwei")
nonce = w3.eth.get_transaction_count(address)
print(f"Nonce: {nonce}")

# ============================================================
# Step 1: approve USDC to Aave pool
# ============================================================
print("\n--- Step 1: approve ---")
approve_amount = usdc_bal  # approve full balance

# check current allowance
allowance = usdc.functions.allowance(address, Web3.to_checksum_address(AAVE_POOL)).call()
print(f"Current allowance: {allowance / 1e6:.2f} USDC")

if allowance < approve_amount:
    approve_tx = usdc.functions.approve(
        Web3.to_checksum_address(AAVE_POOL),
        approve_amount
    ).build_transaction({
        "from": address,
        "nonce": nonce,
        "gasPrice": gas_price,
    })
    
    # estimate gas
    gas_est = w3.eth.estimate_gas(approve_tx)
    approve_tx["gas"] = gas_est
    gas_cost_eth = gas_est * gas_price / 1e18
    gas_cost_usd = gas_cost_eth * 1970  # ~ETH price
    print(f"Gas estimate: {gas_est}, cost: ${gas_cost_usd:.4f}")
    
    signed = account.sign_transaction(approve_tx)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    print(f"Approve tx: {tx_hash.hex()}")
    
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
    print(f"Approve status: {'OK' if receipt.status == 1 else 'FAIL'}")
    nonce += 1
else:
    print("Allowance sufficient, skipping approve")

# ============================================================
# Step 2: supply USDC to Aave
# ============================================================
print("\n--- Step 2: supply ---")
supply_tx = pool.functions.supply(
    Web3.to_checksum_address(USDC_ADDR),
    approve_amount,
    address,
    0  # referralCode
).build_transaction({
    "from": address,
    "nonce": nonce,
    "gasPrice": gas_price,
})

gas_est = w3.eth.estimate_gas(supply_tx)
supply_tx["gas"] = gas_est
gas_cost_eth = gas_est * gas_price / 1e18
gas_cost_usd = gas_cost_eth * 1970
print(f"Gas estimate: {gas_est}, cost: ${gas_cost_usd:.4f}")

signed = account.sign_transaction(supply_tx)
tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
print(f"Supply tx: {tx_hash.hex()}")

receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
print(f"Supply status: {'OK' if receipt.status == 1 else 'FAIL'}")

print("\n=== Done ===")
print(f"Deposited {usdc_bal / 1e6:.2f} USDC to Aave v3 Ethereum")
print(f"APY: {apy:.4f}%")
print(f"Expected monthly gain: ${usdc_bal / 1e6 * apy / 100 / 12:.4f}")
