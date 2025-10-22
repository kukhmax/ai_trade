#!/usr/bin/env python3
"""
Скрипт для удаления кэш-файлов и артефактов сборки в проекте.
Поддерживает режим проверки (dry-run) и опцию удаления виртуального окружения.
"""
import argparse
import os
import shutil
import sys
import stat
from pathlib import Path
from typing import List, Tuple

# Имена директорий, которые будут удалены, если найдены в дереве проекта
DIRS_TO_REMOVE = {
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".ipynb_checkpoints",
    ".cache",
    ".tox",
    "build",
    "dist",
    "htmlcov",
}

# Имена файлов и расширения, которые считаются кэшем/артефактами
FILE_NAMES_TO_REMOVE = {
    ".DS_Store",
    "Thumbs.db",
    ".coverage",
    "coverage.xml",
}
FILE_EXTS_TO_REMOVE = {
    ".pyc",
    ".pyo",
}

VENVS = {".venv", "venv"}


def make_writable(path: Path) -> None:
    """Снимает флаг read-only, чтобы можно было удалить файл/директорию на Windows."""
    try:
        mode = path.stat().st_mode
        path.chmod(mode | stat.S_IWRITE)
    except Exception:
        pass


def handle_remove_readonly(func, path, exc_info):
    """Обработчик для shutil.rmtree на случай read-only файлов/папок."""
    try:
        p = Path(path)
        make_writable(p)
        func(path)
    except Exception:
        # Игнорируем повторную ошибку удаления, чтобы скрипт шел дальше
        pass


def dir_size(path: Path) -> int:
    """Оценивает размер содержимого директории в байтах."""
    total = 0
    for p in path.rglob("*"):
        try:
            if p.is_file():
                total += p.stat().st_size
        except Exception:
            # Пропускаем проблемные файлы
            pass
    return total


def remove_dir(path: Path, dry_run: bool = False, verbose: bool = False) -> int:
    """Удаляет директорию рекурсивно. Возвращает примерный размер очищенного места (байты)."""
    size = dir_size(path)
    if dry_run:
        print(f"[DRY] rmdir {path}")
        return size
    try:
        shutil.rmtree(path, onerror=handle_remove_readonly)
        if verbose:
            print(f"Removed dir {path}")
    except Exception as e:
        print(f"Failed to remove dir {path}: {e}", file=sys.stderr)
    return size


def remove_file(path: Path, dry_run: bool = False, verbose: bool = False) -> int:
    """Удаляет файл. Возвращает размер файла (байты)."""
    try:
        size = path.stat().st_size if path.exists() and path.is_file() else 0
    except Exception:
        size = 0
    if dry_run:
        print(f"[DRY] rm {path}")
        return size
    try:
        make_writable(path)
        path.unlink(missing_ok=True)
        if verbose:
            print(f"Removed file {path}")
        return size
    except Exception as e:
        print(f"Failed to remove file {path}: {e}", file=sys.stderr)
        return 0


def collect_targets(root: Path, include_venv: bool = False) -> Tuple[List[Path], List[Path]]:
    """Собирает директории и файлы для удаления."""
    dirs: List[Path] = []
    files: List[Path] = []

    for p in root.rglob("*"):
        if p.is_dir():
            name = p.name
            lower = name.lower()
            if lower in DIRS_TO_REMOVE:
                dirs.append(p)
            elif lower.endswith(".egg-info"):
                dirs.append(p)
            elif include_venv and lower in VENVS:
                dirs.append(p)
        else:
            name = p.name
            lower = name.lower()
            if lower in FILE_NAMES_TO_REMOVE:
                files.append(p)
            elif p.suffix.lower() in FILE_EXTS_TO_REMOVE:
                files.append(p)
    return dirs, files


def human_bytes(n: int) -> str:
    """Человекочитаемый формат байтов."""
    units = ["B", "KB", "MB", "GB"]
    size = float(n)
    for u in units:
        if size < 1024.0 or u == units[-1]:
            return f"{size:.2f} {u}"
        size /= 1024.0


def main():
    parser = argparse.ArgumentParser(
        description="Удаление кэш-файлов и артефактов сборки в проекте"
    )
    parser.add_argument(
        "--root", "-r",
        default=str(Path.cwd()),
        help="Корневой каталог проекта (по умолчанию текущий)"
    )
    parser.add_argument(
        "--dry-run", "-n",
        action="store_true",
        help="Показать, что будет удалено, без удаления"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Подробные сообщения"
    )
    parser.add_argument(
        "--include-venv",
        action="store_true",
        help="Также удалить виртуальное окружение (.venv/venv)"
    )

    args = parser.parse_args()
    root = Path(args.root).resolve()

    if not root.exists():
        print(f"Корень не найден: {root}", file=sys.stderr)
        sys.exit(1)

    print(f"Root: {root}")

    dirs, files = collect_targets(root, include_venv=args.include_venv)

    # Удаляем сначала вложенные директории (сортируем по длине пути убыв.)
    total_bytes = 0
    for d in sorted(set(dirs), key=lambda p: len(str(p)), reverse=True):
        total_bytes += remove_dir(d, dry_run=args.dry_run, verbose=args.verbose)

    for f in files:
        total_bytes += remove_file(f, dry_run=args.dry_run, verbose=args.verbose)

    print(f"Готово. Удалено директорий: {len(dirs)}, файлов: {len(files)}")
    if args.dry_run:
        print("Режим проверки: ничего не удалено.")
    else:
        print(f"Освобождено примерно: {human_bytes(total_bytes)}")


if __name__ == "__main__":
    main()