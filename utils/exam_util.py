def format_exam_from_llm(response_content):
    if response_content.startswith("```json"):
        response_content = response_content[7:]

    if response_content.endswith("```"):
        response_content = response_content[:-3]

    return response_content