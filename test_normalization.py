#!/usr/bin/env python3
"""Test normalize_answer function edge cases"""

import sys
sys.path.insert(0, '.')
from run_experiment import normalize_answer

def test_normalization():
    test_cases = [
        # (input, expected_output, description)
        ("320085", "320085", "Plain integer string"),
        ("320,085", "320085", "Integer with comma"),
        (" 320085 ", "320085", "Integer with whitespace"),
        ("320085.0", "320085", "Float that's actually integer"),
        ("320,085.00", "320085", "Float with comma and decimals"),
        ("The answer is 42", "theansweris42", "Text with spaces"),
        ("123.456", "123.456", "Actual float"),
        (123, "123", "Integer input (non-string)"),
        (123.0, "123", "Float input that's integer"),
        ("  ABC  ", "abc", "Text with whitespace"),
        ("", "", "Empty string"),
    ]
    
    passed = 0
    failed = 0
    
    for input_val, expected, description in test_cases:
        result = normalize_answer(input_val)
        if result == expected:
            print(f"✅ PASS: {description}")
            print(f"   Input: {repr(input_val)} → Output: {repr(result)}")
            passed += 1
        else:
            print(f"❌ FAIL: {description}")
            print(f"   Input: {repr(input_val)}")
            print(f"   Expected: {repr(expected)}")
            print(f"   Got: {repr(result)}")
            failed += 1
    
    print(f"\n{'='*60}")
    print(f"Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("✅ All normalization tests passed!")
        return 0
    else:
        print("❌ Some tests failed")
        return 1

if __name__ == "__main__":
    exit(test_normalization())
