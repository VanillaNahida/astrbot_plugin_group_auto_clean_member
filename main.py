from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
from astrbot.api import logger
import json
import time
import asyncio

@register(
    "astrbot_plugin_group_auto_clean_member", 
    "香草味的纳西妲喵（VanillaNahida）", 
    "群聊自动满员清人插件", 
    "1.0.2"
    )
class GroupAutoCleanMemberPlugin(Star):
    def __init__(self, context: Context, config: dict = None):
        super().__init__(context)
        self.context = context
        self.config = config or {}
        
        # 加载配置
        self._load_config()

    async def initialize(self):
        """插件初始化方法"""
        logger.info("群聊自动满员清人插件已初始化")

    def _load_config(self):
        """加载插件配置"""
        try:
            # 从配置文件读取全局开关状态
            self.auto_clean_enabled = self.config.get("auto_clean_enabled", False)
            # 从配置文件读取启用的群组列表
            enabled_groups = self.config.get("enabled_groups", [])
            self.enabled_groups = set(map(str, enabled_groups))
            # 从配置文件读取清人延时时间
            self.clean_delay_seconds = self.config.get("clean_delay_seconds", 5)
            logger.info(f"已加载配置，全局自动清人开关：{self.auto_clean_enabled}，启用的群组列表：{self.enabled_groups}，清人延时：{self.clean_delay_seconds}秒")
        except Exception as e:
            logger.error(f"加载配置失败：{e}")
            # 使用默认值
            self.auto_clean_enabled = False
            self.enabled_groups = set()
            self.clean_delay_seconds = 5

    def _save_config(self):
        """保存配置到文件"""
        try:
            # 更新配置字典
            self.config["auto_clean_enabled"] = self.auto_clean_enabled
            self.config["enabled_groups"] = list(self.enabled_groups)
            # 保存到磁盘
            self.config.save_config()
            logger.info("配置已保存到文件")
        except Exception as e:
            logger.error(f"保存配置失败：{e}")

    async def _check_user_permission(self, event: AstrMessageEvent) -> tuple[bool, str]:
        """检查用户权限（bot管理员、群主、管理员才可使用）
        
        返回:
            (True, ""): 用户有权限
            (False, "该命令仅限群主/管理员/Bot管理员使用。"): 用户权限不足
        """
        raw_message = event.message_obj.raw_message
        
        # 检查是否是 Bot 管理员
        if event.is_admin():
            logger.debug("用户为Bot管理员，权限检查通过")
            return (True, "")
        
        # 检查群权限（群主、管理员才可使用）
        sender_role = raw_message.get("sender", {}).get("role", "member") if raw_message else "member"
        if sender_role in ["admin", "owner"]:
            logger.debug(f"用户为{sender_role}，权限检查通过")
            return (True, "")
        
        return (False, "该命令仅限群主/管理员/Bot管理员使用。")

    async def _check_bot_permission(self, event: AstrMessageEvent) -> tuple[bool, str]:
        """检查机器人权限（管理员和群主权限）
        
        返回:
            (True, ""): 机器人有权限
            (False, "bot权限不足，需要管理员权限"): 机器人权限不足
        """
        raw = event.message_obj.raw_message
        gid = raw.get("group_id")
        
        # 检查机器人权限
        try:
            bot_info = await event.bot.api.call_action("get_group_member_info", group_id=gid, user_id=int(event.get_self_id()))
            bot_role = bot_info.get("role")
            if bot_role not in ["admin", "owner"]:
                return (False, "bot权限不足，需要管理员权限")
        except Exception as e:
            logger.error(f"检查机器人权限失败: {e}")
            return (False, "bot权限不足，需要管理员权限")
        
        return (True, "")

    async def terminate(self):
        """插件销毁方法"""
        logger.info("群聊自动满员清人插件已关闭")

    @filter.command("开启自动清人")
    async def enable_auto_clean(self, event: AstrMessageEvent):
        """开启当前群的满员自动清人功能"""
        # 检查权限
        has_user_permission, user_error_msg = await self._check_user_permission(event)
        has_bot_permission, bot_error_msg = await self._check_bot_permission(event)
        
        if not has_user_permission:
            yield event.plain_result(f"❌ {user_error_msg}")
            return
        
        if not has_bot_permission:
            yield event.plain_result(f"❌ {bot_error_msg}")
            return
        
        # 获取当前群号
        group_id = event.get_group_id()
        if not group_id:
            yield event.plain_result("❌ 此命令只能在群聊中使用")
            return
        
        group_id_str = str(group_id)
        
        # 检查是否已经开启
        if group_id_str in self.enabled_groups:
            yield event.plain_result(f"✅ 群 {group_id} 的自动清人功能已经开启啦！")
            return
        
        # 将群号添加到启用列表
        self.enabled_groups.add(group_id_str)
        # 开启全局开关
        self.auto_clean_enabled = True
        # 保存配置
        self._save_config()
        
        logger.info(f"群 {group_id} 满员自动清人功能已开启")
        yield event.plain_result(f"✅ 群 {group_id} 满员自动清人功能已开启")

    @filter.command("关闭自动清人")
    async def disable_auto_clean(self, event: AstrMessageEvent):
        """关闭当前群的满员自动清人功能"""
        # 检查权限
        has_user_permission, user_error_msg = await self._check_user_permission(event)
        has_bot_permission, bot_error_msg = await self._check_bot_permission(event)
        
        if not has_user_permission:
            yield event.plain_result(f"❌ {user_error_msg}")
            return
        
        if not has_bot_permission:
            yield event.plain_result(f"❌ {bot_error_msg}")
            return
        
        # 获取当前群号
        group_id = event.get_group_id()
        if not group_id:
            yield event.plain_result("❌ 此命令只能在群聊中使用")
            return
        
        group_id_str = str(group_id)
        
        # 检查是否已经关闭
        if group_id_str not in self.enabled_groups:
            yield event.plain_result(f"✅ 群 {group_id} 的自动清人功能已经关闭啦！")
            return
        
        # 将群号从启用列表中移除
        self.enabled_groups.remove(group_id_str)
        
        # 如果没有启用的群，关闭全局开关
        if not self.enabled_groups:
            self.auto_clean_enabled = False
        
        # 保存配置
        self._save_config()
        
        logger.info(f"群 {group_id} 满员自动清人功能已关闭")
        yield event.plain_result(f"✅ 群 {group_id} 满员自动清人功能已关闭")

    @filter.command("查看最不活跃成员")
    async def check_inactive_members(self, event: AstrMessageEvent):
        """查看最不活跃的群成员和活跃度倒数第二的群成员"""
        
        # 检查用户权限
        has_user_permission, user_error_msg = await self._check_user_permission(event)
        has_bot_permission, bot_error_msg = await self._check_bot_permission(event)
        
        if not has_user_permission:
            yield event.plain_result(f"❌ {user_error_msg}")
            return
        
        if not has_bot_permission:
            yield event.plain_result(f"❌ {bot_error_msg}")
            return

        # 获取当前群号
        group_id = event.get_group_id()
        if not group_id:
            yield event.plain_result("❌ 此命令只能在群聊中使用")
            return
        
        group_id_str = str(group_id)
        
        # 获取群成员列表
        member_list_result = await self._get_group_member_list(event, group_id_str)
        if not member_list_result:
            yield event.plain_result("❌ 获取群成员列表失败")
            return
        
        # 处理API返回值，参考geetest_verify插件的实现
        member_list = member_list_result if isinstance(member_list_result, list) else member_list_result.get("data", [])
        if len(member_list) < 2:
            yield event.plain_result("❌ 群成员数量不足，无法查询")
            return
        
        # 计算活跃度并排序
        sorted_members = self._calculate_activity(member_list)
        
        # 获取活跃度倒数第一和倒数第二的成员
        least_active_member = sorted_members[0]
        second_least_active_member = sorted_members[1]
        
        # 发送结果消息
        message = f"📊 群 {group_id} 最不活跃成员统计：\n\n"
        message += f"🏆 活跃度倒数第一：\n"
        message += f"   昵称：{least_active_member['nickname']}\n"
        message += f"   QQ号：{least_active_member['user_id']}\n"
        message += f"   加入时间：{least_active_member['join_time_str']}\n"
        message += f"   最后发言：{least_active_member['last_sent_time_str']}\n"
        message += f"   从未发言：{'是' if least_active_member['never_spoken'] else '否'}\n\n"
        
        message += f"🥈 活跃度倒数第二：\n"
        message += f"   昵称：{second_least_active_member['nickname']}\n"
        message += f"   QQ号：{second_least_active_member['user_id']}\n"
        message += f"   加入时间：{second_least_active_member['join_time_str']}\n"
        message += f"   最后发言：{second_least_active_member['last_sent_time_str']}\n"
        message += f"   从未发言：{'是' if second_least_active_member['never_spoken'] else '否'}"
        
        yield event.plain_result(message)


    @filter.command("执行清人操作")
    async def execute_clean(self, event: AstrMessageEvent):
        """执行群成员清理"""
        
        # 检查权限
        has_user_permission, user_error_msg = await self._check_user_permission(event)
        has_bot_permission, bot_error_msg = await self._check_bot_permission(event)
        
        if not has_user_permission:
            yield event.plain_result(f"❌ {user_error_msg}")
            return
        
        if not has_bot_permission:
            yield event.plain_result(f"❌ {bot_error_msg}")
            return

        # 获取当前群号
        group_id = event.get_group_id()
        if not group_id:
            yield event.plain_result("❌ 此命令只能在群聊中使用")
            return
        
        group_id_str = str(group_id)
        
        # 检查该群是否在启用列表中
        if group_id_str not in self.enabled_groups:
            yield event.plain_result(f"❌ 群 {group_id} 的自动清人功能尚未开启，请先使用【开启自动清人】命令或者前往WebUI添加群号")
            return
        
        # 发送开始清理提示
        yield event.plain_result(f"开始执行群 {group_id} 的自动清理任务，将清理最不活跃群成员...")
        
        # 调用自动清人逻辑（手动触发）
        await self._execute_auto_clean(event, group_id_str, is_manual_trigger=True)

    async def _get_group_info(self, event: AstrMessageEvent, group_id: str):
        """获取群信息"""
        try:
            if event.get_platform_name() == "aiocqhttp":
                payloads = {
                    "group_id": group_id,
                    "no_cache": True # 不使用缓存
                }
                ret = await event.bot.api.call_action('get_group_info', **payloads)
                logger.info(f"获取群信息成功：{ret}")
                return ret
            return None
        except Exception as e:
            logger.error(f"获取群信息失败：{e}")
            return None

    async def _get_group_member_list(self, event: AstrMessageEvent, group_id: str):
        """获取群成员列表"""
        try:
            if event.get_platform_name() == "aiocqhttp":
                payloads = {
                    "group_id": group_id,
                }
                ret = await event.bot.api.call_action('get_group_member_list', **payloads)
                # 检查返回值类型
                member_list = ret if isinstance(ret, list) else ret.get('data', [])
                logger.info(f"获取群成员列表成功，共 {len(member_list)} 人")
                return ret
            return None
        except Exception as e:
            logger.error(f"获取群成员列表失败：{e}")
            return None

    def _calculate_activity(self, member_list):
        """计算成员活跃度并排序"""
        all_members = []
        
        # 遍历每个成员
        for item in member_list:
            last_sent_time = item.get("last_sent_time", 0)
            join_time = item.get("join_time", 0)
            
            # 转换时间格式
            join_time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(join_time))
            last_sent_time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(last_sent_time))
            
            all_members.append({
                "user_id": item.get("user_id"),
                "nickname": item.get("nickname", ""),
                "join_time": join_time,
                "join_time_str": join_time_str,
                "last_sent_time": last_sent_time,
                "last_sent_time_str": last_sent_time_str,
                "never_spoken": (last_sent_time == join_time)
            })
        
        # 按活跃度排序（最久没发言的在前）
        # 规则：1. 从未发言的成员按加群时间从早到晚排序
        #      2. 已发言的成员按最后发言时间从早到晚排序
        all_members_sorted = sorted(all_members, key=lambda x: (x["never_spoken"], x["last_sent_time"]))
        
        return all_members_sorted

    async def _kick_member(self, event: AstrMessageEvent, group_id: str, user_id: str, reason: str):
        """移除群成员"""
        try:
            if event.get_platform_name() == "aiocqhttp":
                payloads = {
                    "group_id": group_id,
                    "user_id": user_id,
                    "reason": reason
                }
                ret = await event.bot.api.call_action('set_group_kick', **payloads)
                logger.info(f"移除成员 {user_id} 成功：{ret}")
                # API调用成功（没有抛出异常）即表示成功，返回True
                return True
            return False
        except Exception as e:
            logger.error(f"移除成员 {user_id} 失败：{e}")
            return False

    async def _execute_auto_clean(self, event: AstrMessageEvent, group_id: str, is_manual_trigger: bool = False):
        """执行自动清人
        
        参数:
            is_manual_trigger: 是否为手动触发（True: 手动命令触发, False: 自动触发）
        """
        # 检查自动清人功能是否开启
        if not self.auto_clean_enabled:
            logger.info("自动清人功能已关闭，跳过清人操作")
            return

        # 获取群信息
        group_info = await self._get_group_info(event, group_id)
        if not group_info:
            logger.error("获取群信息失败，无法执行自动清人")
            return

        # 处理API返回值
        # 如果返回的是包含data字段的字典，使用data字段；否则直接使用返回值
        if isinstance(group_info, dict):
            if "status" in group_info and "data" in group_info:
                # API返回的是标准格式，包含status和data字段
                if group_info.get("status") != "ok":
                    logger.error("获取群信息失败，无法执行自动清人")
                    return
                data = group_info.get("data", {})
            else:
                # API返回的是直接的群信息字典
                data = group_info
        else:
            logger.error("获取群信息格式错误，无法执行自动清人")
            return

        member_count = data.get("member_count", 0)
        max_member_count = data.get("max_member_count", 0)

        # 检查群是否满员
        if member_count < max_member_count:
            logger.info(f"群 {group_id} 目前 {member_count}/{max_member_count} 人，未达满员，无需清人")
            # 只有在手动触发时才发送提示消息
            if is_manual_trigger:
                await event.bot.api.call_action('send_group_msg', group_id=group_id, message=f"群 {group_id} 目前 {member_count}/{max_member_count} 人，未达满员，无需清人，任务已结束。")
            return

        logger.info(f"群 {group_id} 已满员 {member_count}/{max_member_count}，开始执行自动清人")

        # 创建异步任务执行延时清人
        asyncio.create_task(self._delayed_clean_member(event, group_id))

    async def _delayed_clean_member(self, event: AstrMessageEvent, group_id: str):
        """延时清人任务"""
        try:            
            # 延时等待
            logger.info(f"开始延时 {self.clean_delay_seconds} 秒")
            await asyncio.sleep(self.clean_delay_seconds)
            
            # 使用检查机器人权限的方法（自动清人场景）
            has_bot_permission, bot_error_msg = await self._check_bot_permission(event)
            if not has_bot_permission:
                logger.error(f"机器人权限检查失败：{bot_error_msg}")
                # 发送权限不足提示
                permission_message = f"❌ 自动清理失败：{bot_error_msg}"
                await event.bot.api.call_action('send_group_msg', group_id=group_id, message=permission_message)
                return

            # 获取群成员列表
            member_list_result = await self._get_group_member_list(event, group_id)
            if not member_list_result:
                logger.error("获取群成员列表失败，无法执行自动清人")
                return

            # 处理API返回值，参考geetest_verify插件的实现
            member_list = member_list_result if isinstance(member_list_result, list) else member_list_result.get("data", [])
            if len(member_list) < 2:
                logger.error("群成员数量不足，无法执行自动清人")
                return

            # 计算活跃度并排序
            sorted_members = self._calculate_activity(member_list)
            
            # 获取活跃度倒数第一和倒数第二的成员
            least_active_member = sorted_members[0]
            second_least_active_member = sorted_members[1]

            logger.info(f"活跃度倒数第一：{least_active_member['nickname']}({least_active_member['user_id']})")
            logger.info(f"活跃度倒数第二：{second_least_active_member['nickname']}({second_least_active_member['user_id']})")

            # 移除活跃度倒数第一的成员
            reason = "群聊满员，自动清理最不活跃成员"
            kick_result = await self._kick_member(event, group_id, least_active_member['user_id'], reason)
            
            if kick_result:
                # 发送提示消息
                at_user = f"[CQ:at,qq={second_least_active_member['user_id']}]"
                message = f"🚨 群人数已满，已自动清理最不活跃成员！\n{at_user} 你目前是活跃度倒数第二，请尽快发言避免被自动清理！"
                try:
                    await event.bot.api.call_action('send_group_msg', group_id=group_id, message=message)
                    logger.info(f"自动清人完成，已移除 {least_active_member['nickname']}({least_active_member['user_id']})，并提示 {second_least_active_member['nickname']}({second_least_active_member['user_id']})")
                except Exception as e:
                    logger.error(f"发送提示消息失败：{e}")
            else:
                logger.error("移除成员失败")

            # 停止事件传播，避免被大模型处理
            event.stop_event()
                
        except Exception as e:
            logger.error(f"延时清人任务执行失败：{e}")
            event.stop_event()

    @filter.event_message_type(filter.EventMessageType.GROUP_MESSAGE)
    async def handle_event(self, event: AstrMessageEvent):
        """处理进群退群事件和监听群消息"""
        try:
            if event.get_platform_name() != "aiocqhttp":
                return

            raw = event.message_obj.raw_message
            if raw is None:
                return
                
            post_type = raw.get("post_type")
            
            if post_type == "notice":
                if raw.get("notice_type") == "group_increase":
                    group_id = str(raw.get("group_id"))
                    # 检查该群是否在启用列表中
                    if group_id in self.enabled_groups:
                        logger.info(f"检测到新成员进群，群 {group_id} 开始执行满员检查")
                        await self._execute_auto_clean(event, group_id)


        except Exception as e:
            logger.error(f"handle_event 处理事件时发生异常: {e}")
