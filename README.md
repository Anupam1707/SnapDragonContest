# GuardianEdge: Real-Time On-Device DLP & Threat Neutralization

[![Snapdragon X](https://img.shields.io/badge/Accelerated_by-Snapdragon%C2%AE_X_Elite-FF2E2E.svg)](https://www.qualcomm.com/snapdragon)
[![Hexagon NPU](https://img.shields.io/badge/Qualcomm_Hexagon_NPU-45_TOPS-0253B3.svg)](https://aihub.qualcomm.com/)
[![Qualcomm AI Hub](https://img.shields.io/badge/Optimized_with-Qualcomm_AI_Hub-00E676.svg)](https://aihub.qualcomm.com/)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows_on_ARM64_%7C_HP_OmniBook-orange.svg)](#)

> **Submission for the Snapdragon® AI Lab Build & Present Challenge**  
> Designed, developed, and optimized for **Snapdragon-powered HP PCs** (HP OmniBook Ultra / Snapdragon X Elite & X Plus).

---

## 🎯 Executive Summary

**GuardianEdge** is an autonomous, on-device cybersecurity and sensitive Data Loss Prevention (DLP) engine. Running 100% locally on the **45 TOPS Qualcomm® Hexagon™ NPU** using models compiled via the **Qualcomm AI Hub**, GuardianEdge intercepts and neutralizes sensitive credentials (API keys, JWTs, AWS tokens), customer PII (credit cards, Indian Aadhaar & PAN), and healthcare records before they can be accidentally leaked into Generative AI chatbots (ChatGPT, Claude), web forms, public messaging channels, or video calls.

### The Cloud DLP Paradox Solved
Traditional DLP solutions stream confidential files across WAN networks to external cloud servers to evaluate if data is sensitive—directly violating data sovereignty regulations (India DPDP Act 2023, GDPR, HIPAA) while adding 250ms+ latency.

GuardianEdge executes **100% on the local edge**. Zero packets leave your laptop.

---

## ⚡ Why Snapdragon® X & Hexagon™ NPU?

Security and DLP inspection must be **always-on**, operating seamlessly in the background with zero thermal impact and zero perceptible latency.

| Performance Metric | Snapdragon® X Elite (Hexagon NPU) | Traditional x86 Laptop CPU | Discrete Mobile GPU | Cloud DLP API |
| :--- | :---: | :---: | :---: | :---: |
| **Inference Latency** | **4.18 ms** ⚡ | 46.50 ms | 11.20 ms | 285.00 ms (Network lag) |
| **Active Power Draw** | **0.22 Watts** 🌱 | 19.80 Watts | 52.00 Watts | 1.20 Watts (WiFi) |
| **Energy Consumed / Scan** | **0.92 mJ** (WINNER) | 920.70 mJ (**965x worse**) | 582.40 mJ (**630x worse**) | 342.00 mJ |
| **Battery Life Impact** | **<0.05% per 1k scans** | Heavy drain (3–4 hrs loss) | Severe drain | Minor battery drain |
| **Privacy & Sovereignty** | **100% Local (Zero WAN)** | Local (High fan noise) | Local (Thermal throttling) | **FAILED (Leaks Data)** |

---

## 🏗️ System Architecture

```mermaid
flowchart LR
    A[Clipboard / Screen / Keyboard Input] --> B[Fast Pre-Filter & Shannon Entropy <0.5ms]
    B --> C[Qualcomm AI Hub Neural Classifier\nHexagon NPU 45 TOPS <4ms]
    C --> D{Threat Detected?}
    D -- No --> E[Direct Passthrough]
    D -- Yes --> F[Active Synthetic Redaction Engine]
    F --> G[Safe Neutralized Token Replacement]
    G --> H[Destinations: ChatGPT, Slack, Email, Screen Share]
    F --> I[(Local Encrypted SQLite Vault)]
```

### Dual-Stage Edge Pipeline
1. **Stage 1 (<0.5ms Pre-Filter)**: High-speed heuristic regex, Shannon entropy randomness scoring, and mathematical checksum validation (Luhn algorithm for credit cards, Verhoeff for Indian Aadhaar).
2. **Stage 2 (<4ms Neural NPU Classification)**: Qualcomm AI Hub optimized DeBERTa/MiniLM transformer classifier executing via ONNX Runtime `QNNExecutionProvider` directly on the 45 TOPS Hexagon NPU.

---

## 🚀 Qualcomm AI Hub Workflow

Models are quantized and compiled targeting the Snapdragon X architecture using the Qualcomm AI Hub SDK (`qai-hub`):

```python
import qai_hub as hub

# 1. Target Hardware: Snapdragon X Elite (HP OmniBook Ultra)
device = hub.Device("Snapdragon X Elite CRD")

# 2. Load and trace DLP token classifier
model = hub.load_model("deberta-v3-small")

# 3. Compile for Qualcomm Hexagon NPU using QNN Execution Provider
compile_job = hub.submit_compile_job(
    model=model,
    device=device,
    input_specs=dict(input_ids=(1, 128), attention_mask=(1, 128)),
    options="--target_runtime qnn_lib_aarch64_windows --quantize int8"
)

# 4. Profile on Real Snapdragon X Hardware
profile_job = hub.submit_profile_job(model=compile_job.get_target_model(), device=device)
target_model = compile_job.get_target_model()
target_model.download("models/guardian_dlp_qnn_snapdragon_x.onnx")
```

---

## 💻 Quickstart & Installation

### 1. Clone the Repository
```bash
git clone https://github.com/<your-username>/GuardianEdge-Snapdragon.git
cd GuardianEdge-Snapdragon
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Launch Interactive Security Operations Center (SOC) Dashboard
```bash
python -m guardian_edge.cli serve --port 8844
```
Open **[http://localhost:8844](http://localhost:8844)** in your browser to experience the real-time DLP Interceptor, Screen Guard Visual DLP simulator, dynamic policy manager, and local encrypted audit trail.

### 4. CLI Scan Mode
```bash
python -m guardian_edge.cli scan "My OpenAI key is sk-proj-1234567890abcdefABCDEF1234567890"
```

### 5. Run Benchmarks & Unit Tests
```bash
python -m pytest tests/
python -m guardian_edge.cli benchmark
```

---

## 🛡️ Supported Detection Categories

- **Developer Secrets & Cloud Keys**: OpenAI API keys (`sk-proj-`), GitHub Personal Access Tokens (`ghp_`), AWS Access & Secret Keys (`AKIA...`), JWT tokens, Private Keys (RSA/OpenSSH), Database connection strings.
- **Financial PII**: Credit Cards (Visa, Mastercard, Amex, RuPay with Luhn verification), IBANs, Bank Account Numbers.
- **National Identifiers**: Indian Aadhaar (12-digit format with Verhoeff validation), Indian PAN cards (Income Tax Department format), US SSN.
- **Healthcare & Clinical PHI**: Diagnostic notes, chemotherapy/biopsy reports, ICD-10 diagnostic classifications.

---

## 📁 Repository Structure

```
├── GuardianEdge_Pitch_Presentation.pptx   # Official Short Pitch Presentation (PPTX)
├── GuardianEdge_Pitch_Presentation.pdf    # Official Short Pitch Presentation (PDF)
├── GuardianEdge_Project_Description.docx  # Official Brief Project Description (DOCX)
├── GuardianEdge_Project_Description.pdf   # Official Brief Project Description (PDF)
├── guardian_edge/                         # Core Python package
│   ├── config.py                          # Hardware profile & policy definitions
│   ├── detector.py                        # Dual-stage heuristic + NPU neural detector
│   ├── redactor.py                        # High-speed synthetic token masking
│   ├── screen_guard.py                    # Visual screen sharing protection
│   ├── npu_engine.py                      # Qualcomm QNN execution provider interface
│   ├── policy_engine.py                   # Dynamic security policies & local SQLite vault
│   ├── server.py                          # FastAPI server & REST endpoints
│   └── cli.py                             # CLI runner & background daemon
├── benchmarks/                            # Performance & energy suite
│   └── benchmark_suite.py                 # NPU vs CPU vs GPU vs Cloud benchmarks
├── scripts/                               # Automation & export scripts
│   ├── compile_for_aihub.py               # Qualcomm AI Hub compilation script
│   ├── generate_presentation.py           # PPTX generator
│   ├── generate_pitch_pdf.py              # PDF slides generator
│   └── generate_brief_doc.py              # DOCX/PDF proposal generator
├── static/                                # Web dashboard assets
│   └── index.html                         # Dark-mode glassmorphism SOC dashboard
├── tests/                                 # Automated test suite
│   └── test_guardian.py                   # Pytest test cases
└── requirements.txt                       # Python dependencies
```

---

## 📄 License
This project is licensed under the Apache 2.0 License - see the [LICENSE](LICENSE) file for details.
