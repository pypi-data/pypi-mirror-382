"""
NLP Suite - A comprehensive collection of NLP tools and libraries.

This package provides easy access to major NLP libraries through optional extras:

Installation Examples:
    pip install nlp-suite                    # Core essentials only
    pip install nlp-suite[core]             # Basic NLP tools
    pip install nlp-suite[deep-learning]    # AI/ML libraries  
    pip install nlp-suite[all]              # Everything

Usage Examples:
    import nlp_suite
    nlp_suite.show_available_extras()       # See what's available
    nlp_suite.check_installed()             # See what's installed
"""

# Package metadata
__version__ = "0.1.0"
__author__ = "Sunil Kumar Pradhan"
__email__ = "sunilkumarweb47@gmail.com"
__license__ = "MIT"
__description__ = "A comprehensive NLP toolkit combining all major Python NLP libraries"

# Define what gets imported with "from nlp_suite import *"
__all__ = [
    "__version__",
    "show_available_extras", 
    "check_installed",
    "get_package_info",
    "AVAILABLE_EXTRAS"
]

# Available extras mapping
AVAILABLE_EXTRAS = {
    "core": {
        "packages": ["nltk", "spacy", "textblob", "stanza", "gensim"],
        "description": "Essential NLP libraries for text processing"
    },
    "deep-learning": {
        "packages": ["transformers", "sentence-transformers", "torchtext", "tensorflow-text"],
        "description": "Modern deep learning NLP frameworks"
    },
    "preprocessing": {
        "packages": ["regex", "beautifulsoup4", "ftfy", "clean-text"],
        "description": "Text cleaning and preprocessing tools"
    },
    "vectorization": {
        "packages": ["scikit-learn", "fasttext"],
        "description": "Text vectorization and embedding tools"
    },
    "topic-modeling": {
        "packages": ["bertopic", "pyLDAvis"],
        "description": "Topic modeling and visualization"
    },
    "sentiment": {
        "packages": ["vaderSentiment"],
        "description": "Sentiment analysis tools"
    },
    "translation": {
        "packages": ["deep-translator", "translate"],
        "description": "Translation and multilingual support"
    },
    "speech": {
        "packages": ["SpeechRecognition", "gTTS", "pyttsx3"],
        "description": "Speech recognition and text-to-speech"
    },
    "visualization": {
        "packages": ["wordcloud", "matplotlib", "seaborn"],
        "description": "Text and data visualization tools"
    },
    "serving": {
        "packages": ["fastapi", "flask", "onnxruntime", "gradio", "streamlit"],
        "description": "Model serving and web deployment"
    },
    "evaluation": {
        "packages": ["seqeval", "evaluate"],
        "description": "Model evaluation and metrics"
    }
}


def show_available_extras():
    """
    Display all available extras and their packages.
    
    This shows users what optional dependencies they can install.
    """
    print("🚀 NLP Suite - Available Installation Options")
    print("=" * 50)
    
    # Show core installation
    print("\n📦 Basic Installation:")
    print("   pip install nlp-suite")
    print("   → Installs: numpy, pandas, tqdm (essentials only)")
    
    print("\n🎯 Optional Extras:")
    for extra_name, extra_info in AVAILABLE_EXTRAS.items():
        packages = extra_info["packages"]
        description = extra_info["description"]
        
        print(f"\n   {extra_name}:")
        print(f"   pip install nlp-suite[{extra_name}]")
        print(f"   → {description}")
        print(f"   → Packages: {', '.join(packages[:3])}{'...' if len(packages) > 3 else ''}")
    
    # Show convenience options
    print(f"\n🎁 Convenience Options:")
    print(f"   pip install nlp-suite[basic]        → Core + preprocessing + sentiment")
    print(f"   pip install nlp-suite[advanced]     → Deep learning + topic modeling + evaluation")
    print(f"   pip install nlp-suite[complete]     → Most popular packages")
    print(f"   pip install nlp-suite[all]          → Everything!")
    
    print(f"\n💡 Combine multiple extras:")
    print(f"   pip install nlp-suite[core,deep-learning,visualization]")


def check_installed():
    """
    Check which optional packages are actually installed.
    
    Returns:
        dict: Mapping of extra names to lists of installed packages
    """
    import importlib.util
    
    print("🔍 Checking Installed Packages...")
    print("=" * 40)
    
    installed_by_extra = {}
    total_available = 0
    total_installed = 0
    
    for extra_name, extra_info in AVAILABLE_EXTRAS.items():
        packages = extra_info["packages"]
        installed_packages = []
        
        for package in packages:
            total_available += 1
            # Handle package name variations
            import_name = _get_import_name(package)
            
            spec = importlib.util.find_spec(import_name)
            if spec is not None:
                installed_packages.append(package)
                total_installed += 1
        
        installed_by_extra[extra_name] = installed_packages
        
        # Print status
        status = "✅" if installed_packages else "❌"
        count = f"({len(installed_packages)}/{len(packages)})"
        print(f"{status} {extra_name:<15} {count:<8} {installed_packages[:2] if installed_packages else 'None installed'}")
    
    print(f"\n📊 Summary: {total_installed}/{total_available} packages installed")
    
    if total_installed == 0:
        print("\n💡 Tip: Install extras with 'pip install nlp-suite[core]'")
    elif total_installed < total_available:
        print(f"\n💡 Tip: Install more with 'pip install nlp-suite[all]'")
    else:
        print(f"\n🎉 All packages installed! You're ready for NLP!")
    
    return installed_by_extra


def get_package_info():
    """
    Get basic information about the nlp-suite package.
    
    Returns:
        dict: Package metadata
    """
    return {
        "name": "nlp-suite",
        "version": __version__,
        "author": __author__,
        "email": __email__,
        "license": __license__,
        "description": __description__,
        "total_extras": len(AVAILABLE_EXTRAS),
        "total_packages": sum(len(extra["packages"]) for extra in AVAILABLE_EXTRAS.values())
    }


def _get_import_name(package_name):
    """
    Convert package name to import name.
    
    Some packages have different names for pip install vs import.
    """
    name_mapping = {
        "SpeechRecognition": "speech_recognition",
        "beautifulsoup4": "bs4",
        "scikit-learn": "sklearn",
        "deep-translator": "deep_translator",
        "clean-text": "cleantext",
        "sentence-transformers": "sentence_transformers",
        "tensorflow-text": "tensorflow_text",
        "pyLDAvis": "pyLDAvis"  # Keep exact case
    }
    
    return name_mapping.get(package_name, package_name.lower().replace("-", "_"))


# Convenience imports - only import what's always available
try:
    import numpy as np
    import pandas as pd
    import tqdm
    
    # Make them available at package level
    numpy = np
    pandas = pd
    
except ImportError:
    # If not available, that's fine - they're optional
    numpy = None
    pandas = None
    tqdm = None


# Package initialization message (optional - remove if you don't want it)
def _show_welcome_message():
    """Show a brief welcome message when package is imported."""
    try:
        installed = check_installed()
        total_installed = sum(len(packages) for packages in installed.values())
        
        if total_installed == 0:
            print("📦 NLP Suite loaded! Run nlp_suite.show_available_extras() to see installation options.")
        else:
            print(f"🚀 NLP Suite loaded with {total_installed} packages! Run nlp_suite.check_installed() for details.")
    except:
        # If anything goes wrong, just show basic message
        print("📦 NLP Suite loaded! Run nlp_suite.show_available_extras() for help.")


# Uncomment the next line if you want a welcome message when package is imported
# _show_welcome_message()

# Version check function
def _check_python_version():
    """Ensure compatible Python version."""
    import sys
    if sys.version_info < (3, 8):
        raise RuntimeError("NLP Suite requires Python 3.8 or higher")

# Run version check
_check_python_version()