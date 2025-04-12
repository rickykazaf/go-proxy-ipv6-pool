#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
kocaptcha.py - 与KoCaptcha API交互的客户端工具

该模块提供了一个封装KoCaptcha API的类，用于处理FunCaptcha验证码的解决方案。
"""

import requests
import time
import json
import logging
from typing import Dict, Any, Optional


class KoCaptchaClient:
    """KoCaptcha API客户端类，用于处理FunCaptcha验证码的解决方案。"""

    # API端点
    BASE_URL = "https://kocaptcha.com/api"
    CREATE_TASK_URL = f"{BASE_URL}/task/create"
    GET_TASK_RESULT_URL = f"{BASE_URL}/task/result"
    
    def __init__(self, client_key: str, timeout: int = 30, polling_interval: int = 1):
        """
        初始化KoCaptcha客户端

        Args:
            client_key: KoCaptcha API密钥
            timeout: 任务超时时间（秒）
            polling_interval: 轮询间隔时间（秒）
        """
        self.client_key = client_key
        self.timeout = timeout
        self.polling_interval = polling_interval
        self.logger = logging.getLogger(__name__)
        
        # 配置日志
        self._setup_logging()
    
    def _setup_logging(self):
        """配置日志记录器"""
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
    
    def create_funcaptcha_task(self, website_url: str, website_key: str, blob: str, 
                               proxy: Optional[str] = None, cn: bool = False) -> Dict[str, Any]:
        """
        创建一个FunCaptcha验证码解决任务

        Args:
            website_url: 需要解决验证码的网站URL
            website_key: FunCaptcha的网站密钥
            blob: FunCaptcha的blob数据
            proxy: 代理服务器地址（格式如"http:host:port"）
            user_agent: 用户代理（格式如"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"）
            cn: 是否为中国区域

        Returns:
            包含任务ID的字典或错误信息
        """
        data_value = {"blob": blob}
        data_json = json.dumps(data_value)
        
        task_data = {
            "clientKey": self.client_key,
            "task": {
                "websiteURL": website_url,
                "websiteKey": website_key,
                "type": "FuncaptchaTaskProxyless",
                "cn": cn,
                "data": data_json, 
                # "userAgent": user_agent
            }
        }
        
        # 如果提供了代理，则添加到请求中
        if proxy:
            task_data["task"]["proxy"] = proxy
        
        try:
            self.logger.info("创建验证码解决任务...")
            response = requests.post(
                self.CREATE_TASK_URL, 
                json=task_data,
                timeout=10
            )
            response.raise_for_status()
            result = response.json()
            
            if result.get("errorId") == 0:
                task_id = result.get("taskId")
                self.logger.info(f"任务创建成功，任务ID: {task_id}")
                return {"success": True, "task_id": task_id}
            else:
                error_msg = result.get("errorDescription", "未知错误")
                self.logger.error(f"任务创建失败: {error_msg}")
                return {"success": False, "error": error_msg}
                
        except requests.RequestException as e:
            self.logger.error(f"API请求异常: {str(e)}")
            return {"success": False, "error": f"API请求异常: {str(e)}"}
    
    def get_task_result(self, task_id: str) -> Dict[str, Any]:
        """
        获取验证码解决任务的结果

        Args:
            task_id: 任务ID

        Returns:
            包含任务结果的字典
        """
        get_task_data = {
            "clientKey": self.client_key,
            "taskId": task_id
        }
        
        try:
            response = requests.post(
                self.GET_TASK_RESULT_URL, 
                json=get_task_data,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            self.logger.error(f"获取任务结果时发生异常: {str(e)}")
            return {"errorId": 1, "errorDescription": f"获取任务结果时发生异常: {str(e)}"}
    
    def wait_for_result(self, task_id: str) -> Dict[str, Any]:
        """
        等待并轮询任务结果，直到任务完成或超时

        Args:
            task_id: 任务ID

        Returns:
            包含任务结果或错误信息的字典
        """
        self.logger.info(f"等待任务 {task_id} 的结果...")
        elapsed_time = 0
        
        # 首次请求前等待一小段时间，让服务器有时间处理
        time.sleep(self.polling_interval)
        
        while elapsed_time < self.timeout:
            result = self.get_task_result(task_id)
            self.logger.debug(f"轮询结果: {result}")
            
            error_id = result.get("errorId", 1)
            if error_id == 0:
                status = result.get("status", "")
                if status == "ready":
                    solution = result.get("solution", {})
                    self.logger.info("任务完成，已获取到解决方案")
                    return {"success": True, "solution": solution}
                else:
                    self.logger.info(f"任务仍在处理中，状态: {status}")
            else:
                error_msg = result.get("errorDescription", "未知错误")
                self.logger.error(f"获取任务结果时出错: {error_msg}")
                return {"success": False, "error": error_msg}
            
            time.sleep(self.polling_interval)
            elapsed_time += self.polling_interval
        
        self.logger.error(f"任务超时，超过了 {self.timeout} 秒")
        return {"success": False, "error": "任务等待超时"}
    
    def solve_funcaptcha(self, website_url: str, website_key: str, blob: str,
                         proxy: Optional[str] = None, cn: bool = False) -> Dict[str, Any]:
        """
        解决FunCaptcha验证码的完整流程

        Args:
            website_url: 需要解决验证码的网站URL
            website_key: FunCaptcha的网站密钥
            blob: FunCaptcha的blob数据
            proxy: 代理服务器地址（格式如"http:host:port:username:password"）
            cn: 是否为中国区域
            user_agent: 用户代理（格式如"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"）
        Returns:
            包含解决方案或错误信息的字典
        """
        # 创建任务
        create_result = self.create_funcaptcha_task(
            website_url=website_url,
            website_key=website_key,
            blob=blob,
            proxy=proxy,
            cn=cn
        )
        
        if not create_result["success"]:
            return create_result
        
        # 等待并获取结果
        return self.wait_for_result(create_result["task_id"])


def example_usage():
    """使用示例函数"""
    # 设置参数
    client_key = "你的client_key"
    website_url = "https://signup.live.com/signup"
    website_key = "85800716-F435-4981-864C-8B90602D10F7"
    blob = "y7zHUM9RWmyyE7uq.uGkMlceNsHpbRZ0jAcqbiZjUfR1uWTEndieEkmdzmTpYJjgrhzIWhyxjbUF+Ameh1JdrRIKNTm9vvtw1NdcLZnmW9ZS2W6PthyXc+KDWYaKlSaVgUZH4yC2D0NSd6p1jrgtF93wdMpRK4BaeVP0+0mtWXQA="
    proxy = ""  # 可选，如不需要可设为None 或者 "", 如果需要设置代理（格式如"http:host:port:username:password"）
    cn = False
    # 当cn为True时，需要使用中国大陆的代理
    # 当cn为False时，需要使用国外的代理
    # 当cn为False时，而且proxy为空，则使用内置的代理


    # 创建客户端实例
    # polling_interval 轮询间隔时间（秒） ------查询任务结果的间隔时间
    client = KoCaptchaClient(client_key, timeout=60, polling_interval=1)
    
    # 解决验证码
    
    result = client.solve_funcaptcha(
        website_url=website_url,
        website_key=website_key,
        blob=blob,
        proxy=proxy,
        cn=cn
    )
    
    # 处理结果
    if result["success"]:
        print("验证码解决成功:")
        print(json.dumps(result["solution"], indent=2, ensure_ascii=False))
    else:
        print(f"验证码解决失败: {result['error']}")


if __name__ == "__main__":
    # 设置日志级别
    logging.basicConfig(level=logging.INFO)
    
    # 运行示例
    example_usage()