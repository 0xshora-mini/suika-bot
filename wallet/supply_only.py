#!/usr/bin/env python3
"""
Supply USDC to Compound v3 (approve済み)
"""
from web3 import Web3
from eth_account import Account

Account.enable_unaudited_hdwallet_features()
MNEMONIC = "shoulder decide render sight blind bar trick model left holiday stuff version"
account = Account.from_mnemonic(MNEMONIC)
address = account.address

w3 = Web3(Web3.HTTPProvider("https://1rpc.io/eth", request_kwargs={"timeout": 15}))

USDC = Web3.to_checksum_address("0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48")
COMET = Web3.to_checksum_address("0xc3d688B66703497DAA19211EEdff47f25384cdc3")

ERC20_ABI = [
    {"name": "balanceOf", "type": "function", "inputs": [{"name": "account", "type": "address"}], "outputs": [{"name": "", "type": "uint256"}], "stateMutability": "view"},
]
COMET_ABI = [
    {"name": "supply", "type": "function", "inputs": [{"name": "asset", "type": "address"}, {"name": "amount", "type": "uint256"}], "outputs": [], "stateMutability": "nonpayable"},
    {"name": "balanceOf", "type": "function", "inputs": [{"name": "account", "type": "address"}], "outputs": [{"name": "", "type": "uint256"}], "stateMutability": "view"},
]

usdc_c = w3.eth.contract(address=USDC, abi=ERC20_ABI)
comet_c = w3.eth.contract(address=COMET, abi=COMET_ABI)

usdc_bal = usdc_c.functions.balanceOf(address).call()
eth_bal = w3.eth.get_balance(address)

# Use minimal gas price (base fee only, no priority fee)
base_fee = w3.eth.get_block("latest")["baseFeePerGas"]
gas_price = int(base_fee * 1.1)  # base + 10% buffer, no priority fee

print(f"ETH: {w3.from_wei(eth_bal, 'ether'):.8f} = {eth_bal} wei")
print(f"USDC to supply: {usdc_bal / 1e6:.2f}")
print(f"base_fee: {base_fee / 1e9:.4f} gwei")
print(f"gas_price: {gas_price / 1e9:.4f} gwei")

# Estimate gas for supply
nonce = w3.eth.get_transaction_count(address)
print(f"Nonce: {nonce}")

# Build supply tx with explicit low gas price
supply_data = comet_c.functions.supply(USDC, usdc_bal)._encode_transaction_data()

# Manual gas estimate via eth_estimateGas
try:
    gas_est = w3.eth.estimate_gas({
        "from": address,
        "to": COMET,
        "data": supply_data,
        "gasPrice": gas_price,
    })
    print(f"Gas estimate: {gas_est}")
except Exception as e:
    print(f"Gas estimate failed: {e}")
    gas_est = 300000  # fallback

gas_cost_wei = gas_est * gas_price
print(f"Gas cost: {gas_cost_wei / 1e18:.8f} ETH = ${gas_cost_wei / 1e18 * 1970:.4f}")
print(f"ETH needed: {gas_cost_wei} wei, ETH have: {eth_bal} wei")

if eth_bal < gas_cost_wei:
    print(f"INSUFFICIENT ETH! Need {(gas_cost_wei - eth_bal) / 1e18:.8f} ETH more")
    # Try with even lower gas
    gas_price2 = base_fee + 1  # absolute minimum
    gas_cost_wei2 = gas_est * gas_price2
    print(f"With minimum gas ({gas_price2/1e9:.4f} gwei): {gas_cost_wei2} wei needed")
    if eth_bal >= gas_cost_wei2:
        gas_price = gas_price2
        gas_cost_wei = gas_cost_wei2
        print("Using minimum gas price")
    else:
        print("Still not enough. Exiting.")
        exit(1)

# Send supply tx
tx = {
    "from": address,
    "to": COMET,
    "data": supply_data,
    "gas": gas_est,
    "gasPrice": gas_price,
    "nonce": nonce,
    "chainId": 1,
}

signed = account.sign_transaction(tx)
tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
print(f"\nSupply tx sent: https://etherscan.io/tx/{tx_hash.hex()}")

receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
status = "SUCCESS" if receipt.status == 1 else "FAIL"
print(f"Supply: {status} (block {receipt['blockNumber']})")

c_bal = comet_c.functions.balanceOf(address).call()
eth_remaining = w3.eth.get_balance(address)
print(f"\ncUSDCv3 balance: {c_bal / 1e6:.4f} USDC")
print(f"ETH remaining: {w3.from_wei(eth_remaining, 'ether'):.8f}")
