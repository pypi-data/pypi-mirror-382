"""メイン処理ロジック"""
import sys
from typing import List, Dict, Optional

from core.file_scanner import FileScanner
from generators.base import ContentGenerator
from utils.statistics import Statistics
from utils.tree import TreeBuilder
from utils.list import ListBuilder


class Merger:
    """ファイルマージの主要ロジックを管理"""

    def __init__(
        self,
        scanner: FileScanner,
        generator: ContentGenerator,
        tree_builder: Optional[TreeBuilder] = None,
        list_builder: Optional[ListBuilder] = None,
    ):
        self.scanner = scanner
        self.generator = generator
        self.tree_builder = tree_builder
        self.list_builder = list_builder

    def merge(
        self,
        target_dir: str,
        output_file: Optional[str] = None,
        to_stdout: bool = False,
        show_tree: bool = False,
        show_list: bool = False,
        show_stats: bool = False,
        skip_confirm: bool = False,
        enable_sanitize: bool = False,
        custom_replacements: Optional[List] = None,
        head_lines: Optional[int] = None,
        tail_lines: Optional[int] = None,
        include_merge: bool = True
    ) -> None:
        """
        ファイルをマージして出力

        Args:
            target_dir: ターゲットディレクトリ
            output_file: 出力ファイル
            to_stdout: 標準出力に出力するか
            show_tree: ツリーを含めるか
            show_stats: 統計を含めるか
            skip_confirm: 確認をスキップするか
            enable_sanitize: サニタイズを有効にするか
            custom_replacements: カスタム置換パターン
            head_lines: 各ファイルの先頭N行のみ
            tail_lines: 各ファイルの末尾N行のみ
            include_merge: ファイル結合を含めるか
        """
        # 表示のみモード判定
        display_only = (show_tree or show_list or show_stats) \
               and not output_file and not to_stdout

        # ファイルスキャン
        if to_stdout:
            print("Scanning files...", file=sys.stderr)
        else:
            print("Scanning files...")

        target_files = self.scanner.scan(target_dir)
        scan_stats = self.scanner.get_stats()

        # スキャン結果を表示
        output_stream = sys.stderr if to_stdout else sys.stdout
        print(f"Found {len(target_files)} files", file=output_stream)

        if scan_stats['glob_filtered'] > 0:
            print(f"Filtered by glob: {scan_stats['glob_filtered']} files", file=output_stream)
        if scan_stats['ignored'] > 0:
            print(f"Ignored by patterns: {scan_stats['ignored']} files/directories", file=output_stream)
        if scan_stats['size_filtered'] > 0:
            print(f"Filtered by size: {scan_stats['size_filtered']} files", file=output_stream)
        if scan_stats['non_text'] > 0:
            print(f"Skipped non-text: {scan_stats['non_text']} files", file=output_stream)

        # ツリー構造を取得（show_tree が True の場合のみ）
        tree_output = None
        if show_tree and self.tree_builder:
            tree_output = self.tree_builder.build(target_dir)

        # リスト構造を取得（show_list が True の場合のみ）
        list_output = None
        if show_list and self.list_builder:
            list_output = self.list_builder.build(target_files)

        # 表示のみモード
        if display_only:
            # ツリー表示
            if show_tree and tree_output:
                if to_stdout:
                    print("\nDirectory tree:", file=sys.stderr)
                    print(tree_output, file=sys.stderr)
                    print("", file=sys.stderr)
                else:
                    print("\nDirectory tree:")
                    print(tree_output)
                    print("")

            # リスト表示
            if show_list and list_output:
                if to_stdout:
                    print("\nFile list:", file=sys.stderr)
                    print(list_output, file=sys.stderr)
                    print("", file=sys.stderr)
                else:
                    print("\nFile list:")
                    print(list_output)
                    print("")

            # 統計表示
            if show_stats:
                stats = Statistics.calculate(target_files)
                Statistics.print_statistics(stats)

            return

        # 確認（stdoutモードまたは表示のみモードではスキップ）
        if not skip_confirm and not to_stdout and output_file:
            response = input(f"Merge into '{output_file}'? (y/n): ")
            if response.lower() not in ['y', 'yes']:
                print("Cancelled")
                return

        # コンテンツ生成と出力
        self._write_output(
            target_files,
            target_dir,
            output_file,
            to_stdout,
            enable_sanitize,
            custom_replacements,
            head_lines,
            tail_lines,
            show_tree,
            show_list,
            show_stats,
            include_merge,
            tree_output,
            list_output
        )

    def _write_output(
        self,
        target_files: List[Dict],
        target_dir: str,
        output_file: Optional[str],
        to_stdout: bool,
        enable_sanitize: bool,
        custom_replacements: Optional[List],
        head_lines: Optional[int],
        tail_lines: Optional[int],
        include_tree: bool,
        include_list: bool,
        include_stats: bool,
        include_merge: bool,
        tree_structure: Optional[str],
        list_structure: Optional[str],
    ) -> None:
        """出力を書き込む"""
        if to_stdout:
            print("Merging...", file=sys.stderr)
        else:
            print("Merging...")

        content, sanitize_stats = self.generator.generate(
            target_files,
            target_dir,
            enable_sanitize,
            custom_replacements,
            head_lines,
            tail_lines,
            include_tree,
            include_list,
            include_stats,
            include_merge,
            tree_structure,
            list_structure,
        )

        if to_stdout:
            print(content)
            print(f"Done! {len(target_files)} files merged", file=sys.stderr)
            if sanitize_stats:
                print("\nSanitization stats:", file=sys.stderr)
                for key, count in sanitize_stats.items():
                    print(f"  {key}: {count}", file=sys.stderr)
        else:
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"\nDone! {len(target_files)} files merged into '{output_file}'")
                if sanitize_stats:
                    print("\nSanitization stats:")
                    for key, count in sanitize_stats.items():
                        print(f"  {key}: {count}")
            except PermissionError:
                print(f"\nError: Permission denied writing to '{output_file}'", file=sys.stderr)
                print("Check that you have write permissions for this location.", file=sys.stderr)
                sys.exit(1)
            except OSError as e:
                print(f"\nError: Cannot write to '{output_file}': {e}", file=sys.stderr)
                sys.exit(1)