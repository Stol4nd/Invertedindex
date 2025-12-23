import os
from collections import defaultdict


def file_update(split_file_path, line_num, files_num):
    tmp_file_path = split_file_path + '.tmp'
    with open(split_file_path, 'r', encoding='utf-8') as src, open(tmp_file_path, 'w', encoding='utf-8') as dst:
        for i, line in enumerate(src):
            line = line.strip()
            line_info = line.split()
            num1, num2 = line_info
            if i == line_num:
                num2 = str(int(num2) + files_num)
            dst.write(f'{num1} {num2}')
    os.replace(tmp_file_path, split_file_path)


def parse_column_value(val, col_idx, offset, per_file):
    """Добавляет слова из одной колонки в per_file[word][offset]."""
    if not val:
        return
    first_char = next((c for c in val if not c.isspace()), "")
    if not first_char or not first_char.isalpha():
        return
    for raw_word in val.split():
        word = raw_word.lower()
        per_file[word][offset].add(col_idx)


def transfer_per_file_data(file_id, per_file, words, group_words):
    """Переносит данные из временного словаря per_file в общие words и group_words."""
    for word, offsets in per_file.items():
        group_words.setdefault(word[0], []).append(word)
        if word not in words:
            words[word] = {}
        if file_id not in words[word]:
            words[word][file_id] = []
        for off, cols in offsets.items():
            words[word][file_id].append((off, sorted(cols)))


def parse_file_content(file_id, file_path, words, group_words):
    """Сканирует файл, добавляя найденные слова в структуру words."""
    per_file = defaultdict(lambda: defaultdict(set))
    with open(file_path, "r", encoding="utf-8") as f:
        offset = 0
        for line in f:
            bline = line.encode("utf-8")
            cols = line.rstrip("\n").split("\t")
            for col_idx, col in enumerate(cols):
                val = col.strip()
                parse_column_value(val, col_idx, offset, per_file)
            offset += len(bline)
    transfer_per_file_data(file_id, per_file, words, group_words)


def get_file_data(files_dict):
    """Возвращает words и group_words по набору файлов."""
    words, group_words = {}, {}
    for fid, path in files_dict.items():
        parse_file_content(fid, path, words, group_words)
    return words, group_words


def get_index_filename(ch):
    """Возвращает имя файла индекса по первой букве"""
    if 'a' <= ch <= 'z':
        return f"{ord(ch) - ord('a'):02d}"
    elif 'а' <= ch <= 'я':
        return f"{ord(ch) - ord('а') + 26:02d}"
    return None


def read_lines(path):
    """Безопасное чтение строк из файла."""
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return f.readlines()


def write_lines(path, lines):
    """Перезапись файла списком строк."""
    with open(path, "w", encoding="utf-8") as f:
        f.writelines(lines)


def build_word_segment(entries):
    """Создаёт строку вида 5[0:1,2][18:1] для одного file_id."""
    parts = []
    for offset, cols in entries:
        cols_str = ",".join(map(str, cols))
        parts.append(f"[{offset}:{cols_str}]")
    return "".join(parts)


def build_new_segments(words, target_words):
    """Формирует словарь {word: '5[0:1,2][18:1] 8[0:0]'}."""
    new_segments = {}
    for w in target_words:
        parts = []
        for fid, entries in words[w].items():
            file_seg = build_word_segment(entries)
            parts.append(f"{fid}{file_seg}")
        new_segments[w] = " ".join(parts)
    return new_segments


def update_index_file(index_path, target_words, new_segments):
    """Обновляет один индексный файл (index/XX)."""
    lines = read_lines(index_path)
    updated, remaining = [], set(target_words)

    for line in lines:
        stripped = line.strip()
        if ":" not in stripped:
            updated.append(line)
            continue
        word, data = stripped.split(":", 1)
        word = word.strip()
        if word in target_words:
            updated.append(f"{word}: {data.strip()} {new_segments[word]}\n")
            remaining.discard(word)
        else:
            updated.append(line)

    for word in sorted(remaining):
        updated.append(f"{word}: {new_segments[word]}\n")

    tmp_path = index_path + ".tmp"
    write_lines(tmp_path, updated)
    os.replace(tmp_path, index_path)


def update_index_files(root_dir, words, group_words):
    """Обновляет все индексные файлы index/XX."""
    index_dir = os.path.join(root_dir, "index")
    os.makedirs(index_dir, exist_ok=True)

    for first_letter, word_list in group_words.items():
        idx_name = get_index_filename(first_letter)
        if not idx_name:
            continue
        idx_path = os.path.join(index_dir, idx_name)
        target_words = set(word_list)
        new_segments = build_new_segments(words, target_words)
        update_index_file(idx_path, target_words, new_segments)


def file_exists(searching_source, searching_file):
    """Проверка на наличие записи о файле"""
    with open(searching_source, 'r', encoding='utf-8') as file:
        for line in file:
            if line.strip().endswith(searching_file):
                return True
    return False


def add_file_id_to_dict(files_dict, file_realpath, splits_file):
    """Считаем идентификатор для текущего файла и кладем его в словарь"""
    if not files_dict:
        file_id = 1
        with open(splits_file, 'r', encoding='utf-8') as file:
            line_info = file.readline().strip().split()
            file_id += int(line_info[1])
        files_dict[file_id] = file_realpath
    else:
        file_id = max(files_dict.keys())
        file_id += 1
        files_dict[file_id] = file_realpath


def add(root_dir, files):
    """Основная функция add"""
    files_dir = os.path.join(root_dir, 'files')
    zero_files = os.path.join(files_dir, '0_files')
    splits_file = os.path.join(files_dir, '.splits')

    files_dict = {}
    # Для каждого файла, переданного в параметрах
    for new_file in files:
        file_realpath = os.path.realpath(os.path.abspath(new_file))

        # Проверяем, что такой файл существует
        if not os.path.exists(new_file):
            print(f'error: file {new_file} does not exist, skipping...')
            continue

        # Если путь файла найден в 0_files - сообщаем, что он уже добавлен
        if file_exists(zero_files, file_realpath):
            print(f'File {new_file} is already exists, skipping')
            continue

        # Считаем идентификатор для файла из .splits и кладем его в словарь
        add_file_id_to_dict(files_dict, file_realpath, splits_file)

    # Записываем все файлы в 0_files
    with open(zero_files, 'a', encoding='utf-8') as file:
        for file_id, file_path in files_dict.items():
            file.write(f'{file_id} {file_path}\n')

    # Обновляем файл .splits в соответствии с количеством добавляемых файлов
    file_update(splits_file, 0, len(files_dict.keys()))

    # # Извлечем данные из всех файлов
    words, group_words = get_file_data(files_dict)
    update_index_files(root_dir, words, group_words)
    print(f"files {str(files)} was successfully added")
