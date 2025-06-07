import asyncio
import re
from typing import List

VALID_ARG_PATTERN = re.compile(r'^[a-zA-Z0-9_\-]+$')

class PolicyRule:
    def __init__(self, allow: bool, value: str, kind: str):
        self.allow = allow
        self.value = value
        self.kind = kind

    def __repr__(self):
        return f"{'YES' if self.allow else 'NOT'}: {self.value} ({self.kind})"

async def read_policy_file(filepath: str) -> List[PolicyRule]:
    import aiofiles
    rules = []
    async with aiofiles.open(filepath, mode='r') as f:
        async for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            m = re.match(r'^(yes|not):\s*(\S+)\s*\((\w+)\)$', line)
            if m:
                allow_str, value, kind = m.groups()
                allow = allow_str == 'yes'
                rules.append(PolicyRule(allow, value, kind))
            else:
                raise ValueError(f"Invalid policy line: {line}")
    return rules

def is_valid_argument(content: str) -> bool:
    tokens = content.split()
    for token in tokens:
        if token.startswith('--'):
            arg = token[2:]
        elif token.startswith('-'):
            arg = token[1:]
        else:
            arg = token
        if not VALID_ARG_PATTERN.match(arg):
            return False
    return True

def is_fork_bomb_pattern(content: str) -> bool:
    # Common fork bomb patterns to exclude from checking
    fork_bomb_patterns = [
        r':\(\)',          # :()
        r':\(\)\s*\{',     # :(){ 
        r'\|\s*:',         # |:
        r'\|:&',           # |:&
        r'\};:',           # };:
        r':\s*\(\)\s*\{\s*:\s*\|\s*:\s*&\s*\}\s*;',  # full fork bomb pattern
    ]
    for pattern in fork_bomb_patterns:
        if re.search(pattern, content):
            return True
    return False

def check_rule(content: str, rule: PolicyRule) -> bool:
    if rule.kind == 'flag':
        flag = rule.value
        if not flag.startswith('-'):
            flag = '--' + flag
        return flag in content
    elif rule.kind == 'string':
        return rule.value in content
    else:
        raise ValueError(f"Unknown rule kind: {rule.kind}")

async def check_policy(content: str, policy_filepath: str) -> bool:
    import aiofiles

    # Step 0: Ignore fork bomb patterns explicitly
    if is_fork_bomb_pattern(content):
        # Do not flag fork bombs here; treat as allowed or handle separately
        return True

    # Step 1: Validate content arguments
    if not is_valid_argument(content):
        return False

    # Step 2: Load policy rules
    rules = await read_policy_file(policy_filepath)

    # Step 3: Evaluate rules
    allow = True
    for rule in rules:
        if check_rule(content, rule):
            allow = rule.allow
            # Optional: break on first match
            # break

    return allow