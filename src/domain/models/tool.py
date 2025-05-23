from pydantic import BaseModel
from typing import Literal, List, Dict, Any, Optional

class ToolEffect(BaseModel):
    """
    定義工具的核心效果，作為乘數。
    """
    trust_multiplier: float = 1.0  # 例如 1.1 表示原始信任變化效果增加10%
    spread_multiplier: float = 1.0 # 例如 1.2 表示原始傳播變化效果增加20%
    # 如果未來需要固定的加/減值效果，可以在此擴展

class DomainTool(BaseModel):
    """
    工具的領域模型表示。
    """
    tool_name: str
    description: str
    applicable_to: Literal["player", "ai", "both"] # 工具適用對象
    effects: ToolEffect # 工具的核心效果
    available_from_round: int = 1 # 從第幾回合開始可用

class AppliedToolEffectDetail(BaseModel):
    """
    記錄單個工具實際應用後的效果細節。
    """
    tool_name: str
    applied_trust_effect_value: int # 工具造成的信任值淨變化
    applied_spread_effect_value: int # 工具造成的傳播率淨變化
    is_effective: bool = True
    message: Optional[str] = None # 例如："Podcast 效果已應用" 