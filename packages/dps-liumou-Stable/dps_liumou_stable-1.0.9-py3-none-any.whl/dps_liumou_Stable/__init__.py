#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Docker镜像拉取智能工具 - 主模块

这个模块提供了智能的Docker镜像拉取功能，支持：
- 自动选择最优镜像源
- 支持多种Linux架构
- 镜像拉取失败自动重试
- 本地镜像管理
"""

import sys
import argparse
from typing import List, Dict, Optional

# 导入其他模块
from .mirror_client import MirrorClient
from .docker_executor import DockerCommandExecutor
from .image_utils import ImageUtils
from .docker_pull_smart import DockerPullSmart


def create_parser():
    """创建命令行参数解析器"""
    parser = argparse.ArgumentParser(
        description="Docker镜像拉取智能工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  dps_liumou_Stable nginx:latest
  dps_liumou_Stable --arch 2 python:3.9
  dps_liumou_Stable --list-mirrors
  dps_liumou_Stable --list-local
  dps_liumou_Stable --force-mirror ubuntu:20.04
  dps_liumou_Stable --select-mirror redis:latest
        """
    )
    
    # 互斥组：镜像操作相关
    action_group = parser.add_mutually_exclusive_group()
    action_group.add_argument(
        "--list-mirrors", 
        action="store_true", 
        help="列出可用镜像源"
    )
    action_group.add_argument(
        "--list-local", 
        action="store_true", 
        help="列出本地镜像"
    )
    
    # 镜像名称参数
    parser.add_argument(
        "image_name", 
        nargs="?", 
        help="要拉取的镜像名称（例如：nginx:latest）"
    )
    
    # 可选参数
    parser.add_argument(
        "--arch", 
        type=int, 
        choices=range(1, 8),
        help="选择架构：1=amd64, 2=arm64, 3=arm/v7, 4=arm/v6, 5=386, 6=ppc64le, 7=s390x"
    )
    parser.add_argument(
        "--timeout", 
        type=int, 
        default=300,
        help="拉取超时时间（秒），默认300"
    )
    parser.add_argument(
        "--max-retries", 
        type=int, 
        default=3,
        help="最大重试次数，默认3"
    )
    parser.add_argument(
        "--debug", 
        action="store_true",
        help="启用调试模式"
    )
    parser.add_argument(
        "--force-mirror", 
        action="store_true",
        help="强制使用镜像站"
    )
    parser.add_argument(
        "--select-mirror", 
        action="store_true",
        help="手动选择镜像源"
    )
    parser.add_argument(
        "--no-filter", 
        action="store_true",
        help="禁用镜像源过滤"
    )
    parser.add_argument(
        "--use-podman", 
        action="store_true",
        help="使用Podman代替Docker"
    )
    
    return parser


def main():
    """主函数"""
    parser = create_parser()
    args = parser.parse_args()
    
    # 创建工具实例
    tool = DockerPullSmart(
        debug=args.debug
    )
    
    # 处理不同的命令行参数
    if args.list_mirrors:
        mirrors = tool.get_available_mirrors(apply_filter=not args.no_filter)
        tool.print_mirror_list(mirrors)
        sys.exit(0)
    
    elif args.list_local:
        tool.list_local_images()
        sys.exit(0)
    
    elif args.image_name:
        # 设置参数
        tool.set_max_retries(args.max_retries)
        tool.set_timeout(args.timeout)
        tool.set_force_mirror(args.force_mirror)
        tool.set_select_mirror(args.select_mirror)
        tool.set_apply_filter(not args.no_filter)
        
        # 调用smart_pull方法
        success = tool.smart_pull(args.image_name, architecture=args.arch)
        sys.exit(0 if success else 1)
    
    else:
        parser.print_help()
        sys.exit(1)


# 导出main函数，使其可以通过命令行调用
__all__ = ['main']

if __name__ == "__main__":
    main()