def extract_label_content(text: str, label: str) -> str:
    start = text.find(f'<{label}>') + len(f'<{label}>')
    end = text.find(f'</{label}>')
    if start == -1 or end == -1:
        return ''
    return text[start:end]

def encapsulate_label_content(text: str, label: str) -> str:
    return f'<{label}>{text}</{label}>'