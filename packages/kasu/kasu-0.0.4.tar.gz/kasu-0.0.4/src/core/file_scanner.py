"""ファイルスキャナー"""
import os
import sys
import chardet
from typing import List, Dict
from filters.base import FileFilter


class FileScanner:
    """ファイルスキャンと収集を管理"""

    def __init__(self, filters: List[FileFilter], debug: bool = False):
        self.filters = filters
        self.debug = debug
        # 統計情報
        self.stats = {
            'scanned': 0,
            'glob_filtered': 0,
            'ignored': 0,
            'non_text': 0,
            'size_filtered': 0,
            'included': 0
        }

    def scan(self, target_dir: str) -> List[Dict[str, any]]:
        """
        ディレクトリをスキャンしてファイル情報を収集

        Args:
            target_dir: スキャン対象ディレクトリ

        Returns:
            ファイル情報のリスト
        """
        target_files = []
        # 統計をリセット
        self.stats = {
            'scanned': 0,
            'glob_filtered': 0,
            'ignored': 0,
            'non_text': 0,
            'size_filtered': 0,
            'included': 0
        }

        # シンボリックリンクを追跡しない（無限ループ防止）
        for root, dirs, files in os.walk(target_dir, followlinks=False):
            # ディレクトリフィルタ適用
            original_dirs = dirs[:]
            dirs[:] = [d for d in dirs if self._should_include_dir(os.path.join(root, d))]

            # 除外されたディレクトリをカウント
            if len(original_dirs) != len(dirs):
                removed_count = len(original_dirs) - len(dirs)
                self.stats['ignored'] += removed_count

            for file in files:
                file_path = os.path.join(root, file)

                # シンボリックリンクはスキップ
                if os.path.islink(file_path):
                    if self.debug:
                        print(f"[SKIPPED SYMLINK] {file_path}")
                    continue

                self.stats['scanned'] += 1

                # 全フィルタを適用（どのフィルタで除外されたか記録）
                filter_result = self._apply_filters(file_path)
                if filter_result != 'included':
                    if filter_result in self.stats:
                        self.stats[filter_result] += 1
                    continue

                # テキストファイル判定
                if self._is_text_file(file_path):
                    file_info = self._get_file_info(file_path)
                    target_files.append(file_info)
                    self.stats['included'] += 1
                    if self.debug:
                        print(f"[ADDED] {file_path}")
                else:
                    self.stats['non_text'] += 1
                    if self.debug:
                        print(f"[SKIPPED NON-TEXT] {file_path}")

        return target_files

    def get_stats(self) -> Dict[str, int]:
        """
        スキャン統計を取得

        Returns:
            統計情報の辞書
        """
        return self.stats.copy()

    def _should_include_dir(self, dir_path: str) -> bool:
        """ディレクトリを含めるべきか判定"""
        for filter_obj in self.filters:
            if not filter_obj.should_include(dir_path):
                return False
        return True

    def _apply_filters(self, file_path: str) -> str:
        """
        フィルタを適用し、どのフィルタで除外されたか返す

        Returns:
            'included', 'glob_filtered', 'ignored', 'size_filtered' のいずれか
        """
        for filter_obj in self.filters:
            if not filter_obj.should_include(file_path):
                # フィルタの種類を判定
                filter_class = filter_obj.__class__.__name__
                if filter_class == 'GlobFilter':
                    return 'glob_filtered'
                elif filter_class == 'IgnoreFilter':
                    return 'ignored'
                return 'ignored'  # デフォルト
        return 'included'

    @staticmethod
    def _is_text_file(file_path: str) -> bool:
        """ファイルがテキストファイルかどうか判定"""
        try:
            with open(file_path, 'rb') as f:
                raw_data = f.read(2048)
            result = chardet.detect(raw_data)
            encoding = result['encoding']
            if encoding:
                with open(file_path, 'r', encoding=encoding) as f:
                    f.read(2048)
                return True
        except Exception:
            return False
        return False

    @staticmethod
    def _get_file_info(file_path: str) -> Dict[str, any]:
        """ファイル情報を取得"""
        info = {
            'path': file_path,
            'size': 0,
            'lines': 0,
        }

        try:
            file_size = os.path.getsize(file_path)
            info['size'] = file_size

            # 巨大ファイル（100MB以上）の場合は警告
            if file_size > 100 * 1024 * 1024:
                print(f"Warning: Large file detected ({file_path}, {file_size / (1024*1024):.1f}MB)", file=sys.stderr)
                print("         This may consume significant memory.", file=sys.stderr)

            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                info['lines'] = sum(1 for _ in f)
        except Exception:
            pass

        return info