from datetime import datetime
import sys

def eratos(n):
    # output all the prime numbers from 2 to n
    mas = [True] * (n + 1)
    i = 2
    while i**2 <= n:
        if mas[i]:
            j = i**2
            while j <= n:
                mas[j] = False
                j += i
        i += 1

    print(f"Primes from 2 to {n}: ", end="")
    for i in range(2, n + 1):
        if mas[i]:
            print(f"{i} ", end="")        

while True:
    try:
        print("Input n > 2: ", end="")
        n = int(input())
        if n <= 2:
            raise ValueError("Number has to be bigger than 2!")
        break
    except ValueError as e:
        print("Error! Bad input.")
        print(f"Exception message: {sys.exc_info()[0]}\t{e}")
        now = datetime.now().strftime(f"%d:%m:%y %H:%M:%S")
        print(f"Exact time: {now}")

eratos(n)