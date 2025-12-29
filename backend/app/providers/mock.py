"""
Mock AI Provider
模拟 AI 响应，用于开发和测试

TODO: 实现真实 AI 接口时，创建对应的 Provider 类
例如：
- OpenAIProvider: 对接 OpenAI GPT
- ClaudeProvider: 对接 Anthropic Claude
- LocalLLMProvider: 对接本地大模型
"""
import asyncio
import random

from app.providers.base import AIProvider
from app.schemas.ai import (
    PPTGenerateRequest,
    PPTGenerateResponse,
    ContentGenerateRequest,
    ContentGenerateResponse,
    ContentEditRequest,
    ContentEditResponse,
    ChatRequest,
    ChatResponse,
)


class MockAIProvider(AIProvider):
    """
    Mock AI Provider
    返回预设的模拟响应

    注意：此类仅用于开发测试，生产环境需实现真实 AI Provider
    """

    async def generate_ppt(self, request: PPTGenerateRequest) -> PPTGenerateResponse:
        """
        生成 PPT 内容（Marp Markdown 格式）

        ai/ppt: 生成 PPT 演示文稿
        """
        # 模拟 AI 处理延迟
        await asyncio.sleep(random.uniform(0.5, 1.5))

        content = f"""---
marp: true
theme: default
paginate: true
---

# {request.title}

---

## 课程概述

### 学习目标
- 理解核心概念
- 掌握基本技能
- 能够实际应用

### 课程安排
- 理论讲解
- 实践练习
- 案例分析

---

## 第一部分：基础概念

### 定义与背景
{request.requirements}

### 核心要点
1. 要点一
2. 要点二
3. 要点三

---

## 第二部分：理论框架

### 基本原理
- 原理说明
- 应用场景

### 关键要素
- 要素 A
- 要素 B
- 要素 C

---

## 第三部分：实践应用

### 应用场景
1. 场景一
2. 场景二
3. 场景三

### 最佳实践
- 实践建议
- 注意事项

---

## 互动讨论

### 思考题
1. 问题一？
2. 问题二？
3. 问题三？

---

## 课程总结

### 重点回顾
- 核心概念
- 关键技能
- 应用方法

### 课后作业
- 完成练习
- 准备下次课程

---

# Q&A

欢迎提问！

---

# 谢谢！
"""

        return PPTGenerateResponse(
            content=content,
            title=request.title
        )

    async def generate_content(self, request: ContentGenerateRequest) -> ContentGenerateResponse:
        """
        生成教学资源内容

        ai/content: 生成教学资源
        """
        await asyncio.sleep(random.uniform(0.5, 1.5))

        references_note = ""
        if request.references:
            ref_names = ", ".join([r.name for r in request.references])
            references_note = f"\n\n> 参考资料：{ref_names}\n"

        content = f"""# {request.title}

{references_note}

## 教学资源说明

根据您的要求：{request.requirements}

---

## 一、课程概述

### 1.1 教学目标
- 知识目标：掌握核心概念和原理
- 能力目标：能够独立完成实践任务
- 素养目标：培养思维能力和创新意识

### 1.2 教学重点
- 重点一
- 重点二

### 1.3 教学难点
- 难点一
- 难点二

---

## 二、教学内容

### 2.1 导入环节（5分钟）
通过实际案例引入主题，激发学生兴趣。

### 2.2 核心知识讲解（20分钟）
1. 概念定义
2. 原理分析
3. 应用场景

### 2.3 互动讨论（10分钟）
- 分组讨论
- 案例分析
- 问题解答

### 2.4 实践操作（10分钟）
- 动手练习
- 即时反馈
- 问题解决

---

## 三、课堂总结（5分钟）

### 3.1 知识回顾
- 核心要点梳理
- 重难点强调

### 3.2 作业布置
- 课后练习
- 预习任务

---

## 四、教学反思

### 4.1 教学效果
待课后评估补充。

### 4.2 改进建议
待课后总结补充。

---

## 五、附录资源

### 5.1 推荐阅读
- 资料一
- 资料二

### 5.2 在线资源
- 网站链接
- 视频教程
"""

        return ContentGenerateResponse(
            content=content,
            title=request.title
        )

    async def edit_content(self, request: ContentEditRequest) -> ContentEditResponse:
        """
        AI 二改内容

        ai/edit: 内容修改
        """
        await asyncio.sleep(random.uniform(0.3, 0.8))

        original = request.original_text

        if request.action == "rewrite":
            # 改写：重新组织表达
            edited = f"【改写】{original}（重新组织了表达方式，使内容更加清晰流畅）"
        elif request.action == "expand":
            # 扩写：补充细节和案例
            edited = f"{original}\n\n【扩展内容】\n这里补充了更多的细节说明和实际案例，帮助读者更好地理解上述内容。具体来说：\n1. 首先，从理论角度分析...\n2. 其次，从实践角度来看...\n3. 最后，通过案例验证..."
        else:
            # 自定义修改
            instruction = request.custom_instruction or "按照要求修改"
            edited = f"【根据指令修改：{instruction}】\n\n{original}\n\n（已按照您的要求进行了相应修改）"

        return ContentEditResponse(
            original_text=original,
            edited_text=edited
        )

    async def chat(self, request: ChatRequest) -> ChatResponse:
        """
        聊天对话

        ai/chat: AI 助手对话
        """
        await asyncio.sleep(random.uniform(0.3, 0.8))

        message = request.message.lower()
        context = request.context or ""

        # 基于关键词的简单回复逻辑
        if "学习" in message or "怎么学" in message:
            response = """关于学习方法，我有以下建议：

1. **制定计划**：设定明确的学习目标，分解为小步骤
2. **主动学习**：多思考、多提问、多实践
3. **定期复习**：使用间隔重复法巩固记忆
4. **实践应用**：将知识应用到实际项目中
5. **寻求反馈**：及时发现问题并改进

希望这些建议对你有帮助！"""
        elif "作业" in message or "题目" in message:
            response = """关于作业，我的建议是：

1. **理解题目**：仔细阅读要求，明确目标
2. **分解任务**：将大作业拆分为小任务
3. **查阅资料**：参考课程内容和相关资料
4. **独立完成**：先独立思考，再寻求帮助
5. **检查修正**：完成后仔细检查

如果有具体问题，欢迎继续提问！"""
        elif "考试" in message or "复习" in message:
            response = """考试复习策略：

1. **整理笔记**：梳理知识框架
2. **重点突破**：针对重难点专项练习
3. **真题练习**：熟悉题型和答题技巧
4. **错题分析**：总结错误原因，避免再犯
5. **适度休息**：保证睡眠，保持良好状态

祝你考试顺利！"""
        elif "时间" in message or "计划" in message:
            response = """时间管理建议：

1. **优先级排序**：区分重要和紧急
2. **番茄工作法**：25分钟专注 + 5分钟休息
3. **避免拖延**：设置具体截止时间
4. **减少干扰**：学习时关闭无关通知
5. **定期回顾**：每天/每周总结

合理安排时间，学习效率会更高！"""
        else:
            if context:
                response = f"关于「{context}」课程的问题，我来为你解答：\n\n你提到的「{request.message}」是一个很好的问题。建议你：\n1. 复习相关章节的内容\n2. 尝试做一些练习题\n3. 与同学讨论交流\n\n如果还有疑问，欢迎继续提问！"
            else:
                response = f"感谢你的提问！关于「{request.message}」：\n\n这是一个值得深入探讨的话题。我建议你：\n1. 先了解基础概念\n2. 结合实例理解\n3. 多做练习巩固\n\n有任何其他问题，随时可以问我！"

        return ChatResponse(
            message=response,
            role="assistant"
        )
