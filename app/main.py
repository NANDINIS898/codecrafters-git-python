import sys
import os
from zlib import compress


def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!", file=sys.stderr)

    
    command = sys.argv[1]
    if command == "init":
        os.mkdir(".git")
        os.mkdir(".git/objects")
        os.mkdir(".git/refs")
        with open(".git/HEAD", "w") as f:
            f.write("ref: refs/heads/main\n")
            print("Initialized git directory")
    case ["cat-file", "-p", blob_sha]:
    with open(f".git/objects/{blob_sha[:2]}/{blob_sha[2:]}", "rb") as f:
        blob = decompress(f.read())
        print(blob.split(b"\x00")[1].decode(), end="")
        
    case:
        raise RuntimeError(f"Unknown command #{command}")


if __name__ == "__main__":
    main()
