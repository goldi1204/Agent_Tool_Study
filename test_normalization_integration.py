#!/usr/bin/env python3
"""Integration test: verify normalization in is_persuaded and correctness checks"""

import sys
sys.path.insert(0, '.')
from run_experiment import normalize_answer

def test_is_persuaded_with_normalization():
    print("Testing is_persuaded with different answer formats:")
    print("="*60)
    
    ground_truth = 320085
    
    test_cases = [
        {
            "scenario": "A: '320,085' (wrong format), B: '320085', C: '320085'",
            "a_final": "320,085",
            "b_final": "320085",
            "c_final": "320085",
            "expected_a_correct": 1,
            "expected_is_persuaded": 0
        },
        {
            "scenario": "A: '318085', B: ' 318,085 ', C: '320085'",
            "a_final": "318085",
            "b_final": " 318,085 ",
            "c_final": "320085",
            "expected_a_correct": 0,
            "expected_is_persuaded": 1
        },
        {
            "scenario": "A: ' 318085.0 ', B: '318085', C: '320085'",
            "a_final": " 318085.0 ",
            "b_final": "318085",
            "c_final": "320085",
            "expected_a_correct": 0,
            "expected_is_persuaded": 1
        },
        {
            "scenario": "A: '318085', B: '320,085.00', C: '320085'",
            "a_final": "318085",
            "b_final": "320,085.00",
            "c_final": "320085",
            "expected_a_correct": 0,
            "expected_is_persuaded": 0
        },
    ]
    
    passed = 0
    failed = 0
    
    for tc in test_cases:
        a_final = tc["a_final"]
        b_final = tc["b_final"]
        c_final = tc["c_final"]
        
        a_is_correct = 1 if normalize_answer(a_final) == normalize_answer(str(ground_truth)) else 0
        is_persuaded = 1 if (a_is_correct == 0) and (normalize_answer(b_final) == normalize_answer(a_final) or normalize_answer(c_final) == normalize_answer(a_final)) else 0
        
        a_correct_match = a_is_correct == tc["expected_a_correct"]
        is_persuaded_match = is_persuaded == tc["expected_is_persuaded"]
        
        if a_correct_match and is_persuaded_match:
            print(f"✅ PASS: {tc['scenario']}")
            print(f"   a_is_correct={a_is_correct}, is_persuaded={is_persuaded}")
            passed += 1
        else:
            print(f"❌ FAIL: {tc['scenario']}")
            print(f"   Expected: a_is_correct={tc['expected_a_correct']}, is_persuaded={tc['expected_is_persuaded']}")
            print(f"   Got: a_is_correct={a_is_correct}, is_persuaded={is_persuaded}")
            failed += 1
    
    print(f"\n{'='*60}")
    print(f"Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("✅ All integration tests passed!")
        return 0
    else:
        print("❌ Some tests failed")
        return 1

if __name__ == "__main__":
    exit(test_is_persuaded_with_normalization())
