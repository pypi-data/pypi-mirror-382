# NLP Suite 🚀

A comprehensive Python package that provides easy access to all major NLP libraries through optional extras. Install only what you need!

[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![PyPI](https://img.shields.io/pypi/v/nlp-suite.svg)](https://pypi.org/project/nlp-suite/)

## 📦 Installation

### Basic Installation (Essentials Only)
```bash
pip install nlp-suite
```
This installs only the core essentials: `numpy`, `pandas`, `tqdm`

### Install with Extras
```bash
# Core NLP tools
pip install nlp-suite[core]

# Deep learning frameworks
pip install nlp-suite[deep-learning]

# Everything at once
pip install nlp-suite[all]

# Combine multiple extras
pip install nlp-suite[core,preprocessing,visualization]
```

## 🎯 Available Extras

| Extra | Description | Key Packages |
|-------|-------------|--------------|
| `core` | Essential NLP libraries | nltk, spacy, textblob, stanza, gensim |
| `deep-learning` | Modern AI/ML frameworks | transformers, sentence-transformers, torchtext |
| `preprocessing` | Text cleaning tools | regex, beautifulsoup4, ftfy, clean-text |
| `vectorization` | Text vectorization | scikit-learn, fasttext |
| `topic-modeling` | Topic analysis | bertopic, pyLDAvis |
| `sentiment` | Sentiment analysis | vaderSentiment |
| `translation` | Translation tools | deep-translator, translate |
| `speech` | Speech processing | SpeechRecognition, gTTS, pyttsx3 |
| `visualization` | Data visualization | wordcloud, matplotlib, seaborn |
| `serving` | Model deployment | fastapi, flask, gradio, streamlit |
| `evaluation` | Model evaluation | seqeval, evaluate |

### 🎁 Convenience Bundles
```bash
pip install nlp-suite[basic]        # core + preprocessing + sentiment
pip install nlp-suite[advanced]     # deep-learning + topic-modeling + evaluation
pip install nlp-suite[complete]     # most popular packages
pip install nlp-suite[all]          # everything!
```

## 🚀 Quick Start

```python
import nlp_suite

# See what's available
nlp_suite.show_available_extras()

# Check what's installed
nlp_suite.check_installed()

# Get package info
info = nlp_suite.get_package_info()
print(f"NLP Suite v{info['version']} with {info['total_packages']} packages available")
```

## 💡 Usage Examples

### Text Processing with Core Tools
```python
# Install: pip install nlp-suite[core]
import nltk
import spacy
from textblob import TextBlob

# Use any of the installed libraries
blob = TextBlob("NLP Suite makes it easy!")
print(blob.sentiment)
```

### Deep Learning NLP
```python
# Install: pip install nlp-suite[deep-learning]
from transformers import pipeline

classifier = pipeline("sentiment-analysis")
result = classifier("I love NLP Suite!")
print(result)
```

### Visualization
```python
# Install: pip install nlp-suite[visualization]
from wordcloud import WordCloud
import matplotlib.pyplot as plt

text = "NLP Suite provides easy access to all major NLP libraries"
wordcloud = WordCloud().generate(text)
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis('off')
plt.show()
```

## 🛠️ Development

```bash
# Clone the repository
git clone https://github.com/sunilkumarpradhan/nlp-suite.git
cd nlp-suite

# Install with Poetry
poetry install

# Run tests
poetry run pytest

# Run tests with coverage
poetry run pytest --cov=nlp_suite
```

## 📋 Requirements

- Python 3.9+
- Individual package requirements vary by extra

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

This package is a convenience wrapper around amazing libraries created by:
- The NLTK team
- The spaCy team  
- Hugging Face
- And many other open-source contributors

## 📞 Support

- 📧 Email: sunilkumarweb47@gmail.com
- 🐛 Issues: [GitHub Issues](https://github.com/sunilkumarpradhan/nlp-suite/issues)
- 📖 Documentation: [Coming Soon]

---

**Made with ❤️ for the NLP community**