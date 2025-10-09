import ctypes
import sys
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Determine library file name based on platform
if sys.platform.startswith("linux"):
    lib_file = os.path.join(BASE_DIR, "lib", "fileops.so")
elif sys.platform == "darwin":
    lib_file = os.path.join(BASE_DIR, "lib", "fileops.dylib")
elif sys.platform == "win32":
    lib_file = os.path.join(BASE_DIR, "lib", "fileops.dll")
else:
    raise RuntimeError(f"Unsupported OS: {sys.platform}")

# Check if library exists
if not os.path.exists(lib_file):
    raise FileNotFoundError(f"Shared library not found: {lib_file}")

# Load the shared library
lib = ctypes.CDLL(lib_file)

# Define encodeFiles function signature
lib.encodeFiles.argtypes = [
    ctypes.POINTER(ctypes.c_char_p),  # const char** file_paths
    ctypes.c_int,                     # int num_files
    ctypes.c_char_p,                  # const char* input_image_path
    ctypes.c_char_p                   # const char* output_image_path
]
lib.encodeFiles.restype = None  # void

def safedrop(folder: str, image: str):
    """
    Encode all files under `folder` into a PNG image.

    Args:
        folder: Path to a folder containing files to encode.
        image: Path to the input PNG (must NOT be inside `folder`).

    Returns:
        Path to the encoded PNG with '_sd' suffix.
    """
    # Validate paths
    folder = os.path.abspath(folder)
    image = os.path.abspath(image)

    if not os.path.isdir(folder):
        raise ValueError(f"❌ Folder not found: {folder}")

    if not os.path.isfile(image):
        raise ValueError(f"❌ Input image not found: {image}")

    # Ensure image is not inside the folder
    if os.path.commonpath([folder]) == os.path.commonpath([folder, image]):
        raise ValueError("❌ Input image cannot be inside the source folder.")

    # Gather all files in folder (recursive)
    file_paths = []
    for root, _, files in os.walk(folder):
        for f in files:
            full_path = os.path.join(root, f)
            file_paths.append(full_path.encode("utf-8"))

    if not file_paths:
        raise ValueError(f"⚠️ No files found under folder: {folder}")

    # Prepare ctypes array
    FileArray = ctypes.c_char_p * len(file_paths)
    file_array = FileArray(*file_paths)

    # Prepare input/output PNG
    input_png = image.encode("utf-8")
    output_png = os.path.splitext(image)[0] + "_sd.png"
    output_png_b = output_png.encode("utf-8")

    print(f"🧩 Safedropping {len(file_paths)} files from {folder}")
    print(f"📥 Input image: {image}")
    print(f"📤 Output image: {output_png}")

    lib.encodeFiles(file_array, len(file_paths), input_png, output_png_b)

    print(f"✅ Your files are safely stored in image: {output_png}")
    return output_png

