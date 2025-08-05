#Jared Chan Xu Yang
import re
from collections import Counter

def generate_gree_expression(valid_strings, invalid_strings):
    if not valid_strings:
        return "^$"
    if not invalid_strings:
        return "^.*$"
    
    # Try patterns in order of specificity
    pattern_generators = [
        check_character_class,
        check_email_pattern,
        check_delimiter_pattern,
        check_prefix_pattern,
        check_suffix_pattern,
        check_common_substring,
        generate_fallback_pattern
    ]
    
    for generator in pattern_generators:
        pattern = generator(valid_strings, invalid_strings)
        if pattern:
            return pattern
    
    return "^.*$"

def is_valid_pattern(pattern, valid_strings, invalid_strings):
    if len(pattern) > 20:
        return False
    
    try:
        regex = re.compile(pattern)
        return (all(regex.fullmatch(s) for s in valid_strings) and 
                not any(regex.fullmatch(s) for s in invalid_strings))
    except:
        return False

def check_character_class(valid_strings, invalid_strings):
    # Check letter vs digit pattern
    if (all(s.isalpha() for s in valid_strings) and 
        all(s.isdigit() for s in invalid_strings)):
        pattern = "^\\D+$"
        if is_valid_pattern(pattern, valid_strings, invalid_strings):
            return pattern
    return None

def check_email_pattern(valid_strings, invalid_strings):
    # Check if all valid are emails and invalid are not
    def is_email(s):
        return '@' in s and '.' in s.split('@')[-1]
    
    if (all(is_email(s) for s in valid_strings) and 
        not any(is_email(s) for s in invalid_strings)):
        pattern = "^\\D+@\\w+\\.\\w+$"
        if is_valid_pattern(pattern, valid_strings, invalid_strings):
            return pattern
    return None

def check_delimiter_pattern(valid_strings, invalid_strings):
    delimiters = ['-', '_', '.', '@']
    
    for delim in delimiters:
        if (all(delim in s for s in valid_strings) and 
            not any(delim in s for s in invalid_strings)):
            pattern = f"^.+{re.escape(delim)}.+$"
            if is_valid_pattern(pattern, valid_strings, invalid_strings):
                return pattern
    return None

def check_prefix_pattern(valid_strings, invalid_strings):
    return check_boundary_pattern(valid_strings, invalid_strings, 
                                get_chars=lambda s: s[0], 
                                format_pattern=lambda c: f"^[{c}].+$")

def check_suffix_pattern(valid_strings, invalid_strings):
    return check_boundary_pattern(valid_strings, invalid_strings,
                                get_chars=lambda s: s[-1],
                                format_pattern=lambda c: f"^.+[{c}]$")

def check_boundary_pattern(valid_strings, invalid_strings, get_chars, format_pattern):
    chars = set(get_chars(s) for s in valid_strings if s)
    if len(chars) == 1:
        pattern = format_pattern(chars.pop())
        if is_valid_pattern(pattern, valid_strings, invalid_strings):
            return pattern
    return None

def check_common_substring(valid_strings, invalid_strings):
    for length in range(1, 4):
        substrings = find_common_substrings(valid_strings, length)
        
        for substring in substrings:
            if not any(substring in s for s in invalid_strings):
                pattern = f"^.*{re.escape(substring)}.*$"
                if is_valid_pattern(pattern, valid_strings, invalid_strings):
                    return pattern
    return None

def find_common_substrings(strings, length):
    counts = Counter()
    for string in strings:
        for i in range(len(string) - length + 1):
            counts[string[i:i+length]] += 1
    
    return [sub for sub, count in counts.items() 
            if count == len(strings)]

def generate_fallback_pattern(valid_strings, invalid_strings):
    chars = set()
    for string in valid_strings:
        chars.update(string)
    
    pattern = f"^[{re.escape(''.join(sorted(chars)))}]+$"
    if is_valid_pattern(pattern, valid_strings, invalid_strings):
        return pattern
    return None

# Test cases
if __name__ == "__main__":
    test_cases = [
        (["abc", "def"], ["123", "456"], "^\\D+$"),
        (["aaa", "abb", "acc"], ["bbb", "bcc", "bca"], "^[a].+$"),
        (["abc1", "bbb1", "ccc1"], ["abc", "bbb", "ccc"], "^.+[1]$"),
        (["abc-1", "bbb-1", "cde-1"], ["abc1", "bbb1", "cde1"], "^.+-.+$"),
        (["foo@abc.com", "bar@def.net"], ["baz@abc", "qux.com"], "^\\D+@\\w+\\.\\w+$")
    ]
    
    for i, (valid, invalid, expected) in enumerate(test_cases, 1):
        result = generate_gree_expression(valid, invalid)
        print(f"Scroll {i}: {result} (expected: {expected})")