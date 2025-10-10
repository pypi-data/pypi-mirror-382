"""
模板管理器

管理 Agent 模板的查询，专注核心功能
"""

import asyncio
import os
from datetime import datetime
from typing import List, Optional

from ppio_sandbox.core.connection_config import ConnectionConfig
from ppio_sandbox.core.api import AsyncApiClient, handle_api_exception
from .auth import AuthManager
from .exceptions import TemplateNotFoundError, NetworkError, AuthenticationError
from .models import AgentTemplate


class TemplateManager:
    """模板管理器 - 简化版本"""
    
    def __init__(self, auth_manager: AuthManager):
        """初始化模板管理器
        
        Args:
            auth_manager: 认证管理器
        """
        self.auth_manager = auth_manager
        
        # 创建连接配置 - 参考 CLI 项目，使用 access_token
        self.connection_config = ConnectionConfig(
            access_token=self.auth_manager.api_key
        )
        self._client = None
    
    async def _get_client(self) -> AsyncApiClient:
        """获取 API 客户端"""
        if self._client is None:
            # 导入 httpx.Limits 用于连接池配置
            import httpx
            self._client = AsyncApiClient(
                self.connection_config, 
                require_api_key=False, 
                require_access_token=True,
                limits=httpx.Limits(max_keepalive_connections=5, max_connections=10)
            )
        return self._client
    
    async def close(self):
        """关闭 HTTP 客户端"""
        if self._client:
            await self._client.get_async_httpx_client().aclose()
            self._client = None
    
    def _map_template_data_to_model(self, template_data: dict) -> AgentTemplate:
        """映射API返回的模板数据到AgentTemplate模型
        
        Args:
            template_data: API返回的模板数据字典
            
        Returns:
            AgentTemplate对象
        """
        return AgentTemplate(
            template_id=template_data.get("templateID") or template_data.get("id"),
            name=template_data.get("aliases", [None])[0] if template_data.get("aliases") else "Unknown",
            version=template_data.get("version", "1.0.0"),
            description=template_data.get("description"),
            author=template_data.get("createdBy", {}).get("email") if template_data.get("createdBy") else None,
            tags=template_data.get("tags", []),
            created_at=datetime.fromisoformat(
                template_data.get("createdAt", datetime.now().isoformat()).replace('Z', '+00:00')
            ) if template_data.get("createdAt") else datetime.now(),
            updated_at=datetime.fromisoformat(
                template_data.get("updatedAt", datetime.now().isoformat()).replace('Z', '+00:00')
            ) if template_data.get("updatedAt") else datetime.now(),
            status="active",  # CLI中没有status字段，默认为active
            metadata=template_data.get("metadata", {}),
            size=None,  # CLI中没有size字段
            build_time=None,  # CLI中没有build_time字段
            dependencies=[],  # CLI中没有dependencies字段
            runtime_info=None  # CLI中没有runtime_info字段
        )
    
    async def list_templates(
        self, 
        tags: Optional[List[str]] = None,
        name_filter: Optional[str] = None
    ) -> List[AgentTemplate]:
        """列出模板
        
        Args:
            tags: 标签过滤
            name_filter: 名称过滤
            
        Returns:
            模板列表，每个模板的 metadata 字段包含 Agent 元信息
        """
        try:
            client = await self._get_client()
            
            # 构建查询参数
            params = {}
            if tags:
                params["tags"] = ",".join(tags)
            if name_filter:
                params["name"] = name_filter
            
            # 使用 ApiClient 进行 HTTP 请求
            response = await client.get_async_httpx_client().request(
                method="GET",
                url="/templates",
                params=params
            )
            
            # 处理响应状态码
            if response.status_code == 401:
                raise AuthenticationError("Invalid or expired API Key")
            elif response.status_code != 200:
                # 使用 handle_api_exception 处理错误
                from ppio_sandbox.core.api.client.types import Response as PPIOResponse
                ppio_response = PPIOResponse(
                    status_code=response.status_code,
                    content=response.content,
                    headers=response.headers,
                    parsed=None
                )
                raise handle_api_exception(ppio_response)
            
            data = response.json()
            templates = []
            
            # 处理响应数据 - 基于CLI中的模式，数据应该直接是模板数组
            template_list = data if isinstance(data, list) else data.get("templates", [])
            
            for template_data in template_list:
                try:
                    # 使用私有方法映射模板数据
                    template = self._map_template_data_to_model(template_data)
                    templates.append(template)
                except Exception as e:
                    # 跳过无效的模板数据，记录错误但不中断处理
                    print(f"Warning: Failed to parse template data: {e}")
                    continue
            
            return templates
            
        except AuthenticationError:
            raise
        except NetworkError:
            raise
        except Exception as e:
            raise NetworkError(f"Failed to list templates: {str(e)}")
    
    async def get_template(self, template_id: str) -> AgentTemplate:
        """获取特定模板
        
        Args:
            template_id: 模板 ID
            
        Returns:
            模板对象，包含完整的 Agent 元信息
            
        Raises:
            TemplateNotFoundError: 模板不存在时抛出
        """
        try:
            client = await self._get_client()
            
            # 使用 ApiClient 进行 HTTP 请求
            response = await client.get_async_httpx_client().request(
                method="GET",
                url=f"/templates/{template_id}"
            )
            
            # 处理响应状态码
            if response.status_code == 401:
                raise AuthenticationError("Invalid or expired API Key")
            elif response.status_code == 404:
                raise TemplateNotFoundError(f"Template {template_id} not found")
            elif response.status_code != 200:
                # 使用 handle_api_exception 处理错误
                from ppio_sandbox.core.api.client.types import Response as PPIOResponse
                ppio_response = PPIOResponse(
                    status_code=response.status_code,
                    content=response.content,
                    headers=response.headers,
                    parsed=None
                )
                raise handle_api_exception(ppio_response)
            
            template_data = response.json()
            
            # 使用私有方法映射模板数据
            return self._map_template_data_to_model(template_data)
            
        except AuthenticationError:
            raise
        except TemplateNotFoundError:
            raise
        except NetworkError:
            raise
        except Exception as e:
            # Fallback: 如果直接获取模板失败，尝试从列表中查找
            try:
                templates = await self.list_templates()
                for template in templates:
                    if template.template_id == template_id:
                        return template
                raise TemplateNotFoundError(f"Template {template_id} not found after fallback: {str(e)}")
            except (AuthenticationError, TemplateNotFoundError, NetworkError):
                raise
            except Exception as fallback_e:
                raise NetworkError(f"Failed to get template: {str(e)}. Fallback also failed: {str(fallback_e)}")
    
    async def template_exists(self, template_id: str) -> bool:
        """检查模板是否存在
        
        Args:
            template_id: 模板 ID
            
        Returns:
            模板是否存在
        """
        try:
            # 由于单个模板API有问题，改用列表方式检查
            templates = await self.list_templates()
            return any(template.template_id == template_id for template in templates)
        except Exception:
            # 网络错误等情况认为模板不存在
            return False