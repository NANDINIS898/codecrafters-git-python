import sys
import os
import zlib
import hashlib


def read_binary_object(sha):
    with open(f".git/objects/{sha[:2]}/{sha[2:]}", "rb") as f:
        data = zlib.decompress(f.read())
        header, content = data.split(b"\0", 1)
        return content


def main():
    command = sys.argv[1]
    if command == "init":
        os.mkdir(".git")
        os.mkdir(".git/objects")
        os.mkdir(".git/refs")
        with open(".git/HEAD", "w") as f:
            f.write("ref: refs/heads/main\n")
        print("Initialized git directory")
    elif command == "cat-file":
        # We don't care about the options yet, but we need to extract them anyway
        if sys.argv[2] == "-p":
            hash = sys.argv[3]
            content = read_binary_object(hash)
            print(content.decode("utf-8"), end="")
    elif command == "hash-object":
        if sys.argv[2] == "-w":
            file = sys.argv[3]
            with open(file, "rb") as f:
                data = f.read()
                header = f"blob {len(data)}\0".encode("utf-8")
                store = header + data
                sha = hashlib.sha1(store).hexdigest()
                os.makedirs(f".git/objects/{sha[:2]}", exist_ok=True)
                with open(f".git/objects/{sha[:2]}/{sha[2:]}", "wb") as f:
                    f.write(zlib.compress(store))
                print(sha)
    elif command == "ls-tree":
        param, hash = sys.argv[2], sys.argv[3]
        if param == "--name-only":
            binary_data = read_binary_object(hash)
            while binary_data:
                mode, binary_data = binary_data.split(b"\0", 1)
                _, name = mode.split()
                binary_data = binary_data[20:]
                print(name.decode("utf-8"))
    else:
        raise RuntimeError(f"Unknown command #{command}")


if __name__ == "__main__":
    main()
