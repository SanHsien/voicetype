# 聲成文 VoxProse

[![Release](https://img.shields.io/github/v/release/SanHsien/voxprose?sort=semver)](https://github.com/SanHsien/voxprose/releases/latest)
[![CI](https://github.com/SanHsien/voxprose/actions/workflows/ci.yml/badge.svg)](https://github.com/SanHsien/voxprose/actions/workflows/ci.yml)
[![CodeQL](https://github.com/SanHsien/voxprose/actions/workflows/codeql.yml/badge.svg)](https://github.com/SanHsien/voxprose/actions/workflows/codeql.yml)
[![Windows Release](https://github.com/SanHsien/voxprose/actions/workflows/release.yml/badge.svg)](https://github.com/SanHsien/voxprose/actions/workflows/release.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10–3.14](https://img.shields.io/badge/Python-3.10--3.14-3776AB.svg?logo=python&logoColor=white)](pyproject.toml)
[![Platform: Windows 10/11](https://img.shields.io/badge/Platform-Windows%2010%2F11-0078D4.svg?logo=windows11&logoColor=white)](https://www.microsoft.com/windows/)
[![Local-first](https://img.shields.io/badge/Architecture-Local--first-2E7D32.svg)](docs/DECISIONS.md)
[![Tests: pytest](https://img.shields.io/badge/Tests-pytest-0A9EDC.svg?logo=pytest&logoColor=white)](tests)

[繁體中文](README.md) | [English](README.en.md)

**聲成文 VoxProse** is a local-first AI voice typing tool built for Windows 10/11. Hold or toggle a global hotkey, speak naturally, transcribe with local Faster-Whisper (or an optional cloud engine), optionally polish the text with an LLM, and paste it back into the app that currently has input focus.

**Speak naturally. Write clearly.**

> This project is a Windows-only fork of [`jfamily4tw/voicetype4tw-mac`](https://github.com/jfamily4tw/voicetype4tw-mac) (VoiceType4TW / 嘴炮輸入法), based on `win-stable` v3.0.1 (`win-go-mask` lineage). The original authors are Jimmy (吉米丘) and CC58TW; go-mask maintains the upstream Windows edition. See [NOTICE.md](NOTICE.md) for the full provenance and attribution.

The [Traditional Chinese README](README.md) is the primary project introduction.

## What it is

- **Local-first by default**: local Faster-Whisper handles recognition, so recordings and personal data do not have to leave your PC.
- **Voice typing in any app**: a global hotkey records your voice and pastes the result into LINE, browsers, Office, or any focused input field.
- **Flexible recognition**: use CPU, NVIDIA CUDA, or bring your own API key for Groq, Gemini, or OpenRouter.
- **Context-aware polishing**: the three-layer Soul System controls tone, scenario, and format, with optional automatic scenario switching by foreground app.

---

## 🚀 Quick Start

### Official release (recommended)

1. Open [GitHub Releases](https://github.com/SanHsien/voxprose/releases/latest) and download the latest package:

   | Package | Best for |
   |---------|----------|
   | `ShengChengWen-Windows-Lite-*.zip` | General PCs or CPU-only use; smaller package without CUDA or a model |
   | `ShengChengWen-Windows-NoModel-*.zip` | NVIDIA GPU users; includes the CUDA runtime but not a model |

2. Extract it to a simple path such as `D:\VoxProse`.
3. Double-click `VoxProse.exe`; the selected speech model downloads on first launch.

Each ZIP has a matching `.sha256` checksum. Release packages are published only after ZIP CRC, UTF-8 filename, and required-resource validation.

### Automatic setup from source

**1. Download the source ZIP**: [download the `main` branch](https://github.com/SanHsien/voxprose/archive/refs/heads/main.zip) (or click the green **Code** button above → **Download ZIP**)

**2. Extract** it to a simple path, e.g. `D:\VoxProse` (avoid `C:\Program Files` — insufficient write permissions will be blocked by the environment check)

**3. Double-click `setup_win.bat`** — everything from here on is automatic:

- No Python installed? It automatically downloads a portable Python (no admin rights needed, doesn't pollute your system)
- Has an NVIDIA GPU? CUDA acceleration is enabled automatically; otherwise it falls back to CPU mode (saving an 800MB download)
- Automatically downloads the speech recognition model (~1.5GB), compiles the launcher, and creates a desktop shortcut

![Batch install](assets/batch-install.jpg)

Requires internet access; depending on connection speed this takes about 10–30 minutes. Once done, double-click the "**聲成文**" shortcut on your desktop to start using it.

> 💡 If Windows pops up a blue "Windows protected your PC" screen when you double-click, click "More info" → "Run anyway" (this happens for any file downloaded from the internet, and won't appear again afterward).
> For troubleshooting, see the "Installation Troubleshooting" section below and the [Install & Download Guide](安裝下載教學.md).

---

## Features (Windows)

- **One-click install**: `setup_win.bat` automatically downloads a portable Python and conditionally installs CUDA based on NVIDIA GPU detection.
- **Global hotkeys**: push-to-talk (PTT) or toggle mode.
- **Always-on mode**: VAD detects speech and automatically segments it for recognition, hands-free; detection engine is switchable between RMS energy threshold (default) and Silero VAD neural network (higher accuracy; normal installs include a compatible `onnxruntime` version directly).
- **Local recognition**: Faster-Whisper with CUDA acceleration support; optionally use Groq / Gemini / OpenRouter cloud engines.
- **Microphone device selection + gain + AGC**: switch between multiple microphones (headset/USB/built-in) from the settings page, with automatic hot-plug detection; manual gain (50–300%) and automatic gain control (AGC) can be toggled independently.
- **Three-layer Soul System**: Base Soul + Scenario Template + Output Format, with tone and style polished via LLM.
- **Automatic scenario switching by foreground app (optional)**: configure an "app → scenario template" mapping so the right scenario is applied automatically based on the active window when you start recording (e.g. Business Reply in Outlook, Social Media Post in LINE); off by default.
- **Multi-monitor follow, position memory, non-intrusive focus injection, smart vocabulary learning, and instant translation magic words.**

## Feature Tour

![Dashboard](assets/screenshot-pc-01.jpg)

### Workflow

1. Press your configured hotkey and start speaking
2. The system recognizes your speech via local Whisper or a cloud engine
3. Choose to output the text directly, or send it to an LLM first for polishing, tone cleanup, and style adjustment
4. The result is automatically sent to whichever application currently has input focus
5. If a magic word is used, translation happens automatically in the pipeline before output

### Floating Recording Status Window

![Floating recording status window](assets/screenshot-miclevel.jpg)

- No "AI" label on the left: recognized and output directly
- "AI" label on the left: output only after LLM polishing is complete
- Yellow mode: recognition begins after you stop speaking
- Translate to English / Japanese: speak Chinese directly, output in the corresponding language

### Recognition & AI Settings

![Recognition & AI settings](assets/screenshot-pc-02.jpg)

Choose the speech engine (local Whisper / Groq / Gemini / OpenRouter), model size, and the LLM used for AI polishing (local Ollama, or cloud services such as OpenAI / Claude / Gemini).

### Soul Governance: Three-Layer Stacking System

![Soul governance](assets/screenshot-pc-03.jpg)

Freely mix and match the AI's "soul composition":

1. **🏠 Base Soul**: defines the AI's core values, e.g. no filler, fix typos, output in Traditional Chinese.
2. **🎭 Scenario Template**: defines the conversational style for a specific context, e.g. `💼 Business Reply`, `🌐 Business English`, `📱 Social Media Post`.
3. **📝 Output Format**: decides how the final result is presented, e.g. email format, bullet-point notes, Markdown table.

Combine different souls anytime from the system tray menu, turning the input method into a true personal assistant.

The Soul settings page also has an "Automatic Scenario Switching by Foreground App" section (off by default): enable it and set up "app filename → scenario template" rules (use the "Detect Current Foreground App" button to find the correct filename), and the scenario matching the active window at the moment you start recording is applied automatically for that recognition; if no rule matches, it falls back to whatever scenario you selected manually. This only affects the LLM-polishing stage, so "AI Polishing/Translation" must be enabled for it to have any effect.

### Vocabulary Memory

![Vocabulary memory](assets/screenshot-pc-04.jpg)

Manually enter proper nouns you want recognized (e.g. a client's brand name); any term that appears three or more times is recorded automatically. Each week's memory is condensed and saved separately, preserving long-term memory over time.

### Translating Together with the Soul and Scenario

Three options — translate to English, translate to Japanese, and restore original — can be stacked on top of the soul-injected result: choose which soul to play, then which language to output in.

### Custom Sync Folder

![Cloud sync](assets/screenshot-pc-07.jpg)

Put your settings in your own sync directory (iCloud, Google Drive, or a NAS all work), so memory and frequently used vocabulary are shared across machines.

### Statistics

![Statistics](assets/screenshot-pc-05.jpg)

Records the total length of speech you've input, converts it using the average person's typing speed, and shows how much time it has saved you.

### System Settings

![System settings](assets/screenshot-pc-06.jpg)

Configure the trigger hotkey (push-to-talk PTT or single-click toggle), auto-paste of results (also saved to the clipboard — press Ctrl-V if auto-paste doesn't happen), and verbose output (for terminal debugging). The "Diagnostics & Repair" section lets you test the microphone and export a one-click diagnostic package (environment info, device list, log excerpts, and a settings summary with API keys stripped, packaged as a desktop zip) to make bug reports easier.

## 🛠️ Installation Troubleshooting

If running `setup_win.bat` gets stuck at "creating virtual environment" or "installing dependencies", it's usually related to **disk write permissions**.

**❌ Common cause: installed in a protected directory**
- The path is under the `C:\` root, `C:\Program Files`, or `C:\Program Files (x86)`
- Windows restricts unauthorized scripts from writing large numbers of small files in these locations

**✅ Solutions (pick one):**
1. **Change the install path (recommended)**: move the entire folder to a non-system drive such as D:, e.g. `D:\Tools\VoxProse`
2. **Move it to your user folder**: if you only have a C: drive, put it in `C:\Users\<your-name>\Documents` or on the Desktop
3. Right-click `setup_win.bat` → "Run as administrator"

For manual steps if the model download gets stuck, see the [Install & Download Guide](安裝下載教學.md).

## Development Environment Setup

Requires Python 3.10–3.14:

```bat
git clone https://github.com/SanHsien/voxprose.git
cd voxprose

py -3.12 -m venv venv
venv\Scripts\activate

pip install -r requirements-win.txt
rem Only needed if you have an NVIDIA GPU:
pip install -r requirements-cuda-win.txt

python main.py
```

For regular end users: run `setup_win.bat` (don't place it under the `C:\` root or a protected path like `Program Files` — a user folder or a non-system drive is recommended).

Packaging a portable ZIP (for developers):

```powershell
.\release_win.ps1            # Full: includes CUDA + medium model (~4GB)
.\release_win.ps1 -Lite      # Lite: no CUDA, no model, downloaded online on first launch (~300MB)
.\release_win.ps1 -NoModel   # NoModel: includes CUDA, no model, downloaded online on first launch (~1-1.5GB)
python tools\verify_release_zip.py dist\ShengChengWen-Windows-Lite-vX.Y.Z.zip
```

Pushing a `v*` tag triggers `.github/workflows/release.yml`, which builds both the Lite and NoModel versions and publishes them only after the ZIP CRC, UTF-8 filenames, and required resources pass validation (manually triggering via `workflow_dispatch` only produces build artifacts). See the "Windows Release 實機驗證" section in [`docs/DEVELOPMENT.md`](docs/DEVELOPMENT.md) for the full Windows verification procedure. Dependabot checks Python and GitHub Actions dependencies weekly, `dependency-freshness.yml` compares direct dependencies with PyPI and tracks open PRs monthly, and CodeQL runs an extended weekly security scan. Windows and CUDA dependency PRs always require human review and are never auto-merged.

## Project Structure

```text
main.py                 Windows application entry point
ui/                     Main app, settings, tray, and floating UI
audio/                  Recording and RMS/Silero VAD
stt/                    Local and cloud speech recognition engines
llm/                    Text-polishing provider integrations
output/                 Pastes results into the focused input field
soul/                   Scenario templates and output formats
vocab/ memory/ stats/   Vocabulary, long-term memory, and usage statistics
tests/                  pytest suite and manual hardware validators
docs/                   Development, decisions, upstream, and references
```

## Settings

The config file lives at `%APPDATA%\VoxProse\` (`config_local.json` for machine-local settings, `config_global.json` participates in cloud sync); most options can be adjusted from the settings window:

| Field | Description | Default |
|------|------|--------|
| `hotkey_ptt` | Push-to-talk hotkey (alt_r / ctrl_r / shift_r / f13-f15 / code:VK) | `alt_r` |
| `hotkey_toggle` | Toggle hotkey | `f13` |
| `auto_trigger_enabled` | Always-on mode (hands-free auto trigger) | `false` |
| `vad_engine` | Always-on mode detection engine (`rms`/`silero`; normal installs directly include a compatible `onnxruntime` version; machine-specific, not cloud-synced) | `rms` |
| `stt_engine` | Speech engine (local_whisper / groq / gemini / openrouter) | `local_whisper` |
| `whisper_model` | Whisper model size (tiny/base/small/medium/large) | `medium` |
| `mic_device` | Microphone input device (sounddevice device index; `null` = system default; machine-specific, not synced to cloud) | `null` |
| `mic_gain` | Manual microphone gain (50~300, 100 = unchanged; machine-specific, not synced to cloud) | `100` |
| `mic_gain_auto` | Whether AGC (automatic gain control) is enabled (machine-specific, not synced to cloud) | `true` |
| `llm_enabled` | Whether AI text polishing is enabled | `false` |
| `llm_engine` | LLM engine (ollama / openai / claude / openrouter / gemini / deepseek / qwen) | `ollama` |
| `openrouter_model` | OpenRouter model (falls back in order if unavailable) | `google/gemini-2.5-flash` |
| `language` | Recognition language | `zh` |

## System Requirements

- Windows 10/11 (no need to have Python installed — `setup_win.bat` automatically fetches a portable Python 3.12, no admin rights required)
- CUDA acceleration is enabled automatically with an NVIDIA GPU; without one, it falls back to CPU mode
- 16GB+ RAM recommended
- ~5GB of disk space (including the recognition model)

## Documentation

- [README.md](README.md): primary Traditional Chinese README
- [CHANGELOG.md](CHANGELOG.md): version history
- [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md): development, testing, packaging, and Windows release verification
- [docs/DECISIONS.md](docs/DECISIONS.md): design and maintenance decisions for this fork
- [docs/UPSTREAM.md](docs/UPSTREAM.md): upstream sync status and reviewed-but-skipped changes
- [REVIEW.md](REVIEW.md): latest project review
- [AGENTS.md](AGENTS.md) / [SKILL.md](SKILL.md): AI-agent collaboration rules and quick index

## Project Source and Credits

This project is forked from [`jfamily4tw/voicetype4tw-mac`](https://github.com/jfamily4tw/voicetype4tw-mac). The original authors are **Jimmy (吉米丘)** and **CC58TW**; **go-mask** maintains the upstream Windows edition. This Windows-only fork is maintained by **SanHsien**. See [NOTICE.md](NOTICE.md) for provenance, version lineage, and third-party notices.

For the macOS version and upstream tutorials, refer to the [upstream project's](https://github.com/jfamily4tw/voicetype4tw-mac) latest documentation. This fork is independently maintained and does not speak for the upstream project.

## License

This project is available under the [MIT License](LICENSE). Please retain the license and the attribution listed in [NOTICE.md](NOTICE.md) when using, modifying, or redistributing it.
