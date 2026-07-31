import json
import re

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
    content = f.read()

# Find all hidden_input JSON strings
input_matches = re.findall(r'hidden_input=(json\.dumps\(\[.*?\]\)),', content, re.DOTALL)

if len(input_matches) == 5:
    for i in range(5):
        # Extract the actual list of strings from the matched json.dumps string
        # using a simple regex since we know the format
        import ast
        list_str = re.search(r'\[.*?\]', input_matches[i], re.DOTALL).group(0)
        # However, it contains literal newlines inside string? No, it has \\n.
        # It's better to just eval the Python list.
        inputs = ast.literal_eval(list_str)
        
        # Calculate correct outputs
        correct_outputs = [funcs[i](inp) for inp in inputs]
        
        # Format as json.dumps string similar to original
        formatted_outputs = 'json.dumps([\n'
        for j, out in enumerate(correct_outputs):
            formatted_outputs += f'                        "{out}"'
            if j < len(correct_outputs) - 1:
                formatted_outputs += ',\n'
            else:
                formatted_outputs += '\n'
        formatted_outputs += '                    ])'
        
        # Replace the hidden_output corresponding to this gate
        # We need to find the specific hidden_output block
        # We can just match the i-th occurrence.
        
        # Split content into parts to replace safely
        parts = content.split('hidden_output=')
        # parts[0] has first gate before hidden_output
        # parts[1] has first gate hidden_output and then second gate
        
        # We need a robust replacement strategy
        pass

# Better approach: Just read the file line by line and reconstruct it.
lines = content.split('\n')
new_lines = []
gate_idx = -1
in_hidden_output = False

for line in lines:
    if 'hidden_input=json.dumps([' in line:
        gate_idx += 1
        
    if 'hidden_output=json.dumps([' in line:
        in_hidden_output = True
        new_lines.append(line)
        
        # Compute the outputs for the current gate
        list_str = re.search(r'\[.*?\]', input_matches[gate_idx], re.DOTALL).group(0)
        inputs = ast.literal_eval(list_str)
        correct_outputs = [funcs[gate_idx](inp) for inp in inputs]
        
        for j, out in enumerate(correct_outputs):
            if j < len(correct_outputs) - 1:
                new_lines.append(f'                        "{out}",')
            else:
                new_lines.append(f'                        "{out}"')
        new_lines.append('                    ]),')
        continue
        
    if in_hidden_output:
        if ']),' in line:
            in_hidden_output = False
        continue
        
    new_lines.append(line)

with open('database.py', 'w') as f:
    f.write('\n'.join(new_lines))
print("Successfully regenerated test cases in database.py")
