import os
import sys
import shutil


def check_dir(root_dir):
    searcher = os.path.join(root_dir, '.searcher')
    if not os.path.exists(searcher):
        return False
    try:
        with open(searcher, 'r') as file:
            content = file.read().strip()
        if content != "IT'S SEARCHER":
            return False
    except Exception:
        return False
    return True


def create_dir(root_dir):
    searcher_file = os.path.join(root_dir, '.searcher')
    index_dir = os.path.join(root_dir, 'index')
    files_dir = os.path.join(root_dir, 'files')
    spilts_file = os.path.join(files_dir, '.splits')
    zero_files = os.path.join(files_dir, '0_files')

    if not os.path.exists(searcher_file):
        with open(searcher_file, 'w', encoding='utf-8') as file:
            file.write("IT'S SEARCHER")

    if os.path.exists(index_dir):
        if os.listdir(index_dir):
            shutil.rmtree(index_dir)
            os.makedirs(index_dir)
    else:
        os.makedirs(index_dir)

    if os.path.exists(files_dir):
        shutil.rmtree(files_dir)
    os.makedirs(files_dir)

    with open(spilts_file, 'w', encoding='utf-8') as file:
        file.write('0 0')
    open(zero_files, 'w', encoding='utf-8').close()
    print(f'Search system initialized successfully at {root_dir}')


def check_if_path_exists(root_dir, drop_existing):
    abs_path = os.path.abspath(root_dir)
    # Если в конце пути файл - ошибка
    if os.path.isfile(root_dir):
        print(f'error: path {abs_path} exists and its a file')
        sys.exit(1)

    # Если в конце пути директория:
    if os.path.isdir(root_dir):

        # Если это искомая директория, т.е. есть файл .searcher
        if check_dir(root_dir):
            if drop_existing:
                print(f'Removing  existing searcher data at path {abs_path}')
                shutil.rmtree(root_dir)
                os.mkdir(root_dir)
            else:
                print(f'Directory {root_dir} is already initialized. Use --drop-existing to reset.')
                sys.exit(1)
        else:
            print(f'error: directory {root_dir} is not initialized as searching directory')
            sys.exit(1)


def init(root_dir, drop_existing):
    # Если путь существует
    if os.path.exists(root_dir):
        check_if_path_exists(root_dir, drop_existing)
    # Если данного каталога не существует, пробуем создать
    else:
        os.makedirs(root_dir)

    create_dir(root_dir)
