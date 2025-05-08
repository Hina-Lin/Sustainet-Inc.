# src/api/routes/tools.py

from fastapi import APIRouter
from src.application.dto.use_tool_dto import UseToolRequest, UseToolResponse
from src.application.services.use_tool import use_tool_service

router = APIRouter()

@router.post("/tools/use", response_model=UseToolResponse)
def use_tool(request: UseToolRequest):
    return use_tool_service(request)
