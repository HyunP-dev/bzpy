from __future__ import annotations
import zipfile
from typing import *
import subprocess
import re
import os


class ArchiveFile:
    def __init__(self, path: str):
        self.path = path

    def infolist(self) -> list[EntryInfo]:
        """Return a list of class EntryInfo instances for files in the archive."""
        p = subprocess.Popen(["bz", "l", self.path],
                             stdout=subprocess.PIPE, text=True)
        stdout, stderr = p.communicate()
        infolist = []
        for line in stdout.splitlines()[6:-2]:
            date_, time_, attr, file_size, compress_size, filename = re.split(
                " +", line, maxsplit=5)
            date_time = date_ + " " + time_
            file_size = int(file_size)
            compress_size = int(compress_size)
            entry_info = EntryInfo(date_time, attr,
                                   file_size, compress_size, filename)
            infolist.append(entry_info)
        return infolist

    def namelist(self) -> list[str]:
        """Return a list of file names in the archive."""
        p = subprocess.Popen(["bz", "l", "-list:s", self.path],
                             stdout=subprocess.PIPE, text=True)
        stdout, stderr = p.communicate()
        return stdout.splitlines()

    def extract(self, member: str | EntryInfo,
                path: str=os.getcwd(), pwd: Optional[bytes]=None):
        """Extract a member from the archive."""
        self.extractall(path, [member], pwd)

    def extractall(self, path: str,
                   members: list[str | EntryInfo] = [],
                   pwd: Optional[bytes] = None) -> Generator[str]:
        """Extract all members from the archive."""
        cmd = (f"bz x -y -o:\"{path}\" {self.path} "
            + " ".join('"' + (member if isinstance(member, str) else member.filename) + '"'
                       for member in members)
            + (pwd.decode() if pwd is not None else ""))
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                             text=True, bufsize=1, shell=False, cwd=os.getcwd())
        for i, line in enumerate(p.stdout):
            print(line)
            if i < 2:
                continue
            yield line.strip()


class EntryInfo:
    def __init__(self, date_time: str, attr: str,
                 file_size: int, compress_size: int, filename: str):
        self.date_time = date_time
        self.attr = attr
        self.file_size = file_size
        self.compress_size = compress_size
        self.filename = filename

    def __repr__(self):
        infos = []
        for name in ["filename", "file_size", "compress_size"]:
            infos.append(name + "=" + repr(getattr(self, name)))
        return f"<EntryInfo {' '.join(infos)}>"
