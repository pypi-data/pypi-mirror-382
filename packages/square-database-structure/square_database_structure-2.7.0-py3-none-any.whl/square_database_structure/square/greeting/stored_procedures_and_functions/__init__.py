from pathlib import Path

directory = Path(__file__).parent
stored_procedures_and_functions = []

for file_path in directory.iterdir():
    if file_path.is_file() and file_path.suffix == ".sql":
        with file_path.open("r") as file:
            content = file.read()
            stored_procedures_and_functions.append(content)
