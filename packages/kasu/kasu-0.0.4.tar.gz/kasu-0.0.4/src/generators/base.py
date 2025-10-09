"""コンテンツジェネレータの基底クラス"""
from abc import ABC, abstractmethod
from typing import List, Dict, Tuple, Optional


class ContentGenerator(ABC):
    """コンテンツ生成の抽象基底クラス"""

    @abstractmethod
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
        list_structure: Optional[str] = None,
    ) -> Tuple[str, Dict[str, int]]:
        """
        ファイルリストからコンテンツを生成

        Args:
            target_files: ファイル情報のリスト
            target_dir: ターゲットディレクトリ
            enable_sanitize: サニタイズを有効にするか
            custom_replacements: カスタム置換パターン
            head_lines: 各ファイルの先頭N行のみ
            tail_lines: 各ファイルの末尾N行のみ
            include_tree: ツリー構造を含めるか
            include_stats: 統計情報を含めるか
            include_merge: ファイル結合を含めるか
            tree_structure: ツリー構造文字列

        Returns:
            (生成されたコンテンツ, サニタイズ統計)
        """
        pass