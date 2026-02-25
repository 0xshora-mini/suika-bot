#!/usr/bin/env python3
import json, urllib.request

RPC = "https://arb1.arbitrum.io/rpc"

def get_eth_price():
    url = "https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd"
    req = urllib.request.Request(url, headers={"Accept": "application/json", "User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=10) as r:
        data = json.loads(r.read())
    return data["ethereum"]["usd"]

def get_dex_quote(rpc, quoter_addr, token_in, token_out, amount_in_wei, fee=500):
    """Uniswap v3 QuoterV2 quoteExactInputSingle"""
    # ABI encode: (address tokenIn, address tokenOut, uint256 amountIn, uint24 fee, uint160 sqrtPriceLimitX96)
    # selector: 0xcdca1753
    def pad32(val, hex_str=False):
        if hex_str:
            return val.replace('0x','').zfill(64)
        return hex(val).replace('0x','').zfill(64)
    
    data = "0xcdca1753"
    data += pad32(token_in, True)
    data += pad32(token_out, True)
    data += pad32(amount_in_wei)
    data += pad32(fee)
    data += pad32(0)  # sqrtPriceLimitX96
    
    payload = {"jsonrpc":"2.0","method":"eth_call","params":[{"to":quoter_addr,"data":data},"latest"],"id":1}
    req = urllib.request.Request(rpc, data=json.dumps(payload).encode(), headers={"Content-Type":"application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=5) as r:
            result = json.loads(r.read())
        if "result" in result and result["result"] and result["result"] != "0x":
            # First 32 bytes = amountOut
            amount_out = int(result["result"][2:66], 16)
            return amount_out
    except:
        pass
    return None

if __name__ == "__main__":
    eth_price = get_eth_price()
    print(f"ETH price (CoinGecko): ${eth_price:,.2f}")
    
    USDC = "0xFF970A61A04b1cA14834A43f5dE4533eBDDB5CC8"
    WETH = "0x82aF49447D8a07e3bd95BD0d56f35241523fBab1"
    UNI_QUOTER = "0x61fFE014bA17989E743c5F6cB21bF9697530B21e"
    
    amount_usdc = 100 * 10**6  # 100 USDC
    
    uni_out = get_dex_quote(RPC, UNI_QUOTER, USDC, WETH, amount_usdc, 500)
    if uni_out:
        uni_eth = uni_out / 10**18
        uni_price = amount_usdc / 10**6 / uni_eth
        print(f"Uniswap v3 (0.05%): 100 USDC = {uni_eth:.6f} ETH (price: ${uni_price:,.2f})")
    else:
        print("Uniswap v3: Quote failed")
    
    print(f"\n価格差があれば裁定機会あり。CoinGecko参考価格: ${eth_price:,.2f}")
