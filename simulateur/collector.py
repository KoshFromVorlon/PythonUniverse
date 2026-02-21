import os

# ==========================================
# НАСТРОЙКИ СБОРЩИКА
# ==========================================
OUTPUT_FILE = "код.txt"
THIS_SCRIPT = os.path.basename(__file__)

# Укажите расширения файлов, которые нужно собрать
ALLOWED_EXTENSIONS = ('.py', '.glade', '.ui', '.txt')

# Папки, которые нужно игнорировать (например, виртуальные окружения или git)
IGNORE_DIRS = set(['.git', 'venv', 'env', '__pycache__'])


def collect_code():
    project_dir = os.getcwd()
    total_files = 0

    with open(OUTPUT_FILE, "w", encoding="utf-8") as outfile:
        for root, dirs, files in os.walk(project_dir):
            # Исключаем ненужные директории из обхода
            dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]

            for file in files:
                # Пропускаем сам скрипт и итоговый файл
                if file == THIS_SCRIPT or file == OUTPUT_FILE:
                    continue

                # Берем только нужные форматы
                if file.endswith(ALLOWED_EXTENSIONS):
                    filepath = os.path.join(root, file)
                    rel_path = os.path.relpath(filepath, project_dir)

                    # Пишем красивый заголовок для AI
                    outfile.write(f"\n{'=' * 60}\n")
                    outfile.write(f"ФАЙЛ: {rel_path}\n")
                    outfile.write(f"{'=' * 60}\n\n")

                    # Пытаемся прочитать файл (с защитой от старых кодировок)
                    try:
                        with open(filepath, "r", encoding="utf-8") as infile:
                            outfile.write(infile.read())
                    except UnicodeDecodeError:
                        # Если файл сохранен в старой Windows-кодировке
                        with open(filepath, "r", encoding="cp1251", errors="replace") as infile:
                            outfile.write(infile.read())

                    outfile.write("\n\n")
                    total_files += 1

    print(f"Готово! Собрано файлов: {total_files}. Результат сохранен в '{OUTPUT_FILE}'.")


if __name__ == "__main__":
    collect_code()