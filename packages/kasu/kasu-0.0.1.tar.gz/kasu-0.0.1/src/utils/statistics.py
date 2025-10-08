import os
from typing import List, Dict

from utils.format_utils import format_size

class Statistics:
    """ファイル統計情報を管理"""

    @staticmethod
    def calculate(target_files: List[Dict[str, any]]) -> Dict[str, any]:
        """
        ファイルリストから統計情報を計算

        Args:
            target_files: ファイル情報のリスト

        Returns:
            統計情報の辞書
        """
        stats = {
            'total_files': len(target_files),
            'total_size': sum(f['size'] for f in target_files),
            'total_lines': sum(f['lines'] for f in target_files),
            'by_extension': {},
        }

        for file_info in target_files:
            ext = os.path.splitext(file_info['path'])[1] or '(no extension)'
            if ext not in stats['by_extension']:
                stats['by_extension'][ext] = {
                    'count': 0,
                    'size': 0,
                    'lines': 0,
                }

            stats['by_extension'][ext]['count'] += 1
            stats['by_extension'][ext]['size'] += file_info['size']
            stats['by_extension'][ext]['lines'] += file_info['lines']

        return stats

    @staticmethod
    def print_statistics(stats: Dict[str, any]) -> None:
        """統計情報を表示"""
        print("\n" + "=" * 50)
        print("Statistics")
        print("=" * 50)
        print(f"Total files:  {stats['total_files']:,}")
        print(f"Total lines:  {stats['total_lines']:,}")
        print(f"Total size:   {format_size(stats['total_size'])}")

        if stats['by_extension']:
            print("\nBy extension:")
            sorted_exts = sorted(
                stats['by_extension'].items(),
                key=lambda x: x[1]['count'],
                reverse=True
            )

            for ext, ext_stats in sorted_exts:
                print(f"  {ext:15} {ext_stats['count']:4} files  "
                      f"{ext_stats['lines']:6,} lines  "
                      f"{format_size(ext_stats['size']):>10}")
        print("=" * 50 + "\n")
