# AGENTS.md

給 Codex 與其他 AI coding agents 在 `SanHsien/voxprose` 工作時使用。**本檔是 AI 維護規則的單一真相源**；Claude 專屬補充只放在 [`CLAUDE.md`](CLAUDE.md)，不要在多份文件重複同一套規則。

## 專案定位

聲成文 VoxProse 是 Windows 10/11 本機優先語音輸入工具：全域快捷鍵或 VAD 錄音 → 本機 Faster-Whisper 或選用雲端 STT → 可選 LLM 潤飾／格式／翻譯 → 貼回目前有輸入焦點的 Windows 應用程式。

本 repo 是 [`jfamily4tw/voicetype4tw-mac`](https://github.com/jfamily4tw/voicetype4tw-mac) 的 Windows-only fork。原作者 Jimmy Chiou（吉米丘）與 CC58TW、上游 Windows 維護脈絡與本 fork 來源不得移除；完整資訊以 [`NOTICE.md`](NOTICE.md) 與 [`docs/UPSTREAM.md`](docs/UPSTREAM.md) 為準。

## 硬性邊界

- **Windows-only**：不要重新加入 macOS 專屬 API、依賴或打包分支。
- **保留署名與 MIT 授權**：`LICENSE` 保持標準 MIT 文字；詳細 provenance 放 `NOTICE.md`，不要把歷史查證敘事塞回 LICENSE。
- **不提交私密／本機／大型資料**：API keys、`config_local.json`、`config_global.json`、`sync_path.txt`、使用者 soul/memory/vocab、錄音、輸出、模型等都不得進版控。
- **不要無故動打包鏈**：`setup_win.bat`、`build_win.py`、`release_win.ps1`、`voicetype_installer.iss`、`tools/get_portable_python.ps1`、`tools/launcher.cs` 只有任務明確涉及安裝／打包／Release 時才修改。
- **不要破壞 STT 子行程隔離**：Windows 上 PyQt6 與 CUDA／CTranslate2 載入順序曾造成無訊息崩潰；本機 Whisper 透過 `stt/subprocess_whisper.py` 隔離。修改 `main.py`、`stt/__init__.py` 或啟動順序前，先讀 [`docs/DEVELOPMENT.md`](docs/DEVELOPMENT.md) 的 Windows 已知地雷。

## 架構速覽

```text
hotkey/ 或 audio/auto_trigger.py
              ↓
audio/recorder.py
              ↓
stt/ ── local subprocess Whisper / Groq / Gemini / OpenRouter
              ↓
(optional) llm/ + soul/
              ↓
output/injector.py → focused Windows app

ui/       PyQt6 主介面、系統匣、浮動狀態、設定
config.py 設定預設值與 LOCAL_KEYS
paths.py  %APPDATA%\VoxProse、同步資料與版本路徑
vocab/    詞彙學習
memory/   長期記憶
stats/    使用統計
```

詳細模組與歷史設計理由不要複製到本檔；需要時直接讀程式碼與 [`docs/DECISIONS.md`](docs/DECISIONS.md)。

## 開發約定

- 實際執行依賴以 `requirements-win.txt` 為主；NVIDIA GPU 再加 `requirements-cuda-win.txt`。`pyproject.toml` 主要提供 metadata 與 pytest 設定，不取代現有 Windows 安裝流程。
- 新增 `config.py` 的設定欄位時，同時判斷是否屬於機器特定設定並加入 `LOCAL_KEYS`。
- 依賴更新一律人工審查。PyQt6、Whisper、ONNX Runtime、CUDA 與 Release actions 可能影響 Windows 真機或發行包，不自動核准／合併 Dependabot PR。
- 維護文件用繁體中文；程式碼與識別字維持英文。
- 不為單純文件修改建立新的 review／decision／postmortem 文件。只有資訊具有長期維護價值時才新增文件。

### REVIEW.md 何時更新

`REVIEW.md` 是**最新一次專案覆核的狀態快照**，不是每個 bug 的流水帳。

只有以下情況要更新：

1. 本次工作正在修正 `REVIEW.md` 已列出的風險或缺陷：更新對應項目的修復狀態。
2. 工作中發現新的重大缺陷，會實質改變現有 review 的風險結論：補進 review。

一般 bug 若未出現在 review、也不改變 review 結論，使用測試、PR 說明與必要的 CHANGELOG 記錄即可，不必為了流程強制回寫 REVIEW。

## 驗證

最低自動化驗證：

```powershell
python -m pytest tests/ -v
```

CI 在 Windows runner 上測 Python 3.10–3.14，並做全 repo `py_compile` + pytest。

依改動範圍追加：

- `python main.py`：UI／熱鍵／焦點貼字整體行為。
- `python self_check.py`：真實 STT 子行程與模型。
- `python diagnose_mic.py`：麥克風環境。
- `tests/manual/`：需要真實 Windows 視窗／硬體的手動檢查。
- 打包鏈變更：依 [`docs/DEVELOPMENT.md`](docs/DEVELOPMENT.md) 執行 Windows Release 實機驗證。

沒有實機證據時，明確寫「未驗證」，不要用「應該可以」代替測試。

## 上游同步

`.github/workflows/upstream-check.yml` 發現上游新 commit 時：

- 逐筆判斷是否適用目前 Windows-only tree。
- **採用**：合併／cherry-pick 後更新 `docs/UPSTREAM.md` 的 `last_merged` 與 `last_reviewed`。
- **不採用**：更新 `last_reviewed`，並在 `docs/UPSTREAM.md` 的 Skipped 紀錄理由；只有具有長期架構意義的取捨才另記 `docs/DECISIONS.md`。

## 文件責任

- `README.md` / `README.en.md`：產品入口、下載、使用方式、隱私邊界。
- `安裝下載教學.md`：安裝與模型下載疑難排解。
- `CHANGELOG.md`：版本歷史。
- `docs/DEVELOPMENT.md`：開發、測試、Windows 已知地雷、打包與 Release 驗證。
- `docs/DECISIONS.md`：需要長期保存的設計決策，不記日常操作流水帳。
- `docs/UPSTREAM.md`：上游同步狀態與跳過理由。
- `NOTICE.md`：來源、署名與第三方聲明。
- `REVIEW.md`：最新專案覆核狀態，不是 bug log。
- `SKILL.md`：AI agent 快速索引；規則衝突時以本檔為準。
