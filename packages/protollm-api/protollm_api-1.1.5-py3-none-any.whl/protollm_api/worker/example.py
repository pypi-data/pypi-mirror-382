from protollm_api.worker.models.cpp_models import CppModel
from protollm_api.worker.models.fake_models import FakeModel
from protollm_api.worker.models.open_api_llm import OpenAPILLM
from protollm_api.worker.models.vllm_models import VllMModel
from protollm_api.worker.services.broker import LLMWrap
from protollm_api.worker.config import Config

def init_fake_llm():
    return FakeModel()


def init_openapi_llm():
    return OpenAPILLM(model_url="https://api.vsegpt.ru/v1",
                      token="sk-or-vv-23fb2234f267c0947760d5e4e1a84c08e2ffb63e9e2d2731e0b07da50239c6cd",
                      default_model="openai/gpt-4o-2024-08-06",)

def init_cpp_llm():
    return CppModel("protollm_api/worker/llm-models/llama-2-7b-chat.Q4_K_M.gguf")


def init_vllm_llm():
    return VllMModel("protollm_api/worker/llm-models/llama-2-7b-chat.Q4_K_M.gguf",
                      config.tensor_parallel_size,
                      config.gpu_memory_utilisation,
                      config.token_len)


if __name__ == "__main__":
    config = Config.read_from_env()
    llm_model = init_fake_llm()
    llm_wrap = LLMWrap(llm_model=llm_model,
                       config= config)
    llm_wrap.start_connection()