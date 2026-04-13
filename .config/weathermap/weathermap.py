import random

for y in range(10):
    row = ""
    for x in range(30):
        t = random.randint(-5,35)
        row += f"{t:2d} "
    print(row)
