"""フィルタの基底クラス"""
from abc import ABC, abstractmethod


class FileFilter(ABC):
    """ファイルフィルタの抽象基底クラス"""

    @abstractmethod
    def should_include(self, file_path: str, **kwargs) -> bool:
        """
        ファイルを含めるべきかどうか判定

        Args:
            file_path: ファイルパス
            **kwargs: 追加の引数

        Returns:
            含める場合True
        """
        pass