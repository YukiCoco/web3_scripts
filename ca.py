#!/usr/bin/env python3

# Required parameters:
# @raycast.schemaVersion 1
# @raycast.title ca
# @raycast.mode fullOutput

# Optional parameters:
# @raycast.icon 🤖
# @raycast.packageName Web3

# Documentation:
# @raycast.description 找到 CA 信息
# @raycast.author Kurisu
# @raycast.authorURL https://kuri.su
# @raycast.argument1 { "type": "dropdown", "placeholder": "Chain", "data": [{"title": "Solana", "value": "501"}, {"title": "Ethereum", "value": "1"}, {"title": "Binance Smart Chain", "value": "56"}, {"title": "Base", "value": "8453"}] }
# @raycast.argument2 { "type": "text", "placeholder": "Contract" }

import sys
import requests
import json
import hmac
import base64
import hashlib
from datetime import datetime
import os

chain_index = sys.argv[1]
token_address = sys.argv[2]

# 需要填写下面的信息：OKX Web3 API
# 访问 https://web3.okx.com/zh-hans/build/dev-portal 获取
api_key = ""
api_passphrase = ""
secret_key = ""

# 构建URL和请求路径
base_url = "https://www.okx.com"
path = f"/api/v5/wallet/token/token-detail?chainIndex={chain_index}&tokenAddress={token_address}"
url = base_url + path

# 生成时间戳（ISO格式 - 确保精确到毫秒并符合OKX要求）
import time
timestamp = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'

# 生成签名
def generate_signature(timestamp, method, request_path, secret_key):
    message = timestamp + method + request_path
    mac = hmac.new(
        bytes(secret_key, encoding='utf8'),
        bytes(message, encoding='utf-8'),
        digestmod=hashlib.sha256
    )
    return base64.b64encode(mac.digest()).decode()

# 构建请求头
method = "GET"
signature = generate_signature(timestamp, method, path, secret_key)

headers = {
    'Content-Type': 'application/json',
    'OK-ACCESS-KEY': api_key,
    'OK-ACCESS-PASSPHRASE': api_passphrase,
    'OK-ACCESS-SIGN': signature,
    'OK-ACCESS-TIMESTAMP': timestamp
}

# 发送请求
response = requests.request(method, url, headers=headers, data={})

# 处理并美化输出响应
def format_token_info(data):
    if not data or not isinstance(data, list) or len(data) == 0:
        print("未找到代币信息")
        return
    
    token = data[0]
    
    # 基本信息
    print(f"\n{'='*50}")
    print(f"代币信息: {token.get('name', 'N/A')} ({token.get('symbol', 'N/A')})")
    print(f"链: {token.get('chainName', 'N/A')} (链ID: {token.get('chainIndex', 'N/A')})")
    print(f"合约地址: {token.get('tokenAddress', 'N/A')}")
    print(f"精度: {token.get('decimals', 'N/A')}")
    print(f"{'='*50}")
    
    # 供应信息
    print(f"\n供应信息:")
    print(f"总供应量: {token.get('totalSupply', 'N/A')}")
    print(f"最大供应量: {token.get('maxSupply', 'N/A')}")
    
    # 市场信息
    print(f"\n市场信息:")
    print(f"市值: ${token.get('marketCap', 'N/A')}")
    print(f"24小时交易量: ${token.get('volume24h', 'N/A') if token.get('volume24h') else 'N/A'}")
    
    # 链接信息
    print(f"\n链接:")
    print(f"Logo URL: {token.get('logoUrl', 'N/A')}")
    print(f"官方网站: {token.get('officialWebsite', 'N/A') if token.get('officialWebsite') else 'N/A'}")
    
    # 社交媒体
    social = token.get('socialUrls', {})
    if social:
        print(f"\n社交媒体:")
        for platform, urls in social.items():
            if urls and isinstance(urls, list) and len(urls) > 0:
                print(f"  {platform.capitalize()}: {', '.join(urls)}")
            else:
                print(f"  {platform.capitalize()}: N/A")

response_json = response.json()
if response_json.get('code') == "0":
    format_token_info(response_json.get('data', []))
else:
    print(f"错误: {response_json.get('msg', '未知错误')} (代码: {response_json.get('code', 'N/A')})")
    # 同时保留原始JSON输出以便调试
    print("\n原始响应:")
    print(json.dumps(response_json, indent=2, ensure_ascii=False))
