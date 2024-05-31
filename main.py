import subprocess

yalFile = "yals/slr-1.yal"
yalpFile = "yalps/slr-1.yalp"

# Run yalexReader
subprocess.run(["python", "-m", "yalexReader", yalFile], check=True)

# Run yalpReader
subprocess.run(["python", "-m", "yalpReader", yalpFile], check=True)

# Run scan
subprocess.run(["python", "-m", "scan"], check=True)

# Run LR0
subprocess.run(["python", "-m", "LR0"], check=True)
