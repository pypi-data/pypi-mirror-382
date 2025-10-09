#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Docker命令执行器模块
负责执行Docker相关命令并处理输出
"""

import subprocess
import time
import shutil
import sys
from typing import List


class DockerCommandExecutor:
    """Docker命令执行器"""
    
    def __init__(self, debug: bool = False, use_podman: bool = False):
        """初始化Docker命令执行器"""
        self.debug = debug
        self.use_podman = use_podman
        self.command_prefix = self._get_command_prefix()
    
    def _get_command_prefix(self) -> str:
        """获取Docker或Podman命令前缀并验证权限"""
        if self.use_podman:
            if shutil.which('podman'):
                # 验证Podman权限
                if not self._verify_permissions('podman'):
                    print("❌ Podman权限验证失败，请确保有权限执行Podman命令")
                    sys.exit(1)
                return 'podman'
            else:
                print("❌ Podman未安装，请安装Podman或移除--use-podman参数")
                sys.exit(1)
        else:
            if shutil.which('docker'):
                # 验证Docker权限
                if not self._verify_permissions('docker'):
                    print("❌ Docker权限验证失败，请确保有权限执行Docker命令")
                    sys.exit(1)
                return 'docker'
            elif shutil.which('podman'):
                print("⚠️  Docker未安装，检测到Podman，将使用Podman")
                # 验证Podman权限
                if not self._verify_permissions('podman'):
                    print("❌ Podman权限验证失败，请确保有权限执行Podman命令")
                    sys.exit(1)
                return 'podman'
            else:
                print("❌ Docker和Podman都未安装，请先安装Docker或Podman")
                sys.exit(1)
    
    def _verify_permissions(self, command_prefix: str) -> bool:
        """验证Docker/Podman权限"""
        print(f"🔍 正在验证{command_prefix}权限...")
        try:
            # 执行ps命令验证权限
            result = subprocess.run(
                [command_prefix, 'ps'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                print(f"✅ {command_prefix}权限验证成功")
                return True
            else:
                error_msg = result.stderr.strip() if result.stderr else result.stdout.strip()
                print(f"❌ {command_prefix}权限验证失败: {error_msg}")
                return False
                
        except subprocess.TimeoutExpired:
            print(f"⏰ {command_prefix}权限验证超时")
            return False
        except Exception as e:
            print(f"❌ {command_prefix}权限验证异常: {e}")
            return False
    
    def run_docker_command(self, command: List[str], timeout: int = None) -> bool:
        """运行Docker命令"""
        if timeout is None:
            timeout = 300  # 默认超时时间
        
        # 使用命令前缀替换docker
        if command and command[0] == 'docker':
            command[0] = self.command_prefix
        
        # 调试模式下输出完整命令
        if self.debug:
            print(f"🔍 执行命令: {' '.join(command)}")
        
        try:
            # 使用实时输出模式运行命令（Windows环境优化）
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding='utf-8',
                bufsize=0,  # 无缓冲，适用于Windows
                universal_newlines=True
            )
            
            # 实时输出命令执行结果
            output_lines = []
            start_time = time.time()
            
            while True:
                # 检查进程是否结束
                if process.poll() is not None:
                    break
                    
                # 读取输出
                output = process.stdout.readline()
                if output:
                    line = output.strip()
                    output_lines.append(line)
                    
                    # 实时输出进度信息（扩展关键词匹配）
                    if any(keyword in line for keyword in ['Downloading', 'Extracting', 'Pulling', 
                                                          'Download', 'Pull', 'Layer', 'Status', 
                                                          'Verifying', 'Waiting', 'Preparing']):
                        print(f"📥 {line}")
                    elif self.debug:  # 调试模式下输出所有信息
                        print(f"📋 {line}")
                    elif line and not line.startswith('\x1b'):  # 过滤ANSI转义序列
                        # 显示其他重要信息（非ANSI转义序列）
                        print(f"ℹ️  {line}")
                else:
                    # 如果没有输出，短暂等待避免CPU占用过高
                    time.sleep(0.1)
            
            # 读取剩余输出
            remaining_output = process.stdout.read()
            if remaining_output:
                for line in remaining_output.strip().split('\n'):
                    if line:
                        output_lines.append(line)
                        if self.debug:
                            print(f"📋 {line}")
            
            end_time = time.time()
            
            if process.returncode == 0:
                if self.debug:
                    print(f"✅ 命令执行成功: {' '.join(command)} (耗时: {end_time - start_time:.1f}秒)")
                return True
            else:
                if self.debug:
                    print(f"❌ 命令执行失败: {' '.join(command)}")
                # 输出错误信息
                for line in output_lines[-5:]:  # 显示最后5行错误信息
                    if line and ('error' in line.lower() or 'failed' in line.lower()):
                        print(f"❌ {line}")
                return False
                
        except subprocess.TimeoutExpired:
            if 'process' in locals():
                process.kill()
            print(f"⏰ 命令超时: {' '.join(command)}")
            return False
        except Exception as e:
            print(f"❌ 运行命令失败: {e}")
            return False
    
    def pull_image_directly(self, image_name: str, architecture: str = None) -> bool:
        """直接使用默认docker pull命令拉取镜像
        
        Args:
            image_name: 镜像名称
            architecture: 架构名称（可选）
        """
        print(f"🔄 将使用默认命令尝试拉取...")
        command = [self.command_prefix, 'pull']
        
        # 如果指定了架构，添加架构参数
        if architecture:
            command.extend(['--platform', architecture])
        
        command.append(image_name)
        
        # 调试模式下输出完整命令
        if self.debug:
            print(f"🔍 执行默认拉取命令: {' '.join(command)}")
        
        success = self.run_docker_command(command)
        
        if success:
            print(f"✅ 镜像拉取成功: {image_name}")
        else:
            print(f"❌ 镜像拉取失败: {image_name}")
        
        return success
    
    def tag_image(self, source_image: str, target_image: str) -> bool:
        """为镜像打标签"""
        print(f"🏷️  设置镜像标签: {source_image} -> {target_image}")
        tag_command = [self.command_prefix, "tag", source_image, target_image]
        return self.run_docker_command(tag_command)
    
    def remove_image(self, image_name: str) -> bool:
        """删除镜像"""
        print(f"🗑️  删除镜像: {image_name}")
        remove_command = [self.command_prefix, "rmi", image_name]
        return self.run_docker_command(remove_command)
    
    def list_local_images(self):
        """列出本地镜像"""
        print("📦 本地镜像列表:")
        command = [self.command_prefix, "images", "--format", "table {{.Repository}}:{{.Tag}}\t{{.ID}}\t{{.CreatedAt}}"]
        self.run_docker_command(command)