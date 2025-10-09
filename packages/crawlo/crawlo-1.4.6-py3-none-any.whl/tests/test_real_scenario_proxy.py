#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
真实场景代理测试
================
使用用户提供的headers、cookies和URL测试代理功能
"""

import asyncio
import aiohttp
import sys
import os
from urllib.parse import urlparse

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# 用户提供的请求头
HEADERS = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
    "cache-control": "no-cache",
    "pragma": "no-cache",
    "priority": "u=0, i",
    "sec-ch-ua": "\"Chromium\";v=\"140\", \"Not=A?Brand\";v=\"24\", \"Google Chrome\";v=\"140\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "none",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36"
}

# 用户提供的cookies
COOKIES = {
    "Hm_lvt_722143063e4892925903024537075d0d": "1758071793",
    "Hm_lvt_929f8b362150b1f77b477230541dbbc2": "1758071793",
    "historystock": "600699",
    "spversion": "20130314",
    "cid": "example_cid_value",
    "u_ukey": "example_u_ukey_value",
    "u_uver": "1.0.0",
    "u_dpass": "example_u_dpass_value",
    "u_did": "example_u_did_value",
    "u_ttype": "WEB",
    "user_status": "0",
    "ttype": "WEB",
    "log": "",
    "Hm_lvt_69929b9dce4c22a060bd22d703b2a280": "example_Hm_lvt_value",
    "HMACCOUNT": "example_HMACCOUNT_value",
    "Hm_lvt_78c58f01938e4d85eaf619eae71b4ed1": "example_Hm_lvt_value",
    "user": "example_user_value",
    "userid": "example_userid_value",
    "u_name": "example_u_name_value",
    "escapename": "example_escapename_value",
    "ticket": "example_ticket_value",
    "utk": "example_utk_value",
    "sess_tk": "example_sess_tk_value",
    "cuc": "example_cuc_value",
    "Hm_lvt_f79b64788a4e377c608617fba4c736e2": "example_Hm_lvt_value",
    "v": "example_v_value",
    "Hm_lpvt_78c58f01938e4d85eaf619eae71b4ed1": "1758163145",
    "Hm_lpvt_f79b64788a4e377c608617fba4c736e2": "1758163145",
    "Hm_lpvt_69929b9dce4c22a060bd22d703b2a280": "1758163145"
}

# 用户提供的URL
URL = "https://stock.10jqka.com.cn/20240315/c655957791.shtml"


async def test_without_proxy():
    """不使用代理直接测试访问"""
    print("=== 不使用代理直接访问 ===")
    print(f"URL: {URL}")
    
    try:
        timeout = aiohttp.ClientTimeout(total=15)
        async with aiohttp.ClientSession(timeout=timeout, headers=HEADERS, cookies=COOKIES) as session:
            async with session.get(URL) as response:
                print(f"状态码: {response.status}")
                if response.status == 200:
                    print("直接访问成功")
                    return True
                else:
                    print(f"直接访问失败，状态码: {response.status}")
                    return False
    except Exception as e:
        print(f"直接访问出错: {e}")
        return False


async def test_with_proxy(proxy_url):
    """使用代理测试访问"""
    print(f"\n=== 使用代理访问 ===")
    print(f"代理地址: {proxy_url}")
    print(f"URL: {URL}")
    
    try:
        timeout = aiohttp.ClientTimeout(total=15)
        async with aiohttp.ClientSession(timeout=timeout, headers=HEADERS, cookies=COOKIES) as session:
            # 处理带认证的代理
            if "@" in proxy_url and "://" in proxy_url:
                parsed = urlparse(proxy_url)
                if parsed.username and parsed.password:
                    # 提取认证信息
                    auth = aiohttp.BasicAuth(parsed.username, parsed.password)
                    # 清理代理URL
                    clean_proxy = f"{parsed.scheme}://{parsed.hostname}"
                    if parsed.port:
                        clean_proxy += f":{parsed.port}"
                    
                    print(f"使用带认证的代理: {clean_proxy}")
                    async with session.get(URL, proxy=clean_proxy, proxy_auth=auth) as response:
                        print(f"状态码: {response.status}")
                        if response.status == 200:
                            print("代理访问成功")
                            return True
                        else:
                            print(f"代理访问失败，状态码: {response.status}")
                            return False
            else:
                # 直接使用代理URL
                print(f"使用代理: {proxy_url}")
                async with session.get(URL, proxy=proxy_url) as response:
                    print(f"状态码: {response.status}")
                    if response.status == 200:
                        print("代理访问成功")
                        return True
                    else:
                        print(f"代理访问失败，状态码: {response.status}")
                        return False
    except Exception as e:
        print(f"代理访问出错: {e}")
        return False


async def get_proxy_from_api():
    """从代理API获取代理"""
    proxy_api = 'http://test.proxy.api:8080/proxy/getitem/'
    print(f"\n=== 从代理API获取代理 ===")
    print(f"API地址: {proxy_api}")
    
    try:
        timeout = aiohttp.ClientTimeout(total=10)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(proxy_api) as response:
                print(f"状态码: {response.status}")
                
                if response.status == 200:
                    data = await response.json()
                    print(f"响应数据: {data}")
                    
                    # 提取代理URL
                    if isinstance(data, dict) and data.get('status') == 0:
                        proxy_info = data.get('proxy', {})
                        if isinstance(proxy_info, dict):
                            proxy_url = proxy_info.get('https') or proxy_info.get('http')
                            if proxy_url:
                                print(f"提取到的代理URL: {proxy_url}")
                                return proxy_url
                print("无法获取代理URL")
                return None
    except Exception as e:
        print(f"API请求出错: {e}")
        return None


async def main():
    """主测试函数"""
    print("开始真实场景代理测试...")
    print("=" * 50)
    
    # 1. 首先测试不使用代理直接访问
    direct_success = await test_without_proxy()
    
    # 2. 从代理API获取代理
    proxy_url = await get_proxy_from_api()
    
    if not proxy_url:
        print("\n无法获取代理，测试结束")
        return
    
    # 3. 使用代理访问
    proxy_success = await test_with_proxy(proxy_url)
    
    # 4. 测试结果总结
    print(f"\n{'='*30}")
    print("测试结果:")
    print(f"直接访问: {'成功' if direct_success else '失败'}")
    print(f"代理访问: {'成功' if proxy_success else '失败'}")


if __name__ == "__main__":
    asyncio.run(main())