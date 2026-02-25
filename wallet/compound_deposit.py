#!/usr/bin/env python3
"""
USDC を Compound v3 (cUSDCv3) Ethereum mainnet に預けるスクリプト
APY ~2.48% (2026-02-19時点)
"""

from web3 import Web3
from eth_account import Account

Account.enable_unaudited_hdwallet_features()
MNEMONIC = "shoulder decide render sight blind bar trick model left holiday stuff version"
account = Account.from_mnemonic(MNEMONIC)
address = account.address
private_key = account.key

RPC_URL = "https://1rpc.io/eth"
w3 = Web3(Web3.HTTPProvider(RPC_URL, request_kwargs={"timeout": 15}))

USDC = Web3.to_checksum_address("0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48")
COMET = Web3.to_checksum_address("0xc3d688B66703497DAA19211EEdff47f25384cdc3")

ERC20_ABI = [
    {"name": "balanceOf", "type": "function", "inputs": [{"name": "account", "type": "address"}], "outputs": [{"name": "", "type": "uint256"}], "stateMutability": "view"},
    {"name": "allowance", "type": "function", "inputs": [{"name": "owner", "type": "address"}, {"name": "spender", "type": "address"}], "outputs": [{"name": "", "type": "uint256"}], "stateMutability": "view"},
    {"name": "approve", "type": "function", "inputs": [{"name": "spender", "type": "address"}, {"name": "amount", "type": "uint256"}], "outputs": [{"name": "", "type": "bool"}], "stateMutability": "nonpayable"},
]

COMET_ABI = [
    {"name": "supply", "type": "function", "inputs": [{"name": "asset", "type": "address"}, {"name": "amount", "type": "uint256"}], "outputs": [], "stateMutability": "nonpayable"},
    {"name": "balanceOf", "type": "function", "inputs": [{"name": "account", "type": "address"}], "outputs": [{"name": "", "type": "uint256"}], "stateMutability": "view"},
]

usdc_contract = w3.eth.contract(address=USDC, abi=ERC20_ABI)
comet_contract = w3.eth.contract(address=COMET, abi=COMET_ABI)

usdc_bal = usdc_contract.functions.balanceOf(address).call()
eth_bal = w3.eth.get_balance(address)
gas_price = w3.eth.gas_price
nonce = w3.eth.get_transaction_count(address)

print(f"Wallet: {address}")
print(f"ETH: {w3.from_wei(eth_bal, 'ether'):.6f}")
print(f"USDC: {usdc_bal / 1e6:.2f}")
print(f"Gas: {gas_price / 1e9:.4f} gwei")
print(f"Nonce: {nonce}")

# Step 1: approve
print("\n=== Step 1: Approve USDC to Compound v3 ===")
allowance = usdc_contract.functions.allowance(address, COMET).call()
print(f"Current allowance: {allowance / 1e6:.2f} USDC")

if allowance < usdc_bal:
    approve_tx = usdc_contract.functions.approve(COMET, usdc_bal).build_transaction({
        "from": address,
        "nonce": nonce,
        "gasPrice": gas_price,
    })
    gas_est = w3.eth.estimate_gas(approve_tx)
    approve_tx["gas"] = gas_est
    gas_cost = gas_est * gas_price / 1e18
    print(f"Approve gas: {gas_est}, cost: {gas_cost:.8f} ETH (${gas_cost * 1970:.4f})")

    signed = account.sign_transaction(approve_tx)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    print(f"Approve tx: https://etherscan.io/tx/{tx_hash.hex()}")
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
    status = "SUCCESS" if receipt.status == 1 else "FAIL"
    print(f"Approve: {status}")
    nonce += 1
else:
    print("Already approved, skipping")

# Step 2: supply
print("\n=== Step 2: Supply USDC to Compound v3 ===")
supply_tx = comet_contract.functions.supply(USDC, usdc_bal).build_transaction({
    "from": address,
    "nonce": nonce,
    "gasPrice": gas_price,
})
gas_est = w3.eth.estimate_gas(supply_tx)
supply_tx["gas"] = gas_est
gas_cost = gas_est * gas_price / 1e18
print(f"Supply gas: {gas_est}, cost: {gas_cost:.8f} ETH (${gas_cost * 1970:.4f})")

signed = account.sign_transaction(supply_tx)
tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
print(f"Supply tx: https://etherscan.io/tx/{tx_hash.hex()}")
receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
status = "SUCCESS" if receipt.status == 1 else "FAIL"
print(f"Supply: {status}")

# Check cUSDCv3 balance
c_bal = comet_contract.functions.balanceOf(address).call()
print(f"\ncUSDCv3 balance: {c_bal / 1e6:.4f}")

print("\n=== Done ===")
print(f"Deposited {usdc_bal / 1e6:.2f} USDC to Compound v3")
print(f"APY ~2.48%, monthly yield ~$0.21")
print(f"Etherscan: https://etherscan.io/address/{address}")
