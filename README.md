# 📝 L2 Writing Style Analyzer

A lightweight Streamlit web application for analyzing stylistic differences between original L2 (Second Language) writing and AI-edited versions. Designed specifically for English Language Teaching (ELT) professionals, researchers, and students.

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](YOUR_STREAMLIT_CLOUD_URL)

## 🎯 Purpose

This tool helps educators and researchers:
- **Identify AI influence** in student writing through quantitative metrics
- **Compare stylistic changes** between original and AI-edited texts
- **Teach writing awareness** by highlighting formulaic AI patterns
- **Generate reports** for academic analysis or feedback

## ✨ Features

### Dual Text Input
- Two side-by-side text areas for original and AI-edited text
- Live word count display for each field
- Real-time processing as you type

### Automated Metrics Calculation

| Metric | Description | Interpretation |
|--------|-------------|----------------|
| **Burstiness Index** | Sentence length variation (std ÷ mean) | < 1.0 = AI-like uniformity; > 1.5 = human-like variation |
| **AI-ism Frequency** | Formulaic LLM markers per 100 words | Higher = more formulaic/AI-influenced |
| **Lexical Diversity (MTLD)** | Vocabulary richness score | Higher = more diverse word usage |
| **Type-Token Ratio (TTR)** | Unique words ÷ total words | Supplementary diversity measure |
| **Syntactic Complexity** | Avg sentence length & subordination ratio | AI tends toward longer, complex sentences |

### Comparison Dashboard
- Side-by-side text visualization
- Highlighted AI-ism markers in the edited version
- Bar charts comparing all metrics
- Color-coded interpretation indicators

### PDF Export
- Comprehensive report generation
- All metrics with comparison tables
- Detected AI-ism breakdown
- Full text preservation
- Interpretation guide included

## 🚀 Quick Start

### Online Access
Visit the deployed app: **[Streamlit Cloud URL]**

### Local Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/l2-writing-analyzer.git
   cd l2-writing-analyzer
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the app**
   ```bash
   streamlit run app.py
   ```

4. **Open in browser**
   Navigate to `http://localhost:8501`

## 📊 Understanding the Metrics

### Burstiness Index
Human writers naturally vary their sentence lengths—mixing short punchy statements with longer, complex ones. AI tends to produce more uniform sentence lengths. This metric captures that difference:

- **< 1.0**: Highly uniform, AI-like pattern
- **1.0 - 1.5**: Moderate variation
- **> 1.5**: High variation, more human-like

### AI-ism Frequency
We've compiled a comprehensive list of common AI writing patterns including:

**Transition markers**: *furthermore, moreover, consequently, therefore*

**Formal hedging**: *it is important to note, plays a crucial role, can be considered*

**Generic intensifiers**: *significantly, substantially, notably, remarkably*

**List structures**: *firstly, secondly, lastly, in conclusion*

The frequency is normalized per 100 words for fair comparison across different text lengths.

### Lexical Diversity (MTLD)
MTLD (Measure of Textual Lexical Diversity) is a sophisticated measure that accounts for text length. Unlike simple TTR which decreases with longer texts, MTLD remains stable.

- **Higher scores** indicate richer, more varied vocabulary
- **Lower scores** suggest repetitive word usage

### Syntactic Complexity
Two measures capture syntactic sophistication:

1. **Average Sentence Length**: Words per sentence
2. **Subordination Ratio**: Subordinate clauses per sentence

AI often produces longer sentences with more complex subordination patterns.

## 📱 Mobile Responsive

The app is fully responsive and works on:
- 💻 Desktop computers
- 📱 Tablets and smartphones
- 🖥️ Projectors for classroom use

## 📖 For ELT Users (Non-Technical)

### How to Use This Tool

1. **Paste your texts**: Enter the original student writing in the left box, and the AI-edited version in the right box

2. **Review the metrics**: Look at the four key metric cards at the top
   - Green indicators suggest human-like characteristics
   - Red indicators suggest AI-like patterns

3. **Compare visually**: Scroll down to see bar charts comparing both versions

4. **Check highlighted AI-isms**: The AI-edited text shows yellow highlights where formulaic patterns were detected

5. **Download the report**: Click the blue download button to save a PDF for your records

### Teaching Applications

**Writing Awareness**: Have students analyze their own writing before and after using AI tools

**Peer Review**: Compare original essays with AI-suggested improvements

**Research**: Collect data on AI influence in L2 writing development

**Feedback**: Include metric comparisons in writing conference discussions

## 🛠️ Technical Details

### Built With
- **Python 3.8+**
- **Streamlit** - Web app framework
- **Matplotlib** - Data visualization
- **NumPy** - Numerical computations
- **FPDF** - PDF generation

### AI-ism Detection
The app detects 80+ formulaic patterns commonly found in LLM output, organized into categories:
- Transition words and phrases
- Formal/academic hedging language
- Generic intensifiers
- Passive voice constructions
- List indicators
- Neutral/hedged conclusions

### Lexical Diversity Algorithm
Implements MTLD (McCarthy & Jarvis, 2010) with forward-backward averaging for robust measurement.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to:
- Report bugs or suggest features via Issues
- Submit pull requests for improvements
- Expand the AI-ism marker list
- Add new linguistic metrics

## 📚 References

- McCarthy, P. M., & Jarvis, S. (2010). MTLD, voc-D, and HD-D: A validation study of sophisticated approaches to lexical diversity assessment. *Behavior Research Methods*, 42(2), 381-392.
- OpenAI. (2023). GPT-4 Technical Report. *arXiv preprint arXiv:2303.08774*.

## 📧 Contact

For questions or feedback, please open an issue on GitHub.

---

**Made for the ELT community** 🌍
