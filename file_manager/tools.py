import json
from pathlib import Path


def collection(
    collection_name: str | Path,
    dest: str | Path,
    thread_id: str,
) -> None:
    """Add a file name to the per-thread list in a JSON collection file.

    If the JSON file doesn't exist, it is created.
    If the thread_id doesn't exist, a new list is created for it.
    Duplicate file names for the same thread_id are ignored.
    """
    collection_path = Path(collection_name)
    dest_path = Path(dest)

    # ۱. اگر فایل وجود ندارد، بساز (و پوشه‌ی پدر را هم اگر لازم بود)
    if not collection_path.exists():
        collection_path.touch()          # فایل خالی می‌سازد

    # ۲. خواندن داده‌ی موجود
    with open(collection_path, "r", encoding="utf-8") as r:
        try:
            data = json.load(r)
        except json.JSONDecodeError:
            data = {}

    # ۳. merge کردن فایل جدید
    file_name = dest_path.stem + dest_path.suffix
    data.setdefault(thread_id, [])
    if file_name not in data[thread_id]:
        data[thread_id].append(file_name)

    # ۴. نوشتن دوباره
    with open(collection_path, "w", encoding="utf-8") as w:
        json.dump(data, w, ensure_ascii=False, indent=2)