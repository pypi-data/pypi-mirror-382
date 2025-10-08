"""
* 文件名: sync_namespace
* 作者: JQQ
* 创建日期: 2025/9/29
* 最后修改日期: 2025/9/29
* 版权: 2023 JQQ. All rights reserved.
* 依赖: socketio, loguru, pydantic
* 描述: 同步版本SMCP协议Namespace实现 / Synchronous SMCP protocol Namespace implementation
"""

import copy

from pydantic import TypeAdapter

from a2c_smcp.server.sync_auth import SyncAuthenticationProvider
from a2c_smcp.server.sync_base import SyncBaseNamespace
from a2c_smcp.server.types import OFFICE_ID, SID
from a2c_smcp.smcp import (
    CANCEL_TOOL_CALL_NOTIFICATION,
    ENTER_OFFICE_NOTIFICATION,
    GET_DESKTOP_EVENT,
    GET_TOOLS_EVENT,
    LEAVE_OFFICE_NOTIFICATION,
    SMCP_NAMESPACE,
    TOOL_CALL_EVENT,
    UPDATE_CONFIG_NOTIFICATION,
    UPDATE_DESKTOP_NOTIFICATION,
    UPDATE_TOOL_LIST_NOTIFICATION,
    AgentCallData,
    EnterOfficeNotification,
    EnterOfficeReq,
    GetDeskTopReq,
    GetDeskTopRet,
    GetToolsReq,
    GetToolsRet,
    LeaveOfficeNotification,
    LeaveOfficeReq,
    UpdateComputerConfigReq,
    UpdateMCPConfigNotification,
)
from a2c_smcp.utils.logger import logger


class SyncSMCPNamespace(SyncBaseNamespace):
    """
    同步SMCP命名空间，处理SMCP相关事件（同步）
    Synchronous Socket.IO namespace for handling SMCP-related events
    """

    def __init__(self, auth_provider: SyncAuthenticationProvider) -> None:
        """
        初始化SMCP命名空间（同步）
        Initialize SMCP namespace (sync)
        """
        super().__init__(namespace=SMCP_NAMESPACE, auth_provider=auth_provider)

    def enter_room(self, sid: SID, room: OFFICE_ID, namespace: str | None = None) -> None:  # type: ignore[override]
        """
        客户端加入房间，维护session中的sid/name/office_id字段（同步）
        Client joins room, maintain sid/name/office_id in session (sync)
        """
        session = self.get_session(sid)

        if session.get("sid") != sid:
            session["sid"] = sid
        if not session.get("name"):
            session["name"] = f"{session.get('role', 'unknown')}_{sid[:6]}"

        if session.get("role") == "agent":
            if session.get("office_id") and session.get("office_id") != room:
                logger.error(f"Agent sid: {sid} already in room: {session.get('office_id')}, can't join room: {room}")
                raise ValueError("Agent sid already in room")
            elif not session.get("office_id"):
                for participant_sid, _participant_eio_sid in self.server.manager.get_participants(SMCP_NAMESPACE, room):
                    participant_session = self.get_session(participant_sid)
                    if participant_session.get("role") == "agent":
                        raise ValueError("Agent already in room")
            else:
                logger.warning(
                    f"Agent sid: {sid} already in room: {session.get('office_id')}. 正在重复加入房间",
                )
                return
        else:
            if session.get("office_id") and (past_room := session.get("office_id")) != room:
                self.leave_room(sid, past_room)
            elif session.get("office_id") == room:
                logger.warning(
                    f"Computer sid: {sid} already in room: {session.get('office_id')}. 正在重复加入房间",
                )
                return

        super().enter_room(sid, room)
        session["office_id"] = room
        self.save_session(sid, session)

        # 根据角色发送不同的通知 / Send different notifications based on role
        notification_data: EnterOfficeNotification = {"office_id": room}
        if session.get("role") == "computer":
            notification_data["computer"] = sid
        else:
            notification_data["agent"] = sid

        self.emit(
            ENTER_OFFICE_NOTIFICATION,
            notification_data,
            skip_sid=sid,
            room=room,
        )

    def leave_room(self, sid: SID, room: OFFICE_ID, namespace: str | None = None) -> None:  # type: ignore[override]
        """
        在离开房间之前发布离开消息（同步）
        Publish leave message before leaving room (sync)
        """
        session = self.get_session(sid)
        notification = (
            LeaveOfficeNotification(office_id=room, computer=sid)
            if session.get("role") == "computer"
            else LeaveOfficeNotification(office_id=room, agent=sid)
        )
        self.emit(LEAVE_OFFICE_NOTIFICATION, notification, skip_sid=sid, room=room)

        if "office_id" in session:
            del session["office_id"]
        self.save_session(sid, session)

        super().leave_room(sid, room)

    def on_server_join_office(self, sid: str, data: EnterOfficeReq) -> tuple[bool, str | None]:
        """
        同步：Computer/Agent加入房间
        Sync: Computer or Agent joins room
        """
        role_info = TypeAdapter(EnterOfficeReq).validate_python(data)
        expected_role = role_info["role"]

        session = self.get_session(sid)
        backup_session = copy.deepcopy(session)

        try:
            if session.get("role") and session["role"] != expected_role:
                return False, f"Role mismatch, expected {expected_role}, but {session['role']} use this sid exists"

            session["role"] = expected_role
            session["name"] = role_info["name"]
            self.save_session(sid, session)

            self.enter_room(sid, role_info["office_id"])
            return True, None
        except Exception as e:
            self.save_session(sid, backup_session)
            return False, f"Internal server error: {str(e)}"

    def on_server_leave_office(self, sid: str, data: LeaveOfficeReq) -> tuple[bool, str | None]:
        """
        同步：Computer/Agent离开房间
        Sync: Computer or Agent leaves room
        """
        try:
            self.leave_room(sid, data["office_id"])
            return True, None
        except Exception as e:
            return False, f"Internal server error: {str(e)}"

    def on_server_tool_call_cancel(self, sid: str, data: AgentCallData) -> None:
        """
        同步：广播取消ToolCall到房间内的其他成员
        Sync: broadcast tool call cancellation to other members in the room
        """
        session = self.get_session(sid)
        assert session["role"] == "agent", "目前仅支持Agent调用取消ToolCall的操作"

        agent_call = TypeAdapter(AgentCallData).validate_python(data)
        assert sid == agent_call["robot_id"], "取消工具调用的广播仅可以由对应Agent发出"

        # 广播到 office 房间，而不是 Agent 的私有房间 / Broadcast to office room, not Agent's private room
        office_id = session.get("office_id")
        self.emit(
            CANCEL_TOOL_CALL_NOTIFICATION,
            agent_call,
            room=office_id,
            skip_sid=sid,
        )

    def on_server_update_config(self, sid: str, data: UpdateComputerConfigReq) -> None:
        """
        同步：广播更新MCP配置
        Sync: broadcast MCP config update
        """
        session = self.get_session(sid)
        assert session["role"] == "computer", "目前仅支持Computer调用更新MCP配置的操作"

        update_config = TypeAdapter(UpdateComputerConfigReq).validate_python(data)
        self.emit(
            UPDATE_CONFIG_NOTIFICATION,
            UpdateMCPConfigNotification(computer=update_config["computer"]),
            room=session["office_id"],
            skip_sid=sid,
        )

    def on_server_update_tool_list(self, sid: str, data: UpdateComputerConfigReq) -> None:
        """
        同步：广播工具列表更新
        Sync: broadcast tool list update
        """
        session = self.get_session(sid)
        assert session["role"] == "computer", "目前仅支持Computer上报工具列表变更"

        update_req = TypeAdapter(UpdateComputerConfigReq).validate_python(data)

        self.emit(
            UPDATE_TOOL_LIST_NOTIFICATION,
            {"computer": update_req["computer"]},
            room=session.get("office_id"),
            skip_sid=sid,
        )

    def on_client_tool_call(self, sid: str, data: dict) -> dict:
        """
        同步：响应工具调用，使用 call 方法等待 Computer 返回结果
        Sync: respond to tool call, use call method to wait for Computer response
        """
        session = self.get_session(sid)
        assert session["role"] == "agent", "目前仅支持Agent调用工具"

        tool_call = TypeAdapter(dict).validate_python(data)

        # 使用 call 方法调用 Computer，等待返回结果 / Use call method to invoke Computer and wait for result
        return self.call(
            TOOL_CALL_EVENT,
            tool_call,
            to=tool_call["computer"],
            namespace=SMCP_NAMESPACE,
        )

    def on_client_get_tools(self, sid: str, data: GetToolsReq) -> GetToolsRet:
        """
        同步：获取指定Computer的工具列表（使用 Socket.IO 的 call 等待客户端返回）
        Sync: get tool list of specified Computer using Socket.IO call
        """
        computer_sid = data["computer"]
        session = self.get_session(computer_sid)
        assert session["role"] == "computer", "目前仅支持Computer获取工具列表"

        agent_session = self.get_session(sid)
        computer_office_id = session.get("office_id")
        agent_office_id = agent_session.get("office_id")
        assert computer_office_id == agent_office_id, "目前仅支持Agent获取自己房间内Computer的工具列表"

        client_response = self.call(
            GET_TOOLS_EVENT,
            data,
            to=data["computer"],
            namespace=SMCP_NAMESPACE,
        )

        return TypeAdapter(GetToolsRet).validate_python(client_response)

    def on_client_get_desktop(self, sid: str, data: GetDeskTopReq) -> GetDeskTopRet:
        """
        同步：获取指定Computer的桌面信息（窗口组织后的视图）
        Sync: get desktop view from specified Computer

        要求：Agent 与 Computer 需在同一 office / Requirement: Agent and Computer must be in the same office
        """
        computer_sid = data["computer"]
        session = self.get_session(computer_sid)
        assert session["role"] == "computer", "目前仅支持Computer获取桌面"

        agent_session = self.get_session(sid)
        computer_office_id = session.get("office_id")
        agent_office_id = agent_session.get("office_id")
        assert computer_office_id == agent_office_id, "目前仅支持Agent获取自己房间内Computer的桌面"

        client_response = self.call(
            GET_DESKTOP_EVENT,
            data,
            to=data["computer"],
            namespace=SMCP_NAMESPACE,
        )

        return TypeAdapter(GetDeskTopRet).validate_python(client_response)

    def on_server_update_desktop(self, sid: str, data: UpdateComputerConfigReq) -> None:
        """
        同步：将事件广播至对应的房间内其他参与者，通知桌面刷新
        Sync: broadcast to others in the room to notify desktop update

        Args:
            sid (str): 发起者ID，应为Computer / Initiator ID, should be Computer
            data (UpdateComputerConfigReq): 载荷复用 UpdateConfigReq，仅需 computer 标识
        """
        session = self.get_session(sid)
        assert session["role"] == "computer", "目前仅支持Computer上报桌面刷新"

        update_req = TypeAdapter(UpdateComputerConfigReq).validate_python(data)
        self.emit(
            UPDATE_DESKTOP_NOTIFICATION,
            {"computer": update_req["computer"]},
            room=session.get("office_id"),
            skip_sid=sid,
        )
