from __future__ import annotations

from app.core.config import Settings


def build_langchain_chat_model(settings: Settings):
    """Return a LangChain chat model when langchain-openai is installed."""

    try:
        from langchain_openai import ChatOpenAI  # type: ignore
    except ImportError as exc:
        raise RuntimeError(
            "Install langchain-openai to enable the LangChain runtime adapter."
        ) from exc
    return ChatOpenAI(
        model=settings.openai_model,
        api_key=settings.openai_api_key,
        base_url=settings.openai_base_url,
        temperature=0.2,
    )

