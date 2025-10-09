import argparse
import sys
import os

from core.config import ConfigLoader
from core.file_scanner import FileScanner
from core.merger import Merger
from generators.text import TextGenerator
from generators.markdown import MarkdownGenerator
from filters.ignore import IgnoreFilter
from filters.glob import GlobFilter
from sanitizers.sanitizer import Sanitizer
from utils.tree import TreeBuilder
from utils.list import ListBuilder


def main():
    parser = argparse.ArgumentParser(
        description="Merge all text files in a directory into one output.",
        epilog="Examples:\n"
               "  ks -i . -o output.txt                       # Basic merge\n"
               "  ks -i . -o output.md -f md                  # Markdown format\n"
               "  ks -i . -o output.txt -t                    # With tree\n"
               "  ks -i . -o output.txt --head 100            # First 100 lines per file\n"
               "  ks -i . -o output.txt --tail 50             # Last 50 lines per file\n"
               "  ks -i . -t                                  # Display tree only\n"
               "  ks -i . -o output.txt -t --no-merge         # Tree only (no files)\n"
               "  ks -i . -o output.txt -g '*.py' '*.js'      # Python and JS only\n"
               "  ks -i . -o output.txt -g 'src/**/*.py'      # Recursive pattern\n"
               "  ks -i . -o output.txt -x 'README.md'        # Exclude specific files\n"
               "  ks -i . -o output.txt -g '*.py' -x 'test_*' # Combine glob and exclude\n"
               "  ks -i project/ -o out.txt -s                # Auto-sanitize sensitive info\n"
               "  ks --config config.yaml                     # Use config file\n"
               "  ks -c config.yaml -o custom.txt             # Config + override\n",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    # 入出力オプション
    io_group = parser.add_argument_group('Input/Output')
    io_group.add_argument(
        "--input", "-i",
        dest="target_dir",
        metavar="DIR",
        help="Directory to search for text files"
    )
    io_group.add_argument(
        "--output", "-o",
        dest="output_file",
        metavar="FILE",
        help="Output file path"
    )
    io_group.add_argument(
        "--stdout",
        action="store_true",
        help="Output to stdout instead of file"
    )
    io_group.add_argument(
        "--format", "-f",
        choices=['text', 'markdown', 'md'],
        default='text',
        help="Output format (default: text)"
    )

    # 情報追加オプション
    include_group = parser.add_argument_group('Information inclusion options')
    include_group.add_argument(
        "--tree", "-t",
        action="store_true",
        help="Include directory tree structure"
    )
    include_group.add_argument(
        "--list", "-l",
        action="store_true",
        help="Include file list"
    )

    include_group.add_argument(
        "--stats",
        action="store_true",
        help="Include file statistics"
    )


    # 除外オプション
    exclude_group = parser.add_argument_group('Exclusion options')
    exclude_group.add_argument(
        "--no-merge",
        action="store_true",
        dest="no_merge",
        help="Exclude file contents (only output metadata)"
    )

    # フィルタリングオプション
    filter_group = parser.add_argument_group('Filtering options')
    filter_group.add_argument(
        "--glob", "-g",
        nargs='+',
        metavar="PATTERN",
        help="File patterns to match (e.g., '*.py' 'src/**/*.js'). Supports glob wildcards."
    )
    filter_group.add_argument(
        "--ignore",
        metavar="FILE",
        dest="ignore_file",
        help="Ignore patterns file (default: auto-detect .gitignore)"
    )
    filter_group.add_argument(
        "--exclude", "-x",
        nargs='+',
        metavar="PATTERN",
        help="Exclude patterns (e.g., 'README.md' '*.log' 'temp/*')"
    )
    filter_group.add_argument(
        "--head",
        type=int,
        metavar="N",
        help="Limit each file to first N lines"
    )
    filter_group.add_argument(
        "--tail",
        type=int,
        metavar="N",
        help="Limit each file to last N lines"
    )
    filter_group.add_argument(
        "--no-auto-ignore",
        action="store_true",
        help="Disable automatic .gitignore detection"
    )

    # サニタイズオプション
    sanitize_group = parser.add_argument_group('Sanitization options')
    sanitize_group.add_argument(
        "--sanitize", "-s",
        action="store_true",
        help="Auto-sanitize sensitive information"
    )
    sanitize_group.add_argument(
        "--replace", "-r",
        dest="replace_file",
        metavar="FILE",
        help="Custom replacement patterns file"
    )

    # 実行制御オプション
    control_group = parser.add_argument_group('Execution control')
    control_group.add_argument(
        "--yes", "-y",
        action="store_true",
        help="Skip confirmation prompt"
    )
    control_group.add_argument(
        "--debug", "-d",
        action="store_true",
        help="Show debug information"
    )

    # その他
    parser.add_argument(
        "--config", "-c",
        metavar="FILE",
        dest="config_file",
        help="Configuration file path (YAML format)"
    )

    args = parser.parse_args()

    # 設定ファイルを読み込み
    config = ConfigLoader.load(args.config_file)
    args = ConfigLoader.merge_with_args(config, args)

    # target_dirのチェック（設定ファイルマージ後に実施）
    if not args.target_dir:
        parser.error("--input/-i is required (either via command line or config file)")

    # 表示のみモード（tree, stats, list のいずれか）
    display_only_mode = (args.tree or args.stats or args.list) \
                        and not args.output_file and not args.stdout

    # output_fileチェック
    if not args.stdout and not display_only_mode and not args.output_file:
        parser.error("--output/-o is required unless using --stdout, --tree, or --stats")
    
    # 出力ファイルパスが空文字列でないかチェック
    if args.output_file is not None and args.output_file.strip() == "":
        parser.error("Output file path cannot be empty")
    
    # --head と --tail の排他チェック
    if args.head and args.tail:
        parser.error("Cannot use both --head and --tail at the same time")

    # target_dirが存在するかチェック
    if not os.path.exists(args.target_dir):
        parser.error(f"Input directory does not exist: {args.target_dir}")

    if not os.path.isdir(args.target_dir):
        parser.error(f"Input path is not a directory: {args.target_dir}")

    # フォーマットの正規化
    if args.format == 'md':
        args.format = 'markdown'

    # Ignoreファイルの決定
    ignore_files = []
    exclude_patterns = []
    auto_vcs_ignore = False

    if args.ignore_file:
        if not os.path.exists(args.ignore_file):
            print(f"Warning: Ignore file not found: {args.ignore_file}", file=sys.stderr)
        else:
            ignore_files.append(args.ignore_file)
            if args.debug:
                print(f"[DEBUG] Using specified ignore file: {args.ignore_file}", file=sys.stderr)

    if not args.no_auto_ignore and not args.ignore_file:
        auto_ignore = IgnoreFilter.auto_detect_ignore_file(args.target_dir)
        if auto_ignore:
            ignore_files.append(auto_ignore)
            auto_vcs_ignore = True
            print(f"Auto-detected and using: {auto_ignore}")

    if args.exclude:
        exclude_patterns = args.exclude
        if args.debug:
            print(f"[DEBUG] Exclude patterns: {exclude_patterns}", file=sys.stderr)

    # フィルタの構築
    filters = []
    ignore_filter = None
    glob_filter = None

    glob_filter = GlobFilter(args.glob, args.target_dir, args.debug)
    filters.append(glob_filter)

    ignore_patterns = []
    if ignore_files:
        ignore_patterns = IgnoreFilter.load_patterns_from_multiple(ignore_files)
    if exclude_patterns:
        ignore_patterns.extend(exclude_patterns)
    
    if ignore_patterns:
        ignore_filter = IgnoreFilter(ignore_patterns, args.target_dir, args.debug, auto_vcs_ignore)
        filters.append(ignore_filter)
    else:
        ignore_filter = IgnoreFilter([], args.target_dir, args.debug, auto_vcs_ignore)
        filters.append(ignore_filter)

    scanner = FileScanner(filters, args.debug)

    # ツリービルダー（tree オプションが指定されている場合のみ）
    tree_builder = None
    if args.tree:
        tree_builder = TreeBuilder(ignore_filter, glob_filter)

    # リストビルダー（list オプションが指定されている場合のみ）
    list_builder = None
    if args.list:
        list_builder = ListBuilder(args.target_dir)

    # ジェネレータ選択
    if args.format == 'markdown':
        generator = MarkdownGenerator()
    else:
        generator = TextGenerator()

    custom_replacements = None
    if args.replace_file:
        if not os.path.exists(args.replace_file):
            print(f"Warning: Replacement patterns file not found: {args.replace_file}", file=sys.stderr)
        else:
            custom_replacements = Sanitizer.load_replacement_patterns(args.replace_file)

    merger = Merger(scanner, generator, tree_builder, list_builder)
    merger.merge(
        args.target_dir,
        args.output_file,
        args.stdout,
        args.tree,
        args.list,
        args.stats,
        args.yes,
        args.sanitize,
        custom_replacements,
        args.head,
        args.tail,
        not args.no_merge
    )


if __name__ == "__main__":
    main()