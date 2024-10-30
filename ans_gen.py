from utils.api import call_chat_api
from utils.common import extract_label_content, encapsulate_label_content
from ground_revise import ground_and_revise
from typing import Literal, List, Tuple
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

def solve(que_id=1, dir: Literal['test1', 'dev']='test1', verbose=False, *, port) -> Tuple[str, List[int]]:
    Question = read_que(que_id, dir)
    # print(f'Id: {que_id}')
    # print(f'Question: {question}')
    
    user_msg = f'''总体要求：

{IA}

下面是问答示例：

{get_examples()}
{Question}

推理过程：
'''

    # print(user_msg)
    if verbose:
        print(Question)

    all_IDs = []
    first_gen_result = False
    history_result = None
    for i in range(3):
        messages = [
            # { 'role': 'system', 'content': 'Answer in English regardless of the language of the question.' },
            { 'role': 'user', 'content': user_msg },
        ]

        if verbose:
            print('======= user_msg=======')
            print(user_msg[-400:])
            print('======= user_msg =======')
            print(f'------- 第 {i+1} 次回答：-------')
        resp = call_chat_api(messages, port=port)
        
        # print(resp)

        question, answer = extract_label_content(resp, 'question'), extract_label_content(resp, 'answer')
        if verbose and (first_gen_result or (question == '' and len(result) > 0)):
            print('推理链结束，根据现在的推理，选出正确的选项...')
        result = extract_label_content(resp, 'result')
        if first_gen_result or (question == '' and len(result) > 0):
            ans_choice = result
            if verbose:
                print(f'选出的答案是：{ans_choice}')
            if ans_choice == '':
                if verbose:
                    print('没有选出答案，用历史答案')
                ans_choice = history_result
            break
            
        if verbose:
            print(f'问题：{question}')
            print(f'回答：{answer}')
            print(f'result：{result if result else "无"}')
        if result:
            first_gen_result = True
            history_result = result

        IDs, answer_revised = ground_and_revise(
            Question, question, answer, max_batch=1000, verbose=verbose,
            port=port,
        )
        all_IDs.extend(IDs)
        if verbose:
            print(f'IDs: {IDs}')
            print(f'answer_revised: {answer_revised}')
            print(f'all_IDs: {all_IDs}')
        
        user_msg += '\n'
        user_msg += encapsulate_label_content(question, 'question')
        user_msg += '\n'
        
        # modify answer to the revised one
        answer = answer_revised

        user_msg += encapsulate_label_content(answer, 'answer')
        user_msg += '\n'
        
        # messages.append({
        #     'role': 'ai',
        #     'content': resp
        # }) 
    if verbose:
        print(f'Final answer: {ans_choice}')

    return ans_choice, list(set(all_IDs))

# def give_choice(S):
#     pass

if __name__ == '__main__':
    # Add argument parser
    parser = argparse.ArgumentParser(description='Answer Deduction')
    parser.add_argument('--que-id', type=int, default=1, help='Question ID')

    parser.add_argument('--port', type=int, required=True, help='Port number')
    parser.add_argument('--verbose', action='store_true', help='Verbose mode')
    
    args = parser.parse_args()
    que_id = args.que_id
    verbose = args.verbose
    port = args.port

    # solve(que_id, 'dev', verbose, port=port)
    ans_choice, all_IDs = solve(que_id, 'dev', verbose, port=port)
    print(f'Final answer: {ans_choice}')
    print(f'All IDs: {all_IDs}')
