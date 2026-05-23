
import hashlib
import os
import pathlib
import sys
import zlib


def main():
    command = sys.argv[1:]
    match command:
        case ["init", *_]:
            os.mkdir(".git")
            os.mkdir(".git/objects")
            os.mkdir(".git/refs")
            with open(".git/HEAD", "w") as f:
                f.write("ref: refs/heads/main\n")
            print("Initialized git directory")
        case ["cat-file", *args, object_id]:
            cat_file(*args, object_id=object_id)
        case ["hash-object", "-w", file_path]:
            contents = pathlib.Path(file_path).read_bytes()
            header = f"blob {len(contents)}".encode()
            object_contents = header + b"\0" + contents
            object_id = hashlib.sha1(object_contents).hexdigest()
            print(object_id)
            object_file = pathlib.Path(".git/objects") / object_id[:2] / object_id[2:]
            object_file.parent.mkdir(parents=True, exist_ok=True)
            object_file.write_bytes(zlib.compress(object_contents))
        case _:
            raise RuntimeError(f"Unknown command #{command[0]}")


def cat_file(*flags, object_id):
    object_file = pathlib.Path(".git/objects") / object_id[:2] / object_id[2:]
    contents = zlib.decompress(object_file.read_bytes())
    size, content = contents.split(b"\0", maxsplit=1)
    match flags:
        case ["-p"]:
            print(content.decode(), end="")
        case ["-s"]:
            _, sz = size.decode().rsplit(maxsplit=1)
            print(sz)
        case _:
            raise RuntimeError(f"Unknown flags #{flags} for cat-file")


if __name__ == "__main__":
    main()

