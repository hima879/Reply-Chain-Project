# 🛡️ Conversation Hijack Detector

A tool that detects **conversation hijacking (reply-chain) attacks** in email threads.

## The Problem

In a reply-chain attack, a hacker gets into a real email conversation, such as an invoice discussion between two companies, and replies inside that trusted thread. The reply usually comes from a look-alike address and asks for a payment to a new bank account or a click on a malicious link.

Because the message sits inside a real thread, it looks safe and normal spam filters often miss it.

**Example:**
- Real sender: `priya@kestrelfoods.com`
- Attacker: `priya@kestre1foods.com` (the letter `l` replaced by the number `1`)

## The Solution

This project reads a whole email thread and gives **each message a risk score from 0 to 100**, along with a plain-language explanation of why it was flagged.

## Approach

A hybrid of two methods:

1. **Rule engine:** checks for look-alike domains, a changed Reply-To, failed SPF/DKIM/DMARC, shortened or suspicious links, risky attachments, "bank details changed" wording, and urgency or secrecy language.
2. **ML text model:** TF-IDF with Logistic Regression, trained to recognise the wording of malicious replies.

The two scores are combined into a final risk score, which is shown in a web app.

## Project Roadmap

| Step | What we build | File | Status |
|------|---------------|------|--------|
| 1 | Email parser (raw email → clean data) | `src/parser.py` | ✅ Done |
| 2 | Rule-based red-flag checks | `src/rules.py` | ⬜ Planned |
| 3 | Dataset and ML model | `generate_dataset.py`, `src/model.py`, `train_model.py` | ⬜ Planned |
| 4 | Combine rules and ML into one score | `src/detector.py` | ⬜ Planned |
| 5 | Web app, tests and deployment | `app_streamlit.py`, `tests/` | ⬜ Planned |

## Project Structure

```
conversation-hijack-detector/
├── src/
│   └── parser.py        # Parses raw emails into a simple Msg object
├── samples/             # Demo email threads (legitimate and hijacked)
├── requirements.txt
└── README.md
```

The structure will grow as each step is added.

## Getting Started

```bash
# 1. Clone the repo
git clone https://github.com/<your-username>/conversation-hijack-detector.git
cd conversation-hijack-detector

# 2. (Optional) create a virtual environment
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
```

## Try It (Day 1: Parser)

```bash
python src/parser.py samples/2_hijacked_bank_change/04.eml
```

This prints the sender, domain, Reply-To, links, attachments and authentication results of the email. In the sample above you can already see the fake domain, the mismatched Reply-To, a risky `.html` attachment and a `bit.ly` link.

## Tech Stack

- Python
- scikit-learn, pandas, NumPy
- Streamlit

## Limitations

This is an educational prototype. The ML model is trained on synthetic data, and the rules are simple heuristics that can produce false positives and negatives. Do not upload confidential emails to a public deployment.

## Author

**Himanshi**: BCA student, AI/ML enthusiast.
