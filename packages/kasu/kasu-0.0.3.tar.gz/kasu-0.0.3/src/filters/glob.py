"""Globパターンフィルタ"""
import os
import pathspec
from typing import List, Optional
from filters.base import FileFilter

class GlobFilter(FileFilter):
    """Globパターンに基づくフィルタ"""

    def __init__(self, patterns: Optional[List[str]] = None, base_dir: str = ".", debug: bool = False):
        """
        Args:
            patterns: Globパターンのリスト (例: ['*.py', 'src/**/*.js'])
            base_dir: ベースディレクトリ
            debug: デバッグモード
        """
        self.patterns = patterns or []
        self.base_dir = base_dir
        self.debug = debug

        # パターンが指定されていない場合は全てマッチ
        if not self.patterns:
            self.spec = None
        else:
            # pathspecを使ってgitignore互換のマッチャーを作成
            try:
                self.spec = pathspec.PathSpec.from_lines('gitwildmatch', self.patterns)
            except Exception as e:
                raise ValueError(f"Invalid glob pattern: {e}")

    def should_include(self, file_path: str, **kwargs) -> bool:
        """
        ファイルがパターンにマッチするか判定

        Args:
            file_path: ファイルパス

        Returns:
            マッチする場合True（パターンが未指定の場合は常にTrue）
        """
        # パターンが指定されていない場合は全て含める
        if self.spec is None:
            return True

        # ディレクトリの場合は常にTrue（中身をスキャンするため）
        if os.path.isdir(file_path):
            return True

        return self._matches_pattern(file_path)

    def is_active(self) -> bool:
        """Globフィルタが有効かどうか"""
        return self.spec is not None

    def _matches_pattern(self, path: str) -> bool:
        """
        指定されたパスがGlobパターンにマッチするかチェック

        Args:
            path: チェック対象のパス

        Returns:
            マッチする場合True
        """
        # 相対パスに変換
        try:
            rel_path = os.path.relpath(path, self.base_dir)
        except ValueError:
            # 異なるドライブなどで相対パスが作れない場合
            return False

        # Windowsパスの場合、スラッシュに変換
        rel_path = rel_path.replace(os.sep, '/')

        # pathspecでマッチング
        if self.spec.match_file(rel_path):
            if self.debug:
                print(f"[GLOB MATCHED] {rel_path}")
            return True

        if self.debug:
            print(f"[GLOB NOT MATCHED] {rel_path}")

        return False