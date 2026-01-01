# RAG 系统测试问题

## 测试目的

验证双索引 RAG 系统的各项功能：
1. 智能路由（全局问题 vs 细节问题）
2. 块级摘要检索
3. 原文索引检索
4. 引用过滤与编号映射
5. 段落边界分块

---

## 一、全局问题（预期路由到 Summary Index）

这类问题需要对文档整体内容有概括性理解。

### 问题1
**问题**: 这篇文档主要讲什么？

**预期路由**: GLOBAL → Summary Index

**预期回答要点**:
- 智能教学系统技术文档
- 面向高校的在线学习平台
- 包含课程管理、AI辅助学习等功能

---

### 问题2
**问题**: 总结一下这个系统的核心功能有哪些？

**预期路由**: GLOBAL → Summary Index

**预期回答要点**:
- 课程管理
- 在线考试
- AI学习助手

---

### 问题3
**问题**: 概括一下这个项目的整体架构是怎样的？

**预期路由**: GLOBAL → Summary Index

**预期回答要点**:
- 前后端分离架构
- 前端 React + TypeScript
- 后端 Python FastAPI
- AI模块 RAG架构

---

## 二、细节问题（预期路由到 Detail Index）

这类问题需要从原文中检索具体信息。

### 问题4
**问题**: 张三在项目中担任什么职位？

**预期路由**: DETAIL → Detail Index

**预期回答**:
- 张三担任技术负责人

**验证引用过滤**:
- 应该只返回包含"张三"相关内容的来源
- 引用编号应该正确映射

---

### 问题5
**问题**: 考试系统支持哪些题型？

**预期路由**: DETAIL → Detail Index

**预期回答要点**:
- 单选题（4个选项）
- 多选题（4-6个选项）
- 判断题
- 填空题
- 简答题

---

### 问题6
**问题**: 用户表（users）有哪些字段？

**预期路由**: DETAIL → Detail Index

**预期回答要点**:
- id (UUID)
- username (VARCHAR)
- email (VARCHAR)
- password_hash (VARCHAR)
- role (ENUM)
- created_at (TIMESTAMP)

---

### 问题7
**问题**: 登录接口的路径是什么？请求体需要哪些字段？

**预期路由**: DETAIL → Detail Index

**预期回答要点**:
- 路径：POST /api/auth/login
- 请求体：username, password

---

### 问题8
**问题**: 如何重置用户密码？

**预期路由**: DETAIL → Detail Index

**预期回答要点**:
- 管理员在后台管理系统中操作
- 选择用户点击"重置密码"
- 系统发送重置链接到用户邮箱

---

### 问题9
**问题**: 后端配置文件需要配置哪些环境变量？

**预期路由**: DETAIL → Detail Index

**预期回答要点**:
- DATABASE_URL
- REDIS_URL
- OPENAI_API_KEY
- JWT_SECRET

---

### 问题10
**问题**: 前端项目的目录结构是怎样的？

**预期路由**: DETAIL → Detail Index

**预期回答要点**:
- src/components
- src/pages
- src/stores
- src/hooks
- src/utils
- src/api

---

## 三、边界测试问题

### 问题11（模糊问题）
**问题**: 这个系统用了什么技术？

**说明**: 这个问题可能被路由到任一索引，两者都应能回答

**预期回答要点**:
- React、TypeScript、FastAPI、PostgreSQL、ChromaDB等

---

### 问题12（无相关内容）
**问题**: 这个系统支持移动端APP吗？

**预期行为**:
- 检索到的内容相关度较低
- AI应诚实回答"文档中未提及相关信息"

---

## 四、引用过滤测试

### 测试场景

假设检索到3个来源：
- [1] 项目概述部分
- [2] 系统架构部分
- [3] 数据库设计部分

如果LLM只引用了 [2] 和 [3]：
- 过滤后应只返回2个来源
- [2] 应映射为 [1]
- [3] 应映射为 [2]
- 回答中的引用编号应同步更新

### 验证方法
```python
# 检查返回的 sources 数量
assert len(response.sources) == 被引用的数量

# 检查回答中的引用编号是否连续从1开始
import re
citations = re.findall(r'\[(\d+)\]', response.message)
unique_citations = sorted(set(int(c) for c in citations))
assert unique_citations == list(range(1, len(response.sources) + 1))
```

---

## 五、分块边界测试

### 测试目标
验证分块是否保持段落完整，不会截断段落中间

### 检查项
1. 上传测试文档到知识库
2. 查看日志中的分块结果
3. 确认每个块都以完整段落开始和结束
4. 确认超长段落按句子分割，而非硬截断

### 预期日志输出示例
```
[CHUNKER] 【分块 0】
[CHUNKER]   小块(298字):
[CHUNKER]   # 智能教学系统技术文档
[CHUNKER]
[CHUNKER]   ## 1. 项目概述
[CHUNKER]
[CHUNKER]   智能教学系统是一款面向高校的在线学习平台...
```

---

## 六、测试脚本

```python
import httpx
import asyncio

BASE_URL = "http://localhost:8001"
HEADERS = {"x-user-id": "test-user"}

async def test_rag():
    async with httpx.AsyncClient() as client:
        # 1. 先上传测试文档
        with open("test_document.md", "rb") as f:
            content = f.read()

        import base64
        content_b64 = base64.b64encode(content).decode()

        resp = await client.post(
            f"{BASE_URL}/knowledge/add",
            json={
                "name": "test_document.md",
                "content_base64": content_b64,
                "source_type": "personal"
            },
            headers=HEADERS
        )
        result = resp.json()
        print(f"上传结果: {result}")
        knowledge_id = result.get("knowledge_id")

        # 2. 测试全局问题
        resp = await client.post(
            f"{BASE_URL}/chat",
            json={
                "message": "这篇文档主要讲什么？",
                "knowledge_ids": [knowledge_id]
            },
            headers=HEADERS
        )
        result = resp.json()
        print(f"\n全局问题回答:")
        print(f"  路由: {result.get('retrieval_info', {}).get('index_type')}")
        print(f"  回答: {result.get('message')[:200]}...")
        print(f"  来源数: {len(result.get('sources', []))}")

        # 3. 测试细节问题
        resp = await client.post(
            f"{BASE_URL}/chat",
            json={
                "message": "张三在项目中担任什么职位？",
                "knowledge_ids": [knowledge_id]
            },
            headers=HEADERS
        )
        result = resp.json()
        print(f"\n细节问题回答:")
        print(f"  路由: {result.get('retrieval_info', {}).get('index_type')}")
        print(f"  回答: {result.get('message')}")
        print(f"  来源数: {len(result.get('sources', []))}")

        # 验证引用过滤
        import re
        citations = re.findall(r'\[(\d+)\]', result.get('message', ''))
        sources_count = len(result.get('sources', []))
        print(f"  引用编号: {citations}")
        print(f"  验证: 引用数={len(set(citations))}, 来源数={sources_count}")

if __name__ == "__main__":
    asyncio.run(test_rag())
```

---

## 七、预期测试结果

| 问题类型 | 路由结果 | 引用过滤 | 编号映射 |
|---------|---------|---------|---------|
| 全局问题 | Summary Index | ✓ | ✓ |
| 细节问题 | Detail Index | ✓ | ✓ |
| 模糊问题 | 任一索引 | ✓ | ✓ |
| 无关问题 | Detail Index | 可能无引用 | N/A |
