import time

text = "the quick brown fox jumps over the lazy dog"
print(text)
start = time.time()
inp = input("> ")
end = time.time()

wpm = len(inp.split()) / ((end-start)/60)
print(f"WPM: {wpm:.2f}")
