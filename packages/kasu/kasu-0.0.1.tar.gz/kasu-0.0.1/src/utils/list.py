"""ファイル一覧表示機能"""
import os
from typing import List, Dict


class ListBuilder:
    """ファイル一覧を生成"""

    def __init__(self, base_dir: str):
        """
        Args:
            base_dir: ベースディレクトリ
        """
        self.base_dir = base_dir

    def build(self, target_files: List[Dict[str, any]]) -> str:
        """
        ファイル一覧を文字列として生成

        Args:
            target_files: ファイル情報のリスト

        Returns:
            ファイル一覧の文字列
        """
        lines = []
        
        for file_info in target_files:
            file_path = file_info['path']
            # ベースディレクトリからの相対パスを取得
            try:
                rel_path = os.path.relpath(file_path, self.base_dir)
            except ValueError:
                # 異なるドライブなどで相対パスが作れない場合は絶対パス
                rel_path = file_path
            
            lines.append(rel_path)

        return "\n".join(lines)

    def build_with_stats(self, target_files: List[Dict[str, any]]) -> str:
        """
        ファイル一覧を統計情報付きで生成

        Args:
            target_files: ファイル情報のリスト

        Returns:
            統計情報付きファイル一覧の文字列
        """
        from .format_utils import format_size
        
        lines = []
        
        for file_info in target_files:
            file_path = file_info['path']
            size = file_info['size']
            line_count = file_info['lines']
            
            # ベースディレクトリからの相対パスを取得
            try:
                rel_path = os.path.relpath(file_path, self.base_dir)
            except ValueError:
                rel_path = file_path
            
            # フォーマット: "path (size, lines lines)"
            lines.append(f"{rel_path} ({format_size(size)}, {line_count:,} lines)")

        return "\n".join(lines)