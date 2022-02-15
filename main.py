#!/usr/bin/env python3

from typing import Iterator
from stack import Stack
from enum import Enum
import sys

class State(Enum):
    NONE = 0
    NUM = 2

OPS = {
    '+': lambda a, b: a + b,
    '-': lambda a, b: a - b,
    '*': lambda a, b: a * b,
    '/': lambda a, b: a / b,
}
PARENS = '()'

def token_scanner(expr: str) -> Iterator[str | int | float]:
    state = State.NONE
    expr = expr.strip() + ' '
    start_index = 0
    num_parse_fn = int
    for index, ch in enumerate(expr):
        if state == State.NONE:
            if ch in OPS or ch in PARENS:
                yield ch
            elif ch.isnumeric():
                state = State.NUM
                start_index = index
                num_parse_fn = int
        elif state == State.NUM:
            if ch == '.':
                num_parse_fn = float
            elif not ch.isnumeric() and ch != '.':
                state = State.NONE
                yield num_parse_fn(expr[start_index:index])
                if ch in OPS or ch in PARENS:
                    yield ch

def parse_prefix(tokens: Iterator[str | int | float]) -> None | int | float:
    def helper(op: str | None) -> None | int | float:
        if op is None:
            return None
        a = next(tokens, None)
        if a in OPS:
            a = helper(a)
        if a is None:
            return None
        b = next(tokens, None)
        if b in OPS:
            b = helper(b)
        if b is None:
            return None
        return OPS[op](a, b)
    result = helper(next(tokens, None))
    if next(tokens, None) is not None:
        return None
    return result

def parse_postfix(tokens: Iterator[str | int | float]) -> None | int | float:
    operands = Stack()
    for token in tokens:
        if token in OPS:
            if len(operands) < 2:
                return None
            b, a = (operands.pop() for _ in range(2))
            operands.push(OPS[token](a, b))
        else:
            operands.push(token)
    if len(operands) == 1:
        return operands.pop()
    else:
        return None

def parse_paren_infix(tokens: Iterator[str | int | float]) -> None | int | float:
    result = next(tokens, None)
    if isinstance(result, int | float):
        return result
    if result == '(':
        a = parse_paren_infix(tokens)
        op = next(tokens, None)
        b = parse_paren_infix(tokens)
        if next(tokens, None) != ')' or None in [a, op, b]:
            return None
        return OPS[op](a, b)
    return None

def get_int(prompt: str, min_value: int, max_value: int) -> int:
    while 1:
        num = input(f'{prompt}\nEnter an integer between {min_value} and {max_value}> ')
        try:
            num = int(num)
        except ValueError:
            print('The input could not be converted to an integer\n')
            continue
        if num < min_value:
            print(f'The input is not allowed to be less than {min_value}')
            continue
        elif num > max_value:
            print(f'The input is not allowed to be more than {max_value}')
            continue
        return num

def main():
    '''Driver Code'''
    while 1:
        choice = get_int(
            '''What kind of mathmatical expressions do you want to parse?
1) prefix                e.g. + 1 * 2 3
2) postfix               e.g. 1 2 3 * +
3) parenthetical infix   e.g. (1 + (2 * 3))
4) quit
''',
            1,
            4
        )
        match choice:
            case 1:
                parser_name = 'prefix'
                parser = parse_prefix
            case 2:
                parser_name = 'postfix'
                parser = parse_postfix
            case 3:
                parser_name = 'parenthetical infix'
                parser = parse_paren_infix
            case 4:
                return
        while 1:
            try:
                expr = input(f'Enter {parser_name} expression> ')
            except EOFError:
                break
            if expr == 'quit' or expr == 'q':
                break
            invalid = False
            operators = Stack()
            result = parser(token_scanner(expr))
            if result is None:
                print(f'\033[41mError:\033[0m Invalid expression {expr!r}')
            else:
                print(f'{expr} = {result}')

if __name__ == '__main__':
    main()
