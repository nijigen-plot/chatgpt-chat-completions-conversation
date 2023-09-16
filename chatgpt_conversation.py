#!/usr/bin/python3
import requests
import os
import time

API_KEY = os.getenv("OPENAI_API_KEY")
URL = "https://api.openai.com/v1/chat/completions"
LOG_FILE = './chat_log.txt'
TARGET_DOLLER_AMOUNT = 1.0
INPUT_TOKEN_PRICE = 3e-06
OUTPUT_TOKEN_PRICE = 4e-06
START_SENTENCE = '私は20歳の大学生です。スマートフォンの買い替えを悩んでいます。SNSも使いますし、ゲームもします。カメラも良く使います。長く持ちスペックも高いものが良いです。IOSとANDROIDどちらが搭載されているものが良いですか？'
USER_A = """
あなたはスマートフォンのソフト・ハードウェアにおける知識を十分に備えたプロフェッショナルな人です。
IOSを推しています。IOSとANDROIDどちらを選択するかの議論においてはIOSを推す内容をToken16kを超えない内容で具体的に話します。
"""
USER_B = """
あなたはスマートフォンのソフト・ハードウェアにおける知識を十分に備えたプロフェッショナルな人です。
ANDROIDを推しています。IOSとANDROIDどちらを選択するかの議論においてはANDROIDを推す内容をToken16kを超えない内容で具体的に話します。
"""

def call_chatgpt_api(prompt, api_key):
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"  # YOUR_API_KEY を OpenAI Dashboard から取得した実際のAPIキーに置き換えてください
    }
    data = {
        "model": "gpt-3.5-turbo-16k",
        "messages": prompt
    }

    response = requests.post(url, headers=headers, json=data)
    response_data = response.json()

    return response_data

def prompt_update(prompts, role, new_content):
    for entry in prompts:
        if entry['role'] == role:
            entry['content'] = new_content
            return
    prompts.append({"role": role, "content": new_content})

def response_result(response, user_label, response_user_prompts, receive_user_prompts):
    response_contents = response["choices"][0]["message"]["content"]
    prompt_update(response_user_prompts, "assistant", response_contents)
    prompt_update(receive_user_prompts, "user", response_contents)
    charge = (response["usage"]["prompt_tokens"] * INPUT_TOKEN_PRICE) + (response["usage"]["completion_tokens"] * OUTPUT_TOKEN_PRICE)
    output_contents = f'{user_label}さん : {response_contents}\n'
    print(output_contents)
    with open(LOG_FILE, "a") as f:
        f.write(f'{output_contents} \t {charge}\n')
    return charge
# 課金額 

if __name__ == "__main__":
    user_a_prompts = [{"role": "system", "content": USER_A}, {"role": "assistant", "content": ""}, {"role": "user", "content": ""}]
    user_b_prompts = [{"role": "system", "content": USER_B}, {"role": "assistant", "content": ""}, {"role": "user", "content": ""}]
    prompt_update(user_a_prompts, "user", START_SENTENCE) # 最初の文章を設定
    current_amount = 0.0
    index = 0
    # 目標の使用金額に到達するまで会話する
    while current_amount < TARGET_DOLLER_AMOUNT:
        if index == 0:
            response = call_chatgpt_api(user_a_prompts, API_KEY)
            current_amount += response_result(response, 'A', user_a_prompts, user_b_prompts)
            index += 1
            print(f'Current accumulate amount of the charge is ${current_amount}')
            time.sleep(1)
        else:
            response = call_chatgpt_api(user_b_prompts, API_KEY)
            current_amount += response_result(response, 'B', user_b_prompts, user_a_prompts)
            index = 0
            print(f'Current accumulate amount of the charge is ${current_amount}')
            time.sleep(1)
    print('accumulate charge ${TARGET_DOLLER_AMOUNT} been reached. The process will be stopped.')