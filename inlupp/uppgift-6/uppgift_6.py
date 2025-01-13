# Uppgift 6
# Skapa en funktion multiplication_table(n, limit) som returnerar multiplikationstabellen för n upp till limit i en lista.

def multiplication_table(n: int, limit: int) -> list:
    result = []
    for i in range(1, limit + 1):
        result.append(n * i)
    return (result)
