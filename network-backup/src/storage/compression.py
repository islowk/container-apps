import io
import zipfile
from pathlib import Path


def compress_backup(backup_dir: Path) -> io.BytesIO:
    """
    Compress backup directory into a ZIP file in memory.
    """
    print(f"\n Compressing backup...")
    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for file_path in backup_dir.rglob("*.json"):
            arcname = file_path.relative_to(backup_dir.parent)
            zf.write(file_path, arcname)

    zip_buffer.seek(0)
    size_mb = len(zip_buffer.getvalue()) / (1024 * 1024)
    print(f"Compressed size: {size_mb:.2f} MB")
    return zip_buffer
