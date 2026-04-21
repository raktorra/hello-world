import time
import random

def enhanced_hello_world():
    colors = ['\033[91m', '\033[92m', '\033[93m', '\033[94m', '\033[95m', '\033[96m']
    reset = '\033[0m'
    bold = '\033[1m'
    
    message = "Hello, World!"
    border = "★" * (len(message) + 4)
    
    print(f"\n{bold}{border}{reset}")
    print(f"{bold}★ {reset}", end="")
    
    for char in message:
        color = random.choice(colors)
        print(f"{bold}{color}{char}{reset}", end="", flush=True)
        time.sleep(0.05)
    
    print(f" {bold}★{reset}")
    print(f"{bold}{border}{reset}\n")

enhanced_hello_world()