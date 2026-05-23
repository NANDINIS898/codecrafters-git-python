import sys
import os
import zlib, hashlib, pathlib

from hashlib import sha1


def read_raw_content(filename):
    with open(filename, "rb") as f:
        return f.read()


def create_header(content):
    count = len(content)
    return f"blob {count}\0".encode()


def compute_sha(header, content):
    return sha1(header + content).hexdigest()


def store_blob(sha, header, content):
    dir_path = os.path.join(".git", "objects", sha[:2])
    file_path = os.path.join(dir_path, sha[2:])
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    compressed = zlib.compress(header + content)
    with open(file_path, "wb") as f:
        f.write(compressed)


def read_binary_object(sha):
    with open(f".git/objects/{sha[:2]}/{sha[2:]}", "rb") as f:
        data = zlib.decompress(f.read())
        header, content = data.split(b"\0", 1)
        return content


def write_tree(dir):
    entries = []
    for entry in sorted(os.listdir(dir)):
        full_path = os.path.join(dir, entry)
        if entry == ".git":
            continue
        if os.path.isdir(full_path):
            sha = write_tree(full_path)
            mode = "40000"
        else:
            content = read_raw_content(full_path)
            header = create_header(content)
            sha = compute_sha(header, content)
            store_blob(sha, header, content)
            mode = "100644"
        entries.append(f"{mode} {entry}\0".encode() + bytes.fromhex(sha))
    tree_data = b"".join(entries)
    tree_header = f"tree {len(tree_data)}\0".encode()
    tree_sha1 = compute_sha(tree_header, tree_data)
    store_blob(tree_sha1, tree_header, tree_data)
    return tree_sha1


def main():
    command = sys.argv[1]
    if command == "init":
        os.mkdir(".git")
        os.mkdir(".git/objects")
        os.mkdir(".git/refs")
        with open(".git/HEAD", "w") as f:
            f.write("ref: refs/heads/main\n")
        print("Initialized git directory")
    elif command == "cat-file" and sys.argv[2] == "-p":
        filename = sys.argv[3]
        with open(f".git/objects/{filename[:2]}/{filename[2:]}", "rb") as f:
            blob = zlib.decompress(f.read()).split(b"\x00")[1]
            print(blob.decode("utf-8"), end="")
    elif command == "hash-object" and sys.argv[2] == "-w":
        file_path = sys.argv[3]
        contents = pathlib.Path(file_path).read_bytes()
        header = f"blob {len(contents)}".encode()
        object_contents = header + b"\0" + contents
        object_id = hashlib.sha1(object_contents).hexdigest()
        print(object_id)
        object_file = pathlib.Path(".git/objects") / object_id[:2] / object_id[2:]
        object_file.parent.mkdir(parents=True, exist_ok=True)
        object_file.write_bytes(zlib.compress(object_contents))

    elif command == "ls-tree":
        param, hash = sys.argv[2], sys.argv[3]
        if param == "--name-only":
            binary_data = read_binary_object(hash)
            while binary_data:
                mode, binary_data = binary_data.split(b"\0", 1)
                _, name = mode.split()
                binary_data = binary_data[20:]
                print(name.decode("utf-8"))

    elif command == "write-tree":
        print(write_tree("."))

    elif command == "commit-tree" and sys.argv[3] == "-p" and sys.argv[5] == "-m":
        content = f"tree {sys.argv[2]}\nparent {sys.argv[4]}\nauthor Inam <inam@gmail.com> 1690116359 +0000\ncommitter Inamul <inamul@gmail.com> 1630516359 +0000\n\n{sys.argv[6]}\n"
        commit_object = f"commit {len(content)}\0{content}".encode("utf-8")
        sha = hashlib.sha1(commit_object).hexdigest()
        os.mkdir(f".git/objects/{sha[:2]}")
        with open(f".git/objects/{sha[:2]}/{sha[2:]}", "wb") as f:
            f.write(zlib.compress(commit_object))
        print(sha)

    else:
        raise RuntimeError(f"Unknown command #{command}")


if __name__ == "__main__":
    main()
