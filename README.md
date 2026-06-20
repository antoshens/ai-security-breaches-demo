# AI Agent Security Guardrails: Implementing Zero Trust for LLMs

This repository contains the Proof-of-Concept (PoC) codebase for defending LLM-based autonomous agents against **Indirect Prompt Injection** and **Data Leakage (PII)**. 

The core architectural philosophy demonstrates how to migrate from a highly volatile *probabilistic defense* (LLM Alignment/RLHF) to a strict *deterministic defense* (Output Guardrails via Microsoft Presidio), enforcing a **Zero Trust Architecture** on AI Agent systems.

---

## 🔬 Theoretical Background: The Missing Security Boundary

In classic operating systems security, the **$W \oplus X$ (Write XOR Execute)** principle acts as a foundational boundary: memory pages can be modified (Writable) OR executed (Executable), but never both simultaneously. This completely mitigates binary exploits like buffer overflows.



### Why $W \oplus X$ Fails in Transformers:
LLM Agents inherently break this paradigm. In a Transformer architecture, the context window treats everything as a single stream of tokens:
1. **System Instructions** (Code)
2. **User Input / Untrusted Data** (Data)
3. **Tool Executions / Image Metadata** (Data)

Because instructions and untrusted data are blended into the same mathematical attention space (**Attention Vectors**), an LLM cannot natively distinguish between an engineering directive and a malicious payload hidden inside an email or an invoice's EXIF metadata.

---

## 🛑 The Vulnerability: Indirect Prompt Injection

While direct jailbreaks (chat-based attacks) are well-known, **Indirect Prompt Injection** presents a much greater risk for production agents. The attack vector unfolds as follows:
* An agent is tasked with processing a corporate asset (e.g., analyzing an invoice image or summarizing an incoming email).
* An attacker injects hidden instructions into the text or media assets.
* When the agent tokens are parsed by the LLM (such as *Gemma-4*), the model's weights shift attention towards the injected payload, causing it to unauthorizedly execute system tools (e.g., `ReadContactsDB`) and leak confidential PII.

---

## 🛡️ The Architecture: Deterministic Zero Trust Guardrails

To mitigate this without sacrificing the agent's autonomy, this project implements a **Dual-Layer Defense Stack**:



1. **Probabilistic Layer (Model Alignment):** Utilizing high-parameter models (like `Gemma-4-26b`) which feature high contextual awareness. The model's cross-attention mechanisms inherently filter out noisy or irrelevant tool-call attempts embedded inside external files.
2. **Deterministic Layer (Microsoft Presidio Output Middleware):** Because we cannot rely on the *probability* of a model staying safe, we apply a strict outbound firewall. If the LLM experiences alignment drift (or token smuggling) and spills data, Presidio captures the raw text, analyzes it via Regex and Named Entity Recognition (NER), and enforces hard masking before the user sees the output.

---

## 🛠️ Repository Structure

```text
├── notebooks/
│   ├── 01_prompt_injection_demo.ipynb       # Email attack & text token smuggling simulation
│   └── 02_multimodal_vision_robustness.ipynb # Vision analysis via Gemma-4 & alignment analysis
├── src/
│   └── middleware.py                        # Customized Microsoft Presidio PII Guardrail
|   └── add_custom_metadata_to_image.py      # Script for adding text to the image (jpg/png files)
├── data/
│   ├── invoice.png                          # Example of invoice image
|   └── poisoned_invoice.jpg                 # Image artifact containing malicious payload
|   └── contacts.json                        # Mock target database containing sensitive PII
│   └── malicious_email.txt.txt              # Text of the malicious email
├── requirements.txt                         # Strictly pinned dependency manifest
└── README.md                                # System architectural manifest
