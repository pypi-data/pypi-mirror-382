# SPDX-License-Identifier: BSD-3-Clause
# Copyright © 2025 UChicago Argonne, LLC. All rights reserved.
# Part of fortfmt-fix. See the LICENSE file in the project root for the full license
# text and warranty disclaimer (BSD 3-Clause).

import re
from dataclasses import dataclass
from typing import Dict, Tuple

# Centralize defaults so tests can import; these match Intel/DEC compiler behavior
DEFAULTS: Dict[str, str] = {
    "I": "I12",         # Iw (or I23 if int64=True)
    "L": "L2",          # logical (updated to match Intel/DEC behavior)
    "F": "F25.16",      # Fw.d
    "E": "E25.16E3",    # Ew.dE#
    "D": "D25.16E3",    # Dw.dE#
    "G": "G25.16",      # Gw.d
    "ES": "ES25.16E3",
    "EN": "EN25.16E3",
}

@dataclass
class Options:
    int64: bool = False
    listify_reads: bool = False
    trace: bool = False

# ------------------------- Utilities -------------------------

def _looks_like_format_literal(content: str) -> bool:
    """
    Heuristic: the literal must be parenthesized and contain at least
    one edit-descriptor token (ES|EN|F|E|D|G|I|A|X|T) followed by ., digit,
    right-paren, comma, whitespace, or end-of-string.
    
    Also check that it's not just a quoted string in parentheses.
    """
    s = content.strip()
    if not (len(s) >= 2 and s[0] == "(" and s[-1] == ")"):
        return False
    inside = s[1:-1].strip()
    
    # If the content is mostly quoted strings, it's probably not a format
    quote_count = inside.count("'") + inside.count('"')
    if quote_count >= 2:  # At least one complete quoted string
        # Check if it contains any actual format descriptors outside quotes
        # This is a simplified check - we'll process it and see if it makes sense
        pass
    
    # Check if it contains any edit descriptors (case insensitive)
    return re.search(
        r"(?i)(?:ES|EN|F|E|D|G|I|L|A|X|T)",
        inside
    ) is not None


def _is_numeric_only_format(content: str) -> Tuple[bool, bool]:
    """
    Check if format content contains only numeric descriptors and determine
    if any numeric descriptor lacks width.
    
    Returns: (is_numeric_only, has_omitted_numeric_width)
    """
    s = content.strip()
    if not (len(s) >= 2 and s[0] == "(" and s[-1] == ")"):
        return False, False
    
    inside = s[1:-1].strip()
    
    # Tokenize while skipping quoted substrings
    tokens = []
    i = 0
    n = len(inside)
    in_str = False
    quote_char = ""
    
    while i < n:
        c = inside[i]
        
        # Handle quotes
        if not in_str and (c == "'" or c == '"'):
            in_str = True
            quote_char = c
            # Collect the entire quoted string
            start = i
            i += 1
            while i < n:
                if inside[i] == quote_char:
                    if i + 1 < n and inside[i + 1] == quote_char:
                        i += 2  # skip doubled quote
                        continue
                    break
                i += 1
            if i < n:
                i += 1  # include closing quote
            tokens.append(inside[start:i])
            continue
        
        if in_str:
            i += 1
            continue
        
        # Skip whitespace
        if c.isspace():
            i += 1
            continue
        
        # Collect token
        start = i
        if c.isdigit():
            # Repeat count
            while i < n and inside[i].isdigit():
                i += 1
            tokens.append(inside[start:i])
        elif c.isalpha():
            # Edit descriptor
            if i + 1 < n and inside[i:i+2].upper() in ("ES", "EN"):
                tokens.append(inside[i:i+2])
                i += 2
            else:
                tokens.append(inside[i])
                i += 1
        else:
            # Punctuation - only allow valid format punctuation
            if c in (',', '(', ')', '.', 'x', 'X'):
                tokens.append(c)
                i += 1
            else:
                # Unknown token - not numeric-only
                return False, False
    
    # Check if all tokens are valid for numeric-only format
    has_omitted_numeric_width = False
    for token in tokens:
        if token in (',', '(', ')', ' '):
            continue
        if token.isdigit():
            continue
        if token in ("'", '"') or (len(token) > 1 and (token[0] in ("'", '"') or token[-1] in ("'", '"'))):
            continue
        if token in ('.', 'x', 'X'):  # Valid format punctuation
            continue
        
        # Check edit descriptors
        if token.upper() in ("ES", "EN", "E", "D", "F", "G", "I", "L", "A", "X", "T"):
            # Only numeric descriptors are allowed for listification
            if token.upper() in ("ES", "EN", "E", "D", "F", "G", "I", "L"):
                # Check if numeric descriptor lacks width
                has_width = False
                for next_token in tokens[tokens.index(token)+1:]:
                    if next_token == '.':
                        has_width = True
                        break
                    if next_token.isdigit():
                        has_width = True
                        break
                    if next_token in (',', ')', ' '):
                        break
                if not has_width:
                    has_omitted_numeric_width = True
            else:
                # Non-numeric descriptor (A, X, T) - not numeric-only
                return False, False
        else:
            # Unknown token - not numeric-only
            return False, False
    
    return True, has_omitted_numeric_width


def _peek_digits(s: str, i: int) -> int:
    """Return index j >= i of first non-digit char."""
    j = i
    while j < len(s) and s[j].isdigit():
        j += 1
    return j


def _apply_defaults_to_format_with_quotes(fmt: str, int64: bool = False) -> str:
    """
    Apply Intel/DEC defaults inside format content while properly preserving quoted strings.
    This function handles the case where format strings may contain quoted content.
    """
    out = []
    i = 0
    n = len(fmt)
    in_str = False
    quote_char = ""

    def consume_real_or_int(pos: int) -> Tuple[str, int]:
        """Consume a real or int descriptor at position pos, returning (replacement, consumed)."""
        nonlocal fmt
        start = pos

        # Check for repeat count at the beginning
        repeat_count = ""
        if pos < n and fmt[pos].isdigit():
            j = pos
            while j < n and fmt[j].isdigit():
                j += 1
            repeat_count = fmt[pos:j]
            pos = j

        # Determine if two-char key (ES/EN) or one-char key
        key = ""
        if pos < n and pos + 1 < n and fmt[pos:pos+2].upper() in ("ES", "EN"):
            key = fmt[pos:pos+2].upper()
            pos += 2
        elif pos < n and fmt[pos].isalpha():
            key = fmt[pos].upper()
            if key not in ("F", "E", "D", "G", "I", "L"):
                return fmt[start], 1
            pos += 1
        else:
            # No valid descriptor found
            return fmt[start], 1

        # Read width digits if any
        j = _peek_digits(fmt, pos)
        has_width = (j > pos)

        if key == "I":
            # Integer: if width present, leave as-is
            if has_width:
                return repeat_count + fmt[start + len(repeat_count):j], j - start
            # Bare I: insert default width
            w = "23" if int64 else "12"
            return repeat_count + "I" + w, pos - start

        if key == "L":
            # Logical: if width present, leave as-is
            if has_width:
                return repeat_count + fmt[start + len(repeat_count):j], j - start
            # Bare L: insert default width (typically 2 for logical to accommodate "T " or "F ")
            return repeat_count + "L2", pos - start

        # Real descriptors
        if has_width:
            # Width already provided -> leave alone
            return repeat_count + fmt[start + len(repeat_count):j], j - start

        # No width. If next char is '.', then we have .d (and maybe E#)
        if pos < n and fmt[pos] == ".":
            m = re.match(r"\.(\d+)([Ee](\d+))?", fmt[pos:])
            if m:
                body = m.group(0)  # includes .d and optional E#
                return repeat_count + key + "25" + body, pos + len(body) - start
            else:
                # malformed; just return the key char
                return fmt[start], 1

        # Bare descriptor (no width, no .d)
        if key in ("E", "D", "ES", "EN"):
            return repeat_count + key + "25.16E3", pos - start
        else:
            return repeat_count + key + "25.16", pos - start

    while i < n:
        c = fmt[i]

        # Handle quotes inside format content (avoid editing within)
        if not in_str and (c == "'" or c == '"'):
            in_str = True
            quote_char = c
            out.append(c)
            i += 1
            continue
        if in_str:
            out.append(c)
            i += 1
            if c == quote_char:
                # handle doubled quote inside string
                if i < n and fmt[i] == quote_char:
                    out.append(fmt[i])
                    i += 1
                else:
                    in_str = False
            continue

        # Outside strings: try to consume a descriptor
        if c.isalpha():
            # Try ES/EN or F/E/D/G/I
            repl, consumed = consume_real_or_int(i)
            if consumed > 1 or (consumed == 1 and repl != fmt[i]):
                out.append(repl)
                i += consumed
                continue

        # Default: copy char
        out.append(c)
        i += 1

    return "".join(out)


def _rewrite_read_to_list_directed(text: str, trace: bool = False) -> str:
    """
    Convert eligible READ statements with inline format literals to list-directed reads.
    Only processes READ statements (never WRITE) that meet the eligibility criteria.
    """
    lines = text.split('\n')
    result_lines = []
    
    for line in lines:
        # Check if this line contains a READ statement
        if re.search(r'(?i)\bread\s*\(', line):
            if trace:
                print(f"[trace] Processing READ line: {line.strip()}")
            
            # Try to find the format literal in this line
            unit_match = re.search(r'(?i)(\bread\s*\()([^,)]+)', line)
            if unit_match:
                read_keyword = unit_match.group(1)  # "read "
                unit_part = unit_match.group(2)     # unit expression
                
                # Now find the format literal and variable list
                format_match = re.search(r'(?:,\s*(?:fmt\s*=\s*)?|\s+)([\'"][^\'"]*[\'"])([^)]*)\)', line)
                
                if format_match:
                    format_literal = format_match.group(1)
                    rest_part = format_match.group(2)
                    
                    if trace:
                        print(f"  Found READ statement:")
                        print(f"    read_keyword: {repr(read_keyword)}")
                        print(f"    unit_part: {repr(unit_part)}")
                        print(f"    format_literal: {repr(format_literal)}")
                        print(f"    rest_part: {repr(rest_part)}")
                    
                    # Check if this is a format literal that looks like a format
                    format_content = format_literal.strip("'\"")
                    if not _looks_like_format_literal(format_content):
                        if trace:
                            print(f"  -> not a format literal, skipping")
                        result_lines.append(line)
                        continue
                    
                    # Check if it's numeric-only and has omitted widths
                    is_numeric, has_omitted = _is_numeric_only_format(format_content)
                    if trace:
                        print(f"  -> numeric_only: {is_numeric}, has_omitted: {has_omitted}")
                    
                    if not is_numeric or not has_omitted:
                        result_lines.append(line)
                        continue
                    
                    # Check for implied DO loops in variable list (skip for safety)
                    if re.search(r'\([^)]*,[^)]*=[^)]*\)', rest_part):
                        if trace:
                            print(f"  -> has implied DO, skipping")
                        result_lines.append(line)
                        continue
                    
                    # Eligible for listification
                    if trace:
                        print(f"[trace] listifying READ: {format_literal} -> *")
                    
                    # Rewrite to list-directed
                    new_line = line.replace(format_literal, '*')
                    
                    if trace:
                        print(f"  -> rewritten line: {repr(new_line)}")
                    
                    result_lines.append(new_line)
                else:
                    # No format literal found, keep as is
                    result_lines.append(line)
            else:
                result_lines.append(line)
        else:
            # Not a READ statement, keep as is
            result_lines.append(line)
    
    return '\n'.join(result_lines)


def _apply_defaults_to_content(fmt: str, int64: bool = False) -> str:
    """
    Apply Intel/DEC defaults inside a *single* format-content string
    (without outer parentheses). Avoid editing inside quoted substrings.
    """
    out = []
    i = 0
    n = len(fmt)
    in_str = False
    quote_char = ""

    def consume_real_or_int(pos: int) -> Tuple[str, int]:
        """Consume a real or int descriptor at position pos, returning (replacement, consumed)."""
        nonlocal fmt
        start = pos

        # Check for repeat count at the beginning
        repeat_count = ""
        if pos < n and fmt[pos].isdigit():
            j = pos
            while j < n and fmt[j].isdigit():
                j += 1
            repeat_count = fmt[pos:j]
            pos = j

        # Determine if two-char key (ES/EN) or one-char key
        key = ""
        if pos < n and pos + 1 < n and fmt[pos:pos+2].upper() in ("ES", "EN"):
            key = fmt[pos:pos+2].upper()
            pos += 2
        elif pos < n and fmt[pos].isalpha():
            key = fmt[pos].upper()
            if key not in ("F", "E", "D", "G", "I", "L"):
                return fmt[start], 1
            pos += 1
        else:
            # No valid descriptor found
            return fmt[start], 1

        # Read width digits if any
        j = _peek_digits(fmt, pos)
        has_width = (j > pos)

        if key == "I":
            # Integer: if width present, leave as-is
            if has_width:
                return repeat_count + fmt[start + len(repeat_count):j], j - start
            # Bare I: insert default width
            w = "23" if int64 else "12"
            return repeat_count + "I" + w, pos - start

        if key == "L":
            # Logical: if width present, leave as-is
            if has_width:
                return repeat_count + fmt[start + len(repeat_count):j], j - start
            # Bare L: insert default width (typically 2 for logical to accommodate "T " or "F ")
            return repeat_count + "L2", pos - start

        # Real descriptors
        if has_width:
            # Width already provided -> leave alone
            return repeat_count + fmt[start + len(repeat_count):j], j - start

        # No width. If next char is '.', then we have .d (and maybe E#)
        if pos < n and fmt[pos] == ".":
            m = re.match(r"\.(\d+)([Ee](\d+))?", fmt[pos:])
            if m:
                body = m.group(0)  # includes .d and optional E#
                return repeat_count + key + "25" + body, pos + len(body) - start
            else:
                # malformed; just return the key char
                return fmt[start], 1

        # Bare descriptor (no width, no .d)
        if key in ("E", "D", "ES", "EN"):
            return repeat_count + key + "25.16E3", pos - start
        else:
            return repeat_count + key + "25.16", pos - start

    while i < n:
        c = fmt[i]

        # Handle quotes inside format content (avoid editing within)
        if not in_str and (c == "'" or c == '"'):
            in_str = True
            quote_char = c
            out.append(c)
            i += 1
            continue
        if in_str:
            out.append(c)
            i += 1
            if c == quote_char:
                # handle doubled quote inside string
                if i < n and fmt[i] == quote_char:
                    out.append(fmt[i])
                    i += 1
                else:
                    in_str = False
            continue

        # Outside strings: try to consume a descriptor
        if c.isalpha():
            # Try ES/EN or F/E/D/G/I
            repl, consumed = consume_real_or_int(i)
            if consumed > 1 or (consumed == 1 and repl != fmt[i]):
                out.append(repl)
                i += consumed
                continue

        # Default: copy char
        out.append(c)
        i += 1

    return "".join(out)


def _fix_format_statements(text: str, int64: bool) -> str:
    """
    Find true FORMAT statements and rewrite their content. Avoid
    confusing 'get_best_format(' etc. Only matches FORMAT( not
    preceded by a letter/underscore.
    """
    out = []
    i = 0
    n = len(text)
    pattern = re.compile(r"(?i)(?<![A-Za-z_])FORMAT\s*\(")

    while i < n:
        m = pattern.search(text, i)
        if not m:
            out.append(text[i:])
            break

        start = m.start()
        out.append(text[i:start])

        # The '(' is the last char of the match; j is its index
        j = m.end() - 1

        # Walk to matching ')' tracking parentheses and skipping strings
        depth = 0
        k = j
        in_str = False
        quote_char = ""

        while k < n:
            ch = text[k]
            if not in_str and (ch == "'" or ch == '"'):
                in_str = True
                quote_char = ch
                k += 1
                continue
            if in_str:
                if ch == quote_char:
                    # doubled?
                    if k + 1 < n and text[k + 1] == quote_char:
                        k += 2
                        continue
                    in_str = False
                k += 1
                continue

            if ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
                if depth == 0:
                    break
            k += 1

        if k >= n:
            # Unbalanced; give up and emit the rest
            out.append(text[start:])
            break

        inner = text[j + 1:k]
        fixed = _apply_defaults_to_content(inner, int64=int64)
        out.append(text[start:j + 1] + fixed + text[k])
        i = k + 1

    return "".join(out)


def _fix_string_literals(text: str, int64: bool, trace: bool = False, skip_listified: bool = False) -> str:
    """
    Rewrite only string literals that *look like* format strings,
    for both single- and double-quoted cases.
    
    If skip_listified is True, skip processing of format literals that have been
    converted to list-directed reads (containing only '*')
    """
    
    def process_format_literal(lit: str, is_single: bool) -> str:
        """Process a format literal, preserving quoted strings within."""
        content = lit[1:-1]  # inside quotes
        
        # Skip if this looks like a listified format (just '*')
        if skip_listified and content.strip() == '*':
            return lit
            
        if trace:
            print(f"[debug] Checking format literal: {lit} -> content: {content}")
            
        if _looks_like_format_literal(content):
            inner = content.strip()[1:-1]  # drop outer () in the literal
            if trace:
                print(f"[debug] Processing format literal: {lit} -> inner: {inner}")
            # Process format content while preserving quoted strings
            fixed = _apply_defaults_to_content(inner, int64=int64)
            if trace:
                print(f"[debug] Applied defaults: {inner} -> {fixed}")
            quote_char = "'" if is_single else '"'
            new_lit = quote_char + "(" + fixed + ")" + quote_char
            if trace:
                print(f"[trace] {'single' if is_single else 'double'}-quote fmt: {lit}  ->  {new_lit}")
            return new_lit
        return lit

    if trace:
        print(f"[debug] Starting _fix_string_literals")
        print(f"[debug] Input text length: {len(text)}")
    
    # Process single-quoted strings by parsing character by character
    # This is more robust than regex for handling doubled quotes
    result = []
    i = 0
    n = len(text)
    
    while i < n:
        if text[i] == "'":
            # Found start of single-quoted string
            start = i
            i += 1
            while i < n:
                if text[i] == "'":
                    if i + 1 < n and text[i + 1] == "'":
                        # Doubled quote
                        i += 2
                        continue
                    else:
                        # End of string
                        i += 1
                        break
                i += 1
            if i <= n:
                literal = text[start:i]
                processed = process_format_literal(literal, True)
                result.append(processed)
            continue
        
        if text[i] == '"':
            # Found start of double-quoted string
            start = i
            i += 1
            while i < n:
                if text[i] == '"':
                    if i + 1 < n and text[i + 1] == '"':
                        # Doubled quote
                        i += 2
                        continue
                    else:
                        # End of string
                        i += 1
                        break
                i += 1
            if i <= n:
                literal = text[start:i]
                processed = process_format_literal(literal, False)
                result.append(processed)
            continue
        
        result.append(text[i])
        i += 1
    
    if trace:
        print(f"[debug] After processing: {len(''.join(result))} characters")
        
    return ''.join(result)


def transform_source(text: str, *, int64: bool = False, listify_reads: bool = False, trace: bool = False) -> str:
    """Return transformed source. Replace omitted-width FORMAT descriptors with explicit widths.
    
    This function provides the core transformation logic for converting Intel/DEC omitted-width
    Fortran FORMAT descriptors to standard-conforming forms.
    """
    result = text

    if listify_reads:
        # Apply listification first (takes precedence)
        result = _rewrite_read_to_list_directed(result, trace=trace)
    
    # Always apply default injection to remaining formats
    result = _fix_format_statements(result, int64=int64)
    result = _fix_string_literals(result, int64=int64, trace=trace, skip_listified=listify_reads)
    
    return result
