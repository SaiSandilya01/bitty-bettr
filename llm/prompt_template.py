"""
llm/prompt_template.py

Builds the LLM prompt for digest generation.
Designed for any curious reader — not software-specific.
"""


SYSTEM_PROMPT = """You are a knowledgeable and engaging teacher writing a daily learning digest for a curious reader.
Your reader may be interested in anything — technology, history, economics, science, general knowledge, philosophy, or culture.
Your goal is to explain each topic clearly, accurately, and with genuine insight.
Write in a warm, accessible tone — like a smart friend explaining something over coffee.
Never hallucinate. If a topic is ambiguous, interpret it in its most commonly understood sense.
Output clean HTML only. No CSS. No markdown."""


def build_user_prompt(topics: list[str]) -> str:
    """
    Build the user-facing prompt from a list of topics.
    Each topic gets a self-contained HTML section.
    """
    topics_list = "\n".join(f"- {t}" for t in topics)

    return f"""Generate a daily learning digest for the following topics:

{topics_list}

For EACH topic, produce a comprehensive HTML <section>. The entire response should be incredibly deep and detailed, serving as a ~20 minute reading experience across all topics.

Provide the following structure for EACH topic:
1. <h2> — Topic title (properly capitalized)
2. <h3>1. What it is</h3><p>...</p> — A clear, accessible introduction and formal definition.
3. <h3>2. The Intuition & History</h3><p>...</p> — Several paragraphs explaining the origin, why it was created, and the core intuition behind it. Make it narrative and engaging.
4. <h3>3. How it works (Deep Dive)</h3><p>...</p> — A detailed, nuanced explanation spanning multiple paragraphs. Break down the mechanics, core principles, and subtleties. Use analogies.
5. <h3>4. Real-world Applications & Examples</h3><p>...</p> — Provide 2-3 detailed real-world case studies or examples showing how this concept is applied in practice.
6. <h3>5. Common Misconceptions</h3><p>...</p> — What do people usually get wrong about this? Clarify the nuances.
7. <h3>6. Key Takeaway</h3><p>...</p> — One profound, memorable insight to hold onto.

Rules:
- 1000–1500 words per topic minimum. Go deep. Write like an engaging, long-form New Yorker profile or Paul Graham essay.
- Use simple, jargon-free language where possible. Explain complex terms when you must use them.
- No CSS, no inline styles
- Clean, valid HTML only
- Each topic must be wrapped in <section class="topic">
- Do not add a wrapping <html>, <head>, or <body> — only the <section> elements
"""
