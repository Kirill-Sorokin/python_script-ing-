import os, json, shutil, sys
from subprocess import PIPE, run


GAME_DIR_PATTERN = "game"
GAME_CODE_EXTENSION = ".go"
GAME_COMPILE_COMMAND = [".go", "build"]  

def find_all_game_paths(source):
    game_paths = []
    for root, dirs, files in os.walk(source):
        for directory in dirs:
            if GAME_DIR_PATTERN in directory.lower():
                path = os.path.join(source, directory)
                game_paths.append(path)
        break
    return game_paths

def get_name_from_paths(paths, to_strip):
    new_names = []
    for path in paths:
        _, dir_name = os.path.split(path)
        new_dir_name = dir_name.replace(to_strip, "")
        new_names.append(new_dir_name)
    return new_names

def create_dir(path):
    if not os.path.exists(path):
        os.mkdir(path)

def copy_and_overwrite(source, dest):
    if os.path.exists(dest):
        shutil.rmtree(dest)
    shutil.copytree(source, dest)

def make_json_metadata_file(path, game_dirs):
    data = {"gameNames": game_dirs,
            "numberOfGames": len(game_dirs)}
    with open(path, "w") as f:
        json.dump(data, f)
    # not using 'with', requires manually closing file, could cause errors (memory leak).

# determine name file.
def compile_game_code(path):
    code_file_name = None
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith(GAME_CODE_EXTENSION):
                code_file_name = file
                break
        break
    if code_file_name is None:
        return
    command = GAME_COMPILE_COMMAND + [code_file_name]

def run_command(command, path):
    cwd = os.getcwd()
    os.chdir(path)
    run(command, stdout = PIPE, stdin = PIPE, universal_newlines=True)

def main(source, target):
    cwd = os.getcwd()
    # "C://..." + .... <- 'String concatenation': different OS have different path dividers, therefore don't do this.
    source_path = os.path.join(cwd, source)
    target_path = os.path.join(cwd, target)
    game_paths = find_all_game_paths(source_path)
    # print(game_paths)
    new_game_dirs = get_name_from_paths(game_paths, "_game")
    # print(new_game_dirs)
    

    # Take matching elements from 2 arrays, combining into tuple that gives us access to them at the same time.
    for src, dest in zip(game_paths, new_game_dirs):
        dest_path = os.path.join(target_path, dest)
        copy_and_overwrite(src, dest_path)

    json_path = os.path.join(target_path, "metadata.json")
    make_json_metadata_file(json_path, new_game_dirs)
    
    create_dir(target_path)

if __name__ == "__main__":
    args = sys.argv
    # print(args)
    if len(args) != 3:
        raise Exception("You must pass a source & target directory - only.")
    
    source, target = args[1:]
    main(source, target)