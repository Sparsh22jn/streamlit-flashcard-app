# 🎴 Streamlit Flashcard App for Complex Topics

A Streamlit-based flashcard application that uses AI (Claude 3.5 Sonnet) to generate educational flashcards on any topic. Features Anki-style spaced repetition, ELI5 explanations, and memory mnemonics.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)
![Claude](https://img.shields.io/badge/Claude-3.5_Sonnet-orange.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## ✨ Features

- **🤖 AI-Powered Generation**: Create comprehensive flashcards using Claude 3.5 Sonnet
- **� BYOK (Bring Your Own Key)**: Users enter their own API key - no shared credits!
- **📚 Multiple Complexity Levels**: Beginner, Intermediate, and Advanced options
- **🔄 Anki-Style Review**: Spaced repetition with Again/Hard/Good/Easy ratings
- **🧒 ELI5 Explanations**: Get simple, child-friendly explanations for any concept
- **🧠 Memory Mnemonics**: AI-generated memory tricks using proven techniques
- **💰 Cost Tracking**: Built-in spending limit protection for API costs
- **🔐 Password Protection**: Secure your deployed app from unauthorized use
- **💾 Persistent Storage**: All flashcards saved to SQLite database
- **📱 Mobile Friendly**: Works great on phones and tablets

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Anthropic Claude API key ([Get one here](https://console.anthropic.com/))

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/streamlit-flashcard-app.git
   cd streamlit-flashcard-app
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   # Copy the example file
   cp .env.example .env
   
   # Edit .env and set a password (API key is entered in the app!)
   APP_PASSWORD=your_secure_password
   ```

5. **Run the app**
   ```bash
   streamlit run app.py
   ```

6. **Open in browser**
   - Navigate to `http://localhost:8501`
   - Enter password (if set)
   - Enter your Claude API key
   - Start learning!

## 📖 How to Use

### First Time Setup
1. **Enter password** (if configured)
2. **Enter your Claude API key** - Get one at [console.anthropic.com](https://console.anthropic.com/)
3. **Set your spending limit** - Protect yourself from unexpected costs

### Generating Flashcards

1. Go to the **Generate** page from the sidebar
2. Enter a topic you want to learn (e.g., "Python decorators")
3. Choose the number of flashcards (5-50)
4. Select complexity level (Beginner/Intermediate/Advanced)
5. Click **Generate Flashcards**
6. Wait for AI to create your personalized flashcards

### Reviewing Flashcards

1. Go to the **Review** page from the sidebar
2. Select a flashcard set from the dropdown
3. Click **Tap to Reveal Answer** to see the answer
4. Rate your recall: **Again** / **Hard** / **Good** / **Easy**
5. Use **⬅️ ELI5** for simple explanations
6. Use **🧠 Memory Trick** for mnemonics

## 🗂️ Project Structure

```
streamlit-flashcard-app/
├── app.py                    # Main application entry point
├── pages/
│   ├── 1_Generate.py        # Flashcard generation page
│   └── 2_Review.py          # Flashcard review page
├── database.py              # SQLite database operations
├── flashcard_generator.py   # Claude API integration
├── utils.py                 # Helper functions
├── requirements.txt         # Python dependencies
├── .env.example            # Environment variables template
├── .gitignore              # Git ignore rules
└── README.md               # This file
```

## 🗄️ Database Schema

### Cardsets Table
| Column | Type | Description |
|--------|------|-------------|
| cardset_id | TEXT | Primary key |
| topic | TEXT | Topic of the flashcard set |
| num_cards | INTEGER | Number of cards |
| complexity_level | TEXT | Beginner/Intermediate/Advanced |
| created_at | TIMESTAMP | Creation timestamp |

### Flashcards Table
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| cardset_id | TEXT | Foreign key to cardsets |
| question | TEXT | The question |
| answer | TEXT | The answer |
| times_reviewed | INTEGER | Review count |
| explanation_eli5 | TEXT | ELI5 explanation |
| explanation_eli10 | TEXT | ELI10 explanation |

## ☁️ Deployment to Streamlit Cloud

### Step 1: Push to GitHub
```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/yourusername/streamlit-flashcard-app.git
git push -u origin main
```

### Step 2: Deploy on Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io/)
2. Sign in with GitHub
3. Click "New app"
4. Select your repository
5. Set main file path: `app.py`

### Step 3: Configure Secrets (Only Password Needed!)

In Streamlit Cloud, go to **App Settings** → **Secrets** and add:

```toml
APP_PASSWORD = "your_secure_password_here"
```

> 🎉 **No API key needed in secrets!** Each user enters their own Claude API key in the app.

### Step 4: Share Securely

- Share the password with trusted users
- Each user uses their OWN API key and credits
- You pay $0 for other users' API usage!

## 💰 Cost Management

**BYOK Model (Bring Your Own Key):**
- Each user enters their own Claude API key
- Each user sets their own spending limit
- You (the app owner) pay nothing for API costs!
|---------|-------------|---------|
| `SPENDING_LIMIT` | Max USD to spend on API | $10.00 |

**Approximate costs (Claude 3.5 Sonnet):**
- Generating 10 flashcards: ~$0.02-0.05
- ELI5 explanation: ~$0.005
- Memory mnemonic: ~$0.005

## 🔐 Authentication

When `APP_PASSWORD` is set:
- Users must enter password to access any page
- Protects your API credits from unauthorized use
- Leave empty for local development (no password required)

## 📱 Mobile Access

### Local Network
```bash
streamlit run app.py
# Access from phone: http://YOUR_IP:8501
```

### Cloud (Recommended)
Deploy to Streamlit Cloud for access from anywhere!

## 🔧 Configuration

### Environment Variables
| Variable | Description | Required |
|----------|-------------|----------|
| `ANTHROPIC_API_KEY` | Your Claude API key | Yes |
| `SPENDING_LIMIT` | Max spend in USD | No (default: $10) |
| `APP_PASSWORD` | Password for app access | No (recommended for deploy) |

### Customization
- Edit prompts in `flashcard_generator.py` for different card formats
- Modify spaced repetition algorithm in `database.py`
- Adjust UI components in page files

## 🐛 Troubleshooting

**"Module not found" errors**
```bash
pip install -r requirements.txt
```

**API authentication errors**
- Verify your API key at [console.anthropic.com](https://console.anthropic.com/)
- Check that `.env` file exists and has the correct key

**Database locked errors**
- Close other connections to the database
- Restart the Streamlit app

**Port already in use**
```bash
streamlit run app.py --server.port 8502
```

**"Could not parse flashcards" error**
- The AI response format was unexpected
- Try generating again with a simpler topic
- Check your API key has sufficient credits

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- [Streamlit](https://streamlit.io/) - The amazing web framework
- [Anthropic](https://anthropic.com/) - Claude AI for flashcard generation
- [SQLite](https://sqlite.org/) - Lightweight database
- [SuperMemo](https://supermemo.com/) - Spaced repetition research

---

**Made with ❤️ for lifelong learners**
