"""フォーマットユーティリティ"""
import re


def parse_size(size_str: str) -> int:
    """
    サイズ文字列をバイト数に変換

    Args:
        size_str: サイズ文字列 (例: "1M", "500K", "1.5G")

    Returns:
        バイト数

    Raises:
        ValueError: 不正な形式の場合
    """
    size_str = size_str.upper().strip()

    units = {
        'B': 1,
        'K': 1024,
        'KB': 1024,
        'M': 1024 * 1024,
        'MB': 1024 * 1024,
        'G': 1024 * 1024 * 1024,
        'GB': 1024 * 1024 * 1024,
    }

    match = re.match(r'^([\d.]+)\s*([KMGB]+)$', size_str)
    if not match:
        raise ValueError(f"Invalid size format: {size_str}. Use format like '1M', '500K', '1.5G'")

    number = float(match.group(1))
    unit = match.group(2)

    if unit not in units:
        raise ValueError(f"Unknown unit: {unit}. Use B, K, M, or G")

    return int(number * units[unit])


def format_size(size_bytes: int) -> str:
    """
    バイト数を人間が読みやすい形式に変換

    Args:
        size_bytes: バイト数

    Returns:
        フォーマットされたサイズ文字列
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"