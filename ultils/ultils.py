def calculate_modulo11_check_digit(number):
    """ Calculate Modulo11 check

    Args:
        number (_type_): A number to check

    Returns:
        _type_: _description_
    """
    weights = [2, 3, 4, 5, 6, 7, 8, 9, 10]
    total = sum(int(digit) * weight for digit, weight in zip(reversed(number), weights))
    remainder = total % 11
    check_digit = 11 - remainder if remainder != 0 else 0
    return check_digit if check_digit < 10 else 'X'