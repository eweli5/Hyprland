import time, random

symbols = ["AAPL","TSLA","GOOG","AMZN"]

while True:
    line = ""
    for s in symbols:
        val = round(random.uniform(100,500),2)
        line += f"{s}:{val} "
    print("\r"+line, end="")
    time.sleep(1)
