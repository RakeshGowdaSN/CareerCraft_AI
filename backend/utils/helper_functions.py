def parse_llm_list_response(llm_response: str):
    items = []
    for line in llm_response.split('\n'):
        if line.startswith("Focus Area"):
            parts = line.split(":", 1)
            if len(parts) == 2:
                item = parts[1].strip()
                items.append(item)
    return items

def parse_llm_reasoning_response(llm_response: str):
    reasoning = {}
    current_focus_area = None
    for line in llm_response.split('\n'):
        if line.startswith("Focus Area"):
            parts = line.split(":", 1)
            if len(parts) == 2:
                current_focus_area = parts[1].strip()
        elif line.startswith("Reasoning"):
            parts = line.split(":", 1)
            if len(parts) == 2 and current_focus_area:
                reasoning[current_focus_area] = parts[1].strip()
    return reasoning