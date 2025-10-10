from __future__ import annotations

import asyncio
import logging
import math
import os
import shutil
import time
import weakref
import zipfile
from collections.abc import Callable
from datetime import datetime, timezone, timedelta
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Optional, Union

from .typings import SampleIndex


class TraceStore:
    """
    Trace storage component for NAS-friendly layout with low metadata IOPS.

    Layout (root directory):
      by-time/YY/MM/DD/HH/<task_index>-<session_id>-<ts><ext | .zip>
      by-session/aa/bb/session_<session_id> -> symlink to by-time files
      by-task/<task_index>/aa/bb/session_<session_id> -> symlink to by-time files

    - aa/bb are two-level buckets derived from session_id to cap files per dir.
    - Writes are atomic via same-directory rename (os.replace).
    - If a temp trace dir contains exactly 1 file, we move that file to final path.
      If it contains >1 files, we zip the directory to a single .zip and store that.
    """

    def __init__(self, root: Union[os.PathLike, str]):
        self.logger = logging.getLogger(__name__)

        self.root = Path(root).resolve()
        self.root.mkdir(parents=True, exist_ok=True)

        self.by_time = self.root / 'by-time'
        self.by_session = self.root / 'by-session'
        self.by_task = self.root / 'by-task'

    def new_trace(self, task_index: SampleIndex, session_id: int, ts: Optional[int] = None) -> TraceWriter:
        """Create a temporary directory for a new trace and return a writer.
        - `ts`: default now (int milliseconds). Used to place by-time.
        """
        if ts is None:
            ts = math.floor(time.time() * 1e3)  # epoch milliseconds
        dir_by_time = self._time_partition_path(self.by_time, ts)

        # final file basename (extension will be decided at finalize)
        file_base = f'{task_index}-{session_id}-{ts}'

        def _finalize(tmp_dir: Path) -> Optional[Path]:
            files = list(tmp_dir.rglob('*'))
            if not files:
                self.logger.info(f'No trace files to save for {task_index=} {session_id=}')
                return None
            self.logger.info(f'Saving {len(files)} trace files for {task_index=} {session_id=}')

            dir_by_time.mkdir(parents=True, exist_ok=True)
            if len(files) == 1 and files[0].is_file():
                file_ext = files[0].suffix or '.bin'
                file_name = file_base + file_ext
                final_path = dir_by_time / file_name
                self._atomic_move(files[0], final_path)
            else:
                file_name = file_base + '.zip'
                final_path = dir_by_time / file_name
                self._zip_dir(tmp_dir, final_path)

            dir_by_task = self._session_bucket(self.by_task / str(task_index), session_id)
            self._create_link(dir_by_task / f'session_{session_id}', final_path)

            dir_by_session = self._session_bucket(self.by_session, session_id)
            self._create_link(dir_by_session / f'session_{session_id}', final_path)

            return final_path

        return TraceWriter(_finalize)

    @staticmethod
    def _create_link(link_path: Path, target_path: Path) -> None:
        link_path.parent.mkdir(parents=True, exist_ok=True)
        relative_path = os.path.relpath(target_path.resolve(), start=link_path.parent.resolve())

        try:
            if link_path.is_symlink() or link_path.exists():
                link_path.unlink()
            link_path.symlink_to(relative_path)
        except FileExistsError:
            # Rare race; best-effort replace.
            try:
                link_path.unlink()
            except FileNotFoundError:
                pass
            link_path.symlink_to(relative_path)

    @staticmethod
    def _session_bucket(root: Path, session_id: int) -> Path:
        """Compute the two-level bucket path for a session_id under root."""
        a = f'{(session_id >> 8) & 0xFF:02x}'
        b = f'{(session_id >> 0) & 0xFF:02x}'
        return root / a / b

    @staticmethod
    def _time_partition_path(root: Path, ts: int) -> Path:
        """Compute the by-time partition path for a given epoch milliseconds timestamp at UTC+8 timezone."""
        dt = datetime.fromtimestamp(ts / 1e3, tz=timezone.utc).astimezone(timezone(timedelta(hours=8)))
        return root / dt.strftime('%y/%m/%d/%H')

    @staticmethod
    def _atomic_move(src: Path, dst: Path) -> None:
        # Move into same filesystem; if different FS, fallback to copy+replace
        try:
            os.replace(src, dst)
        except OSError:
            # Different device or other issue; copy then replace
            tmp = dst.with_suffix(dst.suffix + '.partial')
            shutil.copy2(src, tmp)
            os.replace(tmp, dst)

    @staticmethod
    def _zip_dir(src_dir: Path, dst_zip: Path) -> None:
        tmp = dst_zip.with_suffix(dst_zip.suffix + '.partial')
        with zipfile.ZipFile(tmp, mode='w', compression=zipfile.ZIP_DEFLATED) as zf:
            for p in sorted(src_dir.rglob('*')):
                if p.is_file():
                    arcname = p.relative_to(src_dir).as_posix()
                    zf.write(p, arcname=arcname)
        os.replace(tmp, dst_zip)


class TraceWriter:
    """Context manager wrapping a temporary trace directory."""

    def __init__(self, finalize_callback: Callable[[Path], Optional[Path]]):
        self.tmp_dir = TemporaryDirectory(prefix='trace')
        self.final_path: Optional[Path] = None
        self.finalize_callback = finalize_callback
        self._finalized = False
        self._finalizer = weakref.finalize(self, finalize_callback, Path(self.tmp_dir.name))

    def __enter__(self) -> TraceWriter:
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    async def __aenter__(self) -> TraceWriter:
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.aclose()

    def get_dir(self) -> Path:
        return Path(self.tmp_dir.name)

    def close(self) -> Path:
        if self._finalized:
            return self.final_path
        self.final_path = self.finalize_callback(self.get_dir())
        self._finalized = True
        if self._finalizer.alive:
            self._finalizer()
        return self.final_path

    async def aclose(self) -> Path:
        if self._finalized:
            return self.final_path
        self.final_path = await asyncio.to_thread(self.finalize_callback, self.get_dir())
        self._finalized = True
        if self._finalizer.alive:
            self._finalizer()
        return self.final_path
