"""ファイル拡張子から言語を判定"""
import os
from typing import Dict


class LanguageMapper:
    """拡張子からMarkdown用の言語名を取得"""

    # 拡張子と言語のマッピング
    LANGUAGE_MAP: Dict[str, str] = {
        # Python
        '.py': 'python',
        '.pyi': 'python',
        '.pyw': 'python',

        # JavaScript/TypeScript
        '.js': 'javascript',
        '.jsx': 'jsx',
        '.ts': 'typescript',
        '.tsx': 'tsx',
        '.mjs': 'javascript',
        '.cjs': 'javascript',

        # Web
        '.html': 'html',
        '.htm': 'html',
        '.css': 'css',
        '.scss': 'scss',
        '.sass': 'sass',
        '.less': 'less',

        # Markup/Config
        '.json': 'json',
        '.xml': 'xml',
        '.yaml': 'yaml',
        '.yml': 'yaml',
        '.toml': 'toml',
        '.ini': 'ini',
        '.cfg': 'ini',
        '.conf': 'conf',

        # Shell
        '.sh': 'bash',
        '.bash': 'bash',
        '.zsh': 'zsh',
        '.fish': 'fish',

        # C/C++
        '.c': 'c',
        '.h': 'c',
        '.cpp': 'cpp',
        '.cc': 'cpp',
        '.cxx': 'cpp',
        '.hpp': 'cpp',
        '.hxx': 'cpp',

        # C#
        '.cs': 'csharp',

        # Java/Kotlin/Scala
        '.java': 'java',
        '.kt': 'kotlin',
        '.kts': 'kotlin',
        '.scala': 'scala',

        # Go
        '.go': 'go',

        # Rust
        '.rs': 'rust',

        # Ruby
        '.rb': 'ruby',
        '.rake': 'ruby',

        # PHP
        '.php': 'php',

        # Swift
        '.swift': 'swift',

        # R
        '.r': 'r',
        '.R': 'r',

        # Markdown
        '.md': 'markdown',
        '.markdown': 'markdown',

        # SQL
        '.sql': 'sql',

        # その他
        '.txt': 'text',
        '.log': 'text',
        '.csv': 'csv',
        '.graphql': 'graphql',
        '.proto': 'protobuf',
    }

    # 特殊なファイル名（拡張子なし）
    SPECIAL_FILES: Dict[str, str] = {
        'dockerfile': 'dockerfile',
        'makefile': 'makefile',
        'rakefile': 'ruby',
        'gemfile': 'ruby',
        'vagrantfile': 'ruby',
        '.bashrc': 'bash',
        '.zshrc': 'zsh',
        '.vimrc': 'vim',
        '.gitignore': 'text',
        '.dockerignore': 'text',
        '.npmrc': 'text',
        '.editorconfig': 'ini',
    }

    @classmethod
    def get_language(cls, file_path: str) -> str:
        """
        ファイルパスから言語を判定

        Args:
            file_path: ファイルパス

        Returns:
            Markdown用の言語名
        """
        basename = os.path.basename(file_path).lower()

        # 特殊なファイル名をチェック
        if basename in cls.SPECIAL_FILES:
            return cls.SPECIAL_FILES[basename]

        # 拡張子で判定
        ext = os.path.splitext(file_path)[1].lower()
        if ext in cls.LANGUAGE_MAP:
            return cls.LANGUAGE_MAP[ext]

        # 不明な場合は拡張子をそのまま使用（ドットを除く）
        return ext[1:] if ext else 'text'