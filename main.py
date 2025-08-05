import re
from collections import Counter

def generate_gree_expression(valid_strings, invalid_strings):
    if not valid_strings:
        return "^$"
    if not invalid_strings:
        return "^.*$"
    
    patterns = []
    patterns.extend(find_delimiter_patterns(valid_strings, invalid_strings))
    patterns.extend(find_char_type_patterns(valid_strings, invalid_strings))
    patterns.extend(find_start_patterns(valid_strings, invalid_strings))
    patterns.extend(find_end_patterns(valid_strings, invalid_strings))
    patterns.extend(find_substring_patterns(valid_strings, invalid_strings))
    
    valid_patterns = [p for p in patterns if validate_pattern(p, valid_strings, invalid_strings)]
    
    if valid_patterns:
        valid_patterns.sort(key=get_pattern_priority)
        return valid_patterns[0]
    
    return "^.*$"

def validate_pattern(pattern, valid_strings, invalid_strings):
    if len(pattern) > 20:
        return False
    try:
        regex = re.compile(pattern)
        return (all(regex.fullmatch(s) for s in valid_strings) and 
                not any(regex.fullmatch(s) for s in invalid_strings))
    except:
        return False

def find_start_patterns(valid_strings, invalid_strings):
    patterns = []
    if valid_strings:
        starts = set(s[0] for s in valid_strings if s)
        if len(starts) == 1:
            char = starts.pop()
            if not any(s and s[0] == char for s in invalid_strings):
                patterns.append(f"^[{char}].+$")
    return patterns

def find_end_patterns(valid_strings, invalid_strings):
    patterns = []
    if valid_strings:
        ends = set(s[-1] for s in valid_strings if s)
        if len(ends) == 1:
            char = ends.pop()
            if not any(s and s[-1] == char for s in invalid_strings):
                patterns.append(f"^.+[{char}]$")
    return patterns

def find_char_type_patterns(valid_strings, invalid_strings):
    patterns = []
    
    valid_has_digit = any(any(c.isdigit() for c in s) for s in valid_strings)
    invalid_has_digit = any(any(c.isdigit() for c in s) for s in invalid_strings)
    
    if not valid_has_digit and invalid_has_digit:
        patterns.append("^\\D+$")
    
    return patterns

def find_delimiter_patterns(valid_strings, invalid_strings):
    patterns = []
    
    email_pattern = build_email_pattern(valid_strings, invalid_strings)
    if email_pattern:
        patterns.append(email_pattern)
    
    common_chars = get_common_chars(valid_strings)
    
    for char in common_chars:
        if not any(char in s for s in invalid_strings):
            if all(0 < s.index(char) < len(s) - 1 for s in valid_strings):
                if char == '-':
                    patterns.append(f"^.+-.+$")
                else:
                    patterns.append(f"^.+{re.escape(char)}.+$")
    
    return patterns

def find_substring_patterns(valid_strings, invalid_strings):
    patterns = []
    
    if not valid_strings:
        return patterns
    
    for length in range(1, min(4, len(min(valid_strings, key=len)) + 1)):
        substrings = get_common_substrings(valid_strings, length)
        
        for sub in substrings:
            if not any(sub in s for s in invalid_strings):
                patterns.append(f"^.*{re.escape(sub)}.*$")
    
    return patterns

def get_common_substrings(strings, length):
    if not strings:
        return []
    
    common = get_substrings(strings[0], length)
    for s in strings[1:]:
        common &= get_substrings(s, length)
    
    return list(common)

def get_substrings(string, length):
    return {string[i:i+length] for i in range(len(string) - length + 1)}

def get_common_chars(strings):
    if not strings:
        return set()
    common = set(strings[0])
    for s in strings[1:]:
        common &= set(s)
    return common

def build_email_pattern(valid_strings, invalid_strings):
    if not all('@' in s and '.' in s.split('@')[-1] for s in valid_strings):
        return None
    if any('@' in s and '.' in s.split('@')[-1] for s in invalid_strings):
        return None
    
    before_at_pattern = "\\D+" if all(not any(c.isdigit() for c in s.split('@')[0]) for s in valid_strings) else ".+"
    after_at_pattern = "\\w+\\.\\w+"
    
    return f"^{before_at_pattern}@{after_at_pattern}$"

def get_pattern_priority(pattern):
    if '@' in pattern and '\\.' in pattern:
        return (0, len(pattern))
    elif '\\D' in pattern or '\\w' in pattern:
        return (1, len(pattern))
    elif pattern.startswith('^[') or pattern.endswith(']$'):
        return (2, len(pattern))
    elif '.*' in pattern:
        return (4, len(pattern), pattern.count('.*'))
    else:
        return (3, len(pattern))

# Test cases
if __name__ == "__main__":
    test_cases = [
        (["abc", "def"], ["123", "456"], "^\\D+$"),
        (["aaa", "abb", "acc"], ["bbb", "bcc", "bca"], "^[a].+$"),
        (["abc1", "bbb1", "ccc1"], ["abc", "bbb", "ccc"], "^.+[1]$"),
        (["abc-1", "bbb-1", "cde-1"], ["abc1", "bbb1", "cde1"], "^.+-.+$"),
        (["user@domain.com", "test@site.net"], ["invalid@domain", "test.com"], "^\\D+@\\w+\\.\\w+$")
    ]
    
    for i, (valid, invalid, expected) in enumerate(test_cases, 1):
        result = generate_gree_expression(valid, invalid)
        print(f"Scroll {i}: {result} (expected: {expected})")