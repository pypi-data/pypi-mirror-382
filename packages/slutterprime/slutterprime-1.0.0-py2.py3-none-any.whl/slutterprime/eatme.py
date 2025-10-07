import ast, hashlib, io, re
from types import CodeType
from contextlib import redirect_stdout

__E = {"_": None, "__": None, "result": None, "digest_hashes": set()}

def _hash(code: str) -> str:
    return hashlib.sha256(code.encode()).hexdigest()

def burn(code: str) -> str:
    lines = code.split('\n')
    return ''.join(chr(ord(c) + (i % 5)) for i, l in enumerate(lines) for c in l)

def chew(code: str) -> dict:
    t = ast.parse(code)
    function_count = sum(isinstance(n, ast.FunctionDef) for n in ast.walk(t))
    line_count = len(code.strip().splitlines())
    word_count = len(re.findall(r"\w+", code))
    return {
        "functions": function_count,
        "lines": line_count,
        "words": word_count
    }

def digest(code: str) -> str:
    sandbox = {}
    try:
        exec(code, sandbox)
        __E["result"] = sandbox
        return "Execution successful"
    except Exception as e:
        return f"Execution error: {str(e)}"

def scan(code: str) -> str:
    malicious_patterns = ["document", "import sys", "eval", "exec"]
    for pattern in malicious_patterns:
        if pattern in code:
            return f"Potential malicious code detected: {pattern}"
    return None

def throwup() -> str:
    return __E.get("result", "No result yet")

def full(code: str) -> bool:
    if _hash(code) in __E["digest_hashes"]:
        return False
    __E["digest_hashes"].add(_hash(code))
    return True
def dev(name: str) -> str:
    return {"dev": "t.me/pyd9c"}