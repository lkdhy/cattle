from utils.api import call_chat_api
from utils.common import extract_label_content, encapsulate_label_content
from ground_revise import ground_and_revise
from typing import Literal
import argparse
import json
import os

with open('instructions/ans_deduction_instr_zh.txt', 'r') as file:
    IA = file.read()

def get_examples() -> str:
    res = ''
    for file in os.listdir('instructions'):
        if not file.startswith('example') or not file.endswith('.txt'):
            continue
        with open(f'instructions/{file}', 'r') as f:
            res += f.read()
    return res

def read_que(que_id: int, dir: Literal['test1', 'dev'] = 'test1') -> str:
    with open(f'data/{dir}.json') as file:
        questions = json.load(file)

    assert questions[que_id - 1]['question_id'] == str(que_id)
    return questions[que_id - 1]['question_text']

def test(que_id=1, dir: Literal['test1', 'dev'] = 'test1'):
    Question = read_que(que_id, dir)
    # print(f'Id: {que_id}')
    # print(f'Question: {question}')
    
    user_msg_0 = f'''总体要求：

{IA}

下面是问答示例：

{get_examples()}
{Question}

推理过程：
'''

    # print(user_msg_0)
    print(Question)

    for i in range(2):
        messages = [
            # { 'role': 'system', 'content': 'Answer in English regardless of the language of the question.' },
            { 'role': 'user', 'content': user_msg_0 },
        ]
        # print(user_msg_0[-200:])
        print(f'------- 第 {i+1} 次回答：-------')
        resp = call_chat_api(messages)
        
        # print(resp)

        question, answer = extract_label_content(resp, 'question'), extract_label_content(resp, 'answer')
        result = extract_label_content(resp, 'result')

        print(f'问题：{question}')
        print(f'回答：{answer}')
        print(f'result：{result if result else "无"}')
        
        IDs, answer_revised = ground_and_revise(Question, question, answer, max_batch=20)
        print(f'IDs: {IDs}')
        print(f'answer_revised: {answer_revised}')
        
        user_msg_0 += '\n'
        user_msg_0 += encapsulate_label_content(question, 'question')
        user_msg_0 += '\n'
        
        # modify answer to the revised one
        answer = answer_revised

        user_msg_0 += encapsulate_label_content(answer, 'answer')
        user_msg_0 += '\n'
        
        # messages.append({
        #     'role': 'ai',
        #     'content': resp
        # }) 

if __name__ == '__main__':
    # Add argument parser
    parser = argparse.ArgumentParser(description='Answer Deduction')
    parser.add_argument('--que-id', type=int, default=1, help='Question ID')
    
    args = parser.parse_args()
    que_id = args.que_id

    test(que_id, 'dev')