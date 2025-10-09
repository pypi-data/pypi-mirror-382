import sys
import subprocess

f = sys.argv[1]

with open(f,"r",encoding="utf-8") as f1:
    f2 = f1.read().split("\n")

# Warning: idebug.py don't support advanced syntax, only support basic syntax
# if the requirement.txt use advanced syntax, the script may occurred error
# if you want to support advanced syntax, you can write your own script
# the script is created and modify by wayne931121 cc-by-nc 4.0, last update 20251001.

for i in f2:
    if not i or "#" in i:
        continue
    if ";" in i:
        i1 = i.split(";")
        i = i1[0]
        i2 = ";".join(i1[1:])
        print("Warning: idebug.py don't support advanced syntax, ignore "+i2)
    try:
        print("pip install "+i,end="\n\n")
        result = subprocess.run(
            ["pip","install",i],  # Command that will generate an error
            capture_output=True,         # Capture both stdout and stderr
            text=True,                   # Decode output as text (UTF-8 by default)
            check=True,                   # Raise CalledProcessError if return code is non-zero
            shell=True
        )
        print("    STDOUT:", result.stdout)
        if result.stderr:
            print("    STDERR:", result.stderr)
        else:
            print("    STDERR: EMPTY")
        print("\n")
    except subprocess.CalledProcessError as e:
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print("Error occurred:")
        print(i)
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)
        
        sys.exit()