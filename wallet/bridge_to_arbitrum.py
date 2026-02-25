#!/usr/bin/env python3
"""
Ethereum mainnet USDC → Arbitrum USDC (via Across Protocol)
+ ETH → Arbitrum WETH (for gas)

Plan:
1. Compound v3 から USDC withdraw
2. USDC approve to Across spokepool
3. Across depositV3 USDC 99 → Arbitrum
4. ETH → WETH wrap (0.0003 ETH)
5. WETH approve to Across spokepool
6. Across depositV3 WETH → Arbitrum
"""

from web3 import Web3
from eth_account import Account
import json, urllib.request, time

Account.enable_unaudited_hdwallet_features()
MNEMONIC = "shoulder decide render sight blind bar trick model left holiday stuff version"
account = Account.from_mnemonic(MNEMONIC)
address = account.address

RPC = "https://1rpc.io/eth"
w3 = Web3(Web3.HTTPProvider(RPC, request_kwargs={"timeout": 20}))

# Contracts
USDC = Web3.to_checksum_address("0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48")
COMET = Web3.to_checksum_address("0xc3d688B66703497DAA19211EEdff47f25384cdc3")
WETH = Web3.to_checksum_address("0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2")
ACROSS_SPOKE = Web3.to_checksum_address("0x5c7BCd6E7De5423a257D81B442095A1a6ced35C5")

# ABIs
ERC20_ABI = [
    {"name": "balanceOf", "type": "function", "inputs": [{"name": "account", "type": "address"}], "outputs": [{"name": "", "type": "uint256"}], "stateMutability": "view"},
    {"name": "approve", "type": "function", "inputs": [{"name": "spender", "type": "address"}, {"name": "amount", "type": "uint256"}], "outputs": [{"name": "", "type": "bool"}], "stateMutability": "nonpayable"},
    {"name": "allowance", "type": "function", "inputs": [{"name": "owner", "type": "address"}, {"name": "spender", "type": "address"}], "outputs": [{"name": "", "type": "uint256"}], "stateMutability": "view"},
]
COMET_ABI = [
    {"name": "withdraw", "type": "function", "inputs": [{"name": "asset", "type": "address"}, {"name": "amount", "type": "uint256"}], "outputs": [], "stateMutability": "nonpayable"},
    {"name": "balanceOf", "type": "function", "inputs": [{"name": "account", "type": "address"}], "outputs": [{"name": "", "type": "uint256"}], "stateMutability": "view"},
]
WETH_ABI = ERC20_ABI + [
    {"name": "deposit", "type": "function", "inputs": [], "outputs": [], "stateMutability": "payable"},
]
ACROSS_ABI = [
    {"name": "depositV3", "type": "function", "inputs": [
        {"name": "depositor", "type": "address"},
        {"name": "recipient", "type": "address"},
        {"name": "inputToken", "type": "address"},
        {"name": "outputToken", "type": "address"},
        {"name": "inputAmount", "type": "uint256"},
        {"name": "outputAmount", "type": "uint256"},
        {"name": "destinationChainId", "type": "uint256"},
        {"name": "exclusiveRelayer", "type": "address"},
        {"name": "quoteTimestamp", "type": "uint32"},
        {"name": "fillDeadline", "type": "uint32"},
        {"name": "exclusivityDeadline", "type": "uint32"},
        {"name": "message", "type": "bytes"},
    ], "outputs": [], "stateMutability": "payable"},
]

usdc_c = w3.eth.contract(address=USDC, abi=ERC20_ABI)
comet_c = w3.eth.contract(address=COMET, abi=COMET_ABI)
weth_c = w3.eth.contract(address=WETH, abi=WETH_ABI)
across_c = w3.eth.contract(address=ACROSS_SPOKE, abi=ACROSS_ABI)

def get_gas_price():
    base_fee = w3.eth.get_block("latest")["baseFeePerGas"]
    return int(base_fee * 1.15)

def send_tx(data, to, value=0, nonce=None, gas_price=None):
    if nonce is None:
        nonce = w3.eth.get_transaction_count(address)
    if gas_price is None:
        gas_price = get_gas_price()
    gas_est = w3.eth.estimate_gas({"from": address, "to": to, "data": data, "value": value})
    gas_cost = gas_est * gas_price / 1e18
    print(f"  Gas: {gas_est}, cost: ${gas_cost * 1970:.4f}")
    tx = {"from": address, "to": to, "data": data, "value": value, "gas": gas_est, "gasPrice": gas_price, "nonce": nonce, "chainId": 1}
    signed = account.sign_transaction(tx)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    print(f"  TX: https://etherscan.io/tx/{tx_hash.hex()}")
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
    status = "SUCCESS" if receipt.status == 1 else "FAIL"
    print(f"  Status: {status}")
    return receipt.status == 1

def get_across_quote(input_token, output_token, amount):
    url = f"https://app.across.to/api/suggested-fees?inputToken={input_token}&outputToken={output_token}&originChainId=1&destinationChainId=42161&amount={amount}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read())

# Current state
eth_bal = w3.eth.get_balance(address)
c_bal = comet_c.functions.balanceOf(address).call()
usdc_bal = usdc_c.functions.balanceOf(address).call()
nonce = w3.eth.get_transaction_count(address)

print(f"Wallet: {address}")
print(f"ETH: {w3.from_wei(eth_bal, 'ether'):.6f}")
print(f"cUSDCv3: {c_bal / 1e6:.2f}")
print(f"USDC: {usdc_bal / 1e6:.2f}")
print(f"Nonce: {nonce}")

# ============================================================
# Step 1: Withdraw from Compound
# ============================================================
if c_bal > 0:
    print(f"\n=== Step 1: Withdraw {c_bal / 1e6:.2f} USDC from Compound ===")
    data = comet_c.functions.withdraw(USDC, c_bal)._encode_transaction_data()
    ok = send_tx(data, COMET, nonce=nonce)
    if not ok: exit(1)
    nonce += 1
    usdc_bal = usdc_c.functions.balanceOf(address).call()
    print(f"  USDC balance: {usdc_bal / 1e6:.2f}")

# ============================================================
# Step 2: Get Across quote for USDC
# ============================================================
print(f"\n=== Step 2: Get Across quote for {usdc_bal / 1e6:.2f} USDC ===")
ARBI_USDC = "0xaf88d065e77c8cC2239327C5EDb3A432268e5831"
quote = get_across_quote(USDC, ARBI_USDC, usdc_bal)
output_amount = int(quote["outputAmount"])
fill_deadline = int(quote["fillDeadline"])
quote_timestamp = int(quote["timestamp"])
exclusive_relayer = Web3.to_checksum_address(quote["exclusiveRelayer"])
exclusivity_deadline = int(quote["exclusivityDeadline"])
print(f"  Output: {output_amount / 1e6:.4f} USDC on Arbitrum")
print(f"  Fee: ${(usdc_bal - output_amount) / 1e6:.4f}")

# ============================================================
# Step 3: Approve USDC to Across
# ============================================================
print(f"\n=== Step 3: Approve USDC to Across ===")
allowance = usdc_c.functions.allowance(address, ACROSS_SPOKE).call()
if allowance < usdc_bal:
    data = usdc_c.functions.approve(ACROSS_SPOKE, usdc_bal)._encode_transaction_data()
    ok = send_tx(data, USDC, nonce=nonce)
    if not ok: exit(1)
    nonce += 1

# ============================================================
# Step 4: Across depositV3 USDC → Arbitrum
# ============================================================
print(f"\n=== Step 4: Bridge USDC → Arbitrum via Across ===")
gas_price = get_gas_price()
deposit_data = across_c.functions.depositV3(
    address,   # depositor
    address,   # recipient (same wallet on Arbitrum)
    USDC,      # inputToken
    Web3.to_checksum_address(ARBI_USDC),  # outputToken
    usdc_bal,  # inputAmount
    output_amount,  # outputAmount
    42161,     # destinationChainId (Arbitrum)
    exclusive_relayer,  # exclusiveRelayer
    quote_timestamp,    # quoteTimestamp
    fill_deadline,      # fillDeadline
    exclusivity_deadline,  # exclusivityDeadline
    b"",       # message
)._encode_transaction_data()

ok = send_tx(deposit_data, ACROSS_SPOKE, nonce=nonce, gas_price=gas_price)
if not ok: exit(1)
nonce += 1

# ============================================================
# Step 5: Wrap ETH → WETH and bridge to Arbitrum
# ============================================================
eth_bal = w3.eth.get_balance(address)
print(f"\nETH remaining: {w3.from_wei(eth_bal, 'ether'):.6f}")
weth_to_bridge = min(int(0.0003 * 1e18), eth_bal - int(0.0002 * 1e18))  # keep 0.0002 ETH for gas

if weth_to_bridge > 0:
    print(f"\n=== Step 5: Wrap {weth_to_bridge / 1e18:.6f} ETH → WETH ===")
    data = weth_c.functions.deposit()._encode_transaction_data()
    ok = send_tx(data, WETH, value=weth_to_bridge, nonce=nonce, gas_price=gas_price)
    if not ok: exit(1)
    nonce += 1

    print(f"\n=== Step 6: Approve WETH to Across ===")
    data = weth_c.functions.approve(ACROSS_SPOKE, weth_to_bridge)._encode_transaction_data()
    ok = send_tx(data, WETH, nonce=nonce, gas_price=gas_price)
    if not ok: exit(1)
    nonce += 1

    print(f"\n=== Step 7: Bridge WETH → Arbitrum ===")
    ARBI_WETH = "0x82aF49447D8a07e3bd95BD0d56f35241523fBab1"
    weth_quote = get_across_quote(WETH, ARBI_WETH, weth_to_bridge)
    weth_output = int(weth_quote["outputAmount"])

    deposit_data = across_c.functions.depositV3(
        address, address, WETH, Web3.to_checksum_address(ARBI_WETH),
        weth_to_bridge, weth_output, 42161,
        Web3.to_checksum_address(weth_quote["exclusiveRelayer"]),
        int(weth_quote["timestamp"]), int(weth_quote["fillDeadline"]),
        int(weth_quote["exclusivityDeadline"]), b"",
    )._encode_transaction_data()
    ok = send_tx(deposit_data, ACROSS_SPOKE, nonce=nonce, gas_price=gas_price)
    nonce += 1

eth_final = w3.eth.get_balance(address)
print(f"\n=== Done ===")
print(f"ETH remaining (Ethereum): {w3.from_wei(eth_final, 'ether'):.6f}")
print(f"Arbitrum USDC: ~{output_amount / 1e6:.4f} (arriving in ~5 sec)")
print(f"Arbitrum WETH: ~{weth_to_bridge / 1e18:.6f} (arriving soon)")
print(f"Next: deposit USDC to Hyperliquid on Arbitrum")
