# 要件定義書: コード評価前処理機能（Chord Evaluation Preprocessing）

## はじめに

コード認識評価システムの精度を向上させるため、予測コードと正解コードの前処理機能を実装します。現在の評価システムは、予測コード数（3009個）と正解コード数（125個）の大きな差異により、評価精度が低い状態です（ルート音17.22%、品質12.50%、完全一致0.07%）。この要件定義書では、時間解像度の違いを吸収するコード集約機能と、表記の違いを統一するコード正規化機能の要件を定義します。

## 用語集

- **System**: コード評価前処理システム全体
- **PreprocessingPipeline**: 前処理パイプライン - 正規化と集約を統合するメインコンポーネント
- **ChordNormalizer**: コード正規化器 - コード表記を標準形式に変換するコンポーネント
- **ChordAggregator**: コード集約器 - 予測コードを目標時間解像度に集約するコンポーネント
- **BenchmarkTool**: ベンチマークツール - 評価システムの既存コンポーネント
- **Predicted_Chords**: 予測コード - モデルが生成したコードリスト
- **Ground_Truth_Chords**: 正解コード - 人間がアノテーションした正解データ
- **Timestamp**: タイムスタンプ - コードの開始時刻（秒単位）
- **Normalization**: 正規化 - コード表記を標準形式に変換する処理
- **Aggregation**: 集約 - 高解像度のコードを低解像度に統合する処理
- **Slash_Notation**: スラッシュ記法 - ベース音を含むコード表記（例: C/E）
- **Root_Note**: ルート音 - コードの基音（例: Cメジャーの「C」）
- **Quality**: 品質 - コードの種類（メジャー、マイナー、sus2など）
- **Bass_Note**: ベース音 - スラッシュコードの低音部分
- **Enharmonic_Equivalent**: 異名同音 - 音高が同じで表記が異なる音（例: C#とDb）

## 要件

### 要件1: コード正規化

**ユーザーストーリー:** 開発者として、異なる表記形式のコードを統一された形式に変換したい。これにより、表記の違いによる評価精度の低下を防ぐことができる。

#### 受入基準

1. THE ChordNormalizer SHALL 空白を含むコード文字列から空白を削除する
2. WHEN スラッシュ記法のコード（例: "C/E"）が入力される THEN THE ChordNormalizer SHALL 設定された正規化モードに従って表記を統一する
3. WHEN on記法のコード（例: "ConE"）が入力される THEN THE ChordNormalizer SHALL 設定された正規化モードに従って表記を統一する
4. WHEN 品質表記のバリエーション（例: "maj", "M", "major"）が入力される THEN THE ChordNormalizer SHALL 標準形式（例: "M"）に変換する
5. WHEN 異名同音のルート音（例: "C#" と "Db"）が入力される THEN THE ChordNormalizer SHALL 統一された表記に変換する
6. WHEN 正規化されたコードが再度正規化される THEN THE ChordNormalizer SHALL 同じ結果を返す（冪等性）
7. WHEN 複数のコードが一括正規化される THEN THE ChordNormalizer SHALL 各コードを個別に正規化した結果と同じリストを返す
8. IF 無効なコード表記が入力される THEN THE ChordNormalizer SHALL ValueError を発生させる

### 要件2: コード集約

**ユーザーストーリー:** 開発者として、高解像度の予測コードを低解像度の正解コードに合わせて集約したい。これにより、時間解像度の違いによる評価精度の低下を防ぐことができる。

#### 受入基準

1. WHEN 予測コードと目標タイムスタンプが提供される THEN THE ChordAggregator SHALL 各目標タイムスタンプ区間に対して1つのコードを選択する
2. WHEN 集約戦略が MOST_FREQUENT に設定される THEN THE ChordAggregator SHALL 各区間で最も頻繁に出現するコードを選択する
3. WHEN 集約戦略が LONGEST_DURATION に設定される THEN THE ChordAggregator SHALL 各区間で最も長い持続時間を持つコードを選択する
4. WHEN 集約戦略が FIRST に設定される THEN THE ChordAggregator SHALL 各区間の最初のコードを選択する
5. WHEN 集約戦略が LAST に設定される THEN THE ChordAggregator SHALL 各区間の最後のコードを選択する
6. WHEN 目標タイムスタンプ区間内に予測コードが存在しない THEN THE ChordAggregator SHALL 最も近い予測コードを選択する
7. WHEN 許容誤差が設定される THEN THE ChordAggregator SHALL 許容誤差内のコードを区間内として扱う
8. THE ChordAggregator SHALL 集約後のコード数が目標タイムスタンプ数と一致することを保証する
9. IF 予測コード数とタイムスタンプ数が一致しない THEN THE ChordAggregator SHALL ValueError を発生させる
10. IF タイムスタンプが昇順にソートされていない THEN THE ChordAggregator SHALL ValueError を発生させる

### 要件3: 前処理パイプライン統合

**ユーザーストーリー:** 開発者として、正規化と集約を統合した前処理パイプラインを使用したい。これにより、一貫した前処理を簡単に適用できる。

#### 受入基準

1. WHEN PreprocessingPipeline が初期化される THEN THE System SHALL 設定に基づいて ChordNormalizer と ChordAggregator を初期化する
2. WHEN 正規化が有効に設定される THEN THE PreprocessingPipeline SHALL 予測コードと正解コードの両方を正規化する
3. WHEN 集約が有効に設定される THEN THE PreprocessingPipeline SHALL 予測コードを正解コードの時間解像度に集約する
4. WHEN 正規化と集約の両方が有効に設定される THEN THE PreprocessingPipeline SHALL 正規化を先に実行し、その後集約を実行する
5. WHEN 正規化と集約の両方が無効に設定される THEN THE PreprocessingPipeline SHALL 入力コードをそのまま返す
6. WHEN タイムスタンプが提供されない THEN THE PreprocessingPipeline SHALL 集約をスキップする
7. THE PreprocessingPipeline SHALL 前処理済みの予測コードと正解コードのタプルを返す
8. IF 空のコードリストが入力される THEN THE PreprocessingPipeline SHALL ValueError を発生させる

### 要件4: BenchmarkTool統合

**ユーザーストーリー:** 開発者として、既存のBenchmarkToolに前処理機能を統合したい。これにより、評価時に自動的に前処理が適用される。

#### 受入基準

1. THE BenchmarkTool SHALL PreprocessingPipeline を設定するメソッドを提供する
2. WHEN PreprocessingPipeline が設定される THEN THE BenchmarkTool SHALL 評価前に自動的に前処理を適用する
3. WHEN PreprocessingPipeline が設定されていない THEN THE BenchmarkTool SHALL 前処理なしで評価を実行する
4. THE BenchmarkTool SHALL 前処理の有効/無効を切り替えるオプションを提供する
5. WHEN ベンチマークが実行される THEN THE BenchmarkTool SHALL 前処理済みのコードを Evaluator に渡す

### 要件5: 設定管理

**ユーザーストーリー:** 開発者として、前処理の動作を柔軟に設定したい。これにより、異なるシナリオに応じて最適な前処理を適用できる。

#### 受入基準

1. THE PreprocessingConfig SHALL 正規化の有効/無効を制御するフラグを提供する
2. THE PreprocessingConfig SHALL 集約の有効/無効を制御するフラグを提供する
3. THE PreprocessingConfig SHALL 正規化モード（SLASH, ON, STANDARD）を指定するオプションを提供する
4. THE PreprocessingConfig SHALL 集約戦略（MOST_FREQUENT, LONGEST_DURATION, FIRST, LAST）を指定するオプションを提供する
5. THE PreprocessingConfig SHALL タイムスタンプの許容誤差を指定するオプションを提供する
6. THE PreprocessingConfig SHALL デフォルト値を提供する（正規化: 有効、集約: 有効、モード: STANDARD、戦略: MOST_FREQUENT、許容誤差: 0.1秒）

### 要件6: エラーハンドリング

**ユーザーストーリー:** 開発者として、無効な入力や予期しない状況に対して適切なエラーハンドリングを行いたい。これにより、システムの堅牢性を確保できる。

#### 受入基準

1. IF 無効なコード表記が入力される THEN THE System SHALL ValueError を発生させ、詳細なエラーメッセージを提供する
2. IF コード数とタイムスタンプ数が一致しない THEN THE System SHALL ValueError を発生させる
3. IF 空のコードリストが入力される THEN THE System SHALL ValueError を発生させる
4. IF タイムスタンプが昇順にソートされていない THEN THE System SHALL ValueError を発生させる
5. IF 負のタイムスタンプが入力される THEN THE System SHALL ValueError を発生させる
6. WHEN エラーが発生する THEN THE System SHALL エラー内容をログに記録する

### 要件7: パフォーマンス

**ユーザーストーリー:** 開発者として、大量のコードを効率的に処理したい。これにより、実用的な時間内で評価を完了できる。

#### 受入基準

1. WHEN 3009個の予測コードを125個に集約する THEN THE System SHALL 100ミリ秒以内に処理を完了する
2. WHEN 10,000個のコードを正規化する THEN THE System SHALL 500ミリ秒以内に処理を完了する
3. THE System SHALL メモリ使用量を入力サイズに対して線形（O(n)）に保つ
4. THE System SHALL 処理するコード数の上限を100,000個とする
5. THE System SHALL コード文字列の長さ制限を100文字とする
6. THE System SHALL タイムスタンプの範囲を0秒から10,000秒に制限する

### 要件8: データ整合性

**ユーザーストーリー:** 開発者として、前処理後もコードの音楽的な意味が保持されることを確認したい。これにより、評価の正確性を保証できる。

#### 受入基準

1. WHEN コードが正規化される THEN THE System SHALL ルート音の音高を保持する
2. WHEN コードが正規化される THEN THE System SHALL コードの品質（メジャー、マイナーなど）を保持する
3. WHEN ベース音を含むコードが正規化される THEN THE System SHALL ベース音の音高を保持する
4. WHEN コードが集約される THEN THE System SHALL タイムスタンプの順序を保持する
5. WHEN コードが集約される THEN THE System SHALL 各区間に対して有効なコードを割り当てる

### 要件9: テスト可能性

**ユーザーストーリー:** 開発者として、前処理機能を包括的にテストしたい。これにより、システムの正確性を保証できる。

#### 受入基準

1. THE System SHALL 各コンポーネント（ChordNormalizer, ChordAggregator, PreprocessingPipeline）に対して独立したユニットテストを提供する
2. THE System SHALL プロパティベーステストを使用して正規化の冪等性を検証する
3. THE System SHALL プロパティベーステストを使用して集約後のコード数を検証する
4. THE System SHALL プロパティベーステストを使用してタイムスタンプの順序保持を検証する
5. THE System SHALL 実際の楽曲データを使用した統合テストを提供する
6. THE System SHALL コードカバレッジ90%以上を達成する

### 要件10: ドキュメンテーション

**ユーザーストーリー:** 開発者として、前処理機能の使用方法を理解したい。これにより、システムを効果的に活用できる。

#### 受入基準

1. THE System SHALL 各クラスとメソッドに対して docstring を提供する
2. THE System SHALL 使用例を含むドキュメントを提供する
3. THE System SHALL 設定オプションの説明を提供する
4. THE System SHALL エラーメッセージの説明を提供する
5. THE System SHALL パフォーマンス特性の説明を提供する
