"""Markdown形式のジェネレータ"""
import os
import sys
from typing import List, Dict, Tuple, Optional

from generators.base import ContentGenerator
from sanitizers.sanitizer import Sanitizer
from utils.language_map import LanguageMapper
from utils.format_utils import format_size


class MarkdownGenerator(ContentGenerator):
    """Markdown形式でコンテンツを生成"""

    def __init__(self):
        """初期化"""
        pass

    def generate(
        self,
        target_files: List[Dict[str, any]],
        target_dir: str,
        enable_sanitize: bool = False,
        custom_replacements: Optional[List[Tuple[str, str]]] = None,
        head_lines: Optional[int] = None,
        tail_lines: Optional[int] = None,
        include_tree: bool = False,
        include_list: bool = False,
        include_stats: bool = False,
        include_merge: bool = True,
        tree_structure: Optional[str] = None,
        list_structure: Optional[str] = None
    ) -> Tuple[str, Dict[str, int]]:
        """
        Markdown形式でコンテンツを生成

        Args:
            target_files: ファイル情報のリスト
            target_dir: ターゲットディレクトリ
            enable_sanitize: サニタイズを有効にするか
            custom_replacements: カスタム置換パターン
            head_lines: 各ファイルの先頭N行のみ
            tail_lines: 各ファイルの末尾N行のみ
            include_tree: ツリー構造を含めるか
            include_stats: 統計情報を含めるか
            include_merge: ファイル結合を含めるか
            tree_structure: ツリー構造文字列

        Returns:
            (生成されたMarkdownコンテンツ, サニタイズ統計)
        """
        content_parts = []
        all_stats = {}

        sanitizer = Sanitizer(enable_sanitize, custom_replacements)

        # サマリー統計
        if include_stats:
            total_size = sum(f['size'] for f in target_files)
            total_lines = sum(f['lines'] for f in target_files)

            content_parts.append("## Summary\n\n")
            content_parts.append(f"- **Total files**: {len(target_files)}\n")
            content_parts.append(f"- **Total lines**: {total_lines:,}\n")
            content_parts.append(f"- **Total size**: {format_size(total_size)}\n\n")

            # 拡張子別の統計
            ext_stats = self._calculate_extension_stats(target_files)
            if ext_stats:
                content_parts.append("### By Extension\n\n")
                content_parts.append("| Extension | Files | Lines | Size |\n")
                content_parts.append("|-----------|-------|-------|------|\n")
                for ext, stats in sorted(ext_stats.items(), key=lambda x: x[1]['count'], reverse=True):
                    content_parts.append(
                        f"| {ext} | {stats['count']} | {stats['lines']:,} | {format_size(stats['size'])} |\n"
                    )
                content_parts.append("\n")

            content_parts.append("---\n\n")

        # ディレクトリ構造（ツリー）
        if include_tree and tree_structure:
            content_parts.append("## Directory Structure\n\n")
            content_parts.append("```\n")
            content_parts.append(tree_structure)
            if not tree_structure.endswith('\n'):
                content_parts.append('\n')
            content_parts.append("```\n\n")
            content_parts.append("---\n\n")

        # ファイル一覧
        if include_list and list_structure:
            content_parts.append("## File List\n\n")
            content_parts.append("```\n")
            content_parts.append(list_structure)
            if not list_structure.endswith('\n'):
                content_parts.append('\n')
            content_parts.append("```\n\n")
            content_parts.append("---\n\n")

        # 各ファイルの内容
        if include_merge:
            content_parts.append("## Files\n\n")

            for file_info in target_files:
                file_path = file_info['path']
                language = LanguageMapper.get_language(file_path)

                # ファイル名をヘッダーに
                content_parts.append(f"### `{file_path}`\n\n")

                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        file_content = f.read()

                    # head/tail 処理
                    if head_lines is not None:
                        lines = file_content.split('\n')[:head_lines]
                        file_content = '\n'.join(lines)
                        if len(lines) == head_lines and file_content:
                            file_content += "\n... (truncated)\n"
                    elif tail_lines is not None:
                        lines = file_content.split('\n')[-tail_lines:]
                        file_content = "... (truncated)\n" + '\n'.join(lines)

                    # サニタイズ
                    file_content, stats = sanitizer.sanitize(file_content)
                    for key, count in stats.items():
                        all_stats[key] = all_stats.get(key, 0) + count

                    # コードブロック
                    content_parts.append(f"```{language}\n")
                    content_parts.append(file_content)
                    if not file_content.endswith('\n'):
                        content_parts.append('\n')
                    content_parts.append("```\n\n")
                except UnicodeDecodeError:
                    content_parts.append(f"```text\n[Error: Cannot decode file {file_path} as text]\n```\n\n")
                    print(f"Warning: Failed to read {file_path} (encoding issue)", file=sys.stderr)
                except PermissionError:
                    content_parts.append(f"```text\n[Error: Permission denied reading {file_path}]\n```\n\n")
                    print(f"Warning: Permission denied reading {file_path}", file=sys.stderr)
                except Exception as e:
                    content_parts.append(f"```text\n[Error reading {file_path}: {e}]\n```\n\n")
                    print(f"Warning: Failed to read {file_path}: {e}", file=sys.stderr)

        return ''.join(content_parts), all_stats

    def _calculate_extension_stats(self, target_files: List[Dict[str, any]]) -> Dict[str, Dict]:
        """拡張子別の統計を計算"""
        stats = {}
        for file_info in target_files:
            ext = os.path.splitext(file_info['path'])[1] or '(no extension)'
            if ext not in stats:
                stats[ext] = {'count': 0, 'lines': 0, 'size': 0}
            stats[ext]['count'] += 1
            stats[ext]['lines'] += file_info['lines']
            stats[ext]['size'] += file_info['size']
        return stats