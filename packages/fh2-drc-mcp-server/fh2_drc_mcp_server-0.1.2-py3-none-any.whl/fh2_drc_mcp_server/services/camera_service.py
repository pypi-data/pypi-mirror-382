# -*- coding: utf-8 -*-
"""
相机控制服务 - 拍照、瞄准、云台控制
"""
from typing import Any, Dict, Optional
from mcp.server.fastmcp import FastMCP
from ..core.http_client import post_json
from ..config.settings import USER_TOKEN_FIXED, DEFAULT_PAYLOAD_INDEX
from ..utils.helpers import auto_fill_device_sn, auto_fill_uuid

# 获取全局MCP实例
mcp: Optional[FastMCP] = None


def set_mcp_instance(mcp_instance: FastMCP) -> None:
    """设置MCP实例"""
    global mcp
    mcp = mcp_instance



async def camera_photo_take(
    proj_uuid: str,
    device_sn: str,
    uuid: Optional[str] = None,
    payload_index: str = DEFAULT_PAYLOAD_INDEX,
    token: str = USER_TOKEN_FIXED,
) -> Dict[str, Any] | str:
    """
    发送 `camera_photo_take` 负载控制指令，控制无人机相机拍照。
    
    错误处理:
        如果遇到{"result":{"code":228431,"message":"Bad Request","data":null}}错误码，
        需要先调用cloud_controls_create抢夺飞行和负载控制权["flight","payload_99-0-0"]，然后重试操作。

    Args:
        proj_uuid: 项目 UUID（路径参数）
        device_sn: 设备 SN；默认取最近一次设备推荐里的 *gateway_sn*
        uuid: 项目UUID
        payload_index: 负载索引，默认 "99-0-0"
        token: x-auth-token

    Returns:
        后端响应 JSON 或错误信息字符串。
    """
    filled_device_sn = auto_fill_device_sn(device_sn, use_gateway=True)
    
    if filled_device_sn is None:
        return "device_sn is required (no previous recommendation found)"

    filled_uuid = auto_fill_uuid(uuid, proj_uuid)

    body = {
        "uuid": filled_uuid,
        "device_sn": filled_device_sn,
        "device_cmd_method": "camera_photo_take",
        "device_cmd_data": {
            "payload_index": payload_index
        }
    }
    
    return await post_json(
        f"/manage/api/v1/projects/{proj_uuid}/payload-commands",
        token,
        body,
    )



async def camera_aim(
    proj_uuid: str,
    x: float,
    y: float,
    device_sn: str = None,
    uuid: Optional[str] = None,
    payload_index: str = DEFAULT_PAYLOAD_INDEX,
    camera_type: str = "wide",
    locked: bool = False,
    token: str = USER_TOKEN_FIXED,
) -> Dict[str, Any] | str:
    """
    发送 `camera_aim` 负载控制指令，移动相机镜头角度到指定位置。
    
    错误处理:
        如果遇到{"result":{"code":228431,"message":"Bad Request","data":null}}错误码，
        需要先调用cloud_controls_create抢夺飞行和负载控制权["flight","payload_99-0-0"]，然后重试操作。

    Args:
        proj_uuid: 项目 UUID（路径参数）
        x: 水平方向坐标 (0.0-1.0)
        y: 垂直方向坐标 (0.0-1.0)
        device_sn: 设备 SN；默认取最近一次设备推荐里的 *gateway_sn*
        uuid: 项目UUID
        payload_index: 负载索引，默认 "99-0-0"
        camera_type: 相机类型，默认 "wide"
        locked: 是否锁定，默认 False
        token: x-auth-token

    Returns:
        后端响应 JSON 或错误信息字符串。
    """
    filled_device_sn = auto_fill_device_sn(device_sn, use_gateway=True)
    
    if filled_device_sn is None:
        return "device_sn is required (no previous recommendation found)"

    filled_uuid = auto_fill_uuid(uuid, proj_uuid)

    body = {
        "uuid": filled_uuid,
        "device_sn": filled_device_sn,
        "device_cmd_method": "camera_aim",
        "device_cmd_data": {
            "payload_index": payload_index,
            "camera_type": camera_type,
            "locked": locked,
            "x": x,
            "y": y
        }
    }
    
    return await post_json(
        f"/manage/api/v1/projects/{proj_uuid}/payload-commands",
        token,
        body,
    )



async def camera_look_at(
    proj_uuid: str,
    target_latitude: float,
    target_longitude: float,
    target_height: float,
    device_sn: str = None,
    uuid: Optional[str] = None,
    payload_index: str = DEFAULT_PAYLOAD_INDEX,
    locked: bool = False,
    token: str = USER_TOKEN_FIXED,
) -> Dict[str, Any] | str:
    """
    发送 `camera_look_at` 负载控制指令，让相机朝向指定的地理坐标位置。
    
    错误处理:
        如果遇到{"result":{"code":228431,"message":"Bad Request","data":null}}错误码，
        需要先调用cloud_controls_create抢夺飞行和负载控制权["flight","payload_99-0-0"]，然后重试操作。

    Args:
        proj_uuid: 项目 UUID（路径参数）
        target_latitude: 目标位置纬度
        target_longitude: 目标位置经度
        target_height: 目标位置高度 (米)
        device_sn: 设备 SN；默认取最近一次设备推荐里的 *gateway_sn*
        uuid: 项目UUID
        payload_index: 负载索引，默认 "99-0-0"
        locked: 是否锁定朝向，默认 False
        token: x-auth-token

    Returns:
        后端响应 JSON 或错误信息字符串。
    """
    filled_device_sn = auto_fill_device_sn(device_sn, use_gateway=True)
    
    if filled_device_sn is None:
        return "device_sn is required (no previous recommendation found)"

    filled_uuid = auto_fill_uuid(uuid, proj_uuid)

    body = {
        "uuid": filled_uuid,
        "device_sn": filled_device_sn,
        "device_cmd_method": "camera_look_at",
        "device_cmd_data": {
            "payload_index": payload_index,
            "locked": locked,
            "longitude": target_longitude,
            "latitude": target_latitude,
            "height": target_height
        }
    }
    
    return await post_json(
        f"/manage/api/v1/projects/{proj_uuid}/payload-commands",
        token,
        body,
    )



async def gimbal_reset_horizontal(
    proj_uuid: str,
    device_sn: str = None,
    uuid: Optional[str] = None,
    payload_index: str = DEFAULT_PAYLOAD_INDEX,
    token: str = USER_TOKEN_FIXED,
) -> Dict[str, Any] | str:
    """
    发送 `gimbal_reset` 负载控制指令，将云台复位到水平位置。
    
    错误处理:
        如果遇到{"result":{"code":228431,"message":"Bad Request","data":null}}错误码，
        需要先调用cloud_controls_create抢夺飞行和负载控制权["flight","payload_99-0-0"]，然后重试操作。

    Args:
        proj_uuid: 项目 UUID（路径参数）
        device_sn: 设备 SN；默认取最近一次设备推荐里的 *gateway_sn*
        uuid: 项目UUID
        payload_index: 负载索引，默认 "99-0-0"
        token: x-auth-token

    Returns:
        后端响应 JSON 或错误信息字符串。
    """
    filled_device_sn = auto_fill_device_sn(device_sn, use_gateway=True)
    
    if filled_device_sn is None:
        return "device_sn is required (no previous recommendation found)"

    filled_uuid = auto_fill_uuid(uuid, proj_uuid)

    body = {
        "uuid": filled_uuid,
        "device_sn": filled_device_sn,
        "device_cmd_method": "gimbal_reset",
        "device_cmd_data": {
            "payload_index": payload_index,
            "reset_mode": 0  # 0=水平
        }
    }
    
    return await post_json(
        f"/manage/api/v1/projects/{proj_uuid}/payload-commands",
        token,
        body,
    )



async def gimbal_reset_downward(
    proj_uuid: str,
    device_sn: str = None,
    uuid: Optional[str] = None,
    payload_index: str = DEFAULT_PAYLOAD_INDEX,
    token: str = USER_TOKEN_FIXED,
) -> Dict[str, Any] | str:
    """
    发送 `gimbal_reset` 负载控制指令，将云台复位到向下位置。
    
    错误处理:
        如果遇到{"result":{"code":228431,"message":"Bad Request","data":null}}错误码，
        需要先调用cloud_controls_create抢夺飞行和负载控制权["flight","payload_99-0-0"]，然后重试操作。

    Args:
        proj_uuid: 项目 UUID（路径参数）
        device_sn: 设备 SN；默认取最近一次设备推荐里的 *gateway_sn*
        uuid: 项目UUID
        payload_index: 负载索引，默认 "99-0-0"
        token: x-auth-token

    Returns:
        后端响应 JSON 或错误信息字符串。
    """
    filled_device_sn = auto_fill_device_sn(device_sn, use_gateway=True)
    
    if filled_device_sn is None:
        return "device_sn is required (no previous recommendation found)"

    filled_uuid = auto_fill_uuid(uuid, proj_uuid)

    body = {
        "uuid": filled_uuid,
        "device_sn": filled_device_sn,
        "device_cmd_method": "gimbal_reset",
        "device_cmd_data": {
            "payload_index": payload_index,
            "reset_mode": 1  # 1=向下
        }
    }
    
    return await post_json(
        f"/manage/api/v1/projects/{proj_uuid}/payload-commands",
        token,
        body,
    )
