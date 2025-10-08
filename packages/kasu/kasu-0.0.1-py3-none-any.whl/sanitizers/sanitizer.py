"""コンテンツのサニタイズ機能"""
import re
import os
from typing import List, Tuple, Dict, Optional


class Sanitizer:
    """機密情報をサニタイズするクラス"""

    def __init__(
        self,
        enable_auto_sanitize: bool = False,
        custom_replacements: Optional[List[Tuple[str, str]]] = None
    ):
        self.enable_auto_sanitize = enable_auto_sanitize
        self.custom_replacements = custom_replacements or []

    def sanitize(self, content: str) -> Tuple[str, Dict[str, int]]:
        """
        コンテンツから機密情報を置換

        Args:
            content: 元のコンテンツ

        Returns:
            (置換後のコンテンツ, 置換統計の辞書)
        """
        stats = {}

        # 自動サニタイズ
        if self.enable_auto_sanitize:
            content, stats = self._auto_sanitize(content, stats)

        # カスタム置換
        if self.custom_replacements:
            content, stats = self._custom_sanitize(content, stats)

        return content, stats

    def _auto_sanitize(self, content: str, stats: Dict[str, int]) -> Tuple[str, Dict[str, int]]:
        """自動サニタイズパターンを適用"""

        # IPv4アドレス
        ip_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
        ips = re.findall(ip_pattern, content)
        for i, ip in enumerate(set(ips), 1):
            if not (ip.startswith('127.') or ip.startswith('0.') or 
                    ip.startswith('192.168.') or ip.startswith('10.')):
                content = content.replace(ip, f'[REDACTED_IP_{i}]')
                stats['IP addresses'] = stats.get('IP addresses', 0) + 1

        # メールアドレス
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, content)
        for i, email in enumerate(set(emails), 1):
            content = content.replace(email, f'[REDACTED_EMAIL_{i}]')
            stats['Email addresses'] = stats.get('Email addresses', 0) + 1

        # AWS Access Key
        aws_key_pattern = r'\b(AKIA[0-9A-Z]{16})\b'
        aws_keys = re.findall(aws_key_pattern, content)
        for i, key in enumerate(set(aws_keys), 1):
            content = content.replace(key, f'[REDACTED_AWS_KEY_{i}]')
            stats['AWS Keys'] = stats.get('AWS Keys', 0) + 1

        # API Key
        api_key_pattern = r'(api[_-]?key|apikey|api[_-]?secret)[\s]*[=:]["\']?([a-zA-Z0-9_\-]{20,})["\']?'
        api_keys = re.findall(api_key_pattern, content, re.IGNORECASE)
        for i, (key_type, key_value) in enumerate(set(api_keys), 1):
            content = content.replace(key_value, f'[REDACTED_API_KEY_{i}]')
            stats['API Keys'] = stats.get('API Keys', 0) + 1

        # パスワード
        password_pattern = r'(password|passwd|pwd)[\s]*[=:]["\']?([^\s"\']{6,})["\']?'
        passwords = re.findall(password_pattern, content, re.IGNORECASE)
        for i, (pwd_type, pwd_value) in enumerate(set(passwords), 1):
            content = content.replace(pwd_value, f'[REDACTED_PASSWORD_{i}]')
            stats['Passwords'] = stats.get('Passwords', 0) + 1

        # Private key
        if '-----BEGIN PRIVATE KEY-----' in content or '-----BEGIN RSA PRIVATE KEY-----' in content:
            private_key_pattern = r'-----BEGIN (?:RSA )?PRIVATE KEY-----.*?-----END (?:RSA )?PRIVATE KEY-----'
            content = re.sub(private_key_pattern, '[REDACTED_PRIVATE_KEY]', content, flags=re.DOTALL)
            stats['Private Keys'] = stats.get('Private Keys', 0) + 1

        return content, stats

    def _custom_sanitize(self, content: str, stats: Dict[str, int]) -> Tuple[str, Dict[str, int]]:
        """カスタム置換パターンを適用"""
        for pattern, replacement in self.custom_replacements:
            try:
                matches = re.findall(pattern, content)
                if matches:
                    content = re.sub(pattern, replacement, content)
                    stats[f'Custom: {pattern}'] = len(matches)
            except re.error:
                if pattern in content:
                    count = content.count(pattern)
                    content = content.replace(pattern, replacement)
                    stats[f'Custom: {pattern}'] = count

        return content, stats

    @staticmethod
    def load_replacement_patterns(replace_file_path: str) -> List[Tuple[str, str]]:
        """
        置換パターンファイルから置換ルールを読み込む

        Args:
            replace_file_path: 置換パターンファイルのパス

        Returns:
            (パターン, 置換後文字列) のタプルのリスト
        """
        patterns = []
        if not replace_file_path or not os.path.exists(replace_file_path):
            return patterns

        with open(replace_file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()

                if not line or line.startswith('#'):
                    continue

                # 矢印形式
                if '->' in line:
                    parts = line.split('->', 1)
                    if len(parts) == 2:
                        pattern = parts[0].strip()
                        replacement = parts[1].strip()
                        patterns.append((pattern, replacement))
                        continue

                # スペース/タブ区切り
                parts = line.split(None, 1)
                if len(parts) == 2:
                    pattern = parts[0]
                    replacement = parts[1]
                    patterns.append((pattern, replacement))

        return patterns