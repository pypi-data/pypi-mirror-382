"""除外パターンフィルタ（.gitignore完全互換）"""
import os
import pathspec
from typing import List
from filters.base import FileFilter

class IgnoreFilter(FileFilter):
    """除外パターンに基づくフィルタ（gitignore互換）"""

    # VCS関連の自動除外パターン
    VCS_PATTERNS = [
        '.git/',
        '.svn/',
        '.hg/',
        '.bzr/',
        '.gitignore',
        '.gitattributes',
        '.gitmodules',
    ]

    def __init__(self, patterns: List[str], base_dir: str, debug: bool = False, auto_vcs_ignore: bool = False):
        """
        Args:
            patterns: 除外パターンのリスト
            base_dir: ベースディレクトリ
            debug: デバッグモード
            auto_vcs_ignore: VCSディレクトリを自動除外するか
        """
        self.patterns = patterns
        self.base_dir = base_dir
        self.debug = debug

        # VCS自動除外が有効な場合、パターンに追加
        if auto_vcs_ignore:
            combined_patterns = self.VCS_PATTERNS + patterns
            if self.debug:
                print(f"[DEBUG] Auto-ignoring VCS files/directories: {self.VCS_PATTERNS}")
        else:
            combined_patterns = patterns

        # pathspecを使ってgitignore互換のマッチャーを作成
        self.spec = pathspec.PathSpec.from_lines('gitwildmatch', combined_patterns)

    def should_include(self, file_path: str, **kwargs) -> bool:
        """
        ファイルを含めるべきか判定

        Args:
            file_path: ファイルパス

        Returns:
            含める場合True（除外パターンにマッチしない場合）
        """
        return not self._is_ignored(file_path)

    def _is_ignored(self, path: str) -> bool:
        """
        指定されたパスが除外パターンにマッチするかチェック

        Args:
            path: チェック対象のパス

        Returns:
            除外対象の場合True
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
                print(f"[IGNORED] {rel_path}")
            return True

        # ディレクトリの場合、末尾にスラッシュを付けてもう一度チェック
        if os.path.isdir(path):
            if self.spec.match_file(rel_path + '/'):
                if self.debug:
                    print(f"[IGNORED DIR] {rel_path}/")
                return True

        return False

    @staticmethod
    def load_patterns(ignore_file_path: str) -> List[str]:
        """
        ignoreファイルから除外パターンを読み込む

        Args:
            ignore_file_path: ignoreファイルのパス

        Returns:
            除外パターンのリスト
        """
        patterns = []
        if ignore_file_path and os.path.exists(ignore_file_path):
            with open(ignore_file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    # 空行とコメント行をスキップ
                    if line and not line.startswith('#'):
                        patterns.append(line)
        return patterns

    @staticmethod
    def auto_detect_ignore_file(target_dir: str) -> str:
        """
        対象ディレクトリから.gitignoreを自動検出

        Args:
            target_dir: 検索対象のディレクトリ

        Returns:
            見つかった.gitignoreのパス、なければNone
        """
        gitignore_path = os.path.join(target_dir, '.gitignore')
        if os.path.exists(gitignore_path):
            return gitignore_path
        return None

    @staticmethod
    def load_patterns_from_multiple(file_paths: List[str]) -> List[str]:
        """
        複数のignoreファイルからパターンを読み込んでマージ

        Args:
            file_paths: ignoreファイルのパスのリスト

        Returns:
            マージされた除外パターンのリスト
        """
        all_patterns = []
        for file_path in file_paths:
            if file_path:
                patterns = IgnoreFilter.load_patterns(file_path)
                all_patterns.extend(patterns)
        return all_patterns