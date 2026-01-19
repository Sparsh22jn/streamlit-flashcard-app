# 🎴 Streamlit Flashcard App for Complex Topics

A Streamlit-based flashcard application that uses AI (Claude API) to generate educational flashcards on any topic. Perfect for learning complex subjects with personalized study materials.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## ✨ Features

- **🤖 AI-Powered Generation**: Create flashcards on any topic using Claude AI
- **📚 Multiple Complexity Levels**: Beginner, Intermediate, and Advanced options
- **🔄 Interactive Review**: Flip cards to reveal answers with smooth UI
- **🧒 ELI5/ELI10 Explanations**: Get simplified explanations for any concept
- **💾 Persistent Storage**: All flashcards saved to SQLite database
- **📱 Mobile Friendly**: Works great on phones and tablets
- **☁️ Cloud Ready**: Easy deployment to Streamlit Cloud

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Anthropic API key ([Get one here](https://console.anthropic.com/))

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
   
   # Edit .env and add your Anthropic API key
   ANTHROPIC_API_KEY=your_api_key_here
   ```

5. **Run the app**
   ```bash
   streamlit run app.py
   ```

6. **Open in browser**
   - Navigate to `http://localhost:8501`

## 📖 How to Use

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
3. Click **Show Answer** to flip the card
4. Use **Previous** and **Next** to navigate
5. Click **ELI5** or **ELI10** for simpler explanations

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

1. Push your code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io/)
3. Connect your GitHub account
4. Select your repository
5. Add your `ANTHROPIC_API_KEY` in Secrets:
   ```toml
   ANTHROPIC_API_KEY = "your_api_key_here"
   ```
6. Deploy!

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
| ANTHROPIC_API_KEY | Your Anthropic API key | Yes |

### Customization
- Edit `utils.py` to change card styling
- Modify prompts in `flashcard_generator.py` for different card formats
- Adjust UI components in page files

## 📝 Sample Topics

- Python list comprehensions
- World War II major events
- Photosynthesis process
- Machine learning basics
- Spanish irregular verbs
- Quantum computing fundamentals
- Data structures and algorithms

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

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- [Streamlit](https://streamlit.io/) - The amazing web framework
- [Anthropic](https://anthropic.com/) - Claude AI for flashcard generation
- [SQLite](https://sqlite.org/) - Lightweight database

---

**Made with ❤️ for lifelong learners**
