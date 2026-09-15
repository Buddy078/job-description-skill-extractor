import sys, base64

path = sys.argv[1]
b64_data = sys.stdin.read().strip()
with open(path, "wb") as f:
    f.write(base64.b64decode(b64_data))
print("Wrote", path)
