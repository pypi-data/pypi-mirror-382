#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
日志管理器 - 核心组件
"""

import threading
from typing import Optional, Any
from .config import LogConfig


class LogManager:
    """
    日志管理器 - 单例模式
    
    职责：
    1. 全局日志配置管理
    2. 配置状态跟踪
    3. 线程安全的配置更新
    """
    
    _instance: Optional['LogManager'] = None
    _lock = threading.Lock()
    
    def __new__(cls) -> 'LogManager':
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(LogManager, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if hasattr(self, '_initialized') and self._initialized:
            return
            
        self._config: Optional[LogConfig] = None
        self._configured = False
        self._config_lock = threading.RLock()
        self._initialized = True
    
    @property
    def config(self) -> Optional[LogConfig]:
        """获取当前配置"""
        with self._config_lock:
            return self._config
    
    @property
    def is_configured(self) -> bool:
        """检查是否已配置"""
        return self._configured
    
    def configure(self, settings=None, **kwargs) -> LogConfig:
        """
        配置日志系统
        
        Args:
            settings: 配置对象或None
            **kwargs: 关键字参数配置
            
        Returns:
            LogConfig: 生效的配置对象
        """
        with self._config_lock:
            # 总是重新配置，即使已经配置过
            # 从不同来源创建配置
            if settings is not None:
                # 检查settings是否已经是LogConfig对象
                if isinstance(settings, LogConfig):
                    config = settings
                else:
                    config = LogConfig.from_settings(settings)
            elif kwargs:
                config = LogConfig.from_dict(kwargs)
            else:
                config = LogConfig()  # 使用默认配置
            
            # 验证配置
            if not config.validate():
                raise ValueError("Invalid log configuration")
            
            self._config = config
            self._configured = True
            
            return config
    
    def reset(self):
        """重置配置（主要用于测试）"""
        with self._config_lock:
            self._config = None
            self._configured = False


# 全局实例
_log_manager = LogManager()

# 模块级便捷函数
def configure(settings=None, **kwargs) -> LogConfig:
    """配置日志系统"""
    return _log_manager.configure(settings, **kwargs)

def is_configured() -> bool:
    """检查是否已配置"""
    return _log_manager.is_configured

def get_config() -> Optional[LogConfig]:
    """获取当前配置"""
    return _log_manager.config

def reset():
    """重置配置"""
    _log_manager.reset()