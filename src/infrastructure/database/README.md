# SustaiNet 資料庫 Repository 層文檔

## 目錄
1. [概述](#1-概述)
2. [架構設計](#2-架構設計)
3. [BaseRepository](#3-baserepository)
4. [AgentRepository](#4-agentrepository)
5. [會話管理](#5-會話管理)
6. [使用指南](#6-使用指南)
7. [擴展指南](#7-擴展指南)
8. [最佳實踐](#8-最佳實踐)

---

## 1. 概述

Repository 層是 SustaiNet 專案中的資料存取層，負責處理與資料庫的所有交互操作。它採用同步設計模式，並遵循 Clean Architecture 原則，確保業務邏輯與資料存取邏輯分離。

**主要特點：**
- 同步設計
- 使用 SQLAlchemy 2.0 ORM
- 自動化的會話管理
- 通用 CRUD 操作抽象
- 類型安全的 API
- 支援依賴注入

---

## 2. 架構設計

Repository 層採用了分層設計：

```
BaseRepository (泛型基礎類)
    ↑
AgentRepository (特定實體 Repository)
    ↑
[Service 層調用]
```

**設計原則：**
- **單一職責原則**：每個 Repository 類只負責一種實體的數據操作
- **依賴反轉原則**：上層模組通過依賴注入使用 Repository
- **開放封閉原則**：通過繼承 BaseRepository 可擴展而不修改
- **SOLID 原則**：整體設計遵循 SOLID 設計原則

---

## 3. BaseRepository

`BaseRepository` 是所有具體 Repository 類的基礎類，提供通用的 CRUD 操作。

### 設計概述

```python
class BaseRepository(Generic[T]):
    model: Type[Any] = None  # 必須由子類指定
    
    @with_session
    def get_by_id(self, id: int, db: Optional[Session] = None) -> T: ...
    
    @with_session
    def get_all(self, db: Optional[Session] = None) -> List[T]: ...
    
    @with_session
    def get_by(self, db: Optional[Session] = None, **kwargs) -> List[T]: ...
    
    @with_session
    def create(self, data: Union[Dict[str, Any], T], db: Optional[Session] = None) -> T: ...
    
    @with_session
    def update(self, id: int, data: Dict[str, Any], db: Optional[Session] = None) -> T: ...
    
    @with_session
    def delete(self, id: int, db: Optional[Session] = None) -> None: ...
```

### 主要方法

| 方法 | 描述 | 參數 | 返回值 |
|------|------|------|------|
| `get_by_id` | 根據 ID 獲取實體 | `id`: 實體 ID<br>`db`: 可選的數據庫會話 | 實體對象<br>未找到時拋出 `ResourceNotFoundError` |
| `get_all` | 獲取所有實體 | `db`: 可選的數據庫會話 | 實體列表 |
| `get_by` | 根據指定條件查詢 | `**kwargs`: 查詢條件<br>`db`: 可選的數據庫會話 | 符合條件的實體列表 |
| `create` | 創建新實體 | `data`: 實體數據或實體對象<br>`db`: 可選的數據庫會話 | 新創建的實體 |
| `update` | 更新實體 | `id`: 實體 ID<br>`data`: 需要更新的字段<br>`db`: 可選的數據庫會話 | 更新後的實體 |
| `delete` | 刪除實體 | `id`: 實體 ID<br>`db`: 可選的數據庫會話 | `None` |

---

## 4. AgentRepository

`AgentRepository` 是 Agent 實體的具體 Repository 實現。

### 設計概述

```python
class AgentRepository(BaseRepository[Agent]):
    model = Agent
    
    @with_session
    def get_by_name(self, agent_name: str, db: Optional[Session] = None) -> Optional[Agent]: ...
    
    @with_session
    def create_agent(self, agent_name: str, provider: Optional[str] = "openai", ...) -> Agent: ...
```

### 特有方法

| 方法 | 描述 | 參數 | 返回值 |
|------|------|------|------|
| `get_by_name` | 根據名稱獲取 Agent | `agent_name`: Agent 名稱<br>`db`: 可選的數據庫會話 | Agent 對象或 `None` |
| `create_agent` | 創建 Agent 並設置預設值 | `agent_name`: 必須<br>`provider`: 可選，預設 "openai"<br>其他可選配置參數<br>`db`: 可選的數據庫會話 | 新創建的 Agent |

---

## 5. 會話管理

Repository 層使用裝飾器模式管理資料庫會話，以確保正確的資源管理。

### `@with_session` 裝飾器

```python
def with_session(func: Callable[..., T]) -> Callable[..., T]:
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> T:
        # 檢查是否已提供 db
        db = kwargs.get('db')
        own_session = False
        
        # 如果沒有提供 db，創建一個新的
        if db is None:
            db_context = get_db()
            db = next(db_context)
            kwargs['db'] = db
            own_session = True
        
        try:
            # 調用原函數
            result = func(*args, **kwargs)
            
            # 如果我們創建了自己的 session，則提交
            if own_session:
                db.commit()
                
            return result
        except Exception as e:
            # 如果我們創建了自己的 session，則回滾
            if own_session:
                db.rollback()
            raise e
        finally:
            # 如果我們創建了自己的 session，則關閉
            if own_session:
                db.close()
    
    return wrapper
```

### 會話流程

1. **會話創建**：
   - 如果調用時沒有提供 `db` 參數，自動創建新會話
   - 如果提供了 `db` 參數，使用提供的會話

2. **事務處理**：
   - 成功時自動提交（只有自創建的會話）
   - 發生異常時自動回滾（只有自創建的會話）
  
3. **資源釋放**：
   - 確保自創建的會話在操作結束後被關閉
   - 不關閉外部傳入的會話，由調用者負責管理

---

## 6. 使用指南

### 基本用法

```python
# 建立 Repository 實例
agent_repo = AgentRepository()

# 基本 CRUD 操作
agent = agent_repo.get_by_id(1)
all_agents = agent_repo.get_all()
agents_by_provider = agent_repo.get_by(provider="openai")
new_agent = agent_repo.create_agent(agent_name="NewAgent")
updated_agent = agent_repo.update(1, {"description": "Updated description"})
agent_repo.delete(1)

# 特定實體操作
agent_by_name = agent_repo.get_by_name("MyAgent")
```

### 在服務層使用

```python
class AgentService:
    def __init__(self, db: Optional[Session] = None):
        self.db = db
        self.repo = AgentRepository()
    
    def get_agent(self, agent_id: int) -> AgentResponse:
        # 傳遞 db 參數，確保在同一事務中操作
        agent = self.repo.get_by_id(agent_id, db=self.db)
        return AgentResponse.from_entity(agent)
```

### 在測試中使用

```python
def test_agent_repository():
    # 創建測試專用的 Session
    with Session(engine) as session:
        repo = AgentRepository()
        
        # 創建測試資料
        agent = repo.create_agent(
            agent_name="TestAgent",
            db=session
        )
        
        # 確保在同一會話中進行後續操作
        retrieved = repo.get_by_id(agent.id, db=session)
        assert retrieved.agent_name == "TestAgent"
        
        # 清理測試資料
        repo.delete(agent.id, db=session)
        
        # 提交事務
        session.commit()
```

---

## 7. 擴展指南

### 創建新的 Repository

1. **定義實體模型**：

```python
class NewEntity(Base, TimeStampMixin):
    __tablename__ = 'new_entities'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    # 其他欄位...
```

2. **創建 Repository 類**：

```python
class NewEntityRepository(BaseRepository[NewEntity]):
    model = NewEntity
    
    # 添加特定方法
    @with_session
    def get_by_name(self, name: str, db: Optional[Session] = None) -> Optional[NewEntity]:
        results = self.get_by(db=db, name=name)
        return results[0] if results else None
    
    @with_session
    def create_new_entity(self, name: str, db: Optional[Session] = None, **kwargs) -> NewEntity:
        # 處理特定邏輯
        data = {"name": name, **kwargs}
        return self.create(data, db=db)
```

3. **在服務層使用**：

```python
class NewEntityService:
    def __init__(self, db: Optional[Session] = None):
        self.db = db
        self.repo = NewEntityRepository()
    
    # 添加業務邏輯...
```

---

## 8. 最佳實踐

### 資料庫操作

1. **事務管理**：
   - 總是傳遞 `db` 參數，確保相關操作在同一事務中
   - 不要在 Repository 中手動管理事務，讓 `@with_session` 或調用者處理

2. **異常處理**：
   - Repository 方法應拋出特定的異常，如 `ResourceNotFoundError`
   - 在 Service 層捕獲並轉換這些異常為 API 錯誤

3. **查詢優化**：
   - 使用 `get_by` 方法的查詢條件，避免創建特定方法
   - 對於複雜查詢，考慮添加帶有自定義 SQL 的特定方法

### 代碼組織

1. **類型標註**：
   - 總是使用 `Optional[Type]` 標註可能為 None 的參數
   - 為返回值提供明確的類型標註

2. **方法設計**：
   - 保持方法簡單，一個方法只做一件事
   - 對於複雜邏輯，分解為多個小方法

3. **增量擴展**：
   - 優先使用 BaseRepository 的通用方法
   - 只有特殊需求時才添加特定方法
   - 繼承並擴展現有方法，避免重複代碼

---

此文檔涵蓋了 SustaiNet 專案中 Repository 層的主要設計和使用方式。通過遵循這些指南，可以確保資料存取層的一致性、可測試性和可維護性。