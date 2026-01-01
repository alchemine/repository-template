"""Inference module."""

import re

import tiktoken
from openai import AsyncOpenAI, OpenAI
from transformers import AutoTokenizer
from langchain_openai import ChatOpenAI
from langchain_core.prompt_values import ChatPromptValue

from config import CFG, SERVICE_NAME
from src.common.utils import SingletonBase


TOKENIZER_CACHE = {}


def create_llm_cache(service_name: str, model_name: str):
    """Create LLM cache instance for individual model."""
    cache_key = f"{service_name}_{model_name}"
    try:
        from langchain_community.cache import SQLiteCache

        db_path = f"llm_cache_{cache_key}.db"
        cache = SQLiteCache(database_path=db_path)
        print(f"LLM cache for {cache_key} using SQLiteCache created.")
    except Exception as e:
        print(f"LLM cache using SQLiteCache failed: {e}")
        raise

    return cache


class LLMManager(SingletonBase):
    """LLM manager.

    Attributes:
        provider: provider name
        model_name: model name
        model: LLM model
        batch_config: batch config for LLM

    References:
        - Prompt optimizer: https://platform.openai.com/chat/edit?models=gpt-5&optimize=true
        - Reasoning guide: https://platform.openai.com/docs/guides/reasoning
        - Prompt examples: https://platform.openai.com/docs/guides/reasoning?example=planning#prompt-examples
        - Preambles: https://platform.openai.com/docs/guides/latest-model#preambles
        # PREAMBLES = "Before you call a tool, explain why you are calling it."
    """

    @classmethod
    def _generate_instance_key(cls, provider: str, *args, **kwargs) -> tuple:
        return (provider,)

    def _init_once(self, provider: str, use_cache: bool = False) -> None:
        """Initialize LLM manager."""
        assert (
            provider in CFG.inference.llm.providers
        ), f"provider({provider}) should be in CFG.inference.llm.providers"

        self.provider = provider
        self.model_name = self._get_model_name()
        self.model_config = self._get_model_config()
        self.invoke_config = self._get_invoke_config()
        self.model = self._get_model(use_cache)

    def _get_model(self, use_cache: bool) -> ChatOpenAI:
        """Get LLM model."""
        try:
            # Get llm model
            if use_cache:
                cache = create_llm_cache(SERVICE_NAME, self.model_name)
                if cache is not None:
                    self.model_config["cache"] = cache
            model = ChatOpenAI(**self.model_config)

            if truncate_prompt_tokens := self._get_invoke_config().get(
                "truncate_prompt_tokens"
            ):
                model = model.bind(
                    extra_body={"truncate_prompt_tokens": truncate_prompt_tokens}
                )
            if max_concurrency := self._get_invoke_config().get("max_concurrency"):
                model = model.with_config({"max_concurrency": max_concurrency})

            return model
        except Exception:
            print(f"Invalid model config: {self.model_config}")
            raise ValueError(f"No model config found for {self.provider}")

    def _get_model_name(self) -> str:
        """Get model name."""
        return CFG.inference.llm.providers[self.provider].model_config.model

    def _get_model_config(self) -> dict:
        """Get model config."""
        return CFG.inference.llm.providers[self.provider].model_config

    def _get_invoke_config(self) -> dict:
        """Get invoke config."""
        return CFG.inference.llm.providers[self.provider].invoke_config

    def truncate_text_by_tokens(
        self, text: str, max_input_tokens: int | None = None, model: str | None = None
    ) -> str:
        """Truncate text to fit within token limit"""
        if max_input_tokens is None:
            max_input_tokens = CFG.inference.llm.providers[
                self.provider
            ].max_input_tokens

        try:
            # Use tiktoken
            if model is None:
                model = self.model_name
            encoding = tiktoken.encoding_for_model(model)
            tokens = encoding.encode(text)
            decode = encoding.decode
        except Exception:
            # Use local tokenizer
            if model not in TOKENIZER_CACHE:
                TOKENIZER_CACHE[model] = AutoTokenizer.from_pretrained(
                    model, trust_remote_code=True
                )
            tokenizer = TOKENIZER_CACHE[model]
            if isinstance(text, ChatPromptValue):
                assert (
                    len(text.messages) == 1
                ), "text should be a ChatPromptValue with one message"
                text = text.messages[0].content
            tokens = tokenizer(text, add_special_tokens=False)["input_ids"]
            decode = tokenizer.decode
            # model = "gpt-4o-mini"
            # encoding = tiktoken.encoding_for_model(model)
            # tokens = encoding.encode(text)

        if len(tokens) > max_input_tokens:
            truncated_tokens = tokens[:max_input_tokens]
            truncated_text = decode(truncated_tokens)

            # 문장이 중간에 잘리지 않도록 마지막 완전한 문장까지만 반환
            # TODO: 문장 분리 방법 개선
            sentences = re.split(r"[.!?]+\s+", truncated_text)
            if len(sentences) > 1:
                result = ". ".join(sentences[:-1]) + "."
            else:
                result = truncated_text
        else:
            result = text
        return result

    def get_sync_openai_client(self, **kwargs) -> OpenAI:
        """Get OpenAI client."""
        model_config = CFG.inference.llm.providers[self.provider].get("model_config")
        params = {
            "api_key": model_config.get("openai_api_key"),
            "base_url": model_config.get("openai_api_base"),
            "timeout": model_config.get("timeout"),
            **kwargs,
        }
        params = {k: v for k, v in params.items() if v is not None}
        return OpenAI(**params)

    def get_async_openai_client(self, **kwargs) -> AsyncOpenAI:
        """Get Async OpenAI client."""
        model_config = CFG.inference.llm.providers[self.provider].get("model_config")
        params = {
            "api_key": model_config.get("openai_api_key"),
            "base_url": model_config.get("openai_api_base"),
            "timeout": model_config.get("timeout"),
            **kwargs,
        }
        params = {k: v for k, v in params.items() if v is not None}
        return AsyncOpenAI(**params)


if __name__ == "__main__":
    llm_manager = LLMManager(provider="exaone_35", use_cache=True)
    print(llm_manager.model_name)
