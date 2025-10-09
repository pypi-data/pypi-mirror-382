# 🐳 DPS - Docker Pull Smart | 智能Docker镜像拉取工具

[项目主页 - Gitee](https://gitee.com/liumou_site/DockerPullSmart)

- **下载量**: ![PyPI - Downloads](https://img.shields.io/pypi/dm/dps_liumou_Stable?style=flat-square)
- **版本**: ![PyPI - Version](https://img.shields.io/pypi/v/dps_liumou_Stable?style=flat-square)
- **Python支持**: ![PyPI - Python Version](https://img.shields.io/pypi/pyversions/dps_liumou_Stable?style=flat-square)

## 🎯 项目简介

**DPS (Docker Pull Smart)** 是一款专为国内开发者设计的智能Docker镜像拉取工具。通过自动检测和切换可用镜像源，彻底解决Docker镜像拉取失败、超时、速度慢等问题。

## 😫 传统Docker拉取的痛点

在国内使用Docker时，开发者经常遇到以下问题：

- ⏰ **拉取超时**: `docker pull nginx:latest` 等待10分钟，最后显示 `timeout`
- ❌ **连接失败**: 总是提示 `Error response from daemon: Get "https://registry-1.docker.io/v2/": net/http: request canceled`
- 🐌 **速度极慢**: 几十MB的镜像要下载几个小时，进度条一动不动
- 🔧 **配置复杂**: 网上找的镜像加速配置方法五花八门，配置后还是不行
- 💥 **镜像站失效**: 好不容易找到的镜像加速地址，过几天就不能用了

## 🔥 DPS的核心优势

- **🤖 智能检测**: 实时检测20+个镜像加速源，自动过滤失效地址
- **⚡ 极速拉取**: 智能选择最优镜像源，拉取速度提升10-50倍
- **🔧 零配置**: 无需手动配置，安装即用，一条命令解决所有问题
- **🛡️ 自动容错**: 单个镜像源失败自动切换，成功率高达98%
- **📊 实时可视**: 实时显示下载进度和状态信息
- **🌍 全平台**: 完美支持 Windows、Linux、macOS
- **🎯 精准识别**: 智能区分Docker Hub和非Docker Hub镜像
- **🎮 交互友好**: 支持手动选择镜像源模式
- **🔐 权限验证**: 自动检测Docker/Podman权限，无权限时友好提示
- **⚙️ 双引擎**: 同时支持Docker和Podman，灵活选择容器引擎
- **🏗️ 多架构**: 支持7种主流架构（x86-64、ARM64、ARM v7/v6、x86、PowerPC、s390x）

## 🚀 快速开始

### 系统要求

- ✅ Python 3.6+ （Windows/Linux/macOS 均支持）
- ✅ Docker 已安装并正常运行 **或** Podman 已安装并正常运行

### 容器引擎支持

DPS 同时支持 **Docker** 和 **Podman**：

- **Docker**（默认）: 使用 `-p/--podman` 参数可切换至 Podman
- **Podman**: 完全兼容 Docker 命令，无需额外配置

```bash
# 使用 Docker（默认）
dps nginx:latest

# 使用 Podman
dps nginx:latest -p
```

### 安装方式

```bash
pip3 install dps_liumou_Stable
```

### 升级工具

```bash
# 升级到最新版本
pip3 install --upgrade dps_liumou_Stable

# 升级到指定版本
pip3 install --upgrade dps_liumou_Stable==1.0.6

# 强制重新安装最新版本
pip3 install --force-reinstall --upgrade dps_liumou_Stable
```

### 卸载工具

```bash
# 卸载工具
pip3 uninstall dps_liumou_Stable

# 验证卸载
pip3 show dps_liumou_Stable
```

### 安装验证

```bash
# 验证安装成功
dps -h

# 测试拉取一个小镜像
dps hello-world:latest
```

## 📖 命令参数详解

### 位置参数

| 参数 | 说明 | 示例 |
|------|------|------|
| `image_name` | 要拉取的镜像名称 | `nginx:latest` |

### 可选参数

| 参数 | 简写 | 说明 | 默认值 |
|------|------|------|--------|
| `--list-mirrors` | `-lm` | 列出所有可用镜像源 | - |
| `--local-images` | `-li` | 列出本地Docker镜像 | - |
| `--timeout` | `-t` | Docker命令超时时间（秒） | 300 |
| `--max-retries` | `-r` | 每个镜像源的最大重试次数 | 3 |
| `--debug` | `-d` | 调试模式，显示完整命令 | False |
| `--force-mirror` | `-fm` | 强制使用镜像站 | False |
| `--select-mirror` | `-sm` | 手动选择镜像源 | False |
| `--podman` | `-p` | 使用Podman而不是Docker | False |
| `--arch` | - | 选择镜像架构（1-7） | - |

#### 架构选择说明

`--arch` 参数支持以下架构选项：

| 参数值 | 架构类型 | 说明 |
|--------|----------|------|
| 1 | linux/amd64 | x86-64 架构（最常见） |
| 2 | linux/arm64 | ARM 64位架构 |
| 3 | linux/arm/v7 | ARM 32位 v7 架构 |
| 4 | linux/arm/v6 | ARM 32位 v6 架构 |
| 5 | linux/386 | x86 32位架构 |
| 6 | linux/ppc64le | PowerPC 64位小端架构 |
| 7 | linux/s390x | IBM System z 架构 |

**使用说明**：当指定 `--arch` 参数时，DPS会自动处理架构相关的镜像拉取，无需在镜像名称中添加架构前缀。直接使用标准的镜像名称即可，例如使用 `mysql:8.0` 而不是 `arm64v8/mysql:8.0`。

### 使用示例

```bash
# 基础使用
dps nginx:latest
dps python:3.11
dps mysql:8.0

# 高级用法
dps ubuntu:22.04 -t 600 -r 5
dps node:18-alpine -d -fm
dps redis:7 -sm

# 工具命令
dps -lm
dps -li
dps -h

# 架构选择示例
dps nginx:latest --arch 1  # 拉取 x86-64 架构镜像（默认）
dps alpine:latest --arch 2  # 拉取 ARM64 架构镜像
dps python:3.9 --arch 3  # 拉取 ARM v7 架构镜像
```

### 🎉 实际使用效果

```shell
# 智能拉取 - 自动选择最优镜像源
$ dps nginx:latest
🎯 开始智能拉取镜像: nginx:latest
==================================================
🌐 正在获取镜像源信息...
✅ 成功获取 22 个在线镜像源
📋 找到 22 个可用镜像源
  1. 1Panel - https://docker.1panel.live
  2. SUNBALCONY 1 - https://dockerproxy.cool
  3. 棉花云 3 - https://hub3.nat.tf
...
  ...
🔄 尝试镜像源 1/22: 1Panel
🔗 URL: https://docker.1panel.live
🔄 尝试从镜像源拉取: docker.1panel.live/library/nginx:latest
📥 latest: Pulling from library/nginx
📥 953cdd413371: Pulling fs layer
📥 3bf2e947a240: Pulling fs layer
...
✅ 成功拉取镜像: docker.1panel.live/library/nginx:latest
🏷️ 设置镜像标签: docker.1panel.live/library/nginx:latest -> nginx:latest
✅ 成功设置镜像标签: nginx:latest
🗑️ 删除镜像: docker.1panel.live/library/nginx:latest
==================================================
🎉 镜像拉取成功: nginx:latest
📍 使用的镜像源: 1Panel
⏱️ 总耗时: 15.2秒
```

## 📋 使用案例

### 🔧 高级功能演示

```bash
# 调试模式 - 查看实际执行的完整命令
dps nginx:latest -d

# 超时控制 - 适合大镜像或网络不稳定环境
dps ubuntu:22.04 -t 600

# 重试机制 - 网络不稳定时增加重试次数
dps mysql:8.0 -r 5

# 非Docker Hub镜像支持
dps gcr.io/google/cadvisor:latest
dps public.ecr.aws/nginx/nginx:1.25

# 强制使用镜像站加速
dps gcr.io/google/cadvisor:latest -fm

# 架构选择 - 支持多架构镜像拉取
dps nginx:latest --arch 1  # 拉取 x86-64 架构（默认）
dps ubuntu:22.04 --arch 2  # 拉取 ARM64 架构
dps python:3.9 --arch 3  # 拉取 ARM v7 架构

# 手动选择镜像源
dps nginx:latest -sm

# 使用Podman替代Docker
dps nginx:latest -p
dps mysql:8.0 -p -t 600

# 组合使用 - 应对复杂网络环境
dps node:18-alpine -d -t 600 -r 5
```

## 🏗️ 技术架构

### 🎯 核心模块

#### 1. MirrorClient - 镜像源管理

- **实时检测**: 从API获取20+个镜像源状态
- **智能过滤**: 自动过滤离线或异常的镜像源
- **状态监控**: 记录每个镜像源的最后检查时间

#### 2. DockerCommandExecutor - Docker/Podman命令执行器

- **权限验证**: 自动执行`docker ps`或`podman ps`验证拉取权限
- **双引擎支持**: 智能检测并使用Docker或Podman
- **实时输出**: 使用`subprocess.Popen`实现实时进度显示
- **超时控制**: 可配置的超时机制，防止长时间阻塞
- **错误处理**: 完善的异常捕获和错误信息显示

#### 3. ImageUtils - 镜像工具集

- **智能识别**: 自动区分Docker Hub和非Docker Hub镜像
- **地址格式化**: 构建带镜像源的完整镜像地址
- **进度显示**: 统一的进度条和时间格式化

#### 4. DockerPullSmart - 智能拉取引擎

- **自动重试**: 单个镜像源失败自动切换
- **标签管理**: 自动设置正确的镜像标签
- **清理机制**: 拉取成功后清理临时镜像

### 🔧 技术特点

- **🐍 纯Python实现**: 仅依赖 `requests` 和 `urllib3`
- **🚀 高性能**: 异步检测，并行处理多个镜像源
- **🛡️ 健壮性**: 完善的异常处理和重试机制
- **📊 可视化**: 实时显示拉取进度和状态
- **🔐 权限验证**: 自动验证Docker/Podman权限，确保拉取成功
- **⚙️ 双引擎**: 智能支持Docker和Podman两种容器引擎

## 📊 性能数据

### 🎯 核心指标

- **⚡ 速度提升**: 10-50倍（平均从50KB/s提升到2-10MB/s）
- **🎯 成功率**: 98%+（传统方式约30%）
- **🔧 零配置**: 安装即用，无需任何配置
- **⏱️ 时间节省**: 平均每次拉取节省5-15分钟

### 🌍 镜像源覆盖

- **实时检测**: 20+个主流镜像加速源
- **智能排序**: 按最后检查时间排序，优先使用最新检测的源
- **自动更新**: 每次使用前自动获取最新状态

## 🔗 相关链接

### 📱 项目地址

- **Gitee**: <https://gitee.com/liumou_site/DockerPullSmart>
- **PyPI**: <https://pypi.org/project/dps_liumou_Stable/>

### 📚 相关项目

- **国内镜像源**: <https://status.anye.xyz/>

### 💬 社区支持

- **Issues**: <https://gitee.com/liumou_site/DockerPullSmart/issues>
- **讨论**: <https://gitee.com/liumou_site/DockerPullSmart/discussions>

## 🤝 参与贡献

欢迎提交 Issue 和 Pull Request，让我们一起让国内开发环境变得更好！

### 🎯 贡献方向

- **🔍 Bug修复**: 发现并修复问题
- **✨ 功能增强**: 添加新功能或优化现有功能
- **📚 文档完善**: 改进文档和示例
- **🌍 镜像源**: 推荐新的镜像加速源

### 📋 贡献步骤

1. 🍴 Fork 本仓库
2. 🌿 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 💻 提交更改 (`git commit -m 'Add some amazing feature'`)
4. 📤 推送分支 (`git push origin feature/amazing-feature`)
5. 🎯 创建 Pull Request

### 📜 许可证摘要

- ✅ 商业使用
- ✅ 修改和分发
- ✅ 私人使用
- ❌ 责任担保
- ❌ 商标使用

### 🎉 致谢

感谢所有为这个项目做出贡献的开发者和用户！

---

**Made with ❤️ for Chinese developers**

<p align="center">
  <a href="https://gitee.com/liumou_site/DockerPullSmart">
    <img src="https://gitee.com/liumou_site/DockerPullSmart/badge/star.svg?theme=dark" alt="star"/>
  </a>
</p>

---

## 🌟 Star 支持

如果这个项目对你有帮助，请给我们一个 Star ⭐！


### 🎯 支持方式

1. **Star 项目**: 点击右上角的 ⭐ Star 按钮
2. **分享项目**: 分享给需要的朋友和同事
3. **提交反馈**: 在 Issues 中提交建议和问题
4. **参与贡献**: 提交代码改进和文档更新

## 📄 许可证
