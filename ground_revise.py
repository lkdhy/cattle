from utils.api import call_chat_api
from utils.common import extract_label_content
from typing import List, Tuple
import json
import random

batch_size = 80

with open('data/rules1.json', encoding='utf-8') as f:
    rules = json.load(f)

# add random seed
# random.seed(42)

# randomly shuffle the rules
# random.shuffle(rules)

with open('instructions/ground_revise_instr.txt', 'r', encoding='utf-8') as f:
    prompt = f.read()

batched_rules = []

for i in range(0, len(rules), batch_size):
    rules_str = ''
    for j in range(i, min(i + batch_size, len(rules))):
        rule = rules[j]
        rules_str += str(rule['rule_id']) + '. ' + rule['rule_text'] + '\n'
    batched_rules.append(rules_str)

def validate_ground(Question, rule_id: int, question, answer, *, verbose=False, port):
    rule_str = str(rule_id) + '. ' + rules[rule_id - 1]['rule_text']
    if verbose:
        print(f'Validating rule {rule_id}: ')
    messages=[
        {
            'role': 'user',
            'content': prompt.format(
                Question=Question, rules=rule_str, question=question, answer=answer,
            )
        }
    ]
    res = call_chat_api(messages, port=port)
    ref = extract_label_content(res, 'ref')
    try:
        if ref != 'EMPTY' and ref != '' and isinstance(int(ref), int):
            if verbose:
                print('~Correct!')
            return True
        else:
            if verbose:
                print('~Incorrect~')
            return False
    except:
        if verbose:
            print('~Incorrect~')
        return False
        

def ground_and_revise_in_one_batch(Question, rules, question, answer, *, port):
    messages=[
        {
            'role': 'user',
            'content': prompt.format(
                Question=Question, rules=rules, question=question, answer=answer,
            )
        }
    ]
    response = call_chat_api(messages, port=port)
    return response

def ground_and_revise(Question, question, answer, *, max_batch, verbose=False, port) -> Tuple[List[int], str]:
    IDs = []
    for i in range(0, min(max_batch, len(batched_rules))):
        response = ground_and_revise_in_one_batch(
            Question, batched_rules[i], question, answer,
            port=port,
        )
        if verbose:
            print(f'Batch {i+1}')
            print(response)
        ref = extract_label_content(response, 'ref')
        if ref == 'EMPTY' or ref == '':
            continue
        ref = int(ref)
        if validate_ground(Question, ref, question, answer, verbose=verbose, port=port):
            IDs.append(ref)
            answer_out = extract_label_content(response, 'answer')
            answer = answer_out
    # randomly select 10 IDs if there are more than 10
    if len(IDs) > 10:
        IDs = random.sample(IDs, 10) 
    return IDs, answer 
    
def test():
    print(batched_rules[2])
    # print(prompt.format(
    #     Question='Q',
    #     rules=batched_rules[0],
    #     question='question',
    #     answer='answer',
    # ))


if __name__ == '__main__':
    test()