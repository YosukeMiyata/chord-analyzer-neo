# 要件ドキュメント

## はじめに

chord-analysis-toolは、音声ファイルからコード進行を自動推定し、演奏者の練習とアドリブをサポートするローカル完結型のデスクトップアプリケーションです。本ドキュメントは、設計ドキュメントに基づいて導出された機能要件を定義します。

## 用語集

- **System**: chord-analysis-toolアプリケーション全体
- **AudioEngine**: 音声処理エンジン（AudioProcessingEngine）
- **ChordEstimator**: コード推定モジュール（ChordEstimationModule）
- **LyricsEngine**: 歌詞書き起こしモジュール（LyricsTranscriptionModule）
- **ChordSegment**: タイムスタンプ付きコード情報（開始時刻、終了時刻、ルート音、コード品質、ベース音、拡張音、信頼度）
- **LyricSegment**: タイムスタンプ付き歌詞情報（開始時刻、終了時刻、テキスト、信頼度）
- **AudioAnalysisResult**: 音声解析結果（コード進行、歌詞、テンポ、キー、拍子）
- **Cache**: 解析結果のローカルストレージキャッシュ

## 要件

### 要件1: 音声ファイルの読み込みと検証

**ユーザーストーリー**: 演奏者として、音声ファイルを読み込んで解析できるようにしたい。そうすることで、楽曲のコード進行を学習できる。

#### 受入基準

1. WHEN ユーザーが有効な音声ファイルパスを指定した場合、THE AudioEngine SHALL ファイルを読み込み成功を返す
2. WHEN ユーザーが無効な音声ファイルパスを指定した場合、THE AudioEngine SHALL エラーを返し、システム状態を変更しない
3. WHEN ユーザーがサポートされていない音声フォーマットを指定した場合、THE AudioEngine SHALL エラーを返す
4. THE AudioEngine SHALL 音声ファイルの基本情報（サンプルレート、長さ、チャンネル数）を取得する

### 要件2: コード進行の推定

**ユーザーストーリー**: 演奏者として、音声ファイルからコード進行を自動推定したい。そうすることで、耳コピの時間を短縮できる。

#### 受入基準

1. WHEN 音声データが提供された場合、THE ChordEstimator SHALL コード進行のリストを返す
2. WHEN ボーカル分離が有効な場合、THE ChordEstimator SHALL ボーカルを除去してから解析を実行する
3. THE ChordEstimator SHALL 各コードセグメントに開始時刻と終了時刻を含める
4. THE ChordEstimator SHALL 各コードセグメントにルート音とコード品質を含める
5. THE ChordEstimator SHALL 各コードセグメントに信頼度スコアを含める
6. WHERE 分数コードが検出された場合、THE ChordEstimator SHALL ベース音情報を含める
7. WHERE 拡張音（9th、11th、13th）が検出された場合、THE ChordEstimator SHALL 拡張音情報を含める

### 要件3: ボーカル分離処理

**ユーザーストーリー**: 演奏者として、ボーカルを除去した伴奏のみからコードを推定したい。そうすることで、より正確なコード推定が可能になる。

#### 受入基準

1. WHEN 音声データが提供された場合、THE ChordEstimator SHALL ボーカルを除去した音声データを返す
2. THE ChordEstimator SHALL 元の音声データのサンプルレートを保持する
3. WHEN ボーカル分離が失敗した場合、THE ChordEstimator SHALL エラーを返す

### 要件4: クロマ特徴量の抽出

**ユーザーストーリー**: システム開発者として、音声からクロマ特徴量を抽出したい。そうすることで、コード推定の精度を向上できる。

#### 受入基準

1. WHEN 音声データが提供された場合、THE ChordEstimator SHALL クロマ特徴量を抽出する
2. THE ChordEstimator SHALL 12次元のクロマベクトルを時系列で返す
3. WHEN 無音区間が検出された場合、THE ChordEstimator SHALL ゼロベクトルを返す

### 要件5: 歌詞の自動書き起こし

**ユーザーストーリー**: 演奏者として、音声から歌詞を自動的に書き起こしたい。そうすることで、歌詞とコードの対応関係を把握できる。

#### 受入基準

1. WHEN 音声データが提供された場合、THE LyricsEngine SHALL タイムスタンプ付き歌詞セグメントのリストを返す
2. THE LyricsEngine SHALL 各歌詞セグメントに開始時刻と終了時刻を含める
3. THE LyricsEngine SHALL 各歌詞セグメントにテキストと信頼度スコアを含める
4. WHERE 言語が指定された場合、THE LyricsEngine SHALL 指定された言語で書き起こしを実行する
5. WHEN 音声に歌詞が含まれない場合、THE LyricsEngine SHALL 空のリストを返す

### 要件6: 歌詞とコードの同期

**ユーザーストーリー**: 演奏者として、歌詞とコードを時間軸で同期して表示したい。そうすることで、どの歌詞でどのコードが鳴っているかを把握できる。

#### 受入基準

1. WHEN 歌詞セグメントとコードセグメントが提供された場合、THE LyricsEngine SHALL 同期されたペアのリストを返す
2. THE LyricsEngine SHALL 各歌詞セグメントに対応するコードセグメントを時間範囲の重なりに基づいて関連付ける
3. WHEN 歌詞セグメントに対応するコードが存在しない場合、THE LyricsEngine SHALL 空のコードリストを関連付ける

### 要件7: 音声再生制御

**ユーザーストーリー**: 演奏者として、音声を再生・一時停止・停止できるようにしたい。そうすることで、特定の箇所を繰り返し練習できる。

#### 受入基準

1. WHEN ユーザーが再生を開始した場合、THE AudioEngine SHALL 音声再生を開始する
2. WHEN ユーザーが一時停止した場合、THE AudioEngine SHALL 現在位置で再生を一時停止する
3. WHEN ユーザーが停止した場合、THE AudioEngine SHALL 再生を停止し、位置を先頭にリセットする
4. WHEN ユーザーがシーク位置を指定した場合、THE AudioEngine SHALL 指定された位置に再生位置を変更する
5. WHEN ユーザーが音量を設定した場合、THE AudioEngine SHALL 音量を0.0から1.0の範囲で設定する
6. THE AudioEngine SHALL 現在の再生位置を秒単位で返す

### 要件8: 音声解析結果のキャッシュ

**ユーザーストーリー**: 演奏者として、一度解析した楽曲を再度開いたときに即座に結果を表示したい。そうすることで、待ち時間なく練習を開始できる。

#### 受入基準

1. WHEN 音声ファイルが解析された場合、THE AudioEngine SHALL 解析結果をローカルストレージに保存する
2. WHEN 音声ファイルが読み込まれた場合、THE AudioEngine SHALL キャッシュの存在を確認する
3. WHEN 有効なキャッシュが存在する場合、THE AudioEngine SHALL キャッシュから解析結果を読み込む
4. WHEN キャッシュが存在しない場合、THE AudioEngine SHALL 新規解析を実行する
5. WHERE キャッシュ使用が無効化された場合、THE AudioEngine SHALL 常に新規解析を実行する

### 要件9: 完全な音声解析の実行

**ユーザーストーリー**: 演奏者として、コード、歌詞、テンポ、キーを一度に解析したい。そうすることで、楽曲の全体像を把握できる。

#### 受入基準

1. WHEN 音声解析が要求された場合、THE AudioEngine SHALL AudioAnalysisResultを返す
2. THE AudioEngine SHALL コード進行のリストを含める
3. THE AudioEngine SHALL 歌詞セグメントのリストを含める
4. THE AudioEngine SHALL テンポ（BPM）を含める
5. THE AudioEngine SHALL キー（調）を含める
6. THE AudioEngine SHALL 拍子（time signature）を含める

### 要件10: コード品質の分類

**ユーザーストーリー**: 演奏者として、メジャー、マイナー、セブンスなど様々なコード品質を識別したい。そうすることで、正確なコード進行を学習できる。

#### 受入基準

1. THE ChordEstimator SHALL メジャーコード（maj）を識別する
2. THE ChordEstimator SHALL マイナーコード（min）を識別する
3. THE ChordEstimator SHALL ドミナントセブンスコード（7）を識別する
4. THE ChordEstimator SHALL メジャーセブンスコード（maj7）を識別する
5. THE ChordEstimator SHALL マイナーセブンスコード（min7）を識別する
6. THE ChordEstimator SHALL ディミニッシュコード（dim）を識別する
7. THE ChordEstimator SHALL オーギュメントコード（aug）を識別する
8. THE ChordEstimator SHALL サスフォーコード（sus4）を識別する
9. THE ChordEstimator SHALL サスツーコード（sus2）を識別する
10. THE ChordEstimator SHALL ナインスコード（9）を識別する
11. THE ChordEstimator SHALL イレブンスコード（11）を識別する
12. THE ChordEstimator SHALL サーティーンスコード（13）を識別する

### 要件11: ユーザーによるコード修正

**ユーザーストーリー**: 演奏者として、自動推定されたコードが間違っている場合に手動で修正したい。そうすることで、正確なコード進行で練習できる。

#### 受入基準

1. WHEN ユーザーがコードセグメントを選択した場合、THE System SHALL コード編集UIを表示する
2. WHEN ユーザーがコードを修正した場合、THE System SHALL 修正内容を保存する
3. THE System SHALL 修正履歴をローカルストレージに永続化する
4. WHEN 同じ音声ファイルを再度開いた場合、THE System SHALL 保存された修正を自動的に適用する
5. THE System SHALL 修正データに音声ファイルハッシュ、セグメント位置、元のコード、修正後のコードを含める

### 要件12: コード修正データの管理

**ユーザーストーリー**: システム開発者として、ユーザーの修正データを分析したい。そうすることで、モデルの弱点を特定し、精度を改善できる。

#### 受入基準

1. THE System SHALL 全ての修正データを構造化形式で保存する
2. THE System SHALL 修正統計情報を提供する（最も修正されるコード品質、修正率など）
3. THE System SHALL 修正データをモデル再学習用にエクスポートできる
4. THE System SHALL 修正データに信頼度スコアの変化を記録する

### 要件13: 複数モデルの管理と切り替え

**ユーザーストーリー**: 演奏者として、楽曲のジャンルや用途に応じてコード推定モデルを切り替えたい。そうすることで、より高精度な解析結果を得られる。

#### 受入基準

1. THE System SHALL 複数のコード推定モデルを管理できる
2. THE System SHALL 利用可能なモデルのリストを表示する
3. WHEN ユーザーがモデルを選択した場合、THE System SHALL アクティブなモデルを変更する
4. THE System SHALL 各モデルの説明と精度情報を提供する
5. THE System SHALL カスタムモデルの追加をサポートする
6. THE System SHALL デフォルトモデルを設定できる

### 要件14: 低信頼度コードの強調表示

**ユーザーストーリー**: 演奏者として、推定精度が低いコードを視覚的に識別したい。そうすることで、優先的に確認すべき箇所がわかる。

#### 受入基準

1. WHEN コードセグメントの信頼度が閾値未満の場合、THE System SHALL UIで強調表示する
2. THE System SHALL 信頼度閾値をユーザーが設定できる
3. THE System SHALL 低信頼度セグメントの数を表示する
4. WHERE 代替候補が存在する場合、THE System SHALL 候補リストを表示する
