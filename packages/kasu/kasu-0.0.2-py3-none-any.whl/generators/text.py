"""テキスト形式のジェネレータ"""
import sys
from typing import List, Dict, Tuple, Optional

from generators.base import ContentGenerator
from sanitizers.sanitizer import Sanitizer
from utils.statistics import Statistics
from utils.format_utils import format_size


class TextGenerator(ContentGenerator):
    """プレーンテキスト形式でコンテンツを生成"""

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
        """テキスト形式でコンテンツを生成"""
        content_parts = []
        all_stats = {}

        sanitizer = Sanitizer(enable_sanitize, custom_replacements)

        # # プロジェクト名
        # project_name = os.path.basename(os.path.abspath(target_dir))

        # 統計情報
        if include_stats:
            stats = Statistics.calculate(target_files)
            content_parts.append("=== Statistics ===\n")
            content_parts.append(f"Total files: {stats['total_files']:,}\n")
            content_parts.append(f"Total lines: {stats['total_lines']:,}\n")
            content_parts.append(f"Total size: {format_size(stats['total_size'])}\n")
            
            if stats['by_extension']:
                content_parts.append("\nBy extension:\n")
                sorted_exts = sorted(
                    stats['by_extension'].items(),
                    key=lambda x: x[1]['count'],
                    reverse=True
                )
                for ext, ext_stats in sorted_exts:
                    content_parts.append(
                        f"  {ext:15} {ext_stats['count']:4} files  "
                        f"{ext_stats['lines']:6,} lines  "
                        f"{format_size(ext_stats['size']):>10}\n"
                    )
            
            content_parts.append("\n")

        # ディレクトリツリー
        if include_tree and tree_structure:
            content_parts.append("=== Directory Structure ===\n")
            content_parts.append(tree_structure)
            if not tree_structure.endswith('\n'):
                content_parts.append('\n')
            content_parts.append("\n")

        # ファイル一覧
        if include_list and list_structure:
            content_parts.append("=== File List ===\n")
            content_parts.append(list_structure)
            if not list_structure.endswith('\n'):
                content_parts.append('\n')
            content_parts.append("\n")

        # ファイル結合
        if include_merge:
            # content_parts.append("=== Files ===\n\n")
            for file_info in target_files:
                file_path = file_info['path']
                content_parts.append(f"--- {file_path} ---\n")

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

                    content_parts.append(file_content)
                    content_parts.append('\n\n')
                except UnicodeDecodeError:
                    content_parts.append(f"[Error: Cannot decode file {file_path} as text]\n\n")
                    print(f"Warning: Failed to read {file_path} (encoding issue)", file=sys.stderr)
                except PermissionError:
                    content_parts.append(f"[Error: Permission denied reading {file_path}]\n\n")
                    print(f"Warning: Permission denied reading {file_path}", file=sys.stderr)
                except Exception as e:
                    content_parts.append(f"[Error reading {file_path}: {e}]\n\n")
                    print(f"Warning: Failed to read {file_path}: {e}", file=sys.stderr)

        return ''.join(content_parts), all_stats