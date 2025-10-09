#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
XGO状态读取服务
负责读取XGO机器人的各种状态信息
"""

import logging
from typing import List, Union

# 尝试导入xgolib，如果不存在则使用模拟模式
try:
    from xgolib import XGO
    XGO_AVAILABLE = True
except ImportError:
    XGO_AVAILABLE = False
    logging.warning("xgolib未安装，将使用模拟模式")


class XGOStatusService:
    """XGO状态读取服务类"""
    
    def __init__(self):
        self.dog = None
        self.init_connection()
    
    def init_connection(self):
        """初始化XGO连接"""
        if XGO_AVAILABLE:
            try:
                self.dog = XGO("mini")
                logging.info("XGO连接成功")
            except Exception as e:
                logging.error(f"XGO连接失败: {str(e)}")
        else:
            logging.warning("XGO库不可用，使用模拟模式")
    
    def read_motor(self) -> List[float]:
        """
        读取15个舵机的角度
        
        Returns:
            List[float]: 长度为15的列表，对应编号[11,12,13,21,22,23,31,32,33,41,42,43,51,52,53]的舵机角度
                        读取失败则返回空列表
        """
        if not self.dog:
            logging.warning("XGO未初始化，返回空列表")
            return []
        
        try:
            # 调用XGO的read_motor方法
            motor_angles = self.dog.read_motor()
            
            # 确保返回15个值
            if isinstance(motor_angles, list) and len(motor_angles) == 15:
                logging.info(f"成功读取舵机角度: {motor_angles}")
                return motor_angles
            else:
                logging.error(f"舵机角度数据格式错误: {motor_angles}")
                return []
                
        except Exception as e:
            logging.error(f"读取舵机角度失败: {str(e)}")
            return []
    
    def read_battery(self) -> int:
        """
        读取当前电池电量
        
        Returns:
            int: 1-100的整数，代表电池剩余电量百分比，读取失败则返回0
        """
        if not self.dog:
            logging.warning("XGO未初始化，返回电量0")
            return 0
        
        try:
            # 调用XGO的read_battery方法
            battery_level = self.dog.read_battery()
            
            # 确保返回值在合理范围内
            if isinstance(battery_level, (int, float)):
                battery_level = int(battery_level)
                if 0 <= battery_level <= 100:
                    logging.info(f"成功读取电池电量: {battery_level}%")
                    return battery_level
                else:
                    logging.warning(f"电池电量值超出范围: {battery_level}")
                    return max(0, min(100, battery_level))
            else:
                logging.error(f"电池电量数据格式错误: {battery_level}")
                return 0
                
        except Exception as e:
            logging.error(f"读取电池电量失败: {str(e)}")
            return 0
    
    def read_roll(self) -> float:
        """
        读取当前Roll姿态角度
        
        Returns:
            float: Roll角度，读取失败则返回0.0
        """
        if not self.dog:
            logging.warning("XGO未初始化，返回Roll角度0.0")
            return 0.0
        
        try:
            # 调用XGO的read_roll方法
            roll_angle = self.dog.read_roll()
            
            if isinstance(roll_angle, (int, float)):
                logging.info(f"成功读取Roll角度: {roll_angle}")
                return float(roll_angle)
            else:
                logging.error(f"Roll角度数据格式错误: {roll_angle}")
                return 0.0
                
        except Exception as e:
            logging.error(f"读取Roll角度失败: {str(e)}")
            return 0.0
    
    def read_pitch(self) -> float:
        """
        读取当前Pitch姿态角度
        
        Returns:
            float: Pitch角度，读取失败则返回0.0
        """
        if not self.dog:
            logging.warning("XGO未初始化，返回Pitch角度0.0")
            return 0.0
        
        try:
            # 调用XGO的read_pitch方法
            pitch_angle = self.dog.read_pitch()
            
            if isinstance(pitch_angle, (int, float)):
                logging.info(f"成功读取Pitch角度: {pitch_angle}")
                return float(pitch_angle)
            else:
                logging.error(f"Pitch角度数据格式错误: {pitch_angle}")
                return 0.0
                
        except Exception as e:
            logging.error(f"读取Pitch角度失败: {str(e)}")
            return 0.0
    
    def read_yaw(self) -> float:
        """
        读取当前Yaw姿态角度
        
        Returns:
            float: Yaw角度，读取失败则返回0.0
        """
        if not self.dog:
            logging.warning("XGO未初始化，返回Yaw角度0.0")
            return 0.0
        
        try:
            # 调用XGO的read_yaw方法
            yaw_angle = self.dog.read_yaw()
            
            if isinstance(yaw_angle, (int, float)):
                logging.info(f"成功读取Yaw角度: {yaw_angle}")
                return float(yaw_angle)
            else:
                logging.error(f"Yaw角度数据格式错误: {yaw_angle}")
                return 0.0
                
        except Exception as e:
            logging.error(f"读取Yaw角度失败: {str(e)}")
            return 0.0
    
    def read_all_status(self) -> dict:
        """
        读取所有状态信息
        
        Returns:
            dict: 包含所有状态信息的字典
        """
        return {
            'motor_angles': self.read_motor(),
            'battery_level': self.read_battery(),
            'roll': self.read_roll(),
            'pitch': self.read_pitch(),
            'yaw': self.read_yaw()
        }
    
    def reconnect(self):
        """
        重新连接XGO
        """
        logging.info("尝试重新连接XGO...")
        self.dog = None
        self.init_connection()


# 全局XGO状态服务实例
xgo_status_service = XGOStatusService()