#!/usr/bin/env python3

import os
import sys
import shutil
import hashlib
import json
import platform
from datetime import datetime, timedelta
from pathlib import Path

# ========================================
# НАСТРОЙКИ — меняй под себя
# ========================================

# Автоматически определяем систему
IS_WINDOWS = platform.system() == "Windows"

if IS_WINDOWS:
    SOURCE      = r"C:\Users\Admin\projects"     # Что бэкапим
    BACKUP_DIR  = r"C:\Backups"                  # Куда бэкапим
    STATE_FILE  = r"C:\Backups\.file_state.json"
    LOG_FILE    = r"C:\Backups\backup.log"
else:
    SOURCE      = "/home/user/projects"
    BACKUP_DIR  = "/home/user/backups"
    STATE_FILE  = "/home/user/backups/.file_state.json"
    LOG_FILE    = "/home/user/backups/backup.log"

KEEP_DAYS = 15

# ========================================

def log(msg):
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    line = f"[{now}] {msg}"
    print(line)
    os.makedirs(BACKUP_DIR, exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")

def get_file_hash(filepath):
    h = hashlib.md5()
    try:
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
        return h.hexdigest()
    except:
        return None

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_state(state):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)

def scan_changes(old_state):
    new_state = {}
    changed = []

    for root, dirs, files in os.walk(SOURCE):
        for filename in files:
            filepath = os.path.join(root, filename)
            file_hash = get_file_hash(filepath)
            new_state[filepath] = file_hash

            if filepath not in old_state:
                changed.append((filepath, "НОВЫЙ"))
            elif old_state[filepath] != file_hash:
                changed.append((filepath, "ИЗМЕНЁН"))

    for filepath in old_state:
        if filepath not in new_state:
            changed.append((filepath, "УДАЛЁН"))

    return new_state, changed

def backup_changed_files(changed_files):
    if not changed_files:
        log("✅ Изменений нет — бэкап не нужен")
        return

    date_str = datetime.now().strftime("%Y-%m-%d_%H-%M")
    backup_path = os.path.join(BACKUP_DIR, f"backup_{date_str}")
    os.makedirs(backup_path, exist_ok=True)

    backed_up = 0
    for filepath, status in changed_files:
        if status == "УДАЛЁН":
            log(f"🗑  {status}: {filepath}")
            continue

        relative = os.path.relpath(filepath, SOURCE)
        dest = os.path.join(backup_path, relative)
        os.makedirs(os.path.dirname(dest), exist_ok=True)

        try:
            shutil.copy2(filepath, dest)
            log(f"💾 {status}: {relative}")
            backed_up += 1
        except Exception as e:
            log(f"❌ Ошибка: {filepath}: {e}")

    shutil.make_archive(backup_path, "gztar", backup_path)
    shutil.rmtree(backup_path)
    log(f"📦 Бэкап создан: backup_{date_str}.tar.gz ({backed_up} файлов)")

def cleanup_old_backups():
    cutoff = datetime.now() - timedelta(days=KEEP_DAYS)
    deleted = 0

    for file in Path(BACKUP_DIR).glob("backup_*.tar.gz"):
        if datetime.fromtimestamp(file.stat().st_mtime) < cutoff:
            file.unlink()
            log(f"🗑  Удалён старый бэкап: {file.name}")
            deleted += 1

    if deleted == 0:
        log("🔍 Старых бэкапов нет")

def run():
    log("=" * 40)
    log(f"🚀 Система: {'Windows' if IS_WINDOWS else 'Linux'}")
    log("🚀 Запуск проверки бэкапа")

    old_state = load_state()
    new_state, changed = scan_changes(old_state)

    log(f"🔍 Просканировано файлов: {len(new_state)}")
    log(f"📝 Изменений найдено: {len(changed)}")

    backup_changed_files(changed)
    save_state(new_state)
    cleanup_old_backups()

    log("✅ Готово")
    log("=" * 40)

if __name__ == "__main__":
    run()