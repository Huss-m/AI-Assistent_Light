def block(title: str, content: str) -> str:
    sep = "=" * 70
    return f"{sep}\n{title}\n{sep}\n{content}\n"

def list_lines(title: str, rows: list[str]) -> str:
    if not rows:
        body = "(Inget)"
    else:
        body = "\n".join(f"- {r}" for r in rows)
    return block(title, body)
