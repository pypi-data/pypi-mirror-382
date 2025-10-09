# KASU

AI駆動開発におけるコードベースの抽象化と管理の支援ツール

## 主な機能

- **複数ファイルの統合** - ディレクトリ内のテキストファイルを1ファイルに結合
- **パス付きヘッダー** - 各ファイルの内容をパス付きで区切り
- **出力形式** - プレーンテキストまたはMarkdown形式
- **フィルタリング** - Globパターン、除外パターン、.gitignore対応
- **ディレクトリツリー表示** - プロジェクト構造の可視化
- **ファイル一覧表示** - 対象ファイルのリストアップ
- **部分的な内容抽出** - 各ファイルの先頭/末尾N行のみ抽出
- **機密情報のサニタイズ** - IPアドレス、メール、APIキーなどの自動置換
- **設定ファイル対応** - コマンドラインオプションをYAMLで指定可能

## インストール

- pypiからインストール
    ```bash
    pip install kasu
    ```

- ソースからインストール
    ```bash
    git clone git@github.com:remokasu/kasu.git
    cd kasu
    pip install -e .
    ```

## クイックスタート

### 基本的な使い方（カレントディレクトリを結合）
``` bash
ks -i . -o output.txt
```
### Markdown形式で出力
``` bash
ks -i . -o output.md --format md
```
### Pythonファイルだけを対象に
``` bash
ks -i . -o output.md -g "*.py" --format md
```

## 使い方

### 指定したディレクトリ以下のテキストファイルを結合して1ファイルに出力

- プレーンテキストで出力

    ```bash
    ks -i [DIR] -o [FILE]
    ``` 

- Markdown形式で出力

    ```bash
    ks -i [DIR] -o [FILE.md] --format md
    ```

    または

    ```bash
    ks -i [DIR] -o [FILE.md] -f md
    ```

- 標準出力に出力

    ```bash
    ks -i [DIR] --stdout
    ```

### tree 情報を出力

- 標準出力に出力
    ```bash
    ks -i [DIR] --tree
    ```
    または
    ```bash
    ks -i [DIR] -t
    ```

- `-o` で指定したファイルの先頭に出力
    ```bash
    ks -i [DIR] -o [FILE] --tree
    ```
    または
    ```bash
    ks -i [DIR] -o [FILE] -t
    ```
    - i で指定したディレクトリ以下のファイル内容が続きます。

- `-o` で指定したファイルにtree情報のみを出力
    ```bash
    ks -i [DIR] -o [FILE] --tree --no-merge
    ```
    `--no-merge`を指定することで、-iで指定したディレクトリ以下のファイル内容は出力されません。

- 出力例

    ```
    Auto-detected and using: ./.gitignore
    Scanning files...
    Found 5 files
    Ignored by patterns: 2 files/directories

    Directory tree:
    example-project/
    ├── docs/
    │   └── README.md
    ├── src/
    │   ├── config.json
    │   ├── main.py
    │   └── utils.py
    └── tests/
        └── test_main.py
    ```

### ファイル一覧を標準出力に出力

- 標準出力に出力

    ```bash
    ks -i [DIR] --list
    ```
    または
    ```bash
    ks -i [DIR] -l
    ```
- `-o`で指定したファイルの先頭に出力
    ```bash
    ks -i [DIR] -o [FILE] --list
    ```
    または
    ```bash
    ks -i [DIR] -o [FILE] -l
    ```
    `-i` で指定したディレクトリ以下のファイル内容が続きます。

- `-o` で指定したファイルにファイル一覧のみを出力
    ```bash
    ks -i [DIR] -o [FILE] --list --no-merge
    ```
    `--no-merge`を指定することで、`-i`で指定したディレクトリ以下のファイル内容は出力されません。

- 出力例
    ```
    Auto-detected and using: ./.gitignore
    Scanning files...
    Found 5 files
    Ignored by patterns: 2 files/directories

    File list:
    tests/test_main.py
    src/utils.py
    src/config.json
    src/main.py
    docs/README.md
    ```

### 条件を指定して対象ファイルを絞り込み

- `-g`で含めるファイルパターンを指定します。

    例: `-g "*.py"` で拡張子が.pyのファイルのみ対象にします。

    ```bash
    ks -i [DIR] -o [FILE] -g "*.py"
    ```

    複数指定
    ```bash
    ks -i [DIR] -o [FILE] -g "*.py" "*.md"
    ```

### 対象から特定のファイルを除外
- `-i`で指定したディレクトリ以下に.gitignoreがあれば自動的に除外します。

- `--ignore`で、除去対象を記載したファイルを指定できます。

    このファイルは.gitignoreと同じ書き方ができます。

    `--ignore` を指定した時は`.gitignore` は無視されます。

- `--no-auto-ignore`で.gitignoreの自動検出を無効化できます。

- `-x`で指定したパターンを除外します。

    もし対象に.gitignoreがあり、かつREADME.mdを除外したい場合、以下のようにします。
    ```bash
    ks -i [DIR] -o [FILE] -x "README.md"
    ```

### サニタイズ

- コンフィデンシャルな情報を自動的に検出して置換します。

- ただし、確実に検出できるわけではありません。

- `--sanitize`を指定します。

    ```bash
    ks -i [DIR] -o [FILE] --sanitize
    ```
    または
    ```bash
    ks -i [DIR] -o [FILE] -s
    ```


- 検出するパターン
    1. APIキー: api_key=, apikey=, api-secret= などの後に続く20文字以上の英数字を検出
        ```
        置換形式: [REDACTED_API_KEY_1], [REDACTED_API_KEY_2], ...
        ```

    2. パスワード: password=, passwd=, pwd= などの後に続く6文字以上の値を検出
        ```
        置換形式: [REDACTED_PASSWORD_1], [REDACTED_PASSWORD_2], ...
        ```

    3. AWSキー - AKIA で始まる16文字の英数字を検出
        ```
        置換形式: [REDACTED_AWS_KEY_1], [REDACTED_AWS_KEY_2], ...
        ```

    4. メールアドレス - 標準的なメール形式を検出
        ```
        置換形式: [REDACTED_EMAIL_1], [REDACTED_EMAIL_2], ...
        ```

    5. IPアドレス - パブリックIPのみ検出（ローカルIP 127., 192.168., 10. は除外）
        ```
        置換形式: [REDACTED_IP_1], [REDACTED_IP_2], ...
        ```

    6. 秘密鍵 - PEM形式の秘密鍵全体を検出
        ```
        置換形式: [REDACTED_PRIVATE_KEY]
        ```

### 置換パターンを指定
    
パターンファイルを指定して、カスタム置換を行うことができます。

- パターンファイルフォーマット
    - pattern_file.txt(名前は任意)
        ```
        tanaka.ichiro@group.go.jp hoge@hoge.com
        田中一郎 ほげ山ほげ男
        Company Inc. ほげほげ会社
        ```

    - 左側が置換対象、右側が置換後の文字列です。上記の例では以下の置換が行われます。
        - tanaka.ichiro@group.go.jp → hoge@hoge.com
        - 田中一郎 → ほげ山ほげ男
        - Company Inc. → ほげほげ会社

- 指定方法
    ```bash
    ks -i [DIR] -o [FILE] --replace [PATTERN_FILE]
    ```
    または
    ```bash
    ks -i [DIR] -o [FILE] -r [PATTERN_FILE]
    ```

### 各ファイルの先頭/末尾N行のみ出力

- 先頭N行
    ```bash
    ks -i [DIR] -o [FILE] --head N
    ```
- 末尾N行
    ```bash
    ks -i [DIR] -o [FILE] --tail N
    ```

### 設定ファイルを指定

- `--config [FILE]`, または `-c [FILE]`で設定ファイルを指定できます。

    ``` bash
    ks --config config.yaml
    ```

- config.yaml
    ```yaml
    input: .
    output: output.md
    format: md
    glob:
    - "*.py"
    - "*.md"
    exclude:
    - "tests/"
    - "docs/"
    head: 50
    sanitize: true
    ```


## コマンドラインオプション一覧

| オプション | 短縮形 | 説明 |
|-----------|--------|------|
| `--input DIR` | `-i` | 入力ディレクトリ（デフォルト: `.`） |
| `--output FILE` | `-o` | 出力ファイルパス |
| `--stdout` | - | 標準出力に出力 |
| `--format FORMAT` | `-f` | 出力形式（`text`/`markdown`/`md`） |
| `--glob PATTERN` | `-g` | 含めるファイルパターン |
| `--exclude PATTERN` | `-x` | 除外パターン |
| `--ignore FILE` | - | ignoreファイルを指定 |
| `--no-auto-ignore` | - | .gitignore自動検出を無効化 |
| `--head N` | - | 各ファイルの先頭N行のみ |
| `--tail N` | - | 各ファイルの末尾N行のみ |
| `--tree` | `-t` | ディレクトリツリーを表示 |
| `--stats` | - | 統計情報を表示 |
| `--sanitize` | `-s` | 機密情報を自動サニタイズ |
| `--replace FILE` | `-r` | カスタム置換パターンファイル |
| `--yes` | `-y` | 確認プロンプトをスキップ |
| `--debug` | `-d` | デバッグ情報を表示 |
| `--config FILE` | `-c` | 設定ファイルを指定 |
