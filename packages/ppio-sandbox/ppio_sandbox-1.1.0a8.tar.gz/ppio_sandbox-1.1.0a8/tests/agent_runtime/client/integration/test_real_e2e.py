"""
真实环境端到端测试

这些测试使用真实的 PPIO API 进行测试，需要设置以下环境变量：
- PPIO_API_KEY: 真实的 API Key
- PPIO_TEST_TEMPLATE_ID: （可选）指定的测试模板 ID
"""

import pytest
import asyncio
from ppio_sandbox.agent_runtime.client import AgentRuntimeClient
from ppio_sandbox.agent_runtime.client.models import InvocationRequest, SessionStatus
from ppio_sandbox.agent_runtime.client.exceptions import InvocationError


class TestRealEnvironmentE2E:
    """真实环境端到端测试"""
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    @pytest.mark.network  # 标记需要网络的测试
    async def test_real_template_listing(self, real_api_key):
        """测试真实环境下的模板列表"""
        if not real_api_key:
            pytest.skip("需要真实 API Key 进行集成测试")
        
        # 使用中国区域的API端点
        from ppio_sandbox.agent_runtime.client.models import ClientConfig
        config = ClientConfig()
        
        async with AgentRuntimeClient(api_key=real_api_key, config=config) as client:
            templates = await client.list_templates()
            
            # 验证返回的模板
            assert len(templates) > 0, "应该有至少一个可用的模板"
            
            for template in templates:
                assert hasattr(template, 'template_id'), "模板应该有 template_id"
                assert hasattr(template, 'name'), "模板应该有 name"
                assert template.template_id, "template_id 不应该为空"
                print(f"可用模板: {template.name} ({template.template_id})")
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    @pytest.mark.network
    async def test_real_session_creation_and_invocation(self, real_api_key, real_template):
        """测试真实环境下的会话创建和调用"""
        if not real_api_key:
            pytest.skip("需要真实 API Key 进行集成测试")
        
        print(f"使用模板: {real_template.name} ({real_template.template_id})")
        
        # 使用中国区域的API端点
        from ppio_sandbox.agent_runtime.client.models import ClientConfig
        config = ClientConfig()
        
        async with AgentRuntimeClient(api_key=real_api_key, config=config) as client:
            # 1. 创建会话
            session = await client.create_session(real_template.template_id, timeout_seconds=20)
            assert session is not None, "会话创建应该成功"
            assert session.status == SessionStatus.ACTIVE, "会话应该处于活跃状态"
            print(f"创建会话成功: {session.sandbox_id}")
            
            try:
                # 2. 执行简单调用
                response = await session.invoke("Hello, this is a test message from automated testing")
                assert response is not None, "调用应该返回响应"
                print(f"调用响应: {response}")
                
                # 3. 测试健康检查
                ping_response = await session.ping()
                assert ping_response is not None, "健康检查应该成功"
                print(f"健康检查状态: {ping_response.status}")
                
            finally:
                # 4. 清理会话
                await client.close_session(session.sandbox_id)
                print("会话已关闭")
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    @pytest.mark.network
    async def test_real_convenience_method(self, real_api_key, real_template):
        """测试真实环境下的便利方法"""
        if not real_api_key:
            pytest.skip("需要真实 API Key 进行集成测试")
        
        print(f"使用模板: {real_template.name} ({real_template.template_id})")
        
        # 使用中国区域的API端点
        from ppio_sandbox.agent_runtime.client.models import ClientConfig
        config = ClientConfig()
        
        async with AgentRuntimeClient(api_key=real_api_key, config=config) as client:
            # 使用便利方法直接调用
            response = await client.invoke_agent(
                template_id=real_template.template_id,
                request="Test convenience method call"
            )
            
            assert response is not None, "便利方法调用应该成功"
            print(f"便利方法响应: {response}")
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    @pytest.mark.network 
    @pytest.mark.slow  # 标记为慢速测试
    async def test_real_streaming_invocation(self, real_api_key, real_template):
        """测试真实环境下的流式调用"""
        if not real_api_key:
            pytest.skip("需要真实 API Key 进行集成测试")
        
        print(f"使用模板: {real_template.name} ({real_template.template_id})")
        
        # 使用中国区域的API端点
        from ppio_sandbox.agent_runtime.client.models import ClientConfig
        config = ClientConfig()
        
        async with AgentRuntimeClient(api_key=real_api_key, config=config) as client:
            # 创建会话
            session = await client.create_session(real_template.template_id, timeout_seconds=20)
            
            try:
                # 流式调用
                chunks = []
                async for chunk in await session.invoke("Please generate a short poem about testing", stream=True):
                    chunks.append(chunk)
                    print(f"收到流式数据: {chunk}")
                    
                    # 限制测试时间，避免过长
                    if len(chunks) >= 10:
                        break
                
                assert len(chunks) > 0, "应该接收到至少一个数据块"
                
            finally:
                await client.close_session(session.sandbox_id)
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    @pytest.mark.network
    async def test_real_multiple_sessions(self, real_api_key, real_template):
        """测试真实环境下的多会话管理"""
        if not real_api_key:
            pytest.skip("需要真实 API Key 进行集成测试")
        
        print(f"使用模板: {real_template.name} ({real_template.template_id})")
        
        # 使用中国区域的API端点
        from ppio_sandbox.agent_runtime.client.models import ClientConfig
        config = ClientConfig()
        
        async with AgentRuntimeClient(api_key=real_api_key, config=config) as client:
            sessions = []
            try:
                # 创建多个会话
                for i in range(3):  # 限制数量避免配额消耗
                    session = await client.create_session(real_template.template_id, timeout_seconds=20)
                    sessions.append(session)
                    print(f"创建会话 {i+1}: {session.sandbox_id}")
                
                # 验证所有会话都活跃
                for session in sessions:
                    assert session.status == SessionStatus.ACTIVE
                    
                    # 简单测试每个会话
                    response = await session.invoke(f"Test message for session {session.sandbox_id}")
                    assert response is not None
                    print(f"会话 {session.sandbox_id} 响应正常")
            
            finally:
                # 清理所有会话
                for session in sessions:
                    try:
                        await client.close_session(session.sandbox_id)
                        print(f"关闭会话: {session.sandbox_id}")
                    except Exception as e:
                        print(f"关闭会话失败: {e}")


class TestRealEnvironmentErrorHandling:
    """真实环境错误处理测试"""
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    @pytest.mark.network
    async def test_invalid_template_id(self, real_api_key):
        """测试无效的模板ID处理"""
        if not real_api_key:
            pytest.skip("需要真实 API Key 进行集成测试")
        
        # 使用中国区域的API端点
        from ppio_sandbox.agent_runtime.client.models import ClientConfig
        config = ClientConfig()
        
        async with AgentRuntimeClient(api_key=real_api_key, config=config) as client:
            with pytest.raises(Exception):  # 应该根据实际 API 调整异常类型
                await client.create_session("invalid-template-id-12345")
    
    @pytest.mark.integration  
    @pytest.mark.asyncio
    @pytest.mark.network
    async def test_invalid_api_key(self):
        """测试无效的 API Key 处理"""
        async with AgentRuntimeClient(api_key="invalid-key-12345") as client:
            with pytest.raises(Exception):  # 应该根据实际 API 调整异常类型
                await client.list_templates()
