"""pytest設定ファイル

このファイルは全テストで共有される設定とfixtureを定義します。
"""
import sys
import os
from pathlib import Path

# プロジェクトのルートディレクトリをPythonパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 環境変数の設定（必要に応じて）
os.environ['TESTING'] = '1'


# 共通fixture（必要に応じて追加）
import pytest


@pytest.fixture
def sample_files(tmp_path):
    """テスト用のサンプルファイルを作成するfixture"""
    files = {
        'test.py': 'print("hello")',
        'test.js': 'console.log("world")',
        'test.txt': 'plain text content',
        'README.md': '# Test Project\n\nThis is a test.'
    }
    
    created_files = {}
    for filename, content in files.items():
        file_path = tmp_path / filename
        file_path.write_text(content)
        created_files[filename] = file_path
    
    return created_files


@pytest.fixture
def sample_directory_structure(tmp_path):
    """テスト用のディレクトリ構造を作成するfixture"""
    # ディレクトリ構造
    (tmp_path / "src").mkdir()
    (tmp_path / "tests").mkdir()
    (tmp_path / "docs").mkdir()
    (tmp_path / "build").mkdir()
    
    # ファイル作成
    (tmp_path / "src" / "main.py").write_text("# main")
    (tmp_path / "src" / "utils.py").write_text("# utils")
    (tmp_path / "tests" / "test_main.py").write_text("# test")
    (tmp_path / "docs" / "README.md").write_text("# docs")
    (tmp_path / "build" / "output.txt").write_text("build output")
    (tmp_path / ".gitignore").write_text("build/\n*.pyc\n")
    
    return tmp_path


@pytest.fixture
def config_file(tmp_path):
    """テスト用の設定ファイルを作成するfixture"""
    config = tmp_path / ".config.yaml"
    config.write_text("""
tree: true
sanitize: false
glob:
  - '*.py'
  - '*.js'
""")
    return config