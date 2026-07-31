from sqlmodel import create_engine, Session
from backend.core.config import settings

engine = create_engine(settings.DATABASE_URL, echo=True)

def get_session():
    with Session(engine) as session:
        yield session

def init_db():
    from backend.models import SQLModel, Gate, User
    from backend.core.auth import get_password_hash
    SQLModel.metadata.create_all(engine)
    
    with Session(engine) as session:
        admin_user = session.query(User).filter(User.username == "admin").first()
        if not admin_user:
            admin_user = User(
                username="admin",
                email="admin@kpriet.ac.in",
                hashed_password=get_password_hash("MssMsk@122006"),
                is_admin=True
            )
            session.add(admin_user)
            session.commit()
            
        if session.query(Gate).count() == 0:
            import json
            gates = [
                Gate(
                    id=1, 
                    name="Gate of Pairs", 
                    cipher_type="Hash Maps", 
                    points_awarded=100, 
                    problem_statement="Write a program that reads an integer K on the first line, and a sequence of numbers separated by spaces on the second line. Print the 0-based indices of the two numbers that add up to K, separated by a space. (Two Sum Problem)\n\nNote: If there are multiple valid pairs, output the indices of the first valid pair found. Handle edge cases like negative numbers, zeros, and duplicate values.",
                    sample_input="9\n2 7 11 15",
                    sample_output="0 1",
                    hidden_input=json.dumps([
                        "100\n10 25 75 40 90",
                        "6\n3 3",
                        "-4\n-1 -3 5 2",
                        "0\n0 4 3 0",
                        "18\n2 4 9 6 12",
                        "10\n5 5 5 5"
                    ]),
                    hidden_output=json.dumps([
                        "0 4",
                        "0 1",
                        "0 1",
                        "0 3",
                        "3 4",
                        "0 1"
                    ]),
                    prerequisite_gate_id=None
                ),
                Gate(
                    id=2, 
                    name="Gate of Balance", 
                    cipher_type="Stacks", 
                    points_awarded=200, 
                    problem_statement="Write a program that reads a string of brackets '()', '{}', '[]'. Print 'YES' if the brackets are valid and balanced, and 'NO' otherwise.\n\nNote: An empty string is considered balanced. Handle edge cases such as single unmatched brackets, deep nesting, and interleaved brackets.",
                    sample_input="{[()]}",
                    sample_output="YES",
                    hidden_input=json.dumps([
                        "{[(])}",
                        "",
                        "(",
                        ")",
                        "(((((())))))",
                        "{[]}()",
                        "([)]",
                        "{{{{"
                    ]),
                    hidden_output=json.dumps([
                        "NO",
                        "YES",
                        "NO",
                        "NO",
                        "YES",
                        "YES",
                        "NO",
                        "NO"
                    ]),
                    prerequisite_gate_id=1
                ),
                Gate(
                    id=3, 
                    name="Gate of Subarrays", 
                    cipher_type="Dynamic Programming", 
                    points_awarded=300, 
                    problem_statement="Write a program that reads a sequence of integers separated by spaces and prints the maximum contiguous subarray sum.\n\nAlgorithm Hint: Instead of checking all possible subarrays (which is slow), maintain a running sum. As you iterate through the array, for each element, decide whether to add it to the current running sum or start a new subarray from this element (whichever is larger). Keep track of the maximum running sum seen so far.\n\nNote: Handle edge cases such as all negative numbers (the best subarray is just the maximum single element) and all zeros.",
                    sample_input="-2 1 -3 4 -1 2 1 -5 4",
                    sample_output="6",
                    hidden_input=json.dumps([
                        "-1 -2 -3 -4",
                        "5",
                        "-5",
                        "1 2 3 4 5",
                        "0 0 0 0",
                        "-2 -1 -3 -4 -1 -2 -1 -5 -4",
                        "4 -1 2 1 -5 4"
                    ]),
                    hidden_output=json.dumps([
                        "-1",
                        "5",
                        "-5",
                        "15",
                        "0",
                        "-1",
                        "6"
                    ]),
                    prerequisite_gate_id=2
                ),
                Gate(
                    id=4, 
                    name="Gate of Permutations", 
                    cipher_type="Recursion & Backtracking", 
                    points_awarded=400, 
                    problem_statement="Write a program that reads a string of distinct lowercase English letters. Print all possible permutations of the string, sorted in lexicographical order, and separated by a space.\n\nNote: Use recursion and backtracking to generate the permutations.",
                    sample_input="abc",
                    sample_output="abc acb bac bca cab cba",
                    hidden_input=json.dumps([
                        "a",
                        "ab",
                        "abcd"
                    ]),
                    hidden_output=json.dumps([
                        "a",
                        "ab ba",
                        "abcd abdc acbd acdb adbc adcb bacd badc bcad bcda bdac bdca cabd cadb cbad cbda cdab cdba dabc dacb dbac dbca dcab dcba"
                    ]),
                    prerequisite_gate_id=3
                ),
                Gate(
                    id=5, 
                    name="Gate of the Queens", 
                    cipher_type="Advanced Backtracking", 
                    points_awarded=500, 
                    problem_statement="Write a program that reads an integer N (1 <= N <= 10). Print the total number of distinct solutions to the N-Queens puzzle, where N queens must be placed on an NxN chessboard such that no two queens attack each other.\n\nNote: Use recursion and backtracking to explore all valid queen placements.",
                    sample_input="4",
                    sample_output="2",
                    hidden_input=json.dumps([
                        "1",
                        "5",
                        "8",
                        "9"
                    ]),
                    hidden_output=json.dumps([
                        "1",
                        "10",
                        "92",
                        "352"
                    ]),
                    prerequisite_gate_id=4
                )
            ]
            session.add_all(gates)
            session.commit()