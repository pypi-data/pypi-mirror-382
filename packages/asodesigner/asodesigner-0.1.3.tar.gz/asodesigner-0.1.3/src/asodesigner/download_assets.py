#!/usr/bin/env python3
import asyncio
import gzip
import tarfile
import threading
import time
import types
import zipfile
from pathlib import Path

import requests
from tqdm import tqdm

# ``mega`` depends on ``tenacity`` versions that still expect ``asyncio.coroutine``.
# Python >=3.12 removed this alias, so recreate it if needed before importing mega.
if not hasattr(asyncio, "coroutine"):
    asyncio.coroutine = types.coroutine


def download(task):
    out = Path(task["output"])
    result_path = Path(task.get("result") or out)

    url = task["url"]
    if "mega.nz" in url:
        from mega import Mega
        mega = Mega().login()
        info = mega.get_public_url_info(url)
        name = info.get("name") or "file"
        size = info.get("size")

        out = (out / name) if out.is_dir() or out.suffix == "" else out
        out.parent.mkdir(parents=True, exist_ok=True)
        download_dir = out.parent
        tmp = download_dir / name

        bar = tqdm(total=size, unit="B", unit_scale=True, desc=f"downloading {name}")
        err = []

        def worker():
            try:
                mega.download_url(url, dest_path=str(download_dir))
            except Exception as e:
                err.append(e)

        t = threading.Thread(target=worker, daemon=True)
        t.start()
        prev = 0
        while t.is_alive():
            if tmp.exists():
                cur = tmp.stat().st_size
                bar.update(cur - prev)
                prev = cur
            time.sleep(0.5)
        t.join()
        if tmp.exists():
            cur = tmp.stat().st_size
            bar.update(cur - prev)
            if tmp != out:
                tmp.rename(out)
        bar.close()
        if err:
            raise err[0]
    else:
        out.parent.mkdir(parents=True, exist_ok=True)
        with requests.get(url, stream=True, timeout=60) as r:
            r.raise_for_status()
            total = int(r.headers.get("content-length", 0))
            bar = tqdm(
                total=total or None,
                unit="B",
                unit_scale=True,
                desc=f"downloading {out.name or 'file'}",
            )
            with out.open("wb") as f:
                for chunk in r.iter_content(1 << 20):
                    if chunk:
                        f.write(chunk)
                        bar.update(len(chunk))
            bar.close()
    if task.get("extract"):
        dest = Path(task.get("extract_to") or out.parent)
        dest.mkdir(parents=True, exist_ok=True)
        name = out.name
        if name.endswith(".zip"):
            with zipfile.ZipFile(out) as z:
                for member in tqdm(z.infolist(), unit="file", desc=f"extracting {name}"):
                    z.extract(member, dest)
            if "result" not in task:
                result_path = dest
        elif name.endswith(".tar.gz") or name.endswith(".tgz"):
            with tarfile.open(out, "r:gz") as z:
                for member in tqdm(z.getmembers(), unit="file", desc=f"extracting {name}"):
                    z.extract(member, dest)
            if "result" not in task:
                result_path = dest
        elif name.endswith(".gz"):
            target = dest / out.stem
            bar = tqdm(
                total=out.stat().st_size,
                unit="B",
                unit_scale=True,
                desc=f"extracting {name}"
            )
            with gzip.open(out, "rb") as src, target.open("wb") as dst:
                while True:
                    chunk = src.read(1 << 20)
                    if not chunk:
                        break
                    dst.write(chunk)
                    bar.update(len(chunk))
            bar.close()
            if "result" not in task:
                result_path = target
        if not task.get("keep_archive"):
            out.unlink(missing_ok=True)
    return result_path

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
HUMAN_DATA_ROOT = PACKAGE_ROOT / "data" / "human" / "human_v34"
HUMAN_DB_DIR = HUMAN_DATA_ROOT / "dbs"

TASKS = [
    {
        "name": "human_db",
        "url": "https://mega.nz/file/3MERkYxY#XPQdtz-0AMhASxGFvhNliFZEdldrfrp2kYDs5e3Jd-M",
        "output": str(HUMAN_DB_DIR / "human_gff_basic_introns.db.gz"),
        "extract": True,
        "extract_to": str(HUMAN_DB_DIR),
        "keep_archive": False,
        "result": str(HUMAN_DB_DIR / "human_gff_basic_introns.db"),
    },
    {
        "name": "human_index_structure",
        "url": "https://mega.nz/file/vdNwgJhD#DnUqX1l7w-yt9yn2xD3lZ7UltYDzD7y4biR_Klswu64",
        "output": str(HUMAN_DATA_ROOT / "index_structure.zip"),
        "extract": True,
        "extract_to": str(HUMAN_DATA_ROOT),
        "keep_archive": False,
        "result": str(HUMAN_DATA_ROOT / "index_structure"),
    },
]

__all__ = ["download", "ensure_assets"]


def ensure_assets(force: bool = False):
    """Ensure required human assets exist locally, downloading any missing files."""
    results = []
    for task in TASKS:
        result_path = Path(task.get("result") or task["output"])
        if not force and result_path.exists():
            print(f"{task['name']} already present at {result_path}")
            results.append(result_path)
            continue

        print(f"downloading {task['name']}")
        downloaded = download(task)
        print(f"stored at {downloaded}")
        results.append(downloaded)

    return results


def main() -> None:
    ensure_assets()


if __name__ == "__main__":
    main()
