# 项目重构说明

## 重构概述

原来的 `app.py` 文件包含了所有的路由、业务逻辑和配置，不符合标准的Flask项目架构规范。现在已经将代码重构为更规范的项目结构，采用模块化设计和工厂模式。

## 新的项目结构

```
xgo-blockly-server/
├── app.py                 # 主应用文件（工厂模式）
├── config.py              # 配置管理
├── requirements.txt       # Python依赖
├── services/              # 业务逻辑层
│   ├── __init__.py
│   └── code_executor.py   # 代码执行服务
├── routes/                # 路由处理层
│   ├── __init__.py
│   ├── api.py            # API路由
│   └── static.py         # 静态文件路由
└── dist/                 # Vue3构建产物
```

## 模块说明

### 1. `config.py` - 配置管理
- 统一管理所有配置项
- 支持不同环境配置（开发/生产/测试）
- MIME类型配置管理

### 2. `services/code_executor.py` - 业务逻辑层
- `CodeExecutor` 类：负责Python代码执行
- `ExecutionManager` 类：管理多个执行任务
- 日志管理和任务调度

### 3. `routes/api.py` - API路由处理
- `/api/run-code` - Python代码执行接口
- `/api/health` - 健康检查接口
- 使用Flask Blueprint进行模块化管理

### 4. `routes/static.py` - 静态文件路由
- Vue3应用托管
- 静态资源服务
- MIME类型处理

### 5. `app.py` - 应用工厂
- 采用工厂模式创建Flask应用
- 蓝图注册
- 全局错误处理

## 重构优势

### 1. **代码组织更清晰**
- 按功能模块分离代码
- 单一职责原则
- 便于维护和扩展

### 2. **更好的可测试性**
- 业务逻辑与路由分离
- 依赖注入更容易
- 单元测试更方便

### 3. **配置管理标准化**
- 环境配置分离
- 配置项集中管理
- 支持多环境部署

### 4. **扩展性更强**
- 新增功能只需添加新的蓝图
- 业务逻辑模块化
- 支持插件式架构

## 兼容性保证

**重要：所有原有的接口和功能保持不变**

- ✅ `/api/run-code` - Python代码执行（SSE响应）
- ✅ `/api/health` - 健康检查
- ✅ `/` - Vue3应用主页
- ✅ `/<path>` - 静态资源文件
- ✅ 404错误处理（Vue路由支持）
- ✅ CORS跨域支持
- ✅ MIME类型配置

## 启动方式

启动方式完全保持不变：

```bash
cd xgo-blockly-server
python app.py
```

## 后续开发建议

1. **新增API接口**：在 `routes/` 目录下创建新的路由文件
2. **新增业务逻辑**：在 `services/` 目录下创建新的服务类
3. **配置修改**：统一在 `config.py` 中管理
4. **测试开发**：为每个模块编写单独的单元测试

这样的架构更符合Flask最佳实践，便于团队开发和项目维护。