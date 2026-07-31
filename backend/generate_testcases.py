import json
import ast

def gate1(input_str):
    lines = input_str.strip().split('\n')
    k = int(lines[0].strip())
    arr = list(map(int, lines[1].strip().split()))
    n = len(arr)
    for i in range(n):
        for j in range(i+1, n):
            if arr[i] + arr[j] == k:
                return f"{i} {j}"
    return ""

def gate2(input_str):
    s = input_str.strip()
    stack = []
    pairs = {')': '(', '}': '{', ']': '['}
    for char in s:
        if char in "({[":
            stack.append(char)
        elif char in ")}]":
            if not stack or stack[-1] != pairs[char]:
                return "NO"
            stack.pop()
    return "YES" if not stack else "NO"

def gate3(input_str):
    arr = list(map(int, input_str.strip().split()))
    if not arr: return "0"
    n = len(arr)
    max_sum = -float('inf')
    for i in range(n):
        curr_sum = 0
        for j in range(i, n):
            curr_sum += arr[j]
            max_sum = max(max_sum, curr_sum)
    return str(max_sum)

def gate4(input_str):
    if not input_str.strip(): return ""
    arr = list(map(int, input_str.strip().split()))
    arr.sort()
    return " ".join(map(str, arr))

def gate5(input_str):
    if not input_str.strip(): return "0"
    arr = list(map(int, input_str.strip().split()))
    n = len(arr)
    water = 0
    for i in range(n):
        left_max = max(arr[:i+1]) if i >= 0 else 0
        right_max = max(arr[i:]) if i < n else 0
        water += max(0, min(left_max, right_max) - arr[i])
    return str(water)

funcs = [gate1, gate2, gate3, gate4, gate5]

with open('database.py', 'r') as f:
    lines = f.readlines()

new_lines = []
gate_idx = -1
in_hidden_output = False

inputs_for_gates = [
    [
        "100\n10 25 75 40 90",
        "6\n3 3",
        "-4\n-1 -3 5 2",
        "0\n0 4 3 0",
        "18\n2 4 9 6 12",
        "10\n5 5 5 5"
    ],
    [
        "{[(])}",
        "",
        "(",
        ")",
        "(((((())))))",
        "{[]}()",
        "([)]",
        "{{{{"
    ],
    [
        "-1 -2 -3 -4",
        "5",
        "-5",
        "1 2 3 4 5",
        "0 0 0 0",
        "-2 -1 -3 -4 -1 -2 -1 -5 -4",
        "4 -1 2 1 -5 4"
    ],
    [
        "1 2 0 1 2 0 1 2 0",
        "0",
        "2 2 2 2",
        "0 1 2",
        "2 1 0",
        "1 1 1 0 0 2"
    ],
    [
        "4 2 0 3 2 5",
        "5",
        "1 1 1 1",
        "5 4 3 2 1",
        "1 2 3 4 5",
        "4 2 3",
        "0 0 0 0"
    ]
]

for line in lines:
    if 'hidden_input=json.dumps([' in line:
        gate_idx += 1
        new_lines.append(line)
        continue
        
    if 'hidden_output=json.dumps([' in line:
        in_hidden_output = True
        new_lines.append(line)
        
        correct_outputs = [funcs[gate_idx](inp) for inp in inputs_for_gates[gate_idx]]
        
        for j, out in enumerate(correct_outputs):
            if j < len(correct_outputs) - 1:
                new_lines.append(f'                        "{out}",\n')
            else:
                new_lines.append(f'                        "{out}"\n')
        continue
        
    if in_hidden_output:
        if ']),' in line:
            in_hidden_output = False
            new_lines.append(line)
        continue
        
    new_lines.append(line)

with open('database.py', 'w') as f:
    f.writelines(new_lines)
print("Successfully regenerated database.py")
