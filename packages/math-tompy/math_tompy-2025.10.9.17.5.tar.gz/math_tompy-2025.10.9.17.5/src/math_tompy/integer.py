def factorize(number: int) -> list[int]:
    factors: list[int] = [divisor
                          for divisor in range(1, number + 1)
                          if number % divisor == 0]
    return factors
