"""
    name: fixup
    once: false
    origin: tgpy://module/fixup
    priority: 1674449503.985582
    save_locals: true
"""
import ast
from collections import namedtuple
import functools
import inspect
import itertools
import tokenize

RESERVED_NAMES = ("and", "as", "assert", "break", "class", "continue", "def", "del", "elif", "else", "except", "finally", "for", "from", "global", "if", "import", "in", "is", "lambda", "nonlocal", "not", "or", "pass", "raise", "return", "try", "while", "with", "yield", "async", "await", "match", "case")

FIXUP_OPERATORS = {}

class FixupOperatorInfix:
    def __init__(self, fn, associativity):
        self.fn = fn
        self.associativity = associativity

    def __repr__(self):
        return f"<InfixOperator, {self.associativity}-associative, code {self.fn}>"


def tokenize_code(code, inline=False):
    lines = [line + ("" if inline else "\n") for line in code.splitlines() if line.strip()] + [""]
    i = 0
    def generator():
        nonlocal i
        i += 1
        return lines[i - 1]
    tokens = list(tokenize.generate_tokens(generator))
    if inline:
        return [token for token in tokens if token.type != tokenize.ENDMARKER]
    else:
        return tokens


def fixup_code(code):
    if code.strip().startswith("."):
        return code

    try:
        all_tokens = tokenize_code(code)
    except Exception:
        return code

    fixed_tokens = []
    fixed = False
    is_code = False

    for is_op, group_tokens in itertools.groupby(all_tokens, lambda token: token.type in (tokenize.ERRORTOKEN, tokenize.OP) and token.string not in ("(", ")")):
        group_tokens = list(group_tokens)

        for token in group_tokens:
            if token.string.strip():
                is_code = is_code or (token.type not in (tokenize.NAME, tokenize.STRING, tokenize.NUMBER) and token.string not in ("(", ")", ".", ",", "?", "!", "-", "+", "*", "/", "%", "@", "=")) or token.string in tgpy.variables or token.string in globals() or token.string in __builtins__
            if token.type == tokenize.NAME and not token.string.isascii():
                return code

        if not is_op:
            fixed_tokens += group_tokens
            continue

        for is_space, tokens in itertools.groupby(group_tokens, lambda token: token.string.strip() == ""):
            if is_space:
                fixed_tokens += tokens
                continue

            tokens = list(tokens)

            s = "".join(token.string for token in tokens)
            name = s.strip()

            if name not in FIXUP_OPERATORS:
                if any(token.type == tokenize.ERRORTOKEN for token in tokens):
                    return code
                fixed_tokens += tokens
                continue

            fixed = True
            op = FIXUP_OPERATORS[name]
            if isinstance(op, FixupOperatorInfix):
                part = f"| _FixupOperatorInfix({repr(name)}) |"
            elif isinstance(op, str):
                part = op
            else:
                assert False

            for token in tokenize_code(part, inline=True):
                token = namedtuple("Token", "type string")(token.type, token.string)
                fixed_tokens.append(token)


    tokens = fixed_tokens
    fixed_tokens = []

    last_token_callable = False
    nesting = 0
    prev_line = -1

    for token in tokens:
        if token.string in "({[":
            nesting += 1
        elif token.string in ")}]":
            nesting -= 1

        if token.type in (tokenize.NAME, tokenize.NUMBER, tokenize.STRING) and token.string not in RESERVED_NAMES and (not hasattr(token, "start") or token.start[0] == prev_line or nesting > 0) and last_token_callable:
            fixed = True
            for token1 in tokenize_code("** _FixupOperatorInfix('(&)') **", inline=True):
                fixed_tokens.append((token1.type, token1.string))

        fixed_tokens.append(token)
        last_token_callable = token.type in (tokenize.NAME, tokenize.NUMBER, tokenize.STRING) and token.string not in RESERVED_NAMES or token.string == ")"
        if hasattr(token, "end"):
            prev_line = token.end[0]

    if not fixed or not is_code:
        return code

    try:
        fixed_code = tokenize.untokenize(fixed_tokens)
    except Exception:
        return code

    fixed_code_lines = fixed_code.encode().split(b"\n")
    try:
        tree = ast.parse(fixed_code)
    except Exception:
        return fixed_code

    def is_op(node):
        return isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "_FixupOperatorInfix"

    def contains_parenthesis_between(a, b):
        if a.end_lineno == b.lineno:
            s = fixed_code_lines[a.end_lineno - 1][a.end_col_offset:b.col_offset]
        else:
            s = fixed_code_lines[a.end_lineno - 1][a.end_col_offset:] + b"\n"
            for line in range(a.end_lineno, b.lineno):
                s += line + b"\n"
            s += fixed_code_lines[b.lineno][:b.col_offset]
        return b"(" in s or b")" in s

    def patch(root_node):
        for node in ast.walk(root_node):
            if isinstance(node, ast.BinOp) and isinstance(node.left, ast.BinOp) and is_op(node.left.right) and isinstance(node.left.left, ast.BinOp) and not contains_parenthesis_between(node.left.left, node.left.right) and isinstance(node.left.left.left, ast.BinOp) and is_op(node.left.left.left.right):
                a = node.left.left.left.left
                op1 = node.left.left.left.right
                b = node.left.left.right
                op2 = node.left.right
                c = node.right
                if FIXUP_OPERATORS[op1.args[0].value].associativity == "right":
                    node.left = ast.BinOp(a, ast.BitOr(), op1)
                    node.right = ast.BinOp(ast.BinOp(b, ast.BitOr(), op2), ast.BitOr(), c)
                    ast.fix_missing_locations(node)
                    patch(node)

            elif isinstance(node, ast.BinOp) and isinstance(node.right, ast.BinOp) and is_op(node.right.left) and isinstance(node.right.right, ast.BinOp) and not contains_parenthesis_between(node.right.left, node.right.right) and isinstance(node.right.right.right, ast.BinOp) and is_op(node.right.right.right.left):
                a = node.left
                op1 = node.right.left
                b = node.right.right.left
                op2 = node.right.right.right.left
                c = node.right.right.right.right
                if FIXUP_OPERATORS[op1.args[0].value].associativity == "left":
                    node.left = ast.BinOp(a, ast.BitOr(), ast.BinOp(op1, ast.BitOr(), b))
                    node.right = ast.BinOp(op2, ast.BitOr(), c)
                    ast.fix_missing_locations(node)
                    patch(node)

    patch(tree)

    ast.fix_missing_locations(tree)
    return ast.unparse(tree)


class _FixupOperatorInfix:
    def __init__(self, name):
        self.name = name
    def __or__(self, rhs):
        return _FixupOperatorPostfix(self.name, rhs)
    def __pow__(self, rhs):
        return _FixupOperatorPostfix(self.name, rhs)
    def __ror__(self, lhs):
        return _FixupOperatorPrefix(self.name, lhs)
    def __rpow__(self, lhs):
        return _FixupOperatorPrefix(self.name, lhs)

class _FixupOperatorPrefix:
    def __init__(self, name, lhs):
        self.name = name
        self.lhs = lhs
    def __or__(self, rhs):
        return FIXUP_OPERATORS[self.name].fn(self.lhs, rhs)
    def __pow__(self, rhs):
        return FIXUP_OPERATORS[self.name].fn(self.lhs, rhs)

class _FixupOperatorPostfix:
    def __init__(self, name, rhs):
        self.name = name
        self.rhs = rhs
    def __ror__(self, lhs):
        return FIXUP_OPERATORS[self.name].fn(lhs, self.rhs)
    def __rpow__(self, lhs):
        return FIXUP_OPERATORS[self.name].fn(lhs, self.rhs)

tgpy.add_code_transformer("fixup", fixup_code)


class autocurry:
    def __init__(self, f, args=[], kwargs={}):
        self.f = f
        self.args = args
        self.kwargs = kwargs
        self.__name__ = f.__name__
        self.__wrapped__ = f

        signature = inspect.signature(f)
        self.non_default_args = sum(
            param.default is inspect.Parameter.empty
            and param.kind in (
                inspect.Parameter.POSITIONAL_ONLY,
                inspect.Parameter.POSITIONAL_OR_KEYWORD,
                inspect.Parameter.KEYWORD_ONLY
            )
            for param in signature.parameters.values()
        )

    def __call__(self, *args, **kwargs):
        args = self.args + list(args)
        kwargs = self.kwargs | kwargs
        if len(args) + len(self.kwargs) >= self.non_default_args:
            return self.f(*args, **kwargs)
        else:
            return autocurry(self.f, args, kwargs)

def call_curry(f, x):
    return autocurry(f)(x)

FIXUP_OPERATORS["$"] = FixupOperatorInfix(call_curry, "right")
FIXUP_OPERATORS["(&)"] = FixupOperatorInfix(call_curry, "left")
FIXUP_OPERATORS["\\"] = "lambda"
FIXUP_OPERATORS["->"] = ":"
FIXUP_OPERATORS["!!"] = FixupOperatorInfix(lambda a, x: a[x], "left")
