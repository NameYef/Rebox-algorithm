import os
import sys

# remove files that end with sys.argv[2]
# Usage: python cleanup.py [dir_path]
def cleanup(path):
    try: 
        folder = os.listdir(path)

        i: str
        for i in folder:
            if i.endswith(f".{sys.argv[2]}"):
                delete = os.path.join(path, i)
                os.remove(delete)
                print(f"remove {delete}")

    except FileNotFoundError:
        print("Provide valid dir path")
        print("Usage: python cleanup.py [Dir_path]")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python cleanup.py [Dir_path] [file_format]")

    path = sys.argv[1]

    clean(path)