import os

def remove_files_from_errors(errors_file):
    with open(errors_file, 'r', encoding='utf-8') as f:
        for line in f:
            # Find the path after 'Error in '
            if 'Error in ' in line:
                path_start = line.index('Error in ') + len('Error in ')
                path_end = line.find(':', path_start)
                if path_end != -1:
                    file_path = line[path_start:path_end].strip()
                    # Normalize path separators for current OS
                    file_path = file_path.replace('\\', os.sep).replace('/', os.sep)
                    if os.path.exists(file_path):
                        try:
                            os.remove(file_path)
                            print(f"Removed: {file_path}")
                        except Exception as e:
                            print(f"Failed to remove {file_path}: {e}")
                    else:
                        print(f"File not found: {file_path}")

if __name__ == "__main__":
    remove_files_from_errors("errors.txt")