# 真实环境测试指南

## 📋 概述

该项目包含三种类型的测试：

1. **单元测试** (`unit/`) - 使用 Mock 数据，快速测试单个组件
2. **集成测试** (`integration/`) - 主要使用 Mock 数据，测试组件间交互
3. **真实环境测试** - 使用真实 PPIO API，验证端到端功能

## 🔧 环境变量配置

### 必需的环境变量

```bash
# 真实的 PPIO API Key（必需）
export PPIO_API_KEY="your-actual-api-key-here"

# 指定测试用的沙箱模板 ID
export PPIO_TEST_TEMPLATE_ID="your-test-template-id"
```

### 可选的环境变量

```bash
# 测试超时时间（秒）
export TEST_TIMEOUT=30

# 调试模式
export TEST_DEBUG=false

# 自定义 API 基础 URL
export TEST_BASE_URL=https://api.ppio.cloud
```

## 🚀 运行真实环境测试

### 方法 1：使用测试脚本

```bash
cd /Users/jason/Documents/work/PPLabs/Platform/agent-sandbox-sdks/sdk-python/tests/agent_runtime

# 设置环境变量
export PPIO_API_KEY="your-actual-api-key"

# 运行所有集成测试（包括真实环境测试）
python run_tests.py --client-integration --verbose

# 或者只运行真实环境测试
poetry run pytest client/integration/test_real_e2e.py -v
```

### 方法 2：使用 pytest 标记

```bash
cd /Users/jason/Documents/work/PPLabs/Platform/agent-sandbox-sdks/sdk-python

# 设置环境变量
export PPIO_API_KEY="your-actual-api-key"

# 只运行需要网络的测试
poetry run pytest tests/agent_runtime/ -m network -v

# 运行真实环境测试
poetry run pytest tests/agent_runtime/client/integration/test_real_e2e.py -v

# 排除慢速测试
poetry run pytest tests/agent_runtime/ -m "network and not slow" -v
```

### 方法 3：临时设置环境变量

```bash
cd /Users/jason/Documents/work/PPLabs/Platform/agent-sandbox-sdks/sdk-python

# 临时设置并运行测试
PPIO_API_KEY="your-key" poetry run pytest tests/agent_runtime/client/integration/test_real_e2e.py -v
```

## 📊 测试标记说明

- `@pytest.mark.integration` - 集成测试
- `@pytest.mark.network` - 需要网络连接的测试
- `@pytest.mark.slow` - 执行时间较长的测试
- `@pytest.mark.asyncio` - 异步测试

## 🎯 测试类型

### 1. 基础功能测试

```python
# 测试模板列表
test_real_template_listing()

# 测试会话创建和调用
test_real_session_creation_and_invocation()

# 测试便利方法
test_real_convenience_method()
```

### 2. 高级功能测试

```python
# 测试流式调用
test_real_streaming_invocation()

# 测试多会话管理
test_real_multiple_sessions()
```

### 3. 错误处理测试

```python
# 测试无效模板ID
test_invalid_template_id()

# 测试无效API Key
test_invalid_api_key()
```

## ⚠️ 注意事项

### 资源消耗
- 真实环境测试会消耗 API 配额
- 建议在开发环境中限制测试频率
- 使用测试专用的 API Key

### 测试数据
- 测试会创建真实的沙箱会话
- 所有会话在测试结束后会自动清理
- 如果测试中断，可能需要手动清理资源

### 网络依赖
- 真实环境测试需要稳定的网络连接
- 测试可能因网络问题失败
- 建议在 CI/CD 中设置重试机制

## 🔍 调试真实环境测试

### 启用详细日志

```bash
# 启用调试输出
TEST_DEBUG=true poetry run pytest tests/agent_runtime/client/integration/test_real_e2e.py -v -s

# 显示完整输出
poetry run pytest tests/agent_runtime/client/integration/test_real_e2e.py -v -s --tb=long
```

### 单独运行特定测试

```bash
# 运行单个测试方法
poetry run pytest tests/agent_runtime/client/integration/test_real_e2e.py::TestRealEnvironmentE2E::test_real_template_listing -v -s
```

## 📝 最佳实践

### 开发阶段
1. 主要使用 Mock 测试进行快速验证
2. 定期运行真实环境测试验证集成
3. 在 PR 前运行完整的真实环境测试

### CI/CD 集成
1. 在测试环境中设置专用 API Key
2. 使用环境变量安全地传递凭证
3. 设置合理的超时和重试机制

### 生产部署前
1. 运行完整的真实环境测试套件
2. 验证所有关键路径
3. 检查性能和资源使用情况

## 🛠️ 故障排除

### 常见错误

1. **PPIO_API_KEY not set**
   ```bash
   export PPIO_API_KEY="your-key"
   ```

2. **模板不可用**
   ```bash
   export PPIO_TEST_TEMPLATE_ID="valid-template-id"
   ```

3. **网络连接错误**
   - 检查网络连接
   - 验证 API 端点可访问性

4. **API 配额限制**
   - 检查 API 配额使用情况
   - 减少并发测试数量

## 🔗 相关文件

- `conftest.py` - 测试配置和 fixtures
- `test_real_e2e.py` - 真实环境端到端测试
- `run_tests.py` - 测试执行脚本
- 现有的 `test_end_to_end.py` - 包含部分真实环境测试
