# Sustainet-Inc 設定與錯誤處理指南

## 1. 錯誤處理與異常架構說明

### 1.1 異常類別層次結構

專案使用多層次的異常處理架構，可分為兩個主要部分：

1. **應用程序通用異常 (`src/utils/exceptions.py`)**：
   - `AppError`：所有應用程序異常的基類
   - `ValidationError`：驗證錯誤
   - `ResourceNotFoundError`：資源不存在
   - `AuthorizationError`：授權錯誤
   - `ConfigurationError`：配置錯誤
   - `ExternalServiceError`：外部服務調用錯誤
   - `DatabaseError`：數據庫錯誤
   - `BusinessLogicError`：業務邏輯錯誤

2. **API 特定異常 (`src/api/middleware/error_handler.py`)**：
   - `APIError`：API 錯誤基類，包含 HTTP 狀態碼
   - `BadRequestError` (400)：錯誤的請求
   - `AuthenticationError` (401)：未經授權
   - `ForbiddenError` (403)：禁止訪問
   - `NotFoundError` (404)：資源不存在
   - `ConflictError` (409)：資源衝突
   - `APIValidationError` (422)：API 驗證錯誤
   - `ServerError` (500)：伺服器內部錯誤

### 1.2 錯誤處理中間件的用途

錯誤處理中間件 (`error_handler.py`) 的主要功能：

1. **統一錯誤格式**：將所有異常轉換為具有統一格式的 JSON 響應
2. **自動狀態碼映射**：根據異常類型設置適當的 HTTP 狀態碼
3. **錯誤日誌記錄**：記錄所有異常的詳細信息，便於調試與分析
4. **環境適應**：在開發環境中提供更多詳細信息，在生產環境中隱藏敏感信息
5. **異常分類處理**：
   - 處理 API 特定異常
   - 處理應用程序通用異常
   - 處理 FastAPI 和 Starlette 內置異常
   - 處理請求驗證異常
   - 處理全局未捕獲的異常

### 1.3 異常處理流程

1. 當在應用中拋出異常時，FastAPI 會將其捕獲並路由到相應的異常處理器
2. 異常處理器將異常轉換為標準格式的 JSON 響應
3. 同時記錄詳細的錯誤信息到日誌
4. 返回適當的 HTTP 狀態碼和錯誤消息給客戶端

### 1.4 異常使用示例

```python
# 在 API 層直接使用 API 異常
from src.api.middleware.error_handler import BadRequestError, NotFoundError

@router.get("/items/{item_id}")
async def get_item(item_id: int):
    if item_id <= 0:
        raise BadRequestError(
            message="Item ID must be positive",
            error_code="INVALID_ITEM_ID",
            details={"provided_id": item_id}
        )
    
    item = database.get_item(item_id)
    if not item:
        raise NotFoundError(
            message=f"Item with ID {item_id} not found",
            error_code="ITEM_NOT_FOUND"
        )
    
    return item

# 在業務邏輯層使用應用程序異常
from src.utils.exceptions import ValidationError, ResourceNotFoundError

def validate_user_data(user_data):
    errors = []
    if not user_data.get("email"):
        errors.append({"field": "email", "message": "Email is required"})
    
    if errors:
        raise ValidationError(
            message="Invalid user data",
            error_code="INVALID_USER_DATA",
            errors=errors
        )
```

## 2. 設定類的用法

### 2.1 設定類的設計思路

`settings.py` 提供了一個統一的 `Settings` 類來管理所有應用程序配置：

1. **單一來源**：所有配置都從一個類中獲取，消除多處配置的混亂
2. **環境變數映射**：自動從環境變數加載配置
3. **默認值**：為所有配置提供合理的默認值
4. **類型轉換**：自動將環境變數轉換為正確的數據類型
5. **必要性檢查**：標記哪些配置是必須的
6. **相容性檢查**：檢查當前環境變數與 `.env.sample` 的相容性
7. **友好提醒**：在啟動時提醒缺少的或不正確的配置

### 2.2 設定類的基本用法

```python
# 導入全局設定實例
from src.config import settings

# 使用應用設定
app_env = settings.app_env
port = settings.app_port
log_level = settings.app_log_level

# 使用便捷屬性
if settings.is_development:
    # 開發環境特定代碼
    print("Running in development mode")

# 使用 API 密鑰
openai_key = settings.openai_api_key
google_key = settings.google_api_key

# 使用資料庫設定
db_url_sync = settings.database_url_sync
db_url_async = settings.database_url_async

# 獲取整個配置字典（用於調試）
config_dict = settings.to_dict()
```

### 2.3 擴展設定類

如果需要添加新的配置項，請按照以下步驟進行：

1. 在 `Settings` 類中添加新的欄位，提供合適的默認值
2. 在 `_env_mapping` 字典中添加欄位與環境變數的映射
3. 如果配置是必須的，將其添加到 `_required_fields` 集合中
4. 在 `.env.sample` 文件中添加相應的環境變數示例

```python
# 1. 添加新欄位
redis_url: str = field(default="")

# 2. 添加環境變數映射
settings._env_mapping["redis_url"] = "REDIS_URL"

# 3. 如果必須，添加到必需欄位
settings._required_fields.add("redis_url")

# 4. 更新 .env.sample
# REDIS_URL=redis://localhost:6379/0
```

### 2.4 在設定類中添加業務邏輯

設定類也可以包含與配置相關的業務邏輯：

```python
# 在 Settings 類中添加新方法
def get_database_options(self) -> Dict[str, Any]:
    """獲取資料庫連接選項"""
    return {
        "url": self.database_url,
        "pool_size": 10 if self.is_production else 5,
        "max_overflow": 20 if self.is_production else 10,
        "echo": self.is_development,
    }
```

## 3. 配置與錯誤處理的最佳實踐

### 3.1 領域層使用的異常

在領域層（業務邏輯）中，應該使用通用應用程序異常：

```python
from src.utils.exceptions import ValidationError, BusinessLogicError

def calculate_discount(user, cart):
    if not user.is_active:
        raise ValidationError("User account is not active")
    
    if cart.total_amount < 0:
        raise BusinessLogicError(
            message="Cart amount cannot be negative",
            error_code="NEGATIVE_CART_AMOUNT"
        )
```

### 3.2 API 層使用的異常

在 API 層中，應該使用 API 特定異常：

```python
from src.api.middleware.error_handler import BadRequestError, NotFoundError

@router.post("/orders")
async def create_order(order_data: OrderCreate):
    try:
        order = order_service.create_order(order_data)
        return {"order_id": order.id}
    except ValidationError as e:
        # 將領域層異常轉換為 API 異常
        raise BadRequestError(
            message=str(e),
            error_code="INVALID_ORDER_DATA",
            details=e.details
        )
    except ResourceNotFoundError as e:
        raise NotFoundError(
            message=str(e),
            error_code="RESOURCE_NOT_FOUND",
            details=e.details
        )
```

### 3.3 設定管理最佳實踐

1. **敏感信息處理**：
   - 不要在代碼中硬編碼敏感信息（API 密鑰、密碼等）
   - 始終使用環境變數或安全的配置管理系統

2. **環境特定配置**：
   - 使用 `is_development`、`is_production` 等屬性根據環境調整行為
   - 在開發環境中提供更多調試信息，在生產環境中優化性能

3. **配置驗證**：
   - 在應用啟動時驗證所有必需的配置
   - 提供明確的錯誤消息，指出缺少哪些配置

4. **分層設計**：
   - 將配置邏輯與應用其他部分解耦
   - 避免在多個地方重複讀取環境變數

### 3.4 錯誤處理最佳實踐

1. **使用具體異常**：
   - 使用具體的異常類型而不是通用異常
   - 提供明確的錯誤代碼和消息

2. **保持異常層次**：
   - 在領域層使用領域異常
   - 在 API 層使用 API 異常
   - 必要時進行轉換，保持關注點分離

3. **提供上下文**：
   - 在異常中包含足夠的上下文信息
   - 使用 `details` 字段提供結構化數據

4. **記錄異常**：
   - 在處理異常時記錄詳細信息
   - 在生產環境中避免泄露敏感信息

5. **用戶友好消息**：
   - 向最終用戶提供友好的錯誤消息
   - 保留技術細節供內部使用
