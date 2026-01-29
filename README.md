# Group-Auto-Clean-Member
一个AstrBot的群聊自动满员清人插件，当群聊满员时自动清理最不活跃的成员。

<div align="center">
  
  [![GitHub license](https://img.shields.io/github/license/VanillaNahida/astrbot_plugin_group_auto_clean_member?style=flat-square)](https://github.com/VanillaNahida/astrbot_plugin_group_auto_clean_member/blob/main/LICENSE)
  [![GitHub stars](https://img.shields.io/github/stars/VanillaNahida/astrbot_plugin_group_auto_clean_member?style=flat-square)](https://github.com/VanillaNahida/astrbot_plugin_group_auto_clean_member/stargazers)
  [![GitHub forks](https://img.shields.io/github/forks/VanillaNahida/astrbot_plugin_group_auto_clean_member?style=flat-square)](https://github.com/VanillaNahida/astrbot_plugin_group_auto_clean_member/network)
  [![GitHub issues](https://img.shields.io/github/issues/VanillaNahida/astrbot_plugin_group_auto_clean_member?style=flat-square)](https://github.com/VanillaNahida/astrbot_plugin_group_auto_clean_member/issues)
  [![python3](https://img.shields.io/badge/Python-3.10+-blue.svg?style=flat-square)](https://www.python.org/)
  [![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux-brightgreen.svg?style=flat-square)]()
  
</div>

# 功能特点

- **智能满员检测**：实时监控群聊人数，当群聊满员时自动触发清人
- **活跃度计算**：基于最后发言时间和加群时间计算成员活跃度
- **自动清理**：自动清理最不活跃的成员，确保群聊活跃度
- **权限检查**：严格检查bot和用户权限，确保操作安全
- **智能提醒**：清理后主动提醒活跃度倒数第二的成员

# 使用方法

  > [!WARNING]
  >
  > 请确保您的Bot在群中具有管理员权限，否则无法执行移除成员操作。

## 安装插件

1. 在插件市场搜索插件 `astrbot_plugin_group_auto_clean_member` 或 `群聊自动满员清人插件`
2. 安装插件（可以在插件市场安装，或者复制仓库地址，在WebUI中粘贴地址安装）
3. 配置插件（可选配置项）
4. 保存重载插件配置，使插件生效

  > [!TIP]
  >
  > 安装并配置好插件后建议**重启bot**，确保插件生效。

# 命令总览

| 命令 | 示例用法 | 权限要求 | 说明 |
|------|----------|----------|------|
| `开启自动清人` | `开启自动清人` | 群主/管理员/Bot管理员 | 开启当前群的满员自动清人功能 |
| `关闭自动清人` | `关闭自动清人` | 群主/管理员/Bot管理员 | 关闭当前群的满员自动清人功能 |
| `查看最不活跃成员` | `查看最不活跃成员` | 群主/管理员/Bot管理员 | 查看最不活跃的群成员和活跃度倒数第二的群成员 |

# 工作原理

## 满员检测
插件会监听群成员变动事件，当有新成员加入时，自动检查当前群是否满员。

## 活跃度计算
插件根据以下规则计算成员活跃度：
1. **从未发言的成员**：按加群时间从早到晚排序
2. **已发言的成员**：按最后发言时间从早到晚排序

## 自动清理流程
1. 检测到群聊满员
2. 获取群成员列表并计算活跃度
3. 检查bot是否具有管理员权限
4. 移除活跃度倒数第一的成员
5. 发送提醒消息给活跃度倒数第二的成员

# 权限要求

- **Bot权限**：Bot必须在群中具有管理员或群主权限
- **用户权限**：只有群主、管理员或Bot管理员可以使用相关命令

# 配置说明

插件支持以下配置项：

- `auto_clean_enabled`：全局自动清人开关（布尔值）
- `enabled_groups`：启用的群组列表（数组）

# 注意事项

1. **权限检查**：插件会严格检查bot和用户权限，确保操作安全
2. **成员数量**：群成员数量不足2人时不会执行清人操作
3. **错误处理**：插件具有完善的错误处理机制，确保稳定性
4. **日志记录**：所有操作都会记录详细日志，便于排查问题

# 常见问题

**Q: 为什么插件没有自动清理成员？**
A: 请检查以下条件：
- Bot是否具有群管理员权限
- 群聊是否真正满员
- 插件是否已正确开启

**Q: 如何查看插件运行状态？**
A: 查看Bot日志文件，插件会记录详细的运行信息。

**Q: 插件支持哪些聊天平台？**
A: 目前主要支持基于aiocqhttp的QQ平台。

# bug反馈
如果在使用过程中遇到任何问题，请通过以下方式反馈：
- [Issue](https://github.com/VanillaNahida/astrbot_plugin_group_auto_clean_member/issues)
- QQ群：[195260107](https://qm.qq.com/q/1od5TMYrKE)

# 致谢
感谢AstrBot开发团队提供的优秀框架和插件系统。

# QQ群：
 - 一群：621457510
 - 二群：1031065631
 - 三群：195260107 （推荐）