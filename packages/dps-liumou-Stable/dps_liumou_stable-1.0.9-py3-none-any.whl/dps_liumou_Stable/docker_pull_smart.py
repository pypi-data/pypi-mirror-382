#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Docker镜像拉取智能工具
自动检测可用镜像加速轮询拉取镜像
"""

import sys
import time
from typing import List, Dict

from .mirror_client import MirrorClient
from .docker_executor import DockerCommandExecutor
from .image_utils import ImageUtils


class DockerPullSmart:
    """Docker镜像拉取智能工具"""
    
    # 常见Linux架构映射
    ARCHITECTURE_MAP = {
        1: 'linux/amd64',    # x86-64
        2: 'linux/arm64',    # ARM64
        3: 'linux/arm/v7',   # ARM v7
        4: 'linux/arm/v6',   # ARM v6
        5: 'linux/386',      # x86
        6: 'linux/ppc64le',  # PowerPC 64 LE
        7: 'linux/s390x'     # s390x
    }
    
    def __init__(self, timeout: int = 300, max_retries: int = 3, debug: bool = False):
        """初始化DockerPullSmart
        
        Args:
            timeout: 超时时间（秒）
            max_retries: 最大重试次数
            debug: 是否启用调试模式
        """
        self._timeout = timeout
        self._max_retries = max_retries
        self._debug = debug
        self._force_mirror = False
        self._select_mirror = False
        self._apply_filter = True
        
        # 初始化各个组件
        self.mirror_client = MirrorClient()
        self.docker_executor = DockerCommandExecutor(debug=debug)
        self.image_utils = ImageUtils()
    
    def set_timeout(self, timeout: int):
        """设置超时时间"""
        self._timeout = timeout
    
    def set_max_retries(self, max_retries: int):
        """设置最大重试次数"""
        self._max_retries = max_retries
    
    def set_debug(self, debug: bool):
        """设置调试模式"""
        self._debug = debug
        self.docker_executor.set_debug(debug)
    
    def set_force_mirror(self, force_mirror: bool):
        """设置是否强制使用镜像站"""
        self._force_mirror = force_mirror
    
    def set_select_mirror(self, select_mirror: bool):
        """设置是否手动选择镜像源"""
        self._select_mirror = select_mirror
    
    def set_apply_filter(self, apply_filter: bool):
        """设置是否应用镜像源过滤规则"""
        self._apply_filter = apply_filter
    
    def get_available_mirrors(self, apply_filter: bool = True) -> List[Dict]:
        """获取可用的镜像源列表"""
        return self.mirror_client.get_available_mirrors(apply_filter=apply_filter)
    
    def pull_image_with_mirror(self, image_name: str, mirror_url: str, architecture: str = None) -> bool:
        """使用镜像源拉取镜像
        
        Args:
            image_name: 镜像名称
            mirror_url: 镜像源URL
            architecture: 架构类型（可选）
        """
        # 清理镜像源URL，移除协议前缀
        clean_mirror_url = self.image_utils.clean_mirror_url(mirror_url)
        mirror_image = self.image_utils.format_mirror_image(image_name, mirror_url, architecture)
        print(f"🔄 尝试从镜像源拉取: {mirror_image}")
        
        # 拉取镜像
        pull_command = ["docker", "pull", mirror_image]
        if self.docker_executor.run_docker_command(pull_command):
            print(f"✅ 成功拉取镜像: {mirror_image}")
            return True
        else:
            print(f"❌ 从镜像源拉取失败: {mirror_image}")
            return False
    
    def pull_image_directly(self, image_name: str, architecture: str = None) -> bool:
        """直接使用默认docker pull命令拉取镜像
        
        Args:
            image_name: 镜像名称
            architecture: 架构类型（可选）
        """
        # 如果指定了架构，需要添加架构前缀
        final_image_name = image_name
        if architecture:
            arch_prefix = self.image_utils.get_architecture_prefix(architecture)
            if arch_prefix and not image_name.startswith(f"{arch_prefix}/"):
                final_image_name = f"{arch_prefix}/{image_name}"
        
        return self.docker_executor.pull_image_directly(final_image_name)
    
    def tag_image(self, source_image: str, target_image: str) -> bool:
        """为镜像打标签"""
        return self.docker_executor.tag_image(source_image, target_image)
    
    def remove_image(self, image_name: str) -> bool:
        """删除镜像"""
        return self.docker_executor.remove_image(image_name)
    
    def list_local_images(self):
        """列出本地镜像"""
        self.docker_executor.list_local_images()
    
    def smart_pull(self, image_name: str, architecture: int = None) -> bool:
        """智能拉取镜像
        
        Args:
            image_name: 镜像名称
            architecture: 架构选择（1-7对应不同架构）
        """
        # 打印进度头部信息
        self.image_utils.print_progress_header(image_name)
        
        # 处理架构选择
        if architecture and architecture in self.ARCHITECTURE_MAP:
            selected_arch = self.ARCHITECTURE_MAP[architecture]
            print(f"🏗️  指定架构: {selected_arch}")
        
        # 记录开始时间
        start_time = time.time()
        
        # 判断是否为Docker Hub镜像
        is_docker_hub = self.image_utils.is_docker_hub_image(image_name)
        
        if not is_docker_hub:
            print(f"📦 检测到非Docker Hub镜像: {image_name}")
            if not self._force_mirror:
                print("🔄 非Docker Hub镜像默认不使用镜像站加速")
                success = self.pull_image_directly(image_name)
                # 输出总耗时
                total_time = time.time() - start_time
                self.image_utils.print_progress_footer(image_name, "默认拉取", total_time, success)
                return success
        
        # 如果启用了强制镜像站模式
        if self._force_mirror:
            print("⚡ 强制使用镜像站模式")
        
        # 获取可用镜像源
        available_mirrors = self.get_available_mirrors(apply_filter=self._apply_filter)
        if not available_mirrors:
            print("⚠️  没有可用的镜像加速源")
            print("🔄 将使用默认命令直接拉取镜像...")
            success = self.pull_image_directly(image_name)
            # 输出总耗时
            total_time = time.time() - start_time
            self.image_utils.print_progress_footer(image_name, "默认拉取", total_time, success)
            return success
        
        print(f"📋 找到 {len(available_mirrors)} 个可用镜像源")
        for i, mirror in enumerate(available_mirrors, 1):
            print(f"  {i}. {mirror['name']} - {mirror['url']}")
        print()
        
        # 如果启用了手动选择模式
        if self._select_mirror:
            print("🎯 手动选择镜像源模式")
            selected_mirror = self._select_mirror_interactive(available_mirrors)
            if selected_mirror:
                # 只使用选中的镜像源
                available_mirrors = [selected_mirror]
            else:
                print("❌ 未选择镜像源，将使用默认拉取方式")
                # 获取架构参数
                arch = None
                if architecture and architecture in self.ARCHITECTURE_MAP:
                    arch = self.ARCHITECTURE_MAP[architecture]
                success = self.pull_image_directly(image_name, architecture=arch)
                total_time = time.time() - start_time
                self.image_utils.print_progress_footer(image_name, "默认拉取", total_time, success)
                return success
        
        # 尝试每个镜像源
        for i, mirror in enumerate(available_mirrors):
            mirror_name = mirror['name']
            mirror_url = mirror['url'].rstrip('/')
            
            print(f"🔄 尝试镜像源 {i+1}/{len(available_mirrors)}: {mirror_name}")
            print(f"🔗 URL: {mirror_url}")
            
            # 获取架构参数
            arch = None
            if architecture and architecture in self.ARCHITECTURE_MAP:
                arch = self.ARCHITECTURE_MAP[architecture]
            
            # 尝试拉取镜像
            success = False
            for retry in range(self._max_retries):
                if retry > 0:
                    print(f"🔄 第{retry}次重试...")
                
                success = self.pull_image_with_mirror(image_name, mirror_url, architecture=arch)
                if success:
                    break
                
                if retry < self._max_retries - 1:
                    self.image_utils.sleep_with_message("等待重试", 2)
            
            if success:
                # 输出总耗时
                total_time = time.time() - start_time
                self.image_utils.print_progress_footer(image_name, mirror_name, total_time, success)
                return True
            
            print(f"❌ 镜像源 {mirror_name} 拉取失败")
            if i < len(available_mirrors) - 1:
                print("🔄 尝试下一个镜像源...")
                print()
        
        # 所有镜像源都失败，尝试直接拉取
        print("❌ 所有镜像源都拉取失败")
        print("🔄 将使用默认命令直接拉取镜像...")
        
        # 获取架构参数
        arch = None
        if architecture and architecture in self.ARCHITECTURE_MAP:
            arch = self.ARCHITECTURE_MAP[architecture]
        success = self.pull_image_directly(image_name, architecture=arch)
        
        # 输出总耗时
        total_time = time.time() - start_time
        self.image_utils.print_progress_footer(image_name, "默认拉取", total_time, success)
        return success
    
    def print_mirror_list(self, mirrors: List[Dict]) -> None:
        """打印镜像源列表
        
        Args:
            mirrors: 镜像源列表
        """
        if not mirrors:
            print("❌ 没有找到可用的镜像源")
            return
        
        print(f"📋 找到 {len(mirrors)} 个可用镜像源:")
        for i, mirror in enumerate(mirrors, 1):
            status = "🟢" if mirror.get('available', True) else "🔴"
            print(f"  {i}. {status} {mirror['name']} - {mirror['url']}")
            if 'description' in mirror:
                print(f"     {mirror['description']}")
        print()

    def _select_mirror_interactive(self, available_mirrors: List[Dict]) -> Dict:
        """交互式选择镜像源
        
        Args:
            available_mirrors: 可用镜像源列表
            
        Returns:
            选中的镜像源信息，如果取消则返回None
        """
        print("\n📋 可用镜像源列表:")
        for i, mirror in enumerate(available_mirrors, 1):
            print(f"  {i}. {mirror['name']} - {mirror['url']}")
        
        while True:
            try:
                choice = input("\n🎯 请选择镜像源编号 (输入0取消): ").strip()
                if choice == '0':
                    return None
                
                choice_num = int(choice)
                if 1 <= choice_num <= len(available_mirrors):
                    return available_mirrors[choice_num - 1]
                else:
                    print(f"❌ 请输入1-{len(available_mirrors)}之间的数字")
            except ValueError:
                print("❌ 请输入有效的数字")