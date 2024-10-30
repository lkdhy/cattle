from ans_gen import solve
import argparse
from tqdm import tqdm
import json
import os

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, required=True, help='API Port number')
    parser.add_argument('--min-num', type=int, required=True, help='Minimum question ID')
    parser.add_argument('--max-num', type=int, required=True, help='Maximum question ID')
    parser.add_argument('--ckpt-len', type=int, default=100, help='length of one checkpoint interval')

    args = parser.parse_args()
    res = []
    
    os.makedirs('result', exist_ok=True)
    os.makedirs('result/checkpoint', exist_ok=True)
    
    cnt = 0
    for que_id in tqdm(range(args.min_num, args.max_num+1)):
        ans_choice, all_IDs = solve(que_id, 'dev', verbose=False, port=args.port)
        res.append({
            'question_id': que_id,
            'answer': ans_choice,
            'rule_id': all_IDs
        })
        # implement checkpoint
        cnt += 1
        if cnt % args.ckpt_len == 0:
            with open(f'result/checkpoint/{args.min_num}_{args.max_num}_{cnt}.json', 'w') as f:
                json.dump(res, f, indent=4)
    
    with open(f'result/{args.min_num}_{args.max_num}.json', 'w') as f:
        json.dump(res, f, indent=4)

if __name__ == '__main__':
    main()