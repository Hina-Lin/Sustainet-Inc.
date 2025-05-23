# 🧠 Sustainet Inc. - 永續資訊對抗模擬器

Sustainet Inc. 是一款以永續議題為主題的策略模擬遊戲，探索假訊息如何影響人們對氣候、能源與社會正義等永續議題的認知。玩家將扮演資訊守門人角色，善用查核工具與社群觀察力，與 AI 假訊息操縱者對抗，在動態社群環境中維持公眾信任與資訊透明度。

## 📦 技術架構總覽

本專案採用 Clean Architecture，並結合 Agno 作為 Agent 管理框架。
```
API (FastAPI)
└── Application Layer (Use Cases, DTOs)
    └── Domain Layer (Entities, Logic)
        └── Infrastructure Layer (外部依賴)
```

### 🏗️ 重構後的架構設計

本專案已進行重構，採用更嚴格的 Clean Architecture 原則：

**Application Service Layer** - 只負責流程編排
- `GameService`: 協調各個 Domain Logic 組件
- 保持輕量，避免業務邏輯混入

**Domain Logic Layer** - 核心業務邏輯
- `TurnExecutionLogic`: 負責 AI 和玩家的行動執行
- `GameStateManager`: 負責遊戲狀態管理、GM 評估、工具效果應用
- `ResponseConverter`: 負責 Domain 結果轉換為 API DTO
- `ToolEffectLogic`: 工具效果計算邏輯

**Infrastructure Layer** - 外部依賴
- Repository 模式用於資料存取
- Agent Factory 用於 AI Agent 管理

## 📁 專案目錄結構

```
src/
├── api/                        # FastAPI endpoints
│   ├── routes/                 # 所有路由
│   └── middleware/             # 中間件 (錯誤處理等)
├── application/                # Use Case、DTO
│   ├── services/               # 遊戲服務邏輯（使用工具、提交行動等）
│   └── dto/                    # Pydantic 輸入 / 輸出模型
├── domain/                     # 核心業務邏輯
│   ├── models/                 # Entity / ValueObject
│   └── logic/                  # 業務邏輯組件
│       ├── turn_execution.py   # 回合執行邏輯 (AI/玩家行動)
│       ├── game_state_manager.py # 遊戲狀態管理 (GM評估、工具效果)
│       ├── response_converter.py # 回應格式轉換
│       ├── tool_effect_logic.py  # 工具效果計算
│       └── ...                 # 其他業務邏輯
├── infrastructure/             # GPT/Agno 整合、資料庫、新聞、儲存
│   ├── database/               # 模擬資料庫與 Repository
│   ├── news/                   # 新聞載入器（假新聞拼接來源）
├── utils/                      # 公用工具（日誌、異常處理等）
├── config/                     # 設定管理與環境變數加載
├── tests/                      # 單元與整合測試
└── main.py                     # FastAPI app 入口
```

## 🔄 重構後的流程與工具系統

### 🎆 新的回合執行流程

1. **流程編排** (Application Service)
   - `GameService._execute_turn()` 只負責協調各個 Domain Logic

2. **行動執行** (Domain Logic)
   - `TurnExecutionLogic.execute_actor_turn()` 處理 AI/玩家具體行動
   - 支援 AI 和玩家的統一工具解析邏輯

3. **效果評估** (Domain Logic)
   - `GameStateManager.evaluate_and_apply_effects()` 處理 GM 評估和工具效果

4. **狀態持久化** (Domain Logic)
   - `GameStateManager.persist_turn_result()` 統一的資料庫更新

5. **回應轉換** (Application Service)
   - `ResponseConverter.to_turn_response()` 轉換為 API DTO

### 🔧 統一的工具系統

重構後，AI 和玩家使用相同的工具解析和效果應用邏輯：

1. **AI 工具使用**：透過 System Prompt 中的工具清單，結構化輸出 `tool_used` 欄位
2. **玩家工具使用**：透過 API 請求中的 `tool_used` 欄位
3. **統一處理**：兩者都經過 `ToolEffectLogic.apply_effects()` 進行效果計算

### 🎯 架構改進效益

| 項目 | 重構前 | 重構後 |
|------|---------|---------|
| 工具解析邏輯 | AI 和玩家分離 | 統一處理 |
| `_execute_turn` 行數 | ~150 行 | ~50 行 |
| 職責数量 | 6+ 個職責 | 1 個職責 (流程編排) |
| 可測試性 | 困難 | 容易 |
| 符合 Clean Architecture | ❌ | ✅ |

## 🎮 遊戲機制詳解

### 核心概念

- **信任值**：玩家和AI各自在不同平台上的信任度，範圍為0-100
- **傳播率**：訊息在平台上的傳播程度，影響信任值變化的幅度
- **平台**：不同的社群媒體平台，每個平台有特定的受眾特性
- **工具**：玩家和AI可使用的工具，提升信任值或傳播率

### 玩家反應模式

玩家面對AI發布的新聞有三種反應模式：

1. **澄清（對抗）**：指出新聞錯誤並提供正確資訊，成功時提升自身信任值並降低AI信任值
2. **無動作**：不採取任何行動，通常導致AI信任值緩慢上升
3. **附和**：認同並強化AI的訊息，同時提高雙方信任值，但AI提高更多

### Game Master (GM) 評判機制

GM代理人會根據以下因素判斷行動效果：

- 新聞真實性（完全真實、部分真實、完全虛假）
- 玩家反應質量（證據力、情感共鳴、清晰度）
- 工具使用效果
- 平台特性
- 歷史信任度

## 🗄️ 資料庫設計

### 表格結構

#### 1. 遊戲設置表 (GameSetup)
```python
class GameSetup(Base, TimeStampMixin):
    """
    遊戲初始設置表：記錄遊戲基本配置
    """
    session_id = Column(String(64), primary_key=True)
    # 保留玩家初始信任度和 AI 初始信任度作為基本數值
    player_initial_trust = Column(Integer, nullable=False, default=50)
    ai_initial_trust = Column(Integer, nullable=False, default=50)
    # 使用JSON存儲平台和受眾群體配置，因為這確實是一組相關數據
    platforms = Column(JSON, nullable=False)
    
    def __repr__(self):
        return f"<GameSetup session={self.session_id}>"
```

#### 2. 平台狀態表 (PlatformState)
```python
class PlatformState(Base, TimeStampMixin):
    """
    平台狀態表：記錄每個回合中每個平台的狀態
    """
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(64), ForeignKey("game_setups.session_id"), nullable=False)
    round_number = Column(Integer, nullable=False)
    platform_name = Column(String(32), nullable=False)
    
    # 分開存儲玩家和 AI 的信任度
    player_trust = Column(Integer, nullable=False)
    ai_trust = Column(Integer, nullable=False)
    
    # 傳播率 (百分比存為整數，如75表示75%)
    spread_rate = Column(Integer, nullable=False)
    
    def __repr__(self):
        return f"<PlatformState session={self.session_id}, round={self.round_number}, platform={self.platform_name}>"
```

#### 3. 行動記錄表 (ActionRecord)
```python
class ActionRecord(Base, TimeStampMixin):
    """
    行動記錄表：記錄每個回合中AI和玩家的行動
    """
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(64), ForeignKey("game_setups.session_id"), nullable=False)
    round_number = Column(Integer, nullable=False)
    
    # AI 或 player
    actor = Column(String(32), nullable=False)
    
    # 選擇的平台
    platform = Column(String(32), nullable=False)
    
    # 行動的內容文本
    content = Column(Text, nullable=False)
    
    # GM 判定結果 - 基本數值
    reach_count = Column(Integer, nullable=True)  # 觸及人數
    trust_change = Column(Integer, nullable=True)  # 信任值變化
    spread_change = Column(Integer, nullable=True)  # 傳播率變化
    
    # GM 判定的有效程度 (low, medium, high)
    effectiveness = Column(String(32), nullable=True)
    
    # 模擬留言 - 這個可以用 JSON 因為是不定長度的數組
    simulated_comments = Column(JSON, nullable=True)

    def __repr__(self):
        return f"<ActionRecord session={self.session_id}, round={self.round_number}, actor={self.actor}>"
```

#### 4. 工具使用記錄表 (ToolUsage)
```python
class ToolUsage(Base, TimeStampMixin):
    """
    工具使用記錄表：記錄每次行動中使用的工具
    """
    id = Column(Integer, primary_key=True, autoincrement=True)
    action_id = Column(Integer, ForeignKey("action_records.id"), nullable=False)
    tool_name = Column(String(64), nullable=False)
    
    # 效果數值
    trust_effect = Column(Integer, nullable=True)  # 信任值效果
    spread_effect = Column(Integer, nullable=True)  # 傳播率效果
    
    # 工具使用成功否
    is_effective = Column(Boolean, default=True)
    
    def __repr__(self):
        return f"<ToolUsage id={self.id}, tool={self.tool_name}, action={self.action_id}>"
```

#### 5. 工具定義表 (Tool)
```python
class Tool(Base, TimeStampMixin):
    """
    工具表：定義可用工具及其基本效果
    """
    tool_name = Column(String(64), primary_key=True)
    description = Column(Text, nullable=False)
    
    # 基本效果值
    trust_effect = Column(Integer, nullable=True, default=0)  # 信任值效果
    spread_effect = Column(Integer, nullable=True, default=0)  # 傳播率效果
    
    # 工具適用對象 (player, ai, both)
    applicable_to = Column(String(32), nullable=False, default="both")
    
    def __repr__(self):
        return f"<Tool name={self.tool_name}>"
```

#### 6. 新聞/議題表 (News)
```python
class News(Base, TimeStampMixin):
    """
    新聞/議題表：存儲遊戲中使用的新聞或議題
    """
    news_id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(256), nullable=False)
    content = Column(Text, nullable=False)
    
    # 新聞真實性 (true, false, partial)
    veracity = Column(String(32), nullable=False)
    
    # 新聞類別 (environment, energy, social_justice 等)
    category = Column(String(64), nullable=False)
    
    # 新聞來源
    source = Column(String(128), nullable=False)
    
    # 是否啟用
    is_active = Column(Boolean, default=True)

    def __repr__(self):
        return f"<News id={self.news_id}, title={self.title}>"
```

#### 7. 遊戲回合表 (GameRound)
```python
class GameRound(Base, TimeStampMixin):
    """
    遊戲回合表：記錄每個回合的基本信息
    """
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(64), ForeignKey("game_setups.session_id"), nullable=False)
    round_number = Column(Integer, nullable=False)
    news_id = Column(Integer, ForeignKey("news.news_id"), nullable=False)
    
    # 當前回合是否完成
    is_completed = Column(Boolean, default=False)
    
    def __repr__(self):
        return f"<GameRound session={self.session_id}, round={self.round_number}>"
```

### 資料流程示例

#### 遊戲初始化
1. 創建 `GameSetup` 記錄，設置初始信任度和平台配置
2. 為每個平台創建初始 `PlatformState` 記錄
3. 創建第一個 `GameRound` 記錄，選擇初始新聞

#### AI回合
1. AI選擇平台和新聞
2. 創建 `ActionRecord`，記錄AI的行動內容
3. 如使用工具，創建 `ToolUsage` 記錄
4. GM評判效果，更新 `ActionRecord` 
5. 更新相關平台的 `PlatformState`

#### 玩家回合
1. 玩家選擇平台和反應模式（澄清、無動作、附和）
2. 創建 `ActionRecord`，記錄玩家的行動內容
3. 如使用工具，創建 `ToolUsage` 記錄
4. GM評判效果，更新 `ActionRecord`
5. 更新相關平台的 `PlatformState`
6. 將 `GameRound` 標記為已完成

#### 進入下一回合
1. 創建新的 `GameRound` 記錄
2. 重複以上流程

## 模擬數據示例

### 遊戲設置 (GameSetup)

| session_id | player_initial_trust | ai_initial_trust | platforms | created_at | updated_at |
|------------|---------------------|-----------------|-----------|------------|------------|
| game123    | 50                  | 50              | {"platforms": [{"name": "Facebook", "audience": "一般大眾"}, {"name": "Twitter", "audience": "年輕族群"}, {"name": "LinkedIn", "audience": "專業人士"}, {"name": "Instagram", "audience": "學生"}]} | 2025-05-15 13:00:00 | 2025-05-15 13:00:00 |

### 第一回合數據

#### 遊戲回合 (GameRound)

| id | session_id | round_number | news_id | is_completed | created_at | updated_at |
|----|------------|--------------|---------|--------------|------------|------------|
| 1 | game123 | 1 | 1 | true | 2025-05-15 13:01:00 | 2025-05-15 13:10:00 |

#### 行動記錄 (ActionRecord)

| id | session_id | round_number | actor | platform | content | reach_count | trust_change | spread_change | effectiveness | simulated_comments | created_at | updated_at |
|----|------------|--------------|-------|----------|---------|-------------|--------------|---------------|---------------|-------------------|------------|------------|
| 1 | game123 | 1 | ai | Facebook | 震驚！台灣綠能發展恐造成更嚴重空汙... | 390 | -10 | 15 | high | ["假的啦，再生能源明明比石化好", "我也有看到這個，真的假的", "怎麼沒有主流媒體報？"] | 2025-05-15 13:02:00 | 2025-05-15 13:02:30 |
| 2 | game123 | 1 | player | Facebook | 實際上，太陽能與風力發電的全生命週期碳排放遠低於... | 200 | 8 | -5 | medium | ["原來如此，但還是會怕啦", "謝謝資訊～", "有沒有報告連結可以看?"] | 2025-05-15 13:05:00 | 2025-05-15 13:05:30 |

#### 工具使用記錄 (ToolUsage)

| id | action_id | tool_name | trust_effect | spread_effect | is_effective | created_at | updated_at |
|----|-----------|-----------|--------------|---------------|--------------|------------|------------|
| 1 | 1 | 情緒刺激 | 0 | 10 | true | 2025-05-15 13:02:10 | 2025-05-15 13:02:10 |
| 2 | 2 | AI文案優化 | 2 | 3 | true | 2025-05-15 13:05:10 | 2025-05-15 13:05:10 |
| 3 | 2 | 數據視覺化 | 3 | 2 | true | 2025-05-15 13:05:10 | 2025-05-15 13:05:10 |

#### 平台狀態 (PlatformState)

| id | session_id | round_number | platform_name | player_trust | ai_trust | spread_rate | created_at | updated_at |
|----|------------|--------------|--------------|--------------|----------|-------------|------------|------------|
| 1 | game123 | 1 | Facebook | 58 | 40 | 65 | 2025-05-15 13:05:30 | 2025-05-15 13:05:30 |
| 2 | game123 | 1 | Twitter | 50 | 50 | 50 | 2025-05-15 13:05:30 | 2025-05-15 13:05:30 |
| 3 | game123 | 1 | LinkedIn | 50 | 50 | 50 | 2025-05-15 13:05:30 | 2025-05-15 13:05:30 |
| 4 | game123 | 1 | Instagram | 50 | 50 | 50 | 2025-05-15 13:05:30 | 2025-05-15 13:05:30 |

## 🔌 主要依賴與框架

技術 | 用途
-----|-----
FastAPI | Web 框架 / REST API
Agno | Agent 行為建模與推理
OpenAI API | GPT 模型（生成新聞、澄清、判定）
PostgreSQL | 儲存遊戲狀態與資料
Uvicorn | 非同步應用伺服器
Pydantic | 資料結構驗證與轉換

## 🧰 套件安裝與環境設置（使用 uv）

```bash
# 安裝 uv
pip install uv

# 建立虛擬環境並安裝依賴
uv venv
uv pip install -r requirements.txt(uv sync)
```

如使用 uv 設定依賴：

```bash
uv add (這個會自動將套件更新到.lock以及.toml)
```

## 🚀 啟動方式

```bash
uvicorn main:app --reload
```

前往：http://localhost:8000/docs 查看 Swagger 文件。

## ⚙️ 設定管理

本專案使用統一的設定類來管理所有應用程序配置，支援從環境變數加載設定並提供合理的預設值。

### 設定類使用示例

```python
from src.config import settings

# 使用應用設定
port = settings.app_port
env = settings.app_env

# 檢查環境
if settings.is_development:
    # 開發環境特定代碼
    print("Running in development mode")

# 使用 API 密鑰
openai_key = settings.openai_api_key
google_key = settings.google_api_key
```

## 🔄 統一錯誤處理

專案實作了一個統一的異常處理機制，將各種異常轉換為標準格式的 API 響應：

```json
{
  "success": false,
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "The requested item was not found",
    "details": {
      "resource_type": "game",
      "resource_id": "123"
    }
  }
}
```

### 異常使用示例

```python
# API 層
from src.api.middleware.error_handler import BadRequestError

@router.get("/items/{item_id}")
async def get_item(item_id: int):
    if item_id <= 0:
        raise BadRequestError(
            message="Item ID must be positive",
            error_code="INVALID_ITEM_ID"
        )
    # ...

# 領域層
from src.utils.exceptions import ValidationError

def validate_game_action(action):
    if not action.is_valid():
        raise ValidationError(
            message="Invalid game action",
            error_code="INVALID_ACTION"
        )
    # ...
```

## 🤖 Agno Agent 整合說明

Agno 會作為下列角色執行：

### FakeNewsAgent
接收新聞來源，生成偏頗或拼貼式訊息。

### GameMasterAgent
根據玩家與 AI 的行為模擬社群反應，給出觸及率、信任分數變化與傳播率變化。

### ClarifierAgent
協助玩家撰寫澄清內容。

每個 Agent 的 prompt 與初始化邏輯放於：infrastructure/agents/，並由 AgentFactory 根據 DB 設定進行建構。

Agno Docs: https://docs.agno.com/introduction

## 📡 API 範例說明：重構後的工具系統

此範例展示重構後的 Clean Architecture 設計，工具使用流程更簡潔且統一。

### 🧪 功能：統一的工具可用性管理

每次遊戲操作都會自動返回當前回合的可用工具列表，無需額外的 API 請求。

#### 核心特色：
- **資料驅動**：工具可用性完全由資料庫 `available_from_round` 欄位控制
- **自動返回**：所有回合操作都自動包含 `tool_list` 欄位
- **快取優化**：內建 5 分鐘快取機制，減少資料庫詢詢
- **統一處理**：AI 和玩家使用相同的工具解析和效果應用邏輯

1. **API Layer** (/api/routes/games.py)

```python
@router.post("/games/{session_id}/rounds/{round_number}/player-turn")
def player_turn(request: PlayerTurnRequest):
    return game_service.player_turn(request)
```

職責：接收 HTTP 請求並轉交給 Application Service。

2. **Application Service** (application/services/game_service.py)

```python
def _execute_turn(self, actor, session_id, round_number, article, tool_used, tool_list):
    # 1. 重建遊戲狀態
    game = self.game_state_manager.rebuild_game_state(session_id, round_number)
    
    # 2. 執行行動者回合 (統一處理 AI 和玩家)
    turn_result = self.turn_execution_logic.execute_actor_turn(
        game=game, actor=actor, session_id=session_id, 
        round_number=round_number, article=article, player_tools=tool_used
    )
    
    # 3. 評估效果並應用工具 (統一處理)
    game_turn_result = self.game_state_manager.evaluate_and_apply_effects(
        turn_result, game, self.tool_repo
    )
    
    # 4. 持久化結果
    action_id = self.game_state_manager.persist_turn_result(game_turn_result)
    
    # 5. 轉換為回應 DTO
    return self.response_converter.to_turn_response(game_turn_result, tool_list)
```

職責：流程編排，協調各個 Domain Logic 組件。

3. **Domain Logic - Turn Execution** (domain/logic/turn_execution.py)

```python
def execute_actor_turn(self, game, actor, session_id, round_number, article=None, player_tools=None):
    if actor == "ai":
        return self._execute_ai_action(game, session_id, round_number)
    elif actor == "player":
        return self._execute_player_action(game, session_id, round_number, article, player_tools or [])

def _execute_ai_action(self, game, session_id, round_number):
    # AI 選擇平台、生成新聞、使用工具
    # 從 Agent 回應中解析 tool_used 欄位
    agent_output = self.agent_factory.run_agent_by_name(...)
    tools_used = agent_output.tool_used or []  # 結構化輸出
    
    return TurnExecutionResult(
        actor="ai", session_id=session_id, round_number=round_number,
        article=article, target_platform=platform.name, tools_used=tools_used
    )
```

職責：處理具體的行動執行邏輯，包含工具解析。

4. **Domain Logic - Game State Manager** (domain/logic/game_state_manager.py)

```python
def evaluate_and_apply_effects(self, turn_result, game, tool_repo):
    # 1. GM 評估
    original_gm_result = self._get_gm_evaluation(...)
    
    # 2. 統一的工具效果應用 (AI 和玩家使用相同邏輯)
    if turn_result.tools_used:
        domain_tools = self._get_applicable_tools(turn_result.tools_used, turn_result.actor, tool_repo)
        if domain_tools:
            final_gm_result, tool_effects = self.tool_effect_logic.apply_effects(
                original_gm_result, domain_tools
            )
    
    return GameTurnResult(turn_result, final_gm_result, tool_effects)
```

職責：統一的 GM 評估和工具效果計算。

5. **Domain Logic - Tool Effect** (domain/logic/tool_effect_logic.py)

```python
def apply_effects(self, original_gm_response, tools):
    # 工具效果疊加計算（乘數效果）
    for tool in tools:
        current_trust_change *= tool.effects.trust_multiplier
        current_spread_change *= tool.effects.spread_multiplier
    
    return modified_response, applied_effects_details
```

職責：純粹的工具效果計算邏輯。

### 🔧 重構帶來的改進

| 方面 | 重構前 | 重構後 |
|------|--------|--------|
| **工具處理** | AI/玩家分離邏輯 | 統一處理流程 |
| **代碼行數** | `_execute_turn` ~150行 | `_execute_turn` ~50行 |
| **職責分離** | 單一方法包含所有邏輯 | 每個類別單一職責 |
| **可測試性** | 複雜依賴，難以測試 | 組件獨立，易於測試 |
| **可維護性** | 修改影響面大 | 影響範圍可控 |
| **擴展性** | 新功能難以添加 | 遵循開放封閉原則 |

## 📊 面板設計範例

```
=== 回合 3 ===

【假訊息】
「據說新再生能源其實會導致更多空汙，研究顯示…」
發佈平台：Instagram
新聞類別：能源環保

【社群反應】
- 「假的啦，再生能源明明比石化好」 (質疑)
- 「我也有看到這個，真的假的」 (疑惑)
- 「怎麼沒有主流媒體報？」 (質疑)

【AI 影響評估】
觸及人數：390 人
傳播率變化：+15% (高傳播，因情緒性語句 + 無來源)
信任值變化：-10 點 (從 50 降至 40)

【玩家回應】
使用工具：引用權威 (能源署報告)
回應內容：「實際上，太陽能與風力造成的污染極低，資料來自能源署。」

【澄清效果】
工具加成：信任度 +5
最終效果：中度有效
觸及人數：120 人
信任值變化：+16 點 (從 40 升至 56)

【平台狀態】
Instagram：信任度 56/100 | 傳播率 75%
Facebook：信任度 62/100 | 傳播率 68%
Twitter：信任度 43/100 | 傳播率 82%
Reddit：信任度 58/100 | 傳播率 71%
```
