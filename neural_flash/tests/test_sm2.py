from neural_flash.sm2 import calculate_sm2

def test_sm2_quality_5():
    repetition, interval, ease_factor = calculate_sm2(5, 0, 0, 2.5)
    assert repetition == 1
    assert interval == 1
    assert abs(ease_factor - 2.6) < 1e-9

def test_sm2_quality_4():
    repetition, interval, ease_factor = calculate_sm2(4, 1, 1, 2.5)
    assert repetition == 2
    assert interval == 6
    assert abs(ease_factor - 2.5) < 1e-9

def test_sm2_quality_3():
    repetition, interval, ease_factor = calculate_sm2(3, 2, 6, 2.5)
    assert repetition == 3
    assert interval == 15
    assert abs(ease_factor - 2.36) < 1e-9

def test_sm2_quality_2():
    repetition, interval, ease_factor = calculate_sm2(2, 3, 15, 2.5)
    assert repetition == 0
    assert interval == 1
    assert abs(ease_factor - 2.18) < 1e-9

def test_sm2_quality_1():
    repetition, interval, ease_factor = calculate_sm2(1, 0, 0, 2.5)
    assert repetition == 0
    assert interval == 1
    assert abs(ease_factor - 1.96) < 1e-9

def test_sm2_quality_0():
    repetition, interval, ease_factor = calculate_sm2(0, 0, 0, 2.5)
    assert repetition == 0
    assert interval == 1
    assert abs(ease_factor - 1.7) < 1e-9
