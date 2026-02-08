import requests
from utils.L05_prompts import prompt_1, prompt_2, prompt_3


class LMStudioClient:
    def __init__(self, base_url="http://localhost:1234/v1", api_key=""):
        self.base_url = base_url
        self.api_key = api_key
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}" if api_key else ""
        }

    def chat_completion(self, messages, model=None, temperature=0.7, max_tokens=409600):
        """
        发送聊天完成请求到 LM Studio

        Args:
            messages: 消息列表，格式 [{"role": "user", "content": "你的问题"}]
            model: 模型名称(可选)
            temperature: 温度参数
            max_tokens: 最大token数
        """
        url = f"{self.base_url}/chat/completions"

        data = {
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False
        }

        if model:
            data["model"] = model

        try:
            response = requests.post(url, headers=self.headers, json=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise e

    def get_models(self):
        """获取可用模型列表"""
        url = f"{self.base_url}/models"
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise e


# 使用示例
def test_llm(question):
    # 创建客户端
    client = LMStudioClient()

    # 获取可用模型
    models = client.get_models()
    if models:
        print("可用模型:")
        for model in models.get("data", []):
            print(f"- {model.get('id', 'deepseek-r1-distill-llama-8b')}")

    # 发送聊天请求
    messages = [
        {"role": "user", "content": question}
    ]

    response = client.chat_completion(messages)
    if response:
        content = response.get("choices", [{}])[0].get("message", {}).get("content", "")
        print(f"\nAI回复:\n{content}")

import re

# 处理JSON返回值
def parse_embedded_dicts(string):
    results = []

    # 匹配 {...} 的部分，包括大括号
    matches = re.findall(r'\{[^{}]*\}', string)
    for match in matches:
        # 去掉大括号，按逗号拆分键值对
        inner = match.strip('{}')
        items = inner.split(',')
        d = {}
        for item in items:
            if ':' in item:
                key, value = item.split(':', 1)
                d[key.strip()] = value.strip()
        if d:
            results.append(d)

    return results

def start_llama_ds_llm_api(input_question, job):
    # 创建客户端
    client = LMStudioClient()

    # 发送挖漏洞请求
    total_question = prompt_3 + f"You only need to check the job: {job}" + "\nThe code is as follows:" + input_question
    messages = [
        {"role": "user", "content": total_question}
    ]

    # 得到回复content
    response = client.chat_completion(messages, "deepseek-r1-distill-llama-8b")
    if response:
        content = response.get("choices", [{}])[0].get("message", {}).get("content", "")
        return content
    else:
        raise SyntaxError("得不到AI的回复，请检查模型加载！")

def start_llama_sc_llm_api(input_question):
    # 创建客户端
    client = LMStudioClient()

    # 发送挖漏洞请求
    # total_question = "请分析该workflow代码红是否有自托管runner及由其产生的连带问题,你只需精简回复有分点作答并严格控制字数即可，不用详细说明。代码如下：\n" + input_question
    role_text = "你是一个杰出的GHA Workflow漏洞检测员。"
    instruction_text = "请分析该workflow代码红是否有自托管runner及由其产生的连带问题。"
    step_text = "请一步一步地想，首先判别是否存在自托管runner，再分析这个问题是否造成其他连带问题，最后判断严重性。"
    output_format_text = "如这种格式回答{is_self_hosted_runner:<Yes/No>, vulnerability_type:<Type>, Severity:<High/Mid/Low/Unknown>}。"
    total_question = role_text + instruction_text + step_text + output_format_text + "代码如下：\n" + input_question
    messages = [
        {"role": "user", "content": total_question}
    ]

    # 得到回复content
    response = client.chat_completion(messages, "StarCoder2-7B")
    if response:
        content = response.get("choices", [{}])[0].get("message", {}).get("content", "")
        return content
    else:
        raise SyntaxError("得不到AI的回复，请检查模型加载！")

def select_llm(workflow, job, llm):
    if llm == "star_coder":
        return start_llama_sc_llm_api(workflow)
    elif llm == "llama_ds":
        return start_llama_ds_llm_api(workflow, job)
    else:
        raise "有错误的模型"

if __name__ == "__main__":
    question = "你是什么模型？"
    print(select_llm(question, "silicon_ds"))