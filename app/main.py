import sys
import os
from zlib import compress
from zlib import decompress


def main():
    command = sys.argv[1]
    
    match command:
        case "init":
            os.mkdir(".git")
            os.mkdir(".git/objects")
            os.mkdir(".git/refs")
            with open(".git/HEAD", "w") as f:
                f.write("ref: refs/heads/main\n")
                print("Initialized git directory")
        case "cat-file":
            blob_sha = sys.argv[3]
            with open(f".git/objects/{blob_sha[:2]}/{blob_sha[2:]}", "rb") as f:
                blob = decompress(f.read())
                print(blob.split(b"\x00")[1].decode(), end="")
        case _:
            raise RuntimeError(f"Unknown command #{command}")

if __name__ == "__main__":
    main()
