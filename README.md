🧠 Sustainet Inc. - 永續資訊對抗模擬器

Sustainet Inc. 是一款以永續議題為主題的策略模擬遊戲，探索假訊息如何影響人們對氣候、能源與社會正義等永續議題的認知。玩家將扮演資訊守門人角色，善用查核工具與社群觀察力，與 AI 假訊息操縱者對抗，在動態社群環境中維持公眾信任與資訊透明度。

📦 技術架構總覽

本專案採用 Clean Architecture，並結合 Agno 作為 Agent 管理框架。

API (FastAPI)
└── Application Layer (Use Cases, DTOs)
    └── Domain Layer (Entities, Logic)
        └── Infrastructure Layer (Agno Agent, DB, Prompt, Tools)

📁 專案目錄結構

src/
├── api/                        # FastAPI endpoints
│   └── routes/                # 所有路由
├── application/               # Use Case、DTO
│   ├── services/              # 遊戲服務邏輯（使用工具、提交行動等）
│   └── dto/                   # Pydantic 輸入 / 輸出模型
├── domain/                    # 核心業務邏輯
│   ├── models/                # Entity / ValueObject
│   └── logic/                 # 規則計算器、得分邏輯、工具影響
├── infrastructure/            # GPT/Agno 整合、資料庫、新聞、儲存
│   ├── agents/                # 使用 Agno 創建的 Agent 工廠與實體
│   ├── database/              # 模擬資料庫與 Repository
│   ├── news/                  # 新聞載入器（假新聞拼接來源）
├── utils/                     # 公用工具（如情緒分數、平台偵測器）
├── config/                    # Prompt 與遊戲參數設定
├── tests/                     # 單元與整合測試
└── main.py                    # FastAPI app 入口

📚 遊戲流程概覽

假訊息方（AI Agent）發布訊息（真/假）。

玩家獲得訊息，判斷與使用工具查核。

玩家可選擇查核、澄清、附和或忽略。

Game Master Agent 模擬群眾反應並評分。

雙方回合交替，直到遊戲結束。

🔌 主要依賴與框架

技術

用途

FastAPI

Web 框架 / REST API

Agno

Agent 行為建模與推理

OpenAI API

GPT 模型（生成新聞、澄清、判定）

PostgreSQL

儲存遊戲狀態與資料

Uvicorn

非同步應用伺服器

Pydantic

資料結構驗證與轉換

🧰 套件安裝與環境設置（使用 uv）

# 安裝 uv
pip install uv

# 建立虛擬環境並安裝依賴
uv venv
uv pip install -r requirements.txt

如使用 uv 設定依賴：

uv pip freeze > requirements.txt

🚀 啟動方式

uvicorn main:app --reload

前往：http://localhost:8000/docs 查看 Swagger 文件。

🤖 Agno Agent 整合說明

Agno 會作為下列角色執行：

FakeNewsAgent：接收新聞來源，生成偏頗或拼貼式訊息。

GameMasterAgent：根據玩家與 AI 的行為模擬社群反應，給出觸及率與信任分數。

ClarifierAgent：協助玩家撰寫澄清內容。

每個 Agent 的 prompt 與初始化邏輯放於：infrastructure/agents/，並由 AgentFactory 根據 DB 設定進行建構。

Agno Docs: https://docs.agno.com/introduction

📡 API 範例說明：使用工具（Use Tool）

此範例展示一條從 API 到 Infrastructure 的完整流程，符合 Clean Architecture 設計。

🧪 功能：玩家使用工具（如 Podcast 頻道）以提升信任度

1. API Layer (/api/routes/tools.py)

@router.post("/tools/use")
def use_tool(request: UseToolRequest):
    return use_tool_service(request)

職責：接收 HTTP 請求並轉交 Use Case。

2. DTO (application/dto/use_tool_dto.py)

class UseToolRequest(BaseModel):
    game_id: str
    tool_name: str

class UseToolResponse(BaseModel):
    trust_score: int
    message: str

職責：封裝輸入與輸出資料結構，提供應用層使用。

3. Application Service (application/services/use_tool.py)

from domain.logic.tool_effect import apply_tool_effect
from infrastructure.repositories.game_repo import GameRepository

def use_tool_service(request: UseToolRequest) -> UseToolResponse:
    game = GameRepository.get(request.game_id)
    updated_game = apply_tool_effect(game, request.tool_name)
    GameRepository.save(updated_game)
    return UseToolResponse(trust_score=updated_game.trust_score, message=f"Used {request.tool_name}.")

職責：處理流程邏輯、呼叫核心邏輯並與 Repository 溝通。

4. Domain Layer - Model (domain/models/game.py)

@dataclass
class GameState:
    id: str
    trust_score: int
    tools_used: List[Tool]

職責：描述遊戲狀態的資料模型。

5. Domain Layer - Logic (domain/logic/tool_effect.py)

TOOL_EFFECTS = {"Podcast": 5, "AdBoost": 3}

def apply_tool_effect(game: GameState, tool_name: str) -> GameState:
    delta = TOOL_EFFECTS.get(tool_name, 0)
    game.trust_score += delta
    return game

職責：定義「工具使用後的邏輯行為」。

6. Infrastructure Layer - Repository (infrastructure/repositories/game_repo.py)

class GameRepository:
    @staticmethod
    def get(game_id: str) -> GameState:
        ...

    @staticmethod
    def save(game: GameState) -> None:
        ...

職責：與資料來源溝通（DB 或 in-memory），提供 Domain 使用。