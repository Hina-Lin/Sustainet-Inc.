from typing import Any, Dict, Optional
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
            comments = result.get("comments")
            if isinstance(comments, list):
                return SimulateCommentsResponse(comments=comments)
            elif isinstance(comments, str):
                return SimulateCommentsResponse(comments=[comments])
        if isinstance(result, list):
            return SimulateCommentsResponse(comments=result)
        if isinstance(result, str):
            lines = [x.strip() for x in result.splitlines() if x.strip()]
            return SimulateCommentsResponse(comments=lines)
        return SimulateCommentsResponse(comments=[])

    def generate_comments(
        self, request: SimulateCommentsRequest, input_text: str = "input_text"
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
