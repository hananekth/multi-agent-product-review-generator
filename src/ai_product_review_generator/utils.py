def get_default_llm(provider: str) -> str:
    """Get the default LLM name based on the provider"""
    if provider == "OpenAI":
        return "gpt-4o"
    elif provider == "Gemini":
        return "gemini-2.0-flash"
    elif provider == "Claude":
        return "claude-3-5-sonnet-20241022"
    elif provider == "Grok":
        return "grok-beta"
    else:
        raise ValueError(f"Unsupported provider: {provider}")


example_products = [
    "iPhone 15 Pro Max",
    "Sony WH-1000XM5 Headphones",
    "MacBook Pro M3",
    "PlayStation 5",
    "Samsung Galaxy S24 Ultra",
]

custom_css = """
.center-text h1, .center-text {
    text-align: center;
    font-size: 36px !important;
    font-weight: bold;
}
"""
