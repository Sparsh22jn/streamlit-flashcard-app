# 🧠 Smart FlashCards

AI-powered flashcard app for smarter learning. Generate comprehensive flashcards using Claude AI, study with Anki-style spaced repetition, and master any topic with ELI5 explanations and memory mnemonics.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)
![Claude](https://img.shields.io/badge/Claude-3.5_Sonnet-orange.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## 🌐 Live Demo

**[Try Smart FlashCards →](https://streamlit-flashcard-app.streamlit.app)**

---

## ✨ Features

### 🤖 AI-Powered Generation
- **Claude 3.5 Sonnet** generates comprehensive, well-structured flashcards
- **SuperMemo 20 Rules** inspired prompts for optimal learning
- Answers are detailed (5-12 sentences) with examples and analogies

### 📚 Smart Learning
- **Anki-Style Spaced Repetition** - Again/Hard/Good/Easy ratings
- **SM-2 Algorithm** calculates optimal review intervals
- **ELI5 Explanations** - Get simple, child-friendly explanations
- **Memory Mnemonics** - AI-generated memory tricks (acronyms, stories, associations)

### 🎨 Modern UI
- **Minimal ChatGPT-style interface** - Clean and distraction-free
- **Dark Mode** - Toggle for night study sessions with glowing cards
- **Deck Icons** - Visual grid of your flashcard collections
- **Mobile Responsive** - Works great on phones and tablets

### ⌨️ Controls
| Input | Action |
|-------|--------|
| **Space / Enter** | Show answer / Flip card |
| **1, 2, 3, 4** | Rate: Again, Hard, Good, Easy |
| **← ↓ ↑ →** | Arrow keys for rating |
| **Swipe Left** | Again (mobile/mouse drag) |
| **Swipe Right** | Good (mobile/mouse drag) |

### 🔐 Security
- **BYOK (Bring Your Own Key)** - Users enter their own Claude API key
- **Password Protection** - Secure deployed apps from unauthorized access
- **API Key Validation** - Verify keys before allowing access
- **Spending Limits** - Built-in cost protection

### 💾 Data
- **SQLite Database** - All flashcards persisted locally
- **Progress Tracking** - Review stats and session summaries
- **Export Ready** - Database file can be backed up or synced

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Claude API key ([Get one here](https://console.anthropic.com/))

### Installation

```bash
# Clone the repository
git clone https://github.com/Sparsh22jn/streamlit-flashcard-app.git
cd streamlit-flashcard-app

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (macOS/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up environment (optional - for password protection)
cp .env.example .env
# Edit .env and set APP_PASSWORD=your_password

# Run the app
streamlit run app.py
```

Open http://localhost:8501 in your browser.

---

## 📖 Usage

### 1. Authentication
1. Enter password (if configured)
2. Enter your Claude API key
3. Set your spending limit

### 2. Generate Flashcards
1. Enter a topic (e.g., "Python decorators", "The French Revolution")
2. Choose number of cards (5-30)
3. Select complexity: Beginner / Intermediate / Advanced
4. Click **Generate →**

### 3. Review & Learn
1. Go to **My Decks** to see all your collections
2. Click **Study** on any deck
3. Read the question, then **Show Answer**
4. Rate your recall with the buttons or keyboard
5. Use **🧒 Explain Simply** for ELI5
6. Use **🧠 Memory Trick** for mnemonics

### 4. Dark Mode
Toggle **🌙 Dark Mode** in the sidebar for night studying with beautiful glowing card effects.

---

## 🗂️ Project Structure

```
streamlit-flashcard-app/
├── app.py                 # Main entry, authentication
├── database.py            # SQLite operations, spaced repetition
├── flashcard_generator.py # Claude API integration, prompts
├── utils.py               # Helper functions
├── flashcards.db          # SQLite database (generated)
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (local)
├── .env.example           # Environment template
└── pages/
    ├── 1_Generate.py      # Flashcard generation page
    ├── 2_Decks.py         # Deck grid view
    └── 3_Review.py        # Study/review page
```

---

## 🌐 Deployment (Streamlit Cloud)

1. Push your code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your repository
4. Add secrets in Streamlit Cloud settings:
   ```toml
   APP_PASSWORD = "your_secure_password"
   ```
5. Deploy!

**Note:** The SQLite database is included in the repo. To update flashcards on cloud:
```bash
git add flashcards.db
git commit -m "Update flashcard database"
git push
```

---

## 💰 Cost Information

Using Claude 3.5 Sonnet API:
- **~$0.01-0.03** per flashcard set (10 cards)
- **~$0.002** per ELI5 explanation
- **~$0.002** per mnemonic generation

The app includes a spending limit to protect against unexpected costs.

---

## 🛠️ Tech Stack

- **Frontend**: Streamlit
- **AI**: Claude 3.5 Sonnet (Anthropic)
- **Database**: SQLite
- **Algorithm**: SM-2 Spaced Repetition
- **Deployment**: Streamlit Cloud

---

## 📝 License

MIT License - feel free to use, modify, and distribute.

---

## 🙏 Acknowledgments

- [Anthropic](https://anthropic.com) for Claude AI
- [Streamlit](https://streamlit.io) for the amazing framework
- [SuperMemo](https://supermemo.com) for the 20 Rules of Knowledge Formulation
- [Anki](https://apps.ankiweb.net) for spaced repetition inspiration

---

**Made with ❤️ for smarter learning**
