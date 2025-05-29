from typing import Any, Dict, Optional, List
from src.application.dto.game_dto import SimulateCommentsRequest, SimulateCommentsResponse

class SimulateCommentsLogic:
    """
    群眾留言生成邏輯 - Domain Layer
    """
    def __init__(self, agent_factory):
        self.agent_factory = agent_factory

    def prepare_simulate_comments_variables(
        self, request: SimulateCommentsRequest
    ) -> Dict[str, Any]:

        content = request.article.polished_content or request.article.content

        variables = {
            "title": request.article.title,
            "content": content,
            "source": request.article.source,  # 新增：新聞來源
            "image_url": request.article.image_url,  # 新增：圖片URL
            "platform": request.platform,
            "audience": request.audience,
            "actor": request.actor,
            "round_number": request.round_number,
        }
        
        return variables

    def parse_simulate_comments_result(self, result: Any) -> SimulateCommentsResponse:
        # 處理 agent 回傳格式
        if isinstance(result, SimulateCommentsResponse):
            return result
        if isinstance(result, dict):
            # 檢查是否有reaction欄位
            if "reaction" in result:
                reaction_data = result["reaction"]
                if isinstance(reaction_data, list):
                    return SimulateCommentsResponse(comments=reaction_data)
                elif isinstance(reaction_data, str):
                    # 嘗試從reaction部分的文本
                    lines = [x.strip() for x in reaction_data.splitlines() if x.strip() and not x.strip().startswith('"')]
                    return SimulateCommentsResponse(comments=lines)
            
            comments = result.get("comments")
            if isinstance(comments, list):
                return SimulateCommentsResponse(comments=comments)
            elif isinstance(comments, str):
                return SimulateCommentsResponse(comments=[comments])
        if isinstance(result, list):
            return SimulateCommentsResponse(comments=result)
        if isinstance(result, str):
            # 嘗試解析混亂的JSON格式，提取reaction部分
            lines = self._extract_reactions_from_text(result)
            if lines:
                return SimulateCommentsResponse(comments=lines)
            # 如果沒有reaction，就按行分割
            lines = [x.strip() for x in result.splitlines() if x.strip()]
            return SimulateCommentsResponse(comments=lines)
        return SimulateCommentsResponse(comments=[])
    
    def _extract_reactions_from_text(self, text: str) -> List[str]:
        """從混亂的文本中提取reaction部分"""
        import re
        reactions = []
        
        # 尋找<reaction>標籤或reaction關鍵字
        if "<reaction>" in text:
            # 提取<reaction>標籤內容
            reaction_match = re.search(r'<reaction>(.*?)</reaction>', text, re.DOTALL)
            if reaction_match:
                reaction_content = reaction_match.group(1)
                lines = [x.strip() for x in reaction_content.splitlines() if x.strip()]
                reactions.extend(lines)
        
        # 尋找中文留言樣式
        chinese_comments = re.findall(r'["\u201c]([^"\u201d]*[一-鿿][^"\u201d]*)["\u201d]', text)
        reactions.extend(chinese_comments)
        
        # 過濾掉太短或包含JSON關鍵字的內容
        filtered_reactions = []
        for reaction in reactions:
            if (len(reaction) > 3 and 
                not any(keyword in reaction.lower() for keyword in ['"type"', '"description"', 'spread_change', 'reach_count', 'integer']) and
                reaction not in filtered_reactions):  # 去重
                filtered_reactions.append(reaction)
        
        return filtered_reactions[:10]  # 最多返10條留言

    def generate_comments(
        self, request: SimulateCommentsRequest, input_text: str = "N/A"
    ) -> SimulateCommentsResponse:
        variables = self.prepare_simulate_comments_variables(request)
        result = self.agent_factory.run_agent_by_name(
            session_id=request.session_id,
            agent_name="simulate_comments_agent",
            variables=variables,
            input_text=input_text,
            response_model=SimulateCommentsResponse
        )
        return self.parse_simulate_comments_result(result)
