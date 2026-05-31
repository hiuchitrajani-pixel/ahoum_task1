 # Ahoum AI Q1 - Conversation Evaluation Platform

A comprehensive platform for generating, evaluating, and analyzing AI conversations across diverse emotional and contextual scenarios. This project demonstrates the capability to assess how AI models handle complex human interactions including distress, empathy, technical discussions, and edge cases.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Usage](#usage)
- [Conversation Categories](#conversation-categories)
- [Technologies](#technologies)
- [Data Files](#data-files)
- [Contributing](#contributing)
- [License](#license)

---

## 🎯 Overview

The Ahoum AI Q1 project is designed to evaluate and analyze AI conversational abilities across multiple dimensions:

- **Emotional Intelligence**: How AI responds to distress, empathy, grief, and vulnerability
- **Communication Styles**: Handling arrogance, sarcasm, hostility, and friendliness
- **Practical Scenarios**: Real-world decision-making and problem-solving situations
- **Technical Proficiency**: Explaining complex concepts and debugging code
- **Ethical Reasoning**: Navigating misinformation, ethics, and bias
- **Special Cases**: Creative thinking, curiosity, debate, and validation

This platform provides tools to generate, collect, and evaluate these conversations systematically.

---

## ✨ Features

- **Multi-Category Conversation Generation**: Create conversations across 16+ different categories
- **Interactive Streamlit UI**: User-friendly web interface for evaluation and analysis
- **Extensible Framework**: Easy to add new conversation types and evaluation criteria
- **Data Processing Pipeline**: Clean, preprocess, and analyze conversation data
- **Scalable Architecture**: Supports batch processing of multiple conversations
- **Detailed Facet Analysis**: Track and evaluate conversations across multiple dimensions

---

## 📁 Project Structure

```
ahoum_task1/
├── README.md                          # Project documentation
├── requirements.txt                   # Python dependencies
│
├── conversations/                     # JSON conversation files
│   ├── conv_distress_01.json
│   ├── conv_distress_02.json
│   ├── conv_empathy_01.json
│   ├── conv_hostile_01.json
│   ├── conv_hostile_02.json
│   ├── conv_arrogant_01.json
│   ├── conv_creative_01.json
│   ├── conv_curious_01.json
│   ├── conv_debate_01.json
│   ├── conv_decision_01.json
│   ├── conv_ethics_01.json
│   ├── conv_friendly_01.json
│   ├── conv_grief_01.json
│   ├── conv_misinfo_01.json
│   ├── conv_sarcasm_01.json
│   ├── conv_scenario_01-30.json       # 30 comprehensive scenario conversations
│   ├── conv_spiritual_01.json
│   ├── conv_technical_01-02.json
│   ├── conv_validation_01.json
│   └── conv_vulnerable_01.json
│
├── data/                              # Data files
│   ├── facets_raw.csv                 # Raw evaluation facets
│   └── facets_cleaned.csv             # Cleaned and processed facets
│
├── src/                               # Source code
│   ├── generate_conversations.py      # Generate new conversations
│   ├── evaluator.py                   # Evaluation engine
│   ├── prompt_builder.py              # Build structured prompts
│   ├── preprocess.py                  # Data preprocessing utilities
│
├── ui/                                # User interface
│   └── app.py                         # Streamlit web application
│
└── dockerfile/                        # Docker configuration
```

---

## 🔧 Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Virtual environment (recommended)

### Setup Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/hiuchitrajani-pixel/ahoum_task1.git
   cd ahoum_task1
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv .venv
   
   # On Windows
   .\.venv\Scripts\activate
   
   # On macOS/Linux
   source .venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

### Dependency Details

| Package | Version | Purpose |
|---------|---------|---------|
| pandas | ≥2.0.0 | Data manipulation and analysis |
| requests | ≥2.31.0 | HTTP requests for API calls |
| streamlit | ≥1.35.0 | Web application framework |

---

## 🚀 Usage

### Running the Web Interface

Start the interactive Streamlit application:

```bash
# Navigate to the ui directory
cd ui

# Run the Streamlit app
streamlit run app.py
```

The app will open in your default browser at `http://localhost:8501`

**Features:**
- Browse conversations by category
- Evaluate AI responses on multiple criteria
- View analytics and statistics
- Export evaluation results
- Dark/Light theme support

### Running Analysis Scripts

#### Generate Conversations
```bash
python src/generate_conversations.py
```
Creates new conversation samples across all categories.

#### Evaluate Conversations
```bash
python src/evaluator.py
```
Runs evaluation metrics on existing conversations.

#### Preprocess Data
```bash
python src/preprocess.py
```
Cleans and prepares raw data for analysis.

#### Build Prompts
```bash
python src/prompt_builder.py
```
Constructs structured prompts for conversation generation.

---

## 💬 Conversation Categories

The platform includes **45+ conversation samples** across the following categories:

### Emotional & Psychological (8 categories)
| Category | Files | Focus |
|----------|-------|-------|
| **Distress** | 2 | Handling suicidal ideation and severe emotional pain |
| **Empathy** | 1 | Compassionate responses to loss and grief |
| **Grief** | 1 | Deep emotional support for bereavement |
| **Vulnerable** | 1 | Supporting moments of vulnerability |
| **Hostile** | 2 | De-escalating aggressive or hostile interactions |
| **Friendly** | 1 | Maintaining warm, supportive relationships |
| **Arrogant** | 1 | Responding to overconfident or dismissive users |

### Cognitive & Reasoning (7 categories)
| Category | Files | Focus |
|----------|-------|-------|
| **Technical** | 2 | Explaining complex ML/CS concepts and debugging |
| **Decision** | 1 | Guiding decision-making processes |
| **Debate** | 1 | Facilitating balanced argumentation |
| **Ethics** | 1 | Navigating ethical dilemmas |
| **Misinfo** | 1 | Correcting misinformation tactfully |
| **Spiritual** | 1 | Discussing philosophical and spiritual topics |
| **Creative** | 1 | Encouraging creative expression |

### Practical & Scenario-Based (3 categories)
| Category | Files | Focus |
|----------|-------|-------|
| **Scenarios** | 30 | 30 diverse real-world situations |
| **Curious** | 1 | Answering curious and exploratory questions |
| **Validation** | 1 | Providing emotional validation |

### Advanced Communication (1 category)
| Category | Files | Focus |
|----------|-------|-------|
| **Sarcasm** | 1 | Detecting and responding to sarcasm |

---

## 💾 Data Files

### facets_raw.csv
- **Purpose**: Stores raw evaluation data
- **Contents**: Unprocessed evaluation metrics and scores
- **Use Case**: Source data for analysis and cleaning

### facets_cleaned.csv
- **Purpose**: Cleaned and validated evaluation data
- **Contents**: Processed metrics ready for analysis
- **Use Case**: Data visualization and statistical analysis

**Typical Facets Evaluated:**
- Response accuracy
- Emotional appropriateness
- Clarity and coherence
- Technical correctness
- User satisfaction
- Context awareness

---

## 🛠️ Technologies & Stack

### Backend & Data
- **Python 3.8+**: Core programming language
- **Pandas**: Data manipulation and CSV processing
- **Requests**: API communication

### Frontend & UI
- **Streamlit**: Interactive web framework
- **HTML/CSS**: Custom styling for dark/light themes

### Architecture
- **Modular Design**: Separate concerns (generation, evaluation, preprocessing)
- **Scalable Pipeline**: Batch processing capability
- **JSON-Based Storage**: Easy data interchange and versioning

### Deployment
- **Docker**: Containerized deployment option
- **Git**: Version control and collaborative development

---

## 📊 Analysis Workflow

```
1. Generation
   └─> generate_conversations.py
       └─> Creates new conversation samples

2. Evaluation  
   └─> evaluator.py
       └─> Scores and analyzes conversations

3. Preprocessing
   └─> preprocess.py
       └─> Cleans and prepares data

4. Visualization
   └─> ui/app.py
       └─> Interactive dashboard and reports
```

---

## 🤝 Contributing

We welcome contributions to improve this project!

### Guidelines
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Make your changes and commit them (`git commit -m 'Add AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Areas for Contribution
- Additional conversation categories
- Enhanced evaluation metrics
- UI/UX improvements
- Performance optimizations
- Documentation updates
- Language support

---

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 👨‍💼 Project Information

**Project**: Ahoum AI Q1  
**Repository**: [ahoum_task1](https://github.com/hiuchitrajani-pixel/ahoum_task1)  
**Status**: Active Development  
**Last Updated**: May 31, 2026

---

## 🔗 Quick Links

- [GitHub Repository](https://github.com/hiuchitrajani-pixel/ahoum_task1)
- [Issue Tracker](https://github.com/hiuchitrajani-pixel/ahoum_task1/issues)
- [Conversations Directory](./conversations/)
- [Source Code](./src/)

---

## ❓ FAQ

**Q: How do I add a new conversation category?**  
A: Create a new JSON file in the `conversations/` directory following the existing format, then update the generator to include the new category.

**Q: Can I use this with my own AI model?**  
A: Yes! The framework is model-agnostic. You can modify `prompt_builder.py` to integrate with your preferred AI service.

**Q: Is Docker support required?**  
A: No, it's optional. You can run the project directly with Python and Streamlit.

**Q: How are conversations evaluated?**  
A: The `evaluator.py` script runs multiple metrics including coherence, appropriateness, accuracy, and user satisfaction.

---

## 📞 Support

For questions, issues, or suggestions, please open an issue on GitHub or contact the project maintainers.

**Happy Evaluating! 🧠💬**

