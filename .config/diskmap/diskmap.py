import shutil

total, used, free = shutil.disk_usage("/")

print("Disk Usage:")
print(f"Total: {total//1e9:.1f} GB")
print(f"Used : {used//1e9:.1f} GB")
print(f"Free : {free//1e9:.1f} GB")

bar = int(used/total * 50)
print("[" + "#"*bar + " "*(50-bar) + "]")
