"""設定ファイルの読み込みとマージ"""
import os
import sys
import yaml
from typing import Dict, Any, Optional
import argparse
import re


class ConfigLoader:
    """設定ファイルの読み込みを管理"""

    @classmethod
    def load(cls, config_path: Optional[str] = None) -> Dict[str, Any]:
        """
        設定ファイルを読み込む

        Args:
            config_path: 設定ファイルのパス

        Returns:
            設定内容の辞書
        """
        config = {}

        if config_path:
            # 明示的に指定されたファイルが存在しない場合はエラー
            if not os.path.exists(config_path):
                print(f"Error: Config file not found: {config_path}", file=sys.stderr)
                sys.exit(1)
            
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    loaded_config = yaml.safe_load(f)
                    if loaded_config:
                        config = loaded_config
                        cls._print_config(config, config_path)
            except yaml.YAMLError as e:
                print(f"Error: Invalid YAML in config file {config_path}: {e}", file=sys.stderr)
                sys.exit(1)
            except Exception as e:
                print(f"Error: Cannot read config file {config_path}: {e}", file=sys.stderr)
                sys.exit(1)

        return config

    @staticmethod
    def _print_config(config: Dict[str, Any], config_path: str, line_length: int = 80) -> None:
        """
        設定内容を整形して表示

        Args:
            config: 設定内容
            config_path: 設定ファイルのパス
            line_length: 区切り線の長さ
        """
        try:
            from colorama import Fore, Style, init
            init(autoreset=True)
            use_color = True
        except ImportError:
            use_color = False

        print("=" * line_length)
        if use_color:
            print(f"{Fore.GREEN}Loaded configuration from: {Fore.CYAN}{config_path}{Style.RESET_ALL}")
        else:
            print(f"Loaded configuration from: {config_path}")
        print("-" * line_length)
        
        yaml_str = yaml.dump(config, default_flow_style=False, allow_unicode=True, sort_keys=False)
        
        for line in yaml_str.splitlines():
            if use_color:
                # キー部分を黄色でハイライト
                line = re.sub(r'^(\s*)(\w+):', rf'\1{Fore.YELLOW}\2{Fore.RESET}:', line)
                # 文字列値を緑でハイライト
                line = re.sub(r': (["\'].*["\'])', rf': {Fore.GREEN}\1{Fore.RESET}', line)
            print(line)
        
        print("=" * line_length)

    @staticmethod
    def merge_with_args(config: Dict[str, Any], args: argparse.Namespace) -> argparse.Namespace:
        """
        設定ファイルとコマンドライン引数をマージ
        コマンドライン引数が優先される

        Args:
            config: 設定ファイルの内容
            args: コマンドライン引数

        Returns:
            マージされた設定
        """
        # Input/Output options (コマンドラインで指定されていない場合のみ設定ファイルから読み込む)
        if getattr(args, 'target_dir', None) is None and 'input' in config:
            args.target_dir = config['input']
        
        if getattr(args, 'output_file', None) is None and 'output' in config:
            args.output_file = config['output']
        
        if getattr(args, 'format', None) == 'text' and 'format' in config:  # デフォルト値の場合
            args.format = config['format']
        
        # Integer options
        if getattr(args, 'head', None) is None and 'head' in config:
            args.head = config['head']
        
        if getattr(args, 'tail', None) is None and 'tail' in config:
            args.tail = config['tail']

        # Boolean flags
        for key in ['yes', 'tree', 'list', 'sanitize', 'stats', 'debug', 'no_merge', 'stdout', 'no_auto_ignore']:
            if not getattr(args, key, False) and config.get(key, False):
                setattr(args, key, True)

        # String/Path options
        for key in ['ignore_file', 'replace_file']:
            if getattr(args, key, None) is None and key in config:
                setattr(args, key, config[key])

        # Glob patterns (special handling)
        if args.glob is None and 'glob' in config:
            glob_patterns = config['glob']
            if isinstance(glob_patterns, str):
                args.glob = [pattern.strip() for pattern in glob_patterns.split(',')]
            elif isinstance(glob_patterns, list):
                if all(isinstance(p, str) for p in glob_patterns):
                    args.glob = glob_patterns
                else:
                    print("Warning: Invalid glob patterns in config file (must be strings)", file=sys.stderr)

        # Exclude patterns (special handling)
        if args.exclude is None and 'exclude' in config:
            exclude_patterns = config['exclude']
            if isinstance(exclude_patterns, str):
                args.exclude = [pattern.strip() for pattern in exclude_patterns.split(',')]
            elif isinstance(exclude_patterns, list):
                if all(isinstance(p, str) for p in exclude_patterns):
                    args.exclude = exclude_patterns
                else:
                    print("Warning: Invalid exclude patterns in config file (must be strings)", file=sys.stderr)

        return args