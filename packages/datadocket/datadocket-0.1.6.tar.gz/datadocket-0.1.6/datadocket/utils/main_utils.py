import os
import shutil

def Size(path: str) -> int:
    """
    Get the size of a file or the total size of all files in a directory.

    Args:
        path (str): Path to a file or directory.

    Returns:
        int: Size in bytes.
    """
    if os.path.isfile(path):
        return os.path.getsize(path)
    elif os.path.isdir(path):
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                # Skip if it's a broken symlink
                if os.path.isfile(fp):
                    total_size += os.path.getsize(fp)
        return total_size
    else:
        raise FileNotFoundError(f"No such file or directory: '{path}'")


def Delete(path: str):
    """
    Delete a file or directory at the given path.

    Args:
        path (str): Path to a file or directory.

    Raises:
        FileNotFoundError: If the path does not exist.
        OSError: If deletion fails.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"No such file or directory: '{path}'")
    if os.path.isfile(path) or os.path.islink(path):
        os.remove(path)
    elif os.path.isdir(path):
        import shutil
        shutil.rmtree(path)
    else:
        raise OSError(f"Unable to delete: '{path}'")


def Rename(
    src: str, 
    dst: str):
    """
    Rename a file or directory from src to dst.

    Args:
        src (str): The current path to the file or directory.
        dst (str): The new path for the file or directory.

    Raises:
        FileNotFoundError: If the source path does not exist.
        FileExistsError: If the destination path already exists.
        OSError: If renaming fails.
    """
    if not os.path.exists(src):
        raise FileNotFoundError(f"No such file or directory: '{src}'")
    if os.path.exists(dst):
        raise FileExistsError(f"Destination already exists: '{dst}'")
    os.rename(src, dst)


def Move(
    src: str, 
    dst_dir: str):
    """
    Move a file or directory from its current location to another directory.

    Args:
        src (str): Path to the source file or directory.
        dst_dir (str): Path to the destination directory.

    Raises:
        FileNotFoundError: If the source or destination directory does not exist.
        NotADirectoryError: If the destination path is not a directory.
        OSError: If moving fails.
    """
    if not os.path.exists(src):
        raise FileNotFoundError(f"Source path does not exist: '{src}'")
    if not os.path.exists(dst_dir):
        raise FileNotFoundError(f"Destination directory does not exist: '{dst_dir}'")
    if not os.path.isdir(dst_dir):
        raise NotADirectoryError(f"Destination is not a directory: '{dst_dir}'")

    dst = os.path.join(dst_dir, os.path.basename(src))
    shutil.move(src, dst)


def List(path: str):
    """
    List all files in a directory.

    Args:
        path (str): Path to a directory.

    Returns:
        list: List of file paths.
    """
    return [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]

def Empty(path: str):
    """
    Delete all files in a directory.

    Args:
        path (str): Path to a directory.

    Raises:
        FileNotFoundError: If the path does not exist.
        OSError: If deletion fails.
    """
    for file in List(path):
        Delete(os.path.join(path, file))

def Copy(
    src: str, 
    dst: str):
    """
    Copy a file or directory from src to dst.

    Args:
        src (str): Path to the source file or directory.
        dst (str): Path to the destination file or directory.
    """
    shutil.copy(src, dst)


def MakeDir(path: str):
    """
    Create a directory at the given path.

    Args:
        path (str): Path to the directory.
    """
    os.makedirs(path, exist_ok=True)


def Exists(path: str) -> bool:
    """
    Checks if a file of directory exists at the given path.

    Args:
        path (str): Path to the file or directory.

    Returns:
        bool: True if the file or directory exists, False otherwise.
    """
    return os.path.exists(path)
    