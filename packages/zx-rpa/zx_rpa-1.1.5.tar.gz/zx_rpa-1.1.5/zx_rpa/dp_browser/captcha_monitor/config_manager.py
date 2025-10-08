"""
验证码监控配置管理器

负责加载和管理平台配置文件，提供配置查询和动态更新功能
"""
import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, List
from loguru import logger


class ConfigManager:
    """验证码监控配置管理器"""
    
    def __init__(self, config_dir: Optional[str] = None):
        """初始化配置管理器
        
        Args:
            config_dir (str, optional): 配置文件目录路径，默认使用内置配置目录
        """
        self.config_dir = config_dir or self._get_default_config_dir()
        self.configs: Dict[str, Dict[str, Any]] = {}
        self._load_all_configs()
        # 移除初始化完成的冗余日志
    
    def _get_default_config_dir(self) -> str:
        """获取默认配置目录路径"""
        current_dir = Path(__file__).parent
        return str(current_dir / "configs")
    
    def _load_all_configs(self):
        """加载所有配置文件"""
        config_path = Path(self.config_dir)
        if not config_path.exists():
            logger.debug("配置目录不存在: {}", self.config_dir)
            return
            
        for config_file in config_path.glob("*.yaml"):
            platform_name = config_file.stem
            try:
                self._load_config_file(platform_name, str(config_file))
            except Exception as e:
                logger.debug("加载配置文件失败: {}, 错误: {}", config_file, str(e))
    
    def _load_config_file(self, platform_name: str, file_path: str):
        """加载单个配置文件
        
        Args:
            platform_name (str): 平台名称
            file_path (str): 配置文件路径
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            self.configs[platform_name] = config
            # 移除配置加载的冗余日志
    
    def get_platform_config(self, platform_name: str) -> Dict[str, Any]:
        """获取平台配置
        
        Args:
            platform_name (str): 平台名称
            
        Returns:
            Dict[str, Any]: 平台配置字典，如果不存在则返回默认配置
        """
        config = self.configs.get(platform_name)
        if config is None:
            logger.debug("平台配置不存在，使用默认配置: {}，已加载的平台: {}",
                        platform_name, list(self.configs.keys()))
            return self.configs.get("default", {})
        # 移除配置查找成功的冗余日志
        return config
    
    def get_timing_config(self, platform_name: str) -> Dict[str, float]:
        """获取等待时间配置
        
        Args:
            platform_name (str): 平台名称
            
        Returns:
            Dict[str, float]: 时间配置字典
        """
        config = self.get_platform_config(platform_name)
        return config.get("timing", {})
    
    def get_monitoring_config(self, platform_name: str) -> Dict[str, Any]:
        """获取监控配置
        
        Args:
            platform_name (str): 平台名称
            
        Returns:
            Dict[str, Any]: 监控配置字典
        """
        config = self.get_platform_config(platform_name)
        return config.get("monitoring", {})
    
    def get_captcha_handlers(self, platform_name: str) -> List[Dict[str, Any]]:
        """获取验证码处理器配置列表
        
        Args:
            platform_name (str): 平台名称
            
        Returns:
            List[Dict[str, Any]]: 处理器配置列表，按优先级排序
        """
        config = self.get_platform_config(platform_name)
        handlers = config.get("captcha_handlers", [])
        # 按优先级排序
        return sorted(handlers, key=lambda x: x.get("priority", 999))
    
    def is_high_risk_action(self, platform_name: str, selector: str) -> bool:
        """判断是否为高危操作
        
        Args:
            platform_name (str): 平台名称
            selector (str): 元素选择器
            
        Returns:
            bool: 是否为高危操作
        """
        monitoring_config = self.get_monitoring_config(platform_name)
        keywords = monitoring_config.get("high_risk_keywords", [])
        
        selector_lower = selector.lower()
        for keyword in keywords:
            if keyword.lower() in selector_lower:
                logger.debug("检测到高危操作关键词: {} in {}", keyword, selector)
                return True
        return False
    
    def reload_config(self, platform_name: str):
        """重新加载指定平台配置
        
        Args:
            platform_name (str): 平台名称
        """
        config_file = Path(self.config_dir) / f"{platform_name}.yaml"
        if config_file.exists():
            try:
                self._load_config_file(platform_name, str(config_file))
                logger.debug("重新加载平台配置: {}", platform_name)
            except Exception as e:
                logger.debug("重新加载配置失败: {}, 错误: {}", platform_name, str(e))
