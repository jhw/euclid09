import os
import zipfile

# Step a: Check if /Volumes/M8 exists
m8_path = "/Volumes/M8"
if not os.path.exists(m8_path):
    print(f"Directory {m8_path} does not exist. Exiting.")
    exit()

# Step b: Create /Volumes/M8/Stems/euclid09 if it does not exist
stems_path = os.path.join(m8_path, "Stems", "euclid09")
os.makedirs(stems_path, exist_ok=True)

# Step c: Check if tmp/wav exists
tmp_wav_path = "tmp/wav"
if not os.path.exists(tmp_wav_path):
    print(f"Directory {tmp_wav_path} does not exist. Exiting.")
    exit()

# Step d: Iterate over zip entries in tmp/wav
for entry in os.listdir(tmp_wav_path):
    if entry.endswith(".zip"):
        zip_file_path = os.path.join(tmp_wav_path, entry)
        file_name = os.path.splitext(entry)[0]  # Get the name without extension

        # Step e: Define the target subdirectory path
        target_dir = os.path.join(stems_path, file_name)

        # Skip if the directory already exists
        if os.path.exists(target_dir):
            print(f"Directory {target_dir} already exists. Skipping {entry}.")
            continue

        # Create the subdirectory
        os.makedirs(target_dir, exist_ok=True)

        # Step f: Load the zip file in memory and extract contents
        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            print(f"Extracting {zip_file_path} to {target_dir}")
            zip_ref.extractall(target_dir)

print("Processing complete.")
