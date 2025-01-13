# Uppgift 5
# Skapa en funktion filter_odd(numbers) som returnerar en lista med alla jämna tal från den givna listan.

def filter_odd(numbers: list) -> list:
    result = []
    for num in numbers:
        if num % 2 == 0:
            result.append(num)
    return result