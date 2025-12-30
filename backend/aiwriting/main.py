"""
AI 写作模块 - 使用 LangChain 框架
提供课程资源的 AI 生成和二次改写功能
"""
import os
import io
import base64
import uuid
import uvicorn
from typing import Optional, List
from fastapi import FastAPI, UploadFile, File, HTTPException, Header, Request, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, SystemMessage

# 加载后端主目录的环境变量
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

# 获取当前模块目录
MODULE_DIR = os.path.dirname(__file__)

app = FastAPI(title="AI Writing Assistant", version="1.0.0")

# 允许跨域
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== 数据模型 ====================

class GenerateRequest(BaseModel):
    title: str
    requirements: str
    resource_type: str = "lesson_plan"  # 资源类型
    reference_contents: List[str] = []
    reference_names: List[str] = []

class GenerateResponse(BaseModel):
    success: bool
    content: str = ""
    error: Optional[str] = None

class RewriteRequest(BaseModel):
    selected_text: str
    rewrite_type: str  # 'rewrite', 'expand', 'custom'
    custom_requirement: Optional[str] = None
    context: Optional[str] = None

class RewriteResponse(BaseModel):
    success: bool
    content: str = ""
    error: Optional[str] = None

class ParseFileRequest(BaseModel):
    filename: str
    content_base64: str

class ParseFileResponse(BaseModel):
    success: bool
    text_content: str = ""
    error: Optional[str] = None

# ==================== 资源类型模板 ====================

RESOURCE_TEMPLATES = {
    "lesson_plan": {
        "name": "教案",
        "system_prompt": """你是一位专业的教育内容创作专家，擅长创作高质量的教案。
请根据用户提供的标题、要求和参考资料，生成一份完整的教案文档。

输出要求：
1. 使用 Markdown 格式
2. 结构清晰，包含：课程概述、教学目标、教学重点难点、教学过程（导入、新授、练习、总结）、板书设计、教学反思等部分
3. 内容详实，逻辑性强
4. 语言专业但易于理解
5. 如果提供了参考资料，请结合参考资料的内容进行创作
6. 包含实际可操作的教学活动和互动环节
7. 直接输出教案内容，不要添加额外说明"""
    },
    "exercises": {
        "name": "习题/试卷",
        "system_prompt": """你是一位专业的教育测评专家，擅长设计高质量的习题和试卷。
请根据用户提供的标题、要求和参考资料，生成一套完整的习题或试卷。

输出要求：
1. 使用 Markdown 格式
2. 题目类型多样化，可包含：选择题、填空题、判断题、简答题、计算题、论述题等
3. 每道题目清晰明确，难度适中
4. 提供完整的参考答案和评分标准
5. 如果提供了参考资料，请结合参考资料的内容出题
6. 题目数量和难度根据用户要求调整
7. 直接输出习题内容，不要添加额外说明"""
    },
    "courseware": {
        "name": "课件大纲",
        "system_prompt": """你是一位专业的课件设计专家，擅长设计清晰的课件大纲和内容结构。
请根据用户提供的标题、要求和参考资料，生成一份完整的课件大纲。

输出要求：
1. 使用 Markdown 格式
2. 结构层次分明，适合制作PPT课件
3. 每页/每节的要点清晰，包含关键内容和讲解提示
4. 如果提供了参考资料，请结合参考资料的内容进行设计
5. 包含适当的案例、图表建议
6. 直接输出课件大纲内容，不要添加额外说明"""
    },
    "summary": {
        "name": "知识总结",
        "system_prompt": """你是一位专业的教育内容整理专家，擅长整理和总结知识点。
请根据用户提供的标题、要求和参考资料，生成一份完整的知识总结。

输出要求：
1. 使用 Markdown 格式
2. 知识点条理清晰，层次分明
3. 重点内容突出标注
4. 如果提供了参考资料，请结合参考资料的内容进行整理
5. 适当使用表格、列表等形式增强可读性
6. 直接输出知识总结内容，不要添加额外说明"""
    },
    "activity": {
        "name": "教学活动设计",
        "system_prompt": """你是一位专业的教学活动设计专家，擅长设计富有创意和互动性的教学活动。
请根据用户提供的标题、要求和参考资料，设计一套完整的教学活动方案。

输出要求：
1. 使用 Markdown 格式
2. 活动目标明确，流程清晰
3. 包含活动准备、实施步骤、时间安排、注意事项等
4. 如果提供了参考资料，请结合参考资料的内容进行设计
5. 活动具有可操作性和趣味性
6. 直接输出活动设计内容，不要添加额外说明"""
    },
    "custom": {
        "name": "自定义",
        "system_prompt": """你是一位专业的教育内容创作专家。
请根据用户提供的标题、要求和参考资料，生成相应的教学内容。

输出要求：
1. 使用 Markdown 格式
2. 严格按照用户的要求进行创作
3. 内容详实，逻辑性强
4. 如果提供了参考资料，请结合参考资料的内容进行创作
5. 直接输出内容，不要添加额外说明"""
    }
}

# ==================== 核心功能 ====================

def get_llm(api_key: str = None):
    """获取 LangChain LLM 客户端 (OpenAI GPT-4o)"""
    key = api_key or os.getenv("OPENAI_API_KEY")
    if not key:
        raise HTTPException(400, "OpenAI API Key not configured")

    # 使用配置的模型或默认 gpt-4o
    model = os.getenv("AIWRITING_MODEL") or "gpt-4o"
    base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")

    return ChatOpenAI(
        base_url=base_url,
        api_key=key,
        model=model,
        temperature=0.7,
    )

def parse_file_content(filename: str, content_bytes: bytes) -> str:
    """解析上传文件的内容"""
    ext = filename.lower().split('.')[-1]

    try:
        if ext == 'txt' or ext == 'md':
            # 文本文件直接解码
            return content_bytes.decode('utf-8', errors='ignore')

        elif ext == 'pdf':
            # PDF 文件解析
            try:
                from pypdf import PdfReader
                pdf_reader = PdfReader(io.BytesIO(content_bytes))
                text_parts = []
                for page in pdf_reader.pages:
                    text = page.extract_text()
                    if text:
                        text_parts.append(text)
                return '\n\n'.join(text_parts)
            except Exception as e:
                print(f"PDF parsing error: {e}")
                return f"[PDF文件解析失败: {filename}]"

        elif ext == 'docx':
            # Word 文档解析
            try:
                from docx import Document
                doc = Document(io.BytesIO(content_bytes))
                paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
                return '\n\n'.join(paragraphs)
            except Exception as e:
                print(f"DOCX parsing error: {e}")
                return f"[Word文档解析失败: {filename}]"

        elif ext == 'doc':
            # 旧版 Word 文档
            return f"[不支持旧版 .doc 格式，请转换为 .docx: {filename}]"

        else:
            # 尝试作为文本解析
            try:
                return content_bytes.decode('utf-8', errors='ignore')
            except:
                return f"[无法解析文件: {filename}]"

    except Exception as e:
        print(f"File parsing error: {e}")
        return f"[文件解析错误: {filename}]"

def generate_teaching_resource(
    llm: ChatOpenAI,
    title: str,
    requirements: str,
    resource_type: str,
    references: List[dict]
) -> str:
    """使用 LangChain 生成教学资源"""

    # 构建参考资料部分
    reference_text = ""
    if references:
        reference_parts = []
        for ref in references:
            name = ref.get('name', '未命名文件')
            content = ref.get('content', '')[:2000]  # 限制每个文件内容长度
            reference_parts.append(f"【{name}】\n{content}")
            # 打印解析后的参考资料预览
            preview = content[:200] if content else "[空内容]"
            print(f"[AI Writing] 参考资料 '{name}': {preview}...", flush=True)
        reference_text = "\n\n---\n\n".join(reference_parts)
    else:
        print("[AI Writing] 无参考资料", flush=True)

    # 获取对应类型的模板
    template = RESOURCE_TEMPLATES.get(resource_type, RESOURCE_TEMPLATES["custom"])
    system_prompt = template["system_prompt"]

    print(f"[AI Writing] Using template: {template['name']} for resource_type: {resource_type}", flush=True)

    user_prompt = f"""请为我创作以下内容：

【标题】
{title}

【具体要求】
{requirements}

"""

    if reference_text:
        user_prompt += f"""【参考资料】
以下是提供的参考资料，请结合这些内容进行创作：

{reference_text}
"""

    try:
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]

        response = llm.invoke(messages)
        return response.content

    except Exception as e:
        print(f"LLM generation error: {e}")
        raise HTTPException(500, f"生成失败: {str(e)}")

def rewrite_text(
    llm: ChatOpenAI,
    selected_text: str,
    rewrite_type: str,
    custom_requirement: Optional[str] = None,
    context: Optional[str] = None
) -> str:
    """使用 LangChain 改写文本"""

    system_prompts = {
        'rewrite': """你是一位文字润色专家。请对用户选中的文本进行改写优化。
要求：
1. 保持原意不变
2. 使表达更加流畅、专业
3. 提高可读性
4. 直接输出改写后的内容，不要添加解释""",

        'expand': """你是一位教育内容专家。请对用户选中的文本进行扩写。
要求：
1. 保持原有主题和方向
2. 增加更多细节、例子和解释
3. 扩展后内容约为原文的2-3倍
4. 保持语言风格一致
5. 直接输出扩写后的内容，不要添加解释""",

        'custom': f"""你是一位专业的文字编辑。请按照用户的具体要求修改文本。
用户要求：{custom_requirement}

请直接输出修改后的内容，不要添加解释。"""
    }

    system_prompt = system_prompts.get(rewrite_type, system_prompts['rewrite'])

    user_prompt = f"请处理以下文本：\n\n{selected_text}"

    if context:
        user_prompt = f"【上下文参考】\n{context[:500]}\n\n【需要处理的文本】\n{selected_text}"

    try:
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]

        response = llm.invoke(messages)
        return response.content

    except Exception as e:
        print(f"LLM rewrite error: {e}")
        raise HTTPException(500, f"改写失败: {str(e)}")

# ==================== API 接口 ====================

@app.get("/")
def health_check():
    return {"status": "running", "service": "AI Writing Assistant"}

@app.post("/parse", response_model=ParseFileResponse)
async def parse_uploaded_file(req: ParseFileRequest):
    """解析上传的文件内容"""
    try:
        # 解码 base64 内容
        if ',' in req.content_base64:
            content_base64 = req.content_base64.split(',')[1]
        else:
            content_base64 = req.content_base64

        content_bytes = base64.b64decode(content_base64)
        text_content = parse_file_content(req.filename, content_bytes)

        return ParseFileResponse(success=True, text_content=text_content)

    except Exception as e:
        print(f"Parse file error: {e}")
        return ParseFileResponse(success=False, error=str(e))

@app.post("/generate", response_model=GenerateResponse)
async def generate_resource(
    req: GenerateRequest,
    x_api_key: Optional[str] = Header(None, alias="x-api-key")
):
    """
    生成教学资源
    - title: 资源标题
    - requirements: 生成要求/提示词
    - reference_contents: 参考资料内容列表
    - reference_names: 参考资料文件名列表
    """
    print("=== /generate API called ===", flush=True)
    print(f"Request body: title={req.title}, resource_type={req.resource_type}", flush=True)
    try:
        if not req.title.strip():
            return GenerateResponse(success=False, error="请输入资源标题")

        if not req.requirements.strip():
            return GenerateResponse(success=False, error="请输入生成要求")

        llm = get_llm(x_api_key)

        # 组合参考资料
        references = []
        for i, content in enumerate(req.reference_contents):
            name = req.reference_names[i] if i < len(req.reference_names) else f"参考资料{i+1}"
            references.append({"name": name, "content": content})

        print(f"Generating resource: {req.title} (type: {req.resource_type})", flush=True)
        content = generate_teaching_resource(llm, req.title, req.requirements, req.resource_type, references)

        return GenerateResponse(success=True, content=content)

    except HTTPException as e:
        return GenerateResponse(success=False, error=e.detail)
    except Exception as e:
        print(f"Generate error: {e}")
        return GenerateResponse(success=False, error=str(e))

@app.post("/rewrite", response_model=RewriteResponse)
async def rewrite_content(
    req: RewriteRequest,
    x_api_key: Optional[str] = Header(None, alias="x-api-key")
):
    """
    改写/扩写文本
    - selected_text: 选中的文本
    - rewrite_type: 改写类型 ('rewrite', 'expand', 'custom')
    - custom_requirement: 自定义要求（当 type 为 'custom' 时）
    - context: 上下文（可选）
    """
    try:
        if not req.selected_text.strip():
            return RewriteResponse(success=False, error="请选择要修改的文本")

        llm = get_llm(x_api_key)

        print(f"Rewriting text ({req.rewrite_type}): {req.selected_text[:50]}...")
        content = rewrite_text(
            llm,
            req.selected_text,
            req.rewrite_type,
            req.custom_requirement,
            req.context
        )

        return RewriteResponse(success=True, content=content)

    except HTTPException as e:
        return RewriteResponse(success=False, error=e.detail)
    except Exception as e:
        print(f"Rewrite error: {e}")
        return RewriteResponse(success=False, error=str(e))


def start():
    """启动服务"""
    port = int(os.getenv("AIWRITING_PORT", 8003))
    print(f"🚀 Starting AI Writing Assistant on http://localhost:{port}")
    uvicorn.run("backend.aiwriting.main:app", host="0.0.0.0", port=port, reload=True)


if __name__ == "__main__":
    start()
