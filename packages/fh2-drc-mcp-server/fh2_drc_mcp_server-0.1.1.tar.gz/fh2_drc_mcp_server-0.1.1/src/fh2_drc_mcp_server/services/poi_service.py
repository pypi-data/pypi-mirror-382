# -*- coding: utf-8 -*-
"""
POI兴趣点服务 - POI环绕和退出
"""
from typing import Any, Dict, Optional
from mcp.server.fastmcp import FastMCP
from ..core.http_client import post_json, delete_json
from ..config.settings import USER_TOKEN_FIXED, DEFAULT_PAYLOAD_INDEX
from ..utils.helpers import auto_fill_device_sn

# 获取全局MCP实例
mcp: Optional[FastMCP] = None


def set_mcp_instance(mcp_instance: FastMCP) -> None:
    """设置MCP实例"""
    global mcp
    mcp = mcp_instance



async def poi_enter(
    proj_uuid: str,
    poi_latitude: float,
    poi_longitude: float,
    poi_height: float,
    circle_radius: float,
    device_sn: Optional[str] = None,
    speed: int = -1,
    payload_index: str = DEFAULT_PAYLOAD_INDEX,
    token: str = USER_TOKEN_FIXED,
) -> Dict[str, Any] | str:
    """
    【POI兴趣点环绕】让飞行器围绕指定兴趣点进行环绕飞行 (poi-enter)
    用途: 飞行器围绕目标点进行圆形轨迹飞行，常用于环拍、巡检等任务
    场景: 需要从多个角度观察或拍摄某个目标点时使用
    前提: 飞行器必须已经在空中飞行状态
    
    错误处理:
        如果遇到{"result":{"code":228431,"message":"Bad Request","data":null}}错误码，
        需要先调用cloud_controls_create抢夺飞行和负载控制权["flight","payload_99-0-0"]，然后重试操作。

    Args:
        proj_uuid: 项目 UUID（路径参数）
        poi_latitude: POI中心点纬度
        poi_longitude: POI中心点经度
        poi_height: POI中心点高度 (米)
        circle_radius: 环绕半径 (米)
        device_sn: 设备 SN；默认取最近一次设备推荐里的 *gateway_sn*
        speed: 环绕速度，-1为自动速度
        payload_index: 负载索引，默认 "99-0-0"
        token: x-auth-token

    Returns:
        POI任务执行结果 JSON 或错误信息字符串。
    """
    filled_device_sn = auto_fill_device_sn(device_sn, use_gateway=True)
    
    if filled_device_sn is None:
        return "device_sn is required (no previous recommendation found)"

    body = {
        "device_sn": filled_device_sn,
        "poi_center_point": {
            "latitude": poi_latitude,
            "longitude": poi_longitude,
            "height": poi_height
        },
        "speed": speed,
        "circle_radius": circle_radius,
        "payload_index": payload_index
    }

    return await post_json(
        f"/task/api/v1/workspaces/{proj_uuid}/flight-tasks/poi-enter",
        token,
        body,
    )



async def poi_exit(
    proj_uuid: str,
    device_sn: Optional[str] = None,
    token: str = USER_TOKEN_FIXED,
) -> Dict[str, Any] | str:
    """
    【POI兴趣点退出】停止当前的POI环绕飞行任务 (poi-exit)
    用途: 中断正在进行的POI环绕飞行，让飞行器停止环绕并保持当前位置
    场景: 需要提前结束POI环绕任务或紧急停止时使用
    前提: 飞行器正在执行POI环绕任务
    
    错误处理:
        如果遇到{"result":{"code":228431,"message":"Bad Request","data":null}}错误码，
        需要先调用cloud_controls_create抢夺飞行和负载控制权["flight","payload_99-0-0"]，然后重试操作。

    Args:
        proj_uuid: 项目 UUID（路径参数）
        device_sn: 设备 SN；默认取最近一次设备推荐里的 *gateway_sn*
        token: x-auth-token

    Returns:
        POI退出执行结果 JSON 或错误信息字符串。
    """
    filled_device_sn = auto_fill_device_sn(device_sn, use_gateway=True)
    
    if filled_device_sn is None:
        return "device_sn is required (no previous recommendation found)"

    body = {
        "device_sn": filled_device_sn
    }

    return await delete_json(
        f"/task/api/v1/workspaces/{proj_uuid}/flight-tasks/poi-exit",
        token,
        body,
    )
