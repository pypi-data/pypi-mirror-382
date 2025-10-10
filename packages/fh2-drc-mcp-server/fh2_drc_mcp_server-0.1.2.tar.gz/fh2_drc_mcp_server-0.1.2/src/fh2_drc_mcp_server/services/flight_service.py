# -*- coding: utf-8 -*-
"""
飞行控制服务 - 起飞、飞向目标点、返航
"""
from typing import Any, Dict, Optional
from mcp.server.fastmcp import FastMCP
from ..core.http_client import post_json
from ..config.settings import (
    USER_TOKEN_FIXED, 
    DEFAULT_MAX_SPEED, 
    DEFAULT_RTH_ALTITUDE, 
    DEFAULT_SECURITY_TAKEOFF_HEIGHT
)
from ..utils.helpers import auto_fill_device_sn, auto_fill_uuid

# 获取全局MCP实例
mcp: Optional[FastMCP] = None


def set_mcp_instance(mcp_instance: FastMCP) -> None:
    """设置MCP实例"""
    global mcp
    mcp = mcp_instance


async def drone_takeoff(
    proj_uuid: str,
    media_folder_name: str,
    target_height: float,
    device_sn: str = None,
    commander_flight_mode: int = 1,
    commander_flight_height: float = 100.0,
    target_latitude: float = 0.0,
    target_longitude: float = 0.0,
    rth_mode: int = 1,
    out_of_control_action: str = "ReturnHome",
    max_speed: int = DEFAULT_MAX_SPEED,
    takeoff_mode: str = "TakeoffWithFlyTo",
    token: str = USER_TOKEN_FIXED,
    rth_altitude: int = DEFAULT_RTH_ALTITUDE,
    security_takeoff_height: int = DEFAULT_SECURITY_TAKEOFF_HEIGHT,
) -> Dict[str, Any] | str:
    """
    【一键起飞】让飞行器从地面起飞到空中指定位置 (drone-take-off)
    用途: 飞行器从关机/地面状态启动，自动起飞并飞向目标点
    场景: 任务开始时使用，让飞行器从机场/起降点起飞
    一般需要先通过cloud_controls_create获取到云控权限

    错误处理:
        如果遇到{"result":{"code":228431,"message":"Bad Request","data":null}}错误码，
        需要先调用cloud_controls_create抢夺飞行和负载控制权["flight","payload_99-0-0"]，然后重试操作。

    Args:
        proj_uuid: 项目 UUID（路径参数）
        media_folder_name: 媒体文件夹名称，默认为 "时间(分钟级别）—设备sn—MCP"
        target_height: 目标高度 (m)，2 – 10000
        device_sn: **网关 SN**；默认取上一条推荐里的 gateway_sn
        commander_flight_mode: 1为指点飞行模式
        commander_flight_height: 指点飞行高度 (m)
        target_latitude: 目标纬度 (deg)
        target_longitude: 目标经度 (deg)
        rth_mode: 返航模式
        out_of_control_action: 失控动作 "Hover" | "ReturnHome" | "Continue"
        max_speed: 最大速度 (m/s)
        takeoff_mode: "Takeoff" | "TakeoffWithFlyTo"
        token: x-auth-token
        rth_altitude: 返航高度 (m)，15 – 1500
        security_takeoff_height: 安全起飞高度 (m)，范围 8 – 1500

    Returns:
        { "code": 0, "message": "success", "data": { "flight_id": "...", "fly_to_id": "..." } }
        或错误信息字符串。
    """
    filled_device_sn = auto_fill_device_sn(device_sn, use_gateway=True)
    
    if filled_device_sn is None:
        return "device_sn is required (no previous recommendation found)"

    body = {
        "media_folder_name": media_folder_name,
        "security_takeoff_height": security_takeoff_height,
        "device_sn": filled_device_sn,
        "max_speed": max_speed,
        "out_of_control_action": out_of_control_action,
        "rth_altitude": rth_altitude,
        "target_height": target_height,
        "takeoff_mode": takeoff_mode,
        "commander_flight_mode": commander_flight_mode,
        "commander_flight_height": commander_flight_height,
        "target_latitude": target_latitude,
        "target_longitude": target_longitude,
        "rth_mode": rth_mode,
    }
    
    return await post_json(
        f"/task/api/v1/workspaces/{proj_uuid}/flight-tasks/drone-take-off",
        token,
        {k: v for k, v in body.items() if v is not None},
    )


async def fly_to_points(
    proj_uuid: str,
    target_latitude: float,
    target_longitude: float,
    target_height: float,
    device_sn: Optional[str] = None,
    start_longitude: Optional[float] = None,
    start_latitude: Optional[float] = None,
    start_height: Optional[float] = None,
    max_speed: int = DEFAULT_MAX_SPEED,
    token: str = USER_TOKEN_FIXED,
) -> Dict[str, Any] | str:
    """
    【飞向目标点】在飞行过程中，从当前空中位置飞向另一个指定点 (fly-to-points)
    用途: 飞行器已在空中飞行时，导航到新的目标坐标
    场景: 飞行任务执行中使用，实现空中航点间的移动
    前提: 飞行器必须已经在空中飞行状态,如果不确定是否空中，可以查询一下飞行状态
    
    错误处理:
        如果遇到{"result":{"code":228431,"message":"Bad Request","data":null}}错误码，
        需要先调用cloud_controls_create抢夺飞行和负载控制权["flight","payload_99-0-0"]，然后重试操作。

    Args:
        proj_uuid: 项目 UUID（路径参数）
        target_latitude: 目标纬度
        target_longitude: 目标经度
        target_height: 目标高度 (米)
        device_sn: 设备 SN；默认取最近一次设备推荐里的 *gateway_sn*
        start_latitude: 起始纬度 (可选，默认设置为目标点坐标)
        start_longitude: 起始经度 (可选，默认设置为目标点坐标)
        start_height: 起始高度 (可选，默认设置为目标点坐标)
        max_speed: 最大飞行速度 (m/s)，默认14
        token: x-auth-token

    Returns:
        { "code": 0, "message": "success", "data": { "fly_to_id": "...", "flight_id": "..." } }
        或错误信息字符串。
    """
    filled_device_sn = auto_fill_device_sn(device_sn, use_gateway=True)
    
    if filled_device_sn is None:
        return "device_sn is required (no previous recommendation found)"

    body = {
        "device_sn": filled_device_sn,
        "points": [
            {
                "latitude": target_latitude,
                "longitude": target_longitude,
                "height": target_height
            }
        ],
        "max_speed": max_speed
    }
    
    # 处理起始点信息：如果提供了起始点则使用，否则设置为和目标点一致（避免后端校验问题）
    if all(v is not None for v in [start_latitude, start_longitude, start_height]):
        body["start_point"] = {
            "latitude": start_latitude,
            "longitude": start_longitude,
            "height": start_height
        }
    else:
        # 如果没有提供起始点，设置为和目标点一致
        body["start_point"] = {
            "latitude": target_latitude,
            "longitude": target_longitude,
            "height": target_height
        }

    return await post_json(
        f"/task/api/v1/workspaces/{proj_uuid}/flight-tasks/fly-to-points",
        token,
        body,
    )


async def drone_return_home(
    proj_uuid: str,
    device_sn: str = None,
    uuid: Optional[str] = None,
    token: str = USER_TOKEN_FIXED,
) -> Dict[str, Any] | str:
    """
    发送 `return_home` 飞行控制指令，**单独执行**，无需推荐/云控/起飞步骤。
    
    错误处理:
        如果遇到{"result":{"code":228431,"message":"Bad Request","data":null}}错误码，
        需要先调用cloud_controls_create抢夺飞行和负载控制权["flight","payload_99-0-0"]，然后重试操作。

    Args:
        proj_uuid: 项目 UUID（路径参数）
        device_sn: 设备 SN；默认取最近一次设备推荐里的 *gateway_sn*
        uuid: 项目UUID
        token: x-auth-token

    Returns:
        后端响应 JSON 或错误信息字符串。
    """
    filled_device_sn = auto_fill_device_sn(device_sn, use_gateway=True)
    
    if filled_device_sn is None:
        return "device_sn is required (no previous recommendation found)"

    filled_uuid = auto_fill_uuid(uuid, proj_uuid)

    body = {
        "device_cmd_method": "return_home",
        "device_sn": filled_device_sn,
        "uuid": filled_uuid,
    }
    
    return await post_json(
        f"/manage/api/v1/projects/{proj_uuid}/flight-commands",
        token,
        body,
    )
