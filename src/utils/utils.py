def build_parameters(actor: str, title: str, year: str) -> str:
    lines: list[str] = []

    print(f"Ator recebido: {actor}")
    if actor:

        lines.append(
            f'?dir rdfs:label "{actor}" .')
        
    lines.append('?dir foaf:acts ?mov .')
    lines.append('?mov rdfs:label ?Movies .')
    
    return "\n".join(lines)