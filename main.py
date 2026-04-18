import os
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Load environment variables
load_dotenv()

app = FastAPI(title="SNS Post Consultation App")

# Model Input Schema
class EvaluationRequest(BaseModel):
    text: str

# System Prompt
SYSTEM_PROMPT = """
あなたはSNS投稿のアドバイザーです。ユーザーが入力した文章がSNSでどのように受け取られるかを慎重に評価してください。

評価軸：
- 攻撃性（0〜5）: 他者を攻撃したり、不快にさせる要素が含まれていないか
- 特定可能性（0〜5）: 個人や場所、所属などが特定されるリスクがないか
- 誤解されやすさ（0〜5）: 文脈が不足していたり、意図しない解釈をされる恐れがないか

改善案も提示してください。

レスポンス形式：
この文章がSNSでどう受け取られるか評価して：
- 攻撃性（0〜5）: [スコア]
- 特定可能性（0〜5）: [スコア]
- 誤解されやすさ（0〜5）: [スコア]

- 改善案:
[改善案の記述]
"""

def get_llm():
    llm_type = os.getenv("LLM_TYPE", "openai").lower()
    
    if llm_type == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY is not set")
        return ChatOpenAI(
            model=os.getenv("OPENAI_MODEL", "gpt-4o"),
            api_key=api_key
        )
    elif llm_type == "ollama":
        return ChatOllama(
            model=os.getenv("OLLAMA_MODEL", "llama3"),
            base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        )
    else:
        raise ValueError(f"Unsupported LLM_TYPE: {llm_type}")

@app.post("/evaluate")
async def evaluate_post(request: EvaluationRequest):
    try:
        llm = get_llm()
        prompt = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT),
            ("user", "{text}")
        ])
        
        chain = prompt | llm | StrOutputParser()
        
        response = await chain.ainvoke({"text": request.text})
        return {"evaluation": response}
    except Exception as e:
        print(f"Error during evaluation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Mount static files
app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
