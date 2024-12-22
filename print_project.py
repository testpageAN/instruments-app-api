import os
import sys


def print_files_in_directory(directory, target_dirs):
    # Κανονικοποιούμε τη διαδρομή του βασικού φακέλου
    directory = os.path.abspath(directory)

    # Αναδρομική ανάγνωση όλων των αρχείων στον φάκελο και υποφακέλους
    for root, dirs, files in os.walk(directory):
        # Έλεγχος αν ο φάκελος βρίσκεται στα target_dirs
        relative_root = os.path.relpath(root, directory)  # Παίρνουμε την σχετική διαδρομή
        if relative_root in target_dirs or relative_root == ".":
            for file in files:
                file_path = os.path.join(root, file)
                print(f"---- {file_path} ----")
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        # Εκτύπωση του περιεχομένου του αρχείου
                        sys.stdout.write(f.read())
                except Exception as e:
                    print(f"Could not read file {file_path}: {e}")
                print("\n" + "=" * 50 + "\n")
# Αντικατέστησε με τον φάκελο του Django project σου
project_directory = r"C:\Users\ALEXIS\OneDrive\PYTHON-LESSONS\PYTHON-ALL\instruments_API\instruments-app-api"
target_dirs = ['app/app', 'app/core', 'app/instrument', 'app/user']
print_files_in_directory(project_directory, target_dirs)


# python print_project.py > project_files_content.txt
