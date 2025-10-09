#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
镜像工具模块
提供镜像相关的工具函数
"""

import time
from typing import List, Dict


class ImageUtils:
    """镜像工具类"""
    
    # 架构前缀映射
    ARCHITECTURE_PREFIX_MAP = {
        'linux/amd64': 'amd64',
        'linux/arm64': 'arm64v8',
        'linux/arm/v7': 'arm32v7',
        'linux/arm/v6': 'arm32v6',
        'linux/386': 'i386',
        'linux/ppc64le': 'ppc64le',
        'linux/s390x': 's390x'
    }
    
    @staticmethod
    def get_architecture_prefix(architecture: str) -> str:
        """根据架构类型获取对应的前缀
        
        Args:
            architecture: 架构类型，如 'linux/arm64'
            
        Returns:
            架构前缀，如 'arm64v8'，如果架构不支持则返回None
        """
        return ImageUtils.ARCHITECTURE_PREFIX_MAP.get(architecture)
    
    @staticmethod
    def is_docker_hub_image(image_name: str) -> bool:
        """判断是否为Docker Hub镜像
        
        Docker Hub镜像特点：
        - 不包含'/'或只包含一个'/'（命名空间/镜像名）
        - 非Docker Hub镜像通常包含两个或更多'/'（如registry.example.com/namespace/image）
        """
        # 计算斜杠数量
        slash_count = image_name.count('/')
        
        # Docker Hub镜像：没有斜杠（如nginx:latest）或只有一个斜杠（如library/nginx:latest）
        # 非Docker Hub镜像：两个或更多斜杠（如gcr.io/google/cadvisor:latest）
        return slash_count <= 1
    
    @staticmethod
    def clean_mirror_url(mirror_url: str) -> str:
        """清理镜像源URL，移除协议前缀"""
        return mirror_url.replace('https://', '').replace('http://', '')
    
    @staticmethod
    def format_mirror_image(image_name: str, mirror_url: str, architecture: str = None) -> str:
        """格式化镜像地址，构建带镜像源的完整地址
        
        对于没有命名空间的官方库镜像（如nginx:latest），自动添加library/前缀
        支持架构选择，当指定架构时会自动添加架构前缀
        
        Args:
            image_name: 镜像名称
            mirror_url: 镜像源URL
            architecture: 架构类型（如linux/arm64）
        """
        clean_url = ImageUtils.clean_mirror_url(mirror_url)
        
        # 处理架构前缀
        formatted_image = image_name
        if architecture:
            # 根据架构添加前缀
            arch_prefix = ImageUtils.get_architecture_prefix(architecture)
            if arch_prefix and not image_name.startswith(f"{arch_prefix}/"):
                # 只有当镜像名称不包含架构前缀时才添加
                formatted_image = f"{arch_prefix}/{image_name}"
        
        # 检查是否为官方库镜像（没有'/'或只有'library/'前缀）
        if '/' not in formatted_image or formatted_image.startswith('library/'):
            # 如果已经是library格式，直接使用；否则添加library前缀
            if formatted_image.startswith('library/'):
                final_image = formatted_image
            else:
                final_image = f"library/{formatted_image}"
            return f"{clean_url}/{final_image}"
        else:
            # 非官方库镜像，直接使用处理后的名称
            return f"{clean_url}/{formatted_image}"
    
    @staticmethod
    def format_time_duration(seconds: float) -> str:
        """格式化时间持续时间为易读的字符串"""
        if seconds < 60:
            return f"{seconds:.1f}秒"
        elif seconds < 3600:
            minutes = seconds / 60
            return f"{minutes:.1f}分钟"
        else:
            hours = seconds / 3600
            return f"{hours:.1f}小时"
    
    @staticmethod
    def print_mirror_list(mirrors: List[Dict]):
        """打印镜像源列表"""
        print("🌐 可用镜像源列表:")
        for i, mirror in enumerate(mirrors, 1):
            status = "🟢" if mirror.get('status') == 'online' else "🔴"
            print(f"{status} {i}. {mirror['name']}")
            print(f"   URL: {mirror['url']}")
            print(f"   最后检查: {mirror.get('lastCheck', '未知')}")
            if mirror.get('tags'):
                tags = ', '.join([tag['name'] for tag in mirror['tags']])
                print(f"   标签: {tags}")
            print()
    
    @staticmethod
    def print_progress_header(image_name: str):
        """打印进度条头部信息"""
        print(f"🎯 开始智能拉取镜像: {image_name}")
        print("=" * 50)
    
    @staticmethod
    def print_progress_footer(image_name: str, mirror_name: str, total_time: float, success: bool = True):
        """打印进度条底部信息"""
        print("=" * 50)
        if success:
            print(f"🎉 镜像拉取成功: {image_name}")
            print(f"📍 使用的镜像源: {mirror_name}")
        else:
            print(f"❌ 镜像拉取失败: {image_name}")
        print(f"⏱️  总耗时: {ImageUtils.format_time_duration(total_time)}")
    
    @staticmethod
    def sleep_with_message(seconds: float, message: str = "等待中..."):
        """带消息的延迟
        
        Args:
            seconds: 延迟秒数
            message: 显示的消息
        """
        print(f"⏳ {message} ({seconds}秒)")
        time.sleep(seconds)