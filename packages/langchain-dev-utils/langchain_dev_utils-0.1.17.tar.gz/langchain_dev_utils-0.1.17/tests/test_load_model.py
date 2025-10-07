import datetime

from dotenv import load_dotenv
from langchain_qwq import ChatQwen
from langchain_siliconflow import ChatSiliconFlow
import pytest

from langchain_dev_utils import (
    load_chat_model,
    batch_register_model_provider,
)

load_dotenv()

batch_register_model_provider(
    [
        {
            "provider": "dashscope",
            "chat_model": ChatQwen,
        },
        {
            "provider": "siliconflow",
            "chat_model": ChatSiliconFlow,
        },
        {
            "provider": "openrouter",
            "chat_model": "openai",
            "base_url": "https://openrouter.ai/api/v1",
        },
        {
            "provider": "zai",
            "chat_model": "openai",
        },
    ]
)


def test_model_invoke():
    model1 = load_chat_model("dashscope:qwen-flash", temperature=0)
    model2 = load_chat_model(
        "deepseek-ai/DeepSeek-V3.1", model_provider="siliconflow", temperature=0
    )
    model3 = load_chat_model(
        "openrouter:deepseek/deepseek-chat-v3.1:free", temperature=0
    )
    model4 = load_chat_model("deepseek:deepseek-chat")
    model5 = load_chat_model("zai:glm-4.5")

    assert model1.invoke("what's your name").content
    assert model2.invoke("what's your name").content
    assert model3.invoke("what's your name").content
    assert model4.invoke("what's your name").content
    assert model5.invoke("what's your name").content
    assert model1.invoke("what's your name").content


@pytest.mark.asyncio
async def test_model_ainvoke():
    model1 = load_chat_model("dashscope:qwen-flash", temperature=0)
    model2 = load_chat_model(
        "deepseek-ai/DeepSeek-V3.1", model_provider="siliconflow", temperature=0
    )
    model3 = load_chat_model(
        "openrouter:deepseek/deepseek-chat-v3.1:free", temperature=0
    )
    model4 = load_chat_model("deepseek:deepseek-chat")
    model5 = load_chat_model("zai:glm-4.5")

    response1 = await model1.ainvoke("what's your name")
    response2 = await model2.ainvoke("what's your name")
    response3 = await model3.ainvoke("what's your name")
    response4 = await model4.ainvoke("what's your name")
    response5 = await model5.ainvoke("what's your name")
    assert response1.content
    assert response2.content
    assert response3.content
    assert response4.content
    assert response5.content


def test_model_tool_calling():
    from langchain_core.tools import tool

    @tool
    def get_current_time() -> str:
        """获取当前时间戳"""
        return str(datetime.datetime.now().timestamp())

    model1 = load_chat_model("dashscope:qwen-flash", temperature=0).bind_tools(
        [get_current_time]
    )
    model2 = load_chat_model(
        "deepseek-ai/DeepSeek-V3.1", model_provider="siliconflow", temperature=0
    ).bind_tools([get_current_time])
    model3 = load_chat_model(
        "openrouter:deepseek/deepseek-chat-v3.1:free", temperature=0
    ).bind_tools([get_current_time])
    model4 = load_chat_model("deepseek:deepseek-chat").bind_tools([get_current_time])
    model5 = load_chat_model("zai:glm-4.5").bind_tools([get_current_time])

    response1 = model1.invoke("what's the time")
    assert (
        hasattr(response1, "tool_calls") and len(response1.tool_calls) == 1  # type: ignore
    )
    response2 = model2.invoke("what's the time")

    assert (
        hasattr(response2, "tool_calls") and len(response2.tool_calls) == 1  # type: ignore
    )
    response3 = model3.invoke("what's the time")
    assert (
        hasattr(response3, "tool_calls") and len(response3.tool_calls) == 1  # type: ignore
    )
    response4 = model4.invoke("what's the time")
    assert (
        hasattr(response4, "tool_calls") and len(response4.tool_calls) == 1  # type: ignore
    )
    response5 = model5.invoke("what's the time")
    assert (
        hasattr(response5, "tool_calls") and len(response5.tool_calls) == 1  # type: ignore
    )


@pytest.mark.asyncio
async def test_model_tool_calling_async():
    from langchain_core.tools import tool

    @tool
    def get_current_time() -> str:
        """获取当前时间戳"""
        return str(datetime.datetime.now().timestamp())

    model1 = load_chat_model("dashscope:qwen-flash", temperature=0).bind_tools(
        [get_current_time]
    )
    model2 = load_chat_model(
        "deepseek-ai/DeepSeek-V3.1", model_provider="siliconflow", temperature=0
    ).bind_tools([get_current_time])
    model3 = load_chat_model(
        "openrouter:deepseek/deepseek-chat-v3.1:free", temperature=0
    ).bind_tools([get_current_time])
    model4 = load_chat_model("deepseek:deepseek-chat").bind_tools([get_current_time])
    model5 = load_chat_model("zai:glm-4.5").bind_tools([get_current_time])

    response1 = await model1.ainvoke("what's the time")
    assert (
        hasattr(response1, "tool_calls") and len(response1.tool_calls) == 1  # type: ignore
    )
    response2 = await model2.ainvoke("what's the time")

    assert (
        hasattr(response2, "tool_calls") and len(response2.tool_calls) == 1  # type: ignore
    )
    response3 = await model3.ainvoke("what's the time")
    assert (
        hasattr(response3, "tool_calls") and len(response3.tool_calls) == 1  # type: ignore
    )
    response4 = await model4.ainvoke("what's the time")
    assert (
        hasattr(response4, "tool_calls") and len(response4.tool_calls) == 1  # type: ignore
    )
    response5 = await model5.ainvoke("what's the time")
    assert (
        hasattr(response5, "tool_calls") and len(response5.tool_calls) == 1  # type: ignore
    )
