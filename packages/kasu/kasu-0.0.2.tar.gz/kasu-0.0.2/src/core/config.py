"""設定ファイルの読み込みとマージ"""
import os
import sys
import yaml
from typing import Dict, Any, Optional
import argparse


class ConfigLoader:
    """設定ファイルの読み込みを管理"""

    DEFAULT_CONFIG_FILES = [
        '.config.yaml',
        '.config.yml',
        '.config'
    ]

    @classmethod
    def load(cls, config_path: Optional[str] = None) -> Dict[str, Any]:
        """
        設定ファイルを読み込む

        Args:
            config_path: 設定ファイルのパス（Noneの場合は自動検索）

        Returns:
            設定内容の辞書
        """
        config = {}

        if config_path:
            config_files = [config_path]
        else:
            config_files = cls.DEFAULT_CONFIG_FILES

        for config_file in config_files:
            if os.path.exists(config_file):
                try:
                    with open(config_file, 'r', encoding='utf-8') as f:
                        loaded_config = yaml.safe_load(f)
                        if loaded_config:
                            config = loaded_config
                            print(f"Loaded config from: {config_file}")
                            break
                except yaml.YAMLError as e:
                    print(f"Warning: Error parsing config file {config_file}: {e}")
                except Exception as e:
                    print(f"Warning: Error reading config file {config_file}: {e}")

        return config

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
        # Boolean flags
        for key in ['yes', 'tree', 'list', 'sanitize', 'stats', 'debug',  'no_merge']:
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