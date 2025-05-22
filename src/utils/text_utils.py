import re

def strip_code_block_and_space(text: str) -> str:
    cleaned = re.sub(r"^```[a-zA-Z]*\n", "", text)
    cleaned = re.sub(r"\n?```$", "", cleaned)
    cleaned = cleaned.strip().replace('\u3000', '').replace('\xa0', '')
    return cleaned