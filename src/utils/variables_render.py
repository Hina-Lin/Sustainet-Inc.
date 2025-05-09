"""
模板處理服務 - 處理模板字符串和變數替換
"""
import re
import json
from typing import Dict, Any

class VariablesRenderer:
    """處理模板字符串和變數替換"""
    
    @staticmethod
    def render_variables(text: str, variables: Dict[str, Any]) -> str:
        """
        將文本中的變數佔位符替換為實際值，支援 {variable} 和 {{variable}} 兩種格式
        
        Args:
            text: 要進行變數替換的文本
            variables: 變數名稱和值的字典
            
        Returns:
            替換變數後的字符串
            
        Example:
            >>> text = "你好 {name}，現在是 {{time}}"
            >>> variables = {"name": "小明", "time": "下午3點"}
            >>> VariablesRenderer.render_variables(text, variables)
            '你好 小明，現在是 下午3點'
        """
        if not text:
            return text
            
        # 先處理雙大括號格式 {{variable}}
        double_pattern = r'{{([^{}]+)}}'
        
        def replace_double_var(match):
            var_name = match.group(1).strip()
            value = variables.get(var_name)
            
            # 特殊處理某些類型的值
            if isinstance(value, (dict, list)):
                return json.dumps(value, indent=2, ensure_ascii=False)
            
            # 返回字符串形式的值，如果變數不存在則保留原佔位符
            return str(value) if value is not None else f"{{{{{var_name}}}}}"
        
        # 替換所有匹配的雙大括號變數
        result = re.sub(double_pattern, replace_double_var, text)
        
        # 再處理單大括號格式 {variable}
        single_pattern = r'{([^{}]+)}'
        
        def replace_single_var(match):
            var_name = match.group(1).strip()
            value = variables.get(var_name)
            
            # 特殊處理某些類型的值
            if isinstance(value, (dict, list)):
                return json.dumps(value, indent=2, ensure_ascii=False)
            
            # 返回字符串形式的值，如果變數不存在則保留原佔位符
            return str(value) if value is not None else f"{{{var_name}}}"
        
        # 替換所有匹配的單大括號變數
        return re.sub(single_pattern, replace_single_var, result)
