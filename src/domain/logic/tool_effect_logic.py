from typing import List, Tuple
from src.application.dto.game_dto import GameMasterAgentResponse
from src.domain.models.tool import DomainTool, AppliedToolEffectDetail
import math

class ToolEffectLogic:
    def apply_effects(
        self,
        original_gm_response: GameMasterAgentResponse,
        tools: List[DomainTool] # List of domain tool objects to apply
    ) -> Tuple[GameMasterAgentResponse, List[AppliedToolEffectDetail]]:
        """
        應用一系列工具的效果到 Game Master 的原始評估上。
        效果是疊加計算的（一個工具的結果是下一個工具的輸入）。
        """
        
        modified_response_data = original_gm_response.model_copy(deep=True)
        applied_effects_details: List[AppliedToolEffectDetail] = []

        if not tools:
            return modified_response_data, applied_effects_details

        # Get the initial values from the original GM response
        current_trust_change = float(original_gm_response.trust_change)
        current_spread_change = float(original_gm_response.spread_change)
        # Note: reach_count is typically not affected by these multiplicative tools unless specified

        for tool in tools:
            # Store the state before this specific tool is applied
            trust_change_before_this_tool = current_trust_change
            spread_change_before_this_tool = current_spread_change

            # Apply multiplicative effects
            current_trust_change *= tool.effects.trust_multiplier
            current_spread_change *= tool.effects.spread_multiplier
            
            # Calculate the net effect of *this specific tool*
            # Round the final net change for this tool to the nearest integer, but keep precision for next tool
            net_trust_effect_this_tool = math.floor(current_trust_change - trust_change_before_this_tool) # math.floor or round based on game rule
            net_spread_effect_this_tool = math.floor(current_spread_change - spread_change_before_this_tool)

            applied_effects_details.append(
                AppliedToolEffectDetail(
                    tool_name=tool.tool_name,
                    applied_trust_effect_value=net_trust_effect_this_tool,
                    applied_spread_effect_value=net_spread_effect_this_tool,
                    is_effective=True # Simplified, can be expanded
                )
            )

        # Update the GameMasterAgentResponse with the final, rounded integer values
        modified_response_data.trust_change = math.floor(current_trust_change) # Final result should be int
        modified_response_data.spread_change = math.floor(current_spread_change)
        
        # IMPORTANT: Consider if platform_status within gm_response also needs adjustment.
        # If gm_response.trust_change is a general indicator, and platform_status are absolute
        # values or already incorporate this, then no change here. 
        # If platform_status player_trust/ai_trust are also meant to be affected by tools in the same turn,
        # that logic would need to be added here or handled when _update_database_states is called.
        # For now, this logic only adjusts the top-level trust_change and spread_change.

        return modified_response_data, applied_effects_details 