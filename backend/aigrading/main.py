"""
AI 作业评分模块 - 使用 LangChain 框架
根据教师设定的评分规则文本，对学生提交的作业内容进行智能评分
"""
import os
import sys

# 强制使用 Pydantic v2，避免 Python 3.12 兼容性问题
os.environ["PYDANTIC_V2_MODE"] = "1"

import uvicorn
from typing import Optional
from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

# 加载后端主目录的环境变量
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

# 获取当前模块目录
MODULE_DIR = os.path.dirname(__file__)

app = FastAPI(title="AI Grading Assistant", version="1.0.0")

# 允许跨域
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== 数据模型 ====================

class GradeRequest(BaseModel):
    """评分请求"""
    student_content: str       # 学生提交的文本内容
    grading_criteria: str      # 教师设定的评分规则文本
    homework_title: str = ""   # 作业标题（可选上下文）
    homework_description: str = ""  # 作业描述（可选上下文）

class GradeResponse(BaseModel):
    """评分响应"""
    success: bool
    score: int = 0           # 0-100 分
    feedback: str = ""       # AI 生成的评语
    error: Optional[str] = None

# ==================== 评分系统提示词 ====================

GRADING_SYSTEM_PROMPT = """你是一位专业的教师助手，负责根据评分规则对学生作业进行客观公正的评分。

评分原则：
1. 严格按照教师提供的评分规则进行评分
2. 评分范围为 0-100 分，分数应该合理分布
3. 给出详细、具体、建设性的评语
4. 评语应该指出优点和可改进之处
5. 语气要友好、鼓励性，同时保持专业

评分参考：
- 90-100分：优秀，完成度高，超出预期
- 80-89分：良好，基本完成要求，有一定亮点
- 70-79分：中等，完成基本要求，但有明显不足
- 60-69分：及格，勉强达到最低要求
- 60分以下：不及格，未能达到基本要求

请严格按照以下 JSON 格式输出，不要有其他内容：
{
    "score": <0-100的整数>,
    "feedback": "<详细的评语>"
}"""

# ==================== 核心功能 ====================

def get_llm(api_key: str = None):
    """获取 LangChain LLM 客户端 (OpenAI GPT-4o)"""
    key = api_key or os.getenv("OPENAI_API_KEY")
    if not key:
        raise HTTPException(400, "OpenAI API Key not configured")

    # 使用配置的模型或默认 gpt-4o
    model = os.getenv("AIGRADING_MODEL") or os.getenv("AIWRITING_MODEL") or "gpt-4o"
    base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")

    return ChatOpenAI(
        base_url=base_url,
        api_key=key,
        model=model,
        temperature=0.3,  # 评分任务使用较低温度，保证稳定性
    )

def grade_submission(
    llm: ChatOpenAI,
    student_content: str,
    grading_criteria: str,
    homework_title: str = "",
    homework_description: str = ""
) -> dict:
    """使用 LangChain 进行作业评分"""
    
    # 构建用户提示
    user_prompt_parts = []
    
    if homework_title:
        user_prompt_parts.append(f"【作业标题】\n{homework_title}")
    
    if homework_description:
        user_prompt_parts.append(f"【作业要求】\n{homework_description}")
    
    user_prompt_parts.append(f"【评分规则】\n{grading_criteria}")
    user_prompt_parts.append(f"【学生作业内容】\n{student_content}")
    
    user_prompt = "\n\n".join(user_prompt_parts)
    user_prompt += "\n\n请根据以上评分规则，对学生作业进行评分，并按照 JSON 格式输出结果。"

    try:
        messages = [
            SystemMessage(content=GRADING_SYSTEM_PROMPT),
            HumanMessage(content=user_prompt)
        ]

        response = llm.invoke(messages)
        response_text = response.content.strip()
        
        # 解析 JSON 响应
        import json
        
        # 尝试提取 JSON 部分（处理可能的额外文本）
        if "```json" in response_text:
            start = response_text.find("```json") + 7
            end = response_text.find("```", start)
            response_text = response_text[start:end].strip()
        elif "```" in response_text:
            start = response_text.find("```") + 3
            end = response_text.find("```", start)
            response_text = response_text[start:end].strip()
        
        # 找到 JSON 对象的开始和结束
        json_start = response_text.find("{")
        json_end = response_text.rfind("}") + 1
        if json_start != -1 and json_end > json_start:
            response_text = response_text[json_start:json_end]
        
        result = json.loads(response_text)
        
        score = int(result.get("score", 0))
        # 确保分数在有效范围内
        score = max(0, min(100, score))
        
        feedback = result.get("feedback", "评分完成")
        
        return {
            "score": score,
            "feedback": feedback
        }

    except json.JSONDecodeError as e:
        print(f"JSON parsing error: {e}")
        print(f"Response text: {response_text}")
        # 降级处理：返回默认评分
        return {
            "score": 70,
            "feedback": f"AI 评分解析异常，请教师手动调整。原始响应：{response_text[:200]}"
        }
    except Exception as e:
        print(f"LLM grading error: {e}")
        raise HTTPException(500, f"评分失败: {str(e)}")

# ==================== API 接口 ====================

@app.get("/")
def health_check():
    """健康检查"""
    return {"status": "running", "service": "AI Grading Assistant"}

@app.post("/grade", response_model=GradeResponse)
async def grade_homework(
    req: GradeRequest,
    x_api_key: Optional[str] = Header(None, alias="x-api-key")
):
    """
    AI 作业评分接口
    
    - student_content: 学生提交的文本内容
    - grading_criteria: 教师设定的评分规则文本
    - homework_title: 作业标题（可选）
    - homework_description: 作业描述（可选）
    
    返回：
    - score: 0-100 的评分
    - feedback: AI 生成的评语
    """
    print("=== /grade API called ===", flush=True)
    print(f"Request: homework_title={req.homework_title}", flush=True)
    
    try:
        if not req.student_content.strip():
            return GradeResponse(success=False, error="学生作业内容不能为空")

        if not req.grading_criteria.strip():
            return GradeResponse(success=False, error="评分规则不能为空")

        llm = get_llm(x_api_key)

        print(f"Grading submission for: {req.homework_title}", flush=True)
        result = grade_submission(
            llm,
            req.student_content,
            req.grading_criteria,
            req.homework_title,
            req.homework_description
        )

        return GradeResponse(
            success=True,
            score=result["score"],
            feedback=result["feedback"]
        )

    except HTTPException as e:
        return GradeResponse(success=False, error=e.detail)
    except Exception as e:
        print(f"Grade error: {e}")
        return GradeResponse(success=False, error=str(e))


def start():
    """启动服务"""
    port = int(os.getenv("AIGRADING_PORT", 8005))
    print(f"🚀 Starting AI Grading Assistant on http://localhost:{port}")
    uvicorn.run("backend.aigrading.main:app", host="0.0.0.0", port=port, reload=True)


if __name__ == "__main__":
    start()
