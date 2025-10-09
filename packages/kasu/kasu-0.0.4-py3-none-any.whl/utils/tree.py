"""ツリー表示機能"""
import os
from typing import List


class TreeBuilder:
    """ディレクトリツリー構造を生成"""

    def __init__(self, ignore_filter, glob_filter):
        self.ignore_filter = ignore_filter
        self.glob_filter = glob_filter

    def build(self, target_dir: str) -> str:
        """
        ディレクトリツリー構造を文字列として生成

        Args:
            target_dir: 検索対象のディレクトリ

        Returns:
            ツリー構造の文字列
        """
        lines = []
        # 絶対パスではなくベース名を表示
        base_name = os.path.basename(os.path.abspath(target_dir))
        if not base_name:  # ルートディレクトリの場合
            base_name = target_dir
        lines.append(f"{base_name}/")

        self._walk_directory(target_dir, target_dir, "", lines)

        return "\n".join(lines)

    def _walk_directory(self, directory: str, base_dir: str, prefix: str, lines: List[str]):
        """再帰的にディレクトリを走査"""
        try:
            entries = sorted(os.listdir(directory))
        except PermissionError:
            return

        dirs = []
        files = []

        for entry in entries:
            entry_path = os.path.join(directory, entry)

            # 除外判定
            if not self.ignore_filter.should_include(entry_path):
                continue

            if os.path.isdir(entry_path):
                dirs.append(entry)
            elif os.path.isfile(entry_path):
                # GlobFilterで判定
                if self.glob_filter.should_include(entry_path):
                    from core.file_scanner import FileScanner
                    if FileScanner._is_text_file(entry_path):
                        files.append(entry)

        all_entries = dirs + files
        for i, entry in enumerate(all_entries):
            is_last = (i == len(all_entries) - 1)
            entry_path = os.path.join(directory, entry)

            if is_last:
                lines.append(f"{prefix}└── {entry}" + ("/" if entry in dirs else ""))
                new_prefix = prefix + "    "
            else:
                lines.append(f"{prefix}├── {entry}" + ("/" if entry in dirs else ""))
                new_prefix = prefix + "│   "

            if entry in dirs:
                self._walk_directory(entry_path, base_dir, new_prefix, lines)