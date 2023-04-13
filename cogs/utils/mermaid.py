"""
Hjelpeklasse for å bygge mermaid charts
"""
import base64


async def mermaid(graph):
    """
    Generates image link for mermaid chart
    """
    graphbytes = graph.encode("utf-8")
    base64_bytes = base64.urlsafe_b64encode(graphbytes)
    base64_string = base64_bytes.decode("utf-8")
    return str("https://mermaid.ink/img/" + base64_string)
