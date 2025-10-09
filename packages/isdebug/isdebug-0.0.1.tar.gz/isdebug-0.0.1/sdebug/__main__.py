"""
Warning: sdebug.py don't support advanced syntax, only support basic syntax
if the requirement.txt use advanced syntax, the script may occurred error
if you want to support advanced syntax, you can write your own script
the script is created and modify by wayne931121 cc-by-nc 4.0, last update 20251001.
"""


import sys, subprocess

# Example :
# python "C:\Users\原神\Desktop\sdebug.py" "C:\Users\原神\Desktop\requirements.txt" "C:\Users\原神\Desktop\bug.py"

f = sys.argv[1]

bug = sys.argv[2]


with open( f,  "r",  encoding = "utf-8" ) as f1 :

    f2 = f1.read().split( "\n" )


def cmd( scmd="",  lcmd=[],  output="" ) :


    cmd_ = None
    
    
    if scmd:
    
        cmd_ = scmd.split(" ")
        
    else:
    
        cmd_ = lcmd
    
    
    if output:
    
        print(output)
    
    
    
    
    try:
    
    
        result = subprocess.run(
        
            cmd_,                          # Command that will generate an error
            
            capture_output = True,         # Capture both stdout and stderr
            
            text = True,                   # Decode output as text (UTF-8 by default)
            
            check = True,                  # Raise CalledProcessError if return code is non-zero
            
            shell = True                   # Shell = True
            
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

for i in f2:

    if not i or "#" in i:
    
        continue
    
    
    if ";" in i:
    
        i1 = i.split(";")
        
        i = i1[0]
        
        i2 = ";".join(i1[1:])
        
        print("Warning: idebug.py don't support advanced syntax, ignore "+i2)
    
    output = "pip install "+i+"\n"
    
    cmd( lcmd = ["pip","install",i],  output = output )
    
    cmd( scmd = "python " + bug ,  output = "Detect Bug......\n" )
