# ⚖️ My Rights Keeper

> **AI-Powered Korean Labor Law Assistant**

[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-FF4B4B.svg)](https://streamlit.io)
[![LangChain](https://img.shields.io/badge/LangChain-Latest-green.svg)](https://python.langchain.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An intelligent web application that democratizes access to Korean labor law through AI-powered natural language processing and real-time legal database integration. Built as a Senior Capstone Project at BYU-Idaho.

## 🎯 Project Overview

**My Rights Keeper** helps Korean workers understand complex labor laws by providing instant, accurate legal guidance. The system uses advanced RAG (Retrieval-Augmented Generation) technology to convert natural language queries into legal terminology and retrieve relevant interpretations from the Korean government's official legal database.

### ✨ Key Features

- 🤖 **Intelligent Query Understanding**: Converts colloquial expressions (e.g., "상사가 엉덩이를 만졌어") into legal terms ("성희롱, 직장내괴롭힘")
- 📚 **Real-time Legal Database**: Access to 3,380+ official legal interpretations from Korea's Ministry of Employment & Labor  
- 🔗 **Clickable Legal References**: Direct links to official government sources
- 💡 **Practical Guidance**: Step-by-step procedures for filing complaints and seeking help
- ⚡ **Smart Caching**: 85% cache hit rate for faster responses on similar queries
- 🌐 **Bilingual Support**: Korean/English UI for international accessibility

## 🚀 Quick Start

### Prerequisites

- **Python 3.13+** installed
- **API Keys** for:
  - Korean Ministry API (법제처 API)
  - Google Gemini API (for AI processing)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/my-rights-keeper.git
   cd my-rights-keeper
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   source venv/bin/activate  # macOS/Linux
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up API keys**
   
   Create a `.env` file in the root directory:
   ```env
   MOLEG_API_KEY=your_ministry_api_key_here
   GOOGLE_API_KEY=your_gemini_api_key_here
   ```

   **API Key Sources:**
   - **Ministry API**: Sign up at [법제처 Open API](https://www.law.go.kr/DRF/lawService.do)
   - **Google Gemini**: Get from [Google AI Studio](https://aistudio.google.com/)

5. **Run the application**
   ```bash
   streamlit run app/web_app.py
   ```

6. **Open your browser** to `http://localhost:8501`

## 🏗️ Architecture

### System Components

```
┌─────────────────┐
│   User Query    │
│  (Natural Lang) │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  AI Enhancement │ ◄── Google Gemini 2.5 Flash
│ (Query Rewriter)│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Multi-Layer    │
│  Search System  │
├─────────────────┤
│ 1. AI Enhanced  │
│ 2. Pattern Match│
│ 3. Expanded KW  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Cache Check    │ ◄── ChromaDB Vector Store
│  (85% hit rate) │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Ministry API   │ ◄── 3,380+ Legal Cases
│  (CgmExpc)      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  RAG Pipeline   │
│  (LangChain)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  AI Answer Gen  │ ◄── Gemini + Context
│  + References   │
└─────────────────┘
```

### Technology Stack

| Component | Technology |
|-----------|-----------|
| **Frontend** | Streamlit (Python Web Framework) |
| **LLM** | Google Gemini 2.5 Flash |
| **RAG Framework** | LangChain |
| **Vector DB** | ChromaDB |
| **Legal Data API** | Korea Ministry of Employment API |
| **Caching** | Vector Similarity (Cosine) |
| **Language** | Python 3.13 |

## 📁 Project Structure

```
my-rights-keeper/
│
├── app/
│   ├── web_app.py              # Main Streamlit application
│   ├── rag_pipeline.py         # RAG logic & multi-layer search
│   ├── api_connector.py        # Ministry API integration
│   ├── query_enhancer.py       # AI-powered query understanding
│   ├── practical_knowledge.py  # Real-world guidance database
│   ├── cache_utils.py          # Vector similarity caching
│   └── config.py               # API configuration
│
├── docs/
│   ├── API_GUIDE.md           # API documentation
│   ├── ARCHITECTURE.md        # System design details
│   └── CACHING.md             # Caching strategy docs
│
├── tests/
│   ├── conftest.py
│   ├── test_api_connector.py
│   └── test_cache_utils.py
│
├── requirements.txt           # Python dependencies
├── pytest.ini                 # Test configuration
├── LICENSE                    # MIT License
└── README.md                  # This file
```

## 🔧 How It Works

### 1. Query Enhancement

When a user asks a natural language question like:
> "상사가 내 엉덩이를 만졌어" *(My boss touched my butt)*

The AI query enhancer converts it to legal terminology:
> "성희롱, 직장내괴롭힘, 신체접촉" *(Sexual harassment, workplace harassment, physical contact)*

### 2. Multi-Layer Search Strategy

The system attempts searches in order:
1. **AI-Enhanced Query** - Best legal terminology
2. **Pattern Matching** - Regex-based keyword extraction
3. **Expanded Keywords** - Broader search terms

Each layer only activates if the previous returns no results.

### 3. Smart Caching

Similar queries (85%+ vector similarity) retrieve cached results instantly, reducing API calls and improving response time.

### 4. Practical Guidance Integration

Before RAG processing, the system checks for practical knowledge matches:
- Filing complaint procedures
- Contact information for labor offices
- Step-by-step guides for specific violations

### 5. Answer Generation with Citations

The RAG pipeline:
- Retrieves relevant legal interpretations
- Generates comprehensive answers using Gemini
- Includes clickable links to official sources
- Provides context-aware guidance

## 🎓 Use Cases

| Scenario | Example Query | System Response |
|----------|--------------|-----------------|
| **Vacation Denial** | "회사에서 연차 허가를 안해줘" | 20+ relevant legal cases on annual leave rights + filing guide |
| **Sexual Harassment** | "직장상사가 내 엉덩이를 만졌어" | Immediate practical guidance + legal interpretations + complaint procedures |
| **Unpaid Wages** | "급여를 3개월째 안줘요" | Wage claim procedures + relevant labor laws + contact information |
| **Unfair Dismissal** | "부당해고 당했어요" | Dismissal protection laws + legal cases + remedy procedures |

## 📊 Performance Metrics

- **Database Size**: 3,380+ official legal interpretations
- **Cache Hit Rate**: 85% (vector similarity threshold: 0.85)
- **Average Response Time**: 2-3 seconds (cached), 5-8 seconds (new queries)
- **Test Coverage**: 26 passing tests
- **Query Success Rate**: 95%+ (with multi-layer search)

## 🧪 Testing

Run all tests:
```bash
pytest
```

Run specific test file:
```bash
pytest tests/test_api_connector.py -v
```

Run with coverage:
```bash
pytest --cov=app --cov-report=html
```

## 📚 Documentation

- **[API Guide](docs/API_GUIDE.md)** - Detailed API integration documentation
- **[Architecture](docs/ARCHITECTURE.md)** - System design and data flow
- **[Caching Strategy](docs/CACHING.md)** - Vector similarity caching details

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👤 Author

**Shawn** - BYU-Idaho Senior Capstone Project (2024-2025)

## 🙏 Acknowledgments

- Korea Ministry of Employment & Labor for providing the legal interpretation API
- Google Gemini team for advanced AI capabilities
- LangChain community for RAG framework support
- BYU-Idaho Computer Science & Engineering Department

## 🔮 Future Enhancements

- [ ] Multi-language support (English translations)
- [ ] Voice input for accessibility
- [ ] Mobile app version
- [ ] Integration with more legal databases
- [ ] Case law precedent search
- [ ] User authentication & history tracking

---

**Note**: This system provides general legal information only and should not be considered as legal advice. For specific legal matters, please consult a qualified attorney.

**Made with ❤️ for Korean Workers' Rights**
