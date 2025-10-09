# -*- coding: utf-8 -*-
"""
状态服务 - 飞行状态查询和智能解析
"""
from typing import Any, Dict, Optional
from mcp.server.fastmcp import FastMCP
from ..core.http_client import get_json
from ..config.settings import USER_TOKEN_FIXED
from ..models.enums import TASK_STATUS_MAP, FLYTO_STATUS_MAP, FLIGHT_TYPE_MAP, FlightType
from ..utils.helpers import auto_fill_device_sn

# 获取全局MCP实例
mcp: Optional[FastMCP] = None


def set_mcp_instance(mcp_instance: FastMCP) -> None:
    """设置MCP实例"""
    global mcp
    mcp = mcp_instance



async def get_flight_status(
    proj_uuid: str,
    device_sn: Optional[str] = None,
    token: str = USER_TOKEN_FIXED,
) -> Dict[str, Any] | str:
    """
    查询当前飞行任务状态，用于监控飞行进度和任务执行情况，如果是执行一键起飞后，需要执行到查询到数据为准。直到2min内没查到数据，判定任务失败
    背景知识:如果飞行器关机状态，下发一键起飞，到能够查询到飞行状态需要0-80秒范围内,时间长短不定需要等待。
    **注意**: 此接口建议限制调用频率为 10秒一次，避免频繁请求。
    
    Args:
        proj_uuid: 项目 UUID（路径参数）
        device_sn: 设备 SN；默认取最近一次设备推荐里的 *gateway_sn*
        token: x-auth-token
    
    Returns:
        飞行状态信息 JSON 或错误信息字符串，包含：
        - flight_id: 飞行任务ID
        - flight_task_data: 飞行任务基础数据
            - status: 任务状态 (0=待执行, 1=执行中, 2=完成, 3=失败, 4=超时)
        - flight_type: 飞行类型 (1=航线飞行, 2=手动飞行)
        - fly_to_task: 飞向目标点任务（手动飞行时）
            - status: FlyTo任务状态 (0=待执行, 1=执行中, 2=完成, 3=失败, 4=超时)
            - way_points: 航点列表
            - remaining_distance: 剩余距离(米)
            - remaining_time: 剩余时间(秒)
        - return_home_info: 返航信息
        - is_first_fly_to: 是否首次飞向目标点
    
    状态判断逻辑:
    - 刚下发起飞后可能暂时无数据，需等待几秒
    - 手动飞行中，fly_to_task为null表示已到达目标点
    - flight_task_data.status=2 表示飞行执行中
    - fly_to_task.status=2 表示飞向目标点完成
    """
    filled_device_sn = auto_fill_device_sn(device_sn, use_gateway=True)
    
    if filled_device_sn is None:
        return "device_sn is required (no previous recommendation found)"

    return await get_json(
        f"/task/api/v1/workspaces/{proj_uuid}/flight-tasks/in-flight?sn={filled_device_sn}",
        token,
    )



async def analyze_flight_status(
    proj_uuid: str,
    device_sn: Optional[str] = None,
    token: str = USER_TOKEN_FIXED,
) -> str:
    """
    智能解析飞行状态，提供人性化的状态描述和建议操作。
    
    Args:
        proj_uuid: 项目 UUID
        device_sn: 设备 SN；默认取最近一次设备推荐里的 *gateway_sn*
        token: x-auth-token
    
    Returns:
        人性化的飞行状态描述和建议
    """
    # 获取飞行状态
    status_result = await get_flight_status(proj_uuid, device_sn, token)
    
    if isinstance(status_result, str):
        return f"获取飞行状态失败: {status_result}"
    
    try:
        data = status_result.get("data")
        if not data:
            return "当前无飞行任务数据，可能任务尚未开始或已结束"
        
        flight_task = data.get("flight_task_data", {})
        fly_to_task = data.get("fly_to_task")
        flight_type = data.get("flight_type", 0)
        
        main_status = TASK_STATUS_MAP.get(flight_task.get("status", -1), "未知状态")
        flight_type_desc = FLIGHT_TYPE_MAP.get(flight_type, "未知类型")
        
        result = [f"📍 飞行类型: {flight_type_desc}"]
        result.append(f"🔄 主任务状态: {main_status}")
        
        # 手动飞行的详细分析
        if flight_type == FlightType.MANUAL_FLIGHT:
            if fly_to_task is None:
                if main_status == "执行中":
                    result.append("✅ 已到达目标点，可以执行拍照等操作")
                else:
                    result.append("ℹ️  无飞向目标任务")
            else:
                flyto_status = FLYTO_STATUS_MAP.get(fly_to_task.get("status", -1), "未知")
                result.append(f"🎯 飞向目标状态: {flyto_status}")
                
                if fly_to_task.get("remaining_distance"):
                    distance = fly_to_task["remaining_distance"]
                    time = fly_to_task.get("remaining_time", 0)
                    result.append(f"📏 剩余距离: {distance:.1f}米")
                    result.append(f"⏱️  预计剩余时间: {time:.1f}秒")
                
                way_points = fly_to_task.get("way_points", [])
                way_point_index = fly_to_task.get("way_point_index", 0)
                if way_points:
                    result.append(f"🗺️  航点进度: {way_point_index}/{len(way_points)}")
        
        # 根据状态给出建议
        if main_status == "执行中":
            if fly_to_task is None and flight_type == FlightType.MANUAL_FLIGHT:
                result.append("\n💡 建议: 无人机已到达目标点，现在可以执行拍照指令")
            elif fly_to_task and fly_to_task.get("status") == 1:
                result.append("\n💡 建议: 无人机正在飞向目标点，请等待到达")
        elif main_status in ["成功", "终止"]:
            result.append("\n💡 建议: 飞行任务已结束")
        elif main_status == "待开始":
            result.append("\n💡 建议: 任务尚未开始，可能需要等待几秒钟")
        
        return "\n".join(result)
        
    except Exception as e:
        return f"解析飞行状态时出错: {str(e)}"
