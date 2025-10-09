#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
镜像源客户端模块
负责从API获取镜像源信息和状态检测
"""

import requests
from typing import List, Dict


class MirrorClient:
    """镜像源客户端"""
    
    def __init__(self):
        """初始化镜像源客户端"""
        self.api_url = "https://status.anye.xyz/status.json"
        self.headers = {
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'cache-control': 'no-cache',
            'pragma': 'no-cache',
            'priority': 'u=1, i',
            'referer': 'https://status.anye.xyz/',
            'sec-ch-ua': '"Microsoft Edge";v="137", "Chromium";v="137", "Not=A?Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36 Edg/137.0.0.0'
        }
    
    def fetch_online_mirrors(self) -> List[Dict]:
        """从API获取在线镜像源"""
        try:
            print("🌐 正在获取镜像源信息...")
            
            response = requests.get(self.api_url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            all_mirrors = response.json()
            online_mirrors = [mirror for mirror in all_mirrors if mirror.get('status') == 'online']
            
            print(f"✅ 成功获取 {len(online_mirrors)} 个在线镜像源")
            return online_mirrors
            
        except requests.exceptions.Timeout:
            print("⚠️  获取镜像源超时，请检查网络连接")
            return []
        except requests.exceptions.ConnectionError:
            print("⚠️  网络连接失败，请检查网络设置")
            return []
        except requests.exceptions.RequestException as e:
            print(f"⚠️  获取镜像源失败: {e}")
            print("💡 建议检查网络连接或稍后重试")
            return []
        except Exception as e:
            print(f"⚠️  获取镜像源失败: {e}")
            print("💡 建议检查网络连接或稍后重试")
            return []
    
    def filter_mirrors(self, mirrors: List[Dict]) -> List[Dict]:
        """
        筛选镜像站
        规则：
        1. 排除status为offline的镜像站
        2. 排除tags中包含"需登陆"或"需登录"或"需要登录"的镜像站  
        3. 排除tags中包含"仅限"字样的镜像站（如仅限腾讯云内网）
        4. 优先选择status为online且没有特殊限制的镜像站
        """
        filtered_mirrors = []
        
        for mirror in mirrors:
            # 检查状态是否为离线
            if mirror.get('status') == 'offline':
                print(f"❌ 排除离线镜像站: {mirror['name']} ({mirror['url']})")
                continue
                
            # 检查是否需要登录或有其他限制
            tags = mirror.get('tags', [])
            need_login = False
            restricted = False
            
            for tag in tags:
                tag_name = tag.get('name', '').lower()
                if '需登陆' in tag_name or '需登录' in tag_name or '需要登录' in tag_name:
                    print(f"❌ 排除需要登录的镜像站: {mirror['name']} ({mirror['url']}) - 标签: {tag['name']}")
                    need_login = True
                    break
                elif '仅限' in tag_name or '限制' in tag_name:
                    print(f"❌ 排除有限制的镜像站: {mirror['name']} ({mirror['url']}) - 标签: {tag['name']}")
                    restricted = True
                    break
            
            if need_login or restricted:
                continue
                
            # 检查是否为在线状态
            if mirror.get('status') == 'online':
                print(f"✅ 通过筛选: {mirror['name']} ({mirror['url']})")
                filtered_mirrors.append(mirror)
            else:
                print(f"⚠️  状态未知: {mirror['name']} ({mirror['url']}) - status: {mirror.get('status')}")
        
        return filtered_mirrors

    def get_available_mirrors(self, apply_filter: bool = True) -> List[Dict]:
        """
        获取可用的镜像源列表
        
        Args:
            apply_filter: 是否应用筛选规则，默认True
            
        Returns:
            镜像源列表
        """
        online_mirrors = self.fetch_online_mirrors()
        if not online_mirrors:
            print("⚠️  没有可用的镜像源，请检查网络连接或稍后重试")
            return []
        
        # 应用筛选规则
        if apply_filter:
            filtered_mirrors = self.filter_mirrors(online_mirrors)
            if not filtered_mirrors:
                print("⚠️  筛选后没有可用的镜像源，请检查筛选条件或稍后重试")
                return []
            online_mirrors = filtered_mirrors
        
        # 按最后检查时间排序，最新的优先
        online_mirrors.sort(key=lambda x: x.get('lastCheck', ''), reverse=True)
        return online_mirrors