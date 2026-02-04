"""
L2 Writing Style Analyzer
A Streamlit app for analyzing stylistic differences between original L2 writing and AI-edited versions.
"""

import streamlit as st
import re
import math
from collections import Counter
import matplotlib.pyplot as plt
import numpy as np
from fpdf import FPDF
import base64
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="L2 Writing Style Analyzer",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 1rem;
        border-left: 4px solid #1f77b4;
    }
    .ai-ism-highlight {
        background-color: #ffeb3b;
        padding: 2px 4px;
        border-radius: 3px;
    }
    .word-count {
        font-size: 0.85rem;
        color: #666;
        text-align: right;
    }
    .stTextArea textarea {
        font-family: 'Georgia', serif;
        font-size: 14px;
        line-height: 1.6;
    }
</style>
""", unsafe_allow_html=True)

# AI-ism markers list
AI_ISMS = [
    # Transition words and phrases
    "furthermore", "moreover", "additionally", "consequently", "therefore",
    "thus", "hence", "nonetheless", "nevertheless", "however",
    "in conclusion", "to summarize", "in summary", "overall",
    "on the other hand", "in contrast", "conversely", "similarly",
    "for instance", "for example", "specifically", "particularly",
    "in addition", "as a result", "due to", "in order to",
    
    # Formal/Academic phrases
    "it is important to note", "it should be noted", "it is worth noting",
    "plays a crucial role", "plays an important role", "essential aspect",
    "significant impact", "key factor", "critical component",
    "in the context of", "with respect to", "in terms of",
    "can be seen as", "can be considered", "it can be argued",
    "this suggests that", "this indicates that", "this demonstrates that",
    
    # Hedging language
    "may", "might", "could", "would", "should",
    "potentially", "likely", "probably", "arguably",
    "to some extent", "in general", "generally speaking",
    "it seems that", "it appears that",
    
    # Repetitive structures
    "not only", "but also", "both", "and",
    "whether", "or not", "if and only if",
    
    # Generic intensifiers
    "significantly", "substantially", "considerably", "notably",
    "remarkably", "particularly", "especially", "extremely",
    
    # Passive voice indicators
    "is considered", "are considered", "was considered", "were considered",
    "is regarded", "are regarded", "is seen as", "are seen as",
    "has been", "have been", "had been",
    
    # List indicators
    "firstly", "secondly", "thirdly", "lastly", "finally",
    "first", "second", "third", "last", "in conclusion",
    
    # Neutral/hedged conclusions
    "in light of", "taking into account", "considering the",
    "based on the above", "as mentioned earlier", "as discussed above"
]


def count_words(text):
    """Count words in text."""
    if not text or not text.strip():
        return 0
    words = re.findall(r'\b\w+\b', text.lower())
    return len(words)


def get_sentences(text):
    """Split text into sentences."""
    if not text or not text.strip():
        return []
    # Simple sentence splitting
    sentences = re.split(r'[.!?]+', text)
    return [s.strip() for s in sentences if s.strip()]


def calculate_burstiness(text):
    """
    Calculate burstiness index: sentence length standard deviation / mean.
    < 1.0 = AI-like, > 1.5 = human-like
    """
    sentences = get_sentences(text)
    if len(sentences) < 2:
        return 0
    
    sentence_lengths = [len(re.findall(r'\b\w+\b', s)) for s in sentences]
    mean_length = np.mean(sentence_lengths)
    std_length = np.std(sentence_lengths, ddof=1) if len(sentence_lengths) > 1 else 0
    
    if mean_length == 0:
        return 0
    
    return std_length / mean_length


def count_ai_isms(text):
    """Count AI-ism markers per 100 words."""
    if not text or not text.strip():
        return 0
    
    text_lower = text.lower()
    word_count = count_words(text)
    
    if word_count == 0:
        return 0
    
    ai_ism_count = 0
    found_ai_isms = []
    
    for ai_ism in AI_ISMS:
        count = len(re.findall(r'\b' + re.escape(ai_ism) + r'\b', text_lower))
        if count > 0:
            ai_ism_count += count
            found_ai_isms.append((ai_ism, count))
    
    # Per 100 words
    frequency = (ai_ism_count / word_count) * 100
    return frequency, found_ai_isms


def calculate_lexical_diversity(text):
    """
    Calculate lexical diversity using MTLD (Measure of Textual Lexical Diversity).
    Falls back to TTR if text is too short.
    """
    if not text or not text.strip():
        return 0, 0
    
    words = re.findall(r'\b\w+\b', text.lower())
    word_count = len(words)
    
    if word_count == 0:
        return 0, 0
    
    unique_words = set(words)
    type_count = len(unique_words)
    
    # TTR (Type-Token Ratio)
    ttr = type_count / word_count if word_count > 0 else 0
    
    # MTLD approximation
    mtld = calculate_mtld(words)
    
    return mtld, ttr


def calculate_mtld(words, ttr_threshold=0.72):
    """
    Calculate MTLD (Measure of Textual Lexical Diversity).
    This is an approximation of the full MTLD algorithm.
    """
    if len(words) < 10:
        return len(words) * 10  # Approximation for short texts
    
    # Forward MTLD
    forward_count = 0
    types = set()
    tokens = 0
    
    for word in words:
        types.add(word)
        tokens += 1
        ttr = len(types) / tokens
        if ttr < ttr_threshold:
            forward_count += 1
            types = set()
            tokens = 0
    
    # Add partial factor
    if tokens > 0:
        forward_count += (1 - (len(types) / tokens) / ttr_threshold)
    
    # Backward MTLD
    backward_count = 0
    types = set()
    tokens = 0
    
    for word in reversed(words):
        types.add(word)
        tokens += 1
        ttr = len(types) / tokens
        if ttr < ttr_threshold:
            backward_count += 1
            types = set()
            tokens = 0
    
    if tokens > 0:
        backward_count += (1 - (len(types) / tokens) / ttr_threshold)
    
    # Average MTLD
    avg_count = (forward_count + backward_count) / 2
    if avg_count == 0:
        return len(words) * 10
    
    mtld = len(words) / avg_count
    return mtld


def calculate_syntactic_complexity(text):
    """
    Calculate syntactic complexity metrics.
    Returns average sentence length and subordination ratio.
    """
    if not text or not text.strip():
        return 0, 0
    
    sentences = get_sentences(text)
    if not sentences:
        return 0, 0
    
    # Average sentence length
    total_words = count_words(text)
    avg_sentence_length = total_words / len(sentences)
    
    # Subordination ratio (clauses per sentence)
    # Count subordinating conjunctions and relative pronouns
    subordinators = [
        'because', 'since', 'as', 'although', 'though', 'while', 'whereas',
        'if', 'unless', 'until', 'before', 'after', 'when', 'whenever',
        'that', 'which', 'who', 'whom', 'whose', 'where', 'why'
    ]
    
    text_lower = text.lower()
    subordinator_count = sum(len(re.findall(r'\b' + re.escape(sub) + r'\b', text_lower)) 
                            for sub in subordinators)
    
    subordination_ratio = subordinator_count / len(sentences) if sentences else 0
    
    return avg_sentence_length, subordination_ratio


def highlight_ai_isms(text):
    """Highlight AI-ism markers in text."""
    if not text:
        return text
    
    text_lower = text.lower()
    highlighted = text
    
    # Sort by length (longest first) to avoid partial replacements
    sorted_ai_isms = sorted(AI_ISMS, key=len, reverse=True)
    
    for ai_ism in sorted_ai_isms:
        pattern = re.compile(r'\b(' + re.escape(ai_ism) + r')\b', re.IGNORECASE)
        highlighted = pattern.sub(r'<span class="ai-ism-highlight">\1</span>', highlighted)
    
    return highlighted


def create_comparison_chart(metrics_orig, metrics_edited):
    """Create bar chart comparing metrics."""
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    fig.suptitle('Metrics Comparison: Original vs. AI-Edited', fontsize=16, fontweight='bold')
    
    categories = ['Original', 'AI-Edited']
    colors = ['#1f77b4', '#ff7f0e']
    
    # Burstiness Index
    ax1 = axes[0, 0]
    values = [metrics_orig['burstiness'], metrics_edited['burstiness']]
    bars = ax1.bar(categories, values, color=colors, edgecolor='black', linewidth=1.2)
    ax1.set_ylabel('Burstiness Index')
    ax1.set_title('Burstiness Index (Higher = More Human-like)')
    ax1.axhline(y=1.0, color='r', linestyle='--', alpha=0.7, label='AI-like threshold')
    ax1.axhline(y=1.5, color='g', linestyle='--', alpha=0.7, label='Human-like threshold')
    ax1.legend(fontsize=8)
    ax1.set_ylim(0, max(values + [2]) * 1.1)
    for bar, val in zip(bars, values):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05, 
                f'{val:.2f}', ha='center', va='bottom', fontweight='bold')
    
    # AI-ism Frequency
    ax2 = axes[0, 1]
    values = [metrics_orig['ai_ism_freq'], metrics_edited['ai_ism_freq']]
    bars = ax2.bar(categories, values, color=colors, edgecolor='black', linewidth=1.2)
    ax2.set_ylabel('AI-isms per 100 words')
    ax2.set_title('AI-ism Frequency (Lower = Less Formulaic)')
    ax2.set_ylim(0, max(values + [5]) * 1.1)
    for bar, val in zip(bars, values):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1, 
                f'{val:.2f}', ha='center', va='bottom', fontweight='bold')
    
    # Lexical Diversity (MTLD)
    ax3 = axes[1, 0]
    values = [metrics_orig['mtld'], metrics_edited['mtld']]
    bars = ax3.bar(categories, values, color=colors, edgecolor='black', linewidth=1.2)
    ax3.set_ylabel('MTLD Score')
    ax3.set_title('Lexical Diversity (Higher = More Diverse)')
    ax3.set_ylim(0, max(values + [50]) * 1.1)
    for bar, val in zip(bars, values):
        ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, 
                f'{val:.1f}', ha='center', va='bottom', fontweight='bold')
    
    # Average Sentence Length
    ax4 = axes[1, 1]
    values = [metrics_orig['avg_sentence_length'], metrics_edited['avg_sentence_length']]
    bars = ax4.bar(categories, values, color=colors, edgecolor='black', linewidth=1.2)
    ax4.set_ylabel('Words per sentence')
    ax4.set_title('Average Sentence Length')
    ax4.set_ylim(0, max(values + [20]) * 1.1)
    for bar, val in zip(bars, values):
        ax4.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3, 
                f'{val:.1f}', ha='center', va='bottom', fontweight='bold')
    
    plt.tight_layout()
    return fig


def create_pdf_report(original_text, edited_text, metrics_orig, metrics_edited, found_ai_isms_orig, found_ai_isms_edited):
    """Generate PDF report with all metrics and comparison."""
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Title page
    pdf.add_page()
    pdf.set_font('Arial', 'B', 20)
    pdf.cell(0, 20, 'L2 Writing Style Analysis Report', ln=True, align='C')
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 10, f'Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M")}', ln=True, align='C')
    pdf.ln(10)
    
    # Summary section
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'Executive Summary', ln=True)
    pdf.set_font('Arial', '', 11)
    
    word_count_orig = count_words(original_text)
    word_count_edited = count_words(edited_text)
    
    pdf.multi_cell(0, 8, 
        f'This report analyzes stylistic differences between original L2 writing and its AI-edited version.\n\n'
        f'Original Text: {word_count_orig} words\n'
        f'AI-Edited Text: {word_count_edited} words\n\n'
        f'Key Findings:\n'
        f'- Burstiness Index changed from {metrics_orig["burstiness"]:.2f} to {metrics_edited["burstiness"]:.2f}\n'
        f'- AI-ism frequency: {metrics_orig["ai_ism_freq"]:.2f} → {metrics_edited["ai_ism_freq"]:.2f} per 100 words\n'
        f'- Lexical diversity (MTLD): {metrics_orig["mtld"]:.1f} → {metrics_edited["mtld"]:.1f}\n'
    )
    pdf.ln(5)
    
    # Detailed metrics
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'Detailed Metrics Comparison', ln=True)
    pdf.ln(5)
    
    # Create metrics table
    pdf.set_font('Arial', 'B', 11)
    pdf.cell(80, 8, 'Metric', 1)
    pdf.cell(50, 8, 'Original', 1, align='C')
    pdf.cell(50, 8, 'AI-Edited', 1, align='C')
    pdf.ln()
    
    metrics_data = [
        ('Word Count', f'{word_count_orig}', f'{word_count_edited}'),
        ('Sentence Count', f'{metrics_orig["sentence_count"]}', f'{metrics_edited["sentence_count"]}'),
        ('Burstiness Index', f'{metrics_orig["burstiness"]:.2f}', f'{metrics_edited["burstiness"]:.2f}'),
        ('AI-ism Frequency (per 100 words)', f'{metrics_orig["ai_ism_freq"]:.2f}', f'{metrics_edited["ai_ism_freq"]:.2f}'),
        ('Lexical Diversity (MTLD)', f'{metrics_orig["mtld"]:.1f}', f'{metrics_edited["mtld"]:.1f}'),
        ('Type-Token Ratio (TTR)', f'{metrics_orig["ttr"]:.3f}', f'{metrics_edited["ttr"]:.3f}'),
        ('Avg Sentence Length', f'{metrics_orig["avg_sentence_length"]:.1f}', f'{metrics_edited["avg_sentence_length"]:.1f}'),
        ('Subordination Ratio', f'{metrics_orig["subordination_ratio"]:.2f}', f'{metrics_edited["subordination_ratio"]:.2f}'),
    ]
    
    pdf.set_font('Arial', '', 10)
    for metric, orig, edited in metrics_data:
        pdf.cell(80, 7, metric, 1)
        pdf.cell(50, 7, orig, 1, align='C')
        pdf.cell(50, 7, edited, 1, align='C')
        pdf.ln()
    
    pdf.ln(10)
    
    # AI-isms found
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'AI-ism Markers Detected', ln=True)
    pdf.ln(5)
    
    if found_ai_isms_edited:
        pdf.set_font('Arial', 'B', 11)
        pdf.cell(0, 8, 'In AI-Edited Text:', ln=True)
        pdf.set_font('Arial', '', 10)
        for ai_ism, count in sorted(found_ai_isms_edited, key=lambda x: x[1], reverse=True)[:15]:
            pdf.cell(0, 6, f'  • "{ai_ism}" - {count} occurrence(s)', ln=True)
    else:
        pdf.set_font('Arial', '', 10)
        pdf.cell(0, 8, 'No AI-ism markers detected in AI-edited text.', ln=True)
    
    pdf.ln(5)
    
    if found_ai_isms_orig:
        pdf.set_font('Arial', 'B', 11)
        pdf.cell(0, 8, 'In Original Text:', ln=True)
        pdf.set_font('Arial', '', 10)
        for ai_ism, count in sorted(found_ai_isms_orig, key=lambda x: x[1], reverse=True)[:10]:
            pdf.cell(0, 6, f'  • "{ai_ism}" - {count} occurrence(s)', ln=True)
    
    # Interpretation guide
    pdf.add_page()
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'Interpretation Guide', ln=True)
    pdf.ln(5)
    
    pdf.set_font('Arial', '', 10)
    interpretations = [
        ('Burstiness Index', 
         'Measures sentence length variation. < 1.0 suggests AI-like uniformity; > 1.5 indicates human-like variation.'),
        ('AI-ism Frequency', 
         'Counts formulaic LLM markers per 100 words. Higher values suggest more formulaic, AI-influenced writing.'),
        ('Lexical Diversity (MTLD)', 
         'Measures vocabulary richness. Higher scores indicate more diverse word usage.'),
        ('Type-Token Ratio (TTR)', 
         'Ratio of unique words to total words. Higher values suggest richer vocabulary.'),
        ('Average Sentence Length', 
         'Average words per sentence. AI often produces longer, more complex sentences.'),
        ('Subordination Ratio', 
         'Clauses per sentence. Higher values indicate more complex syntactic structures.'),
    ]
    
    for metric, desc in interpretations:
        pdf.set_font('Arial', 'B', 10)
        pdf.cell(0, 7, f'{metric}:', ln=True)
        pdf.set_font('Arial', '', 10)
        pdf.multi_cell(0, 6, f'  {desc}')
        pdf.ln(2)
    
    # Full texts
    pdf.add_page()
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'Original Text', ln=True)
    pdf.ln(5)
    pdf.set_font('Arial', '', 10)
    
    # Handle encoding issues
    safe_original = original_text.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 6, safe_original)
    
    pdf.add_page()
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'AI-Edited Text', ln=True)
    pdf.ln(5)
    pdf.set_font('Arial', '', 10)
    
    safe_edited = edited_text.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 6, safe_edited)
    
    return pdf.output(dest='S').encode('latin-1')


def get_pdf_download_link(pdf_bytes, filename="analysis_report.pdf"):
    """Generate download link for PDF."""
    b64 = base64.b64encode(pdf_bytes).decode()
    return f'<a href="data:application/octet-stream;base64,{b64}" download="{filename}" ' \
           f'style="display: inline-block; padding: 10px 20px; background-color: #1f77b4; ' \
           f'color: white; text-decoration: none; border-radius: 5px; font-weight: bold;">' \
           f'📥 Download PDF Report</a>'


def main():
    # Header
    st.markdown('<p class="main-header">📝 L2 Writing Style Analyzer</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Compare stylistic differences between original L2 writing and AI-edited versions</p>', 
                unsafe_allow_html=True)
    
    # Sidebar with information
    with st.sidebar:
        st.header("📊 About the Metrics")
        
        with st.expander("Burstiness Index", expanded=False):
            st.markdown("""
            **Formula:** Sentence length standard deviation ÷ mean
            
            **Interpretation:**
            - **< 1.0**: AI-like uniformity
            - **1.0 - 1.5**: Moderate variation
            - **> 1.5**: Human-like variation
            
            Humans naturally vary sentence length more than AI.
            """)
        
        with st.expander("AI-ism Frequency", expanded=False):
            st.markdown("""
            **Formula:** Count of formulaic LLM markers per 100 words
            
            Detects patterns like:
            - Transition words (furthermore, moreover)
            - Formal hedging (it is important to note)
            - Generic intensifiers (significantly, notably)
            - List structures (firstly, secondly)
            
            **Higher values** suggest more formulaic writing.
            """)
        
        with st.expander("Lexical Diversity (MTLD)", expanded=False):
            st.markdown("""
            **MTLD** (Measure of Textual Lexical Diversity)
            
            Measures vocabulary richness accounting for text length.
            
            **Higher scores** indicate more diverse word usage.
            
            Also reports TTR (Type-Token Ratio) as supplementary metric.
            """)
        
        with st.expander("Syntactic Complexity", expanded=False):
            st.markdown("""
            Two measures:
            
            1. **Average Sentence Length**: Words per sentence
            2. **Subordination Ratio**: Clauses per sentence
            
            AI often produces longer, more complex sentences with more subordination.
            """)
        
        st.markdown("---")
        st.info("💡 **Tip**: Paste your original text and AI-edited version to see real-time comparisons!")
    
    # Main content - Text input section
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("✏️ Original Text")
        original_text = st.text_area(
            "Paste your original L2 writing here",
            height=250,
            key="original_input",
            placeholder="Enter your original text here..."
        )
        word_count_orig = count_words(original_text)
        st.markdown(f'<p class="word-count">Words: {word_count_orig}</p>', unsafe_allow_html=True)
    
    with col2:
        st.subheader("🤖 AI-Edited Text")
        edited_text = st.text_area(
            "Paste the AI-edited version here",
            height=250,
            key="edited_input",
            placeholder="Enter the AI-edited text here..."
        )
        word_count_edited = count_words(edited_text)
        st.markdown(f'<p class="word-count">Words: {word_count_edited}</p>', unsafe_allow_html=True)
    
    # Calculate metrics
    if original_text.strip() or edited_text.strip():
        
        # Original text metrics
        metrics_orig = {}
        if original_text.strip():
            metrics_orig['burstiness'] = calculate_burstiness(original_text)
            metrics_orig['ai_ism_freq'], found_ai_isms_orig = count_ai_isms(original_text)
            metrics_orig['mtld'], metrics_orig['ttr'] = calculate_lexical_diversity(original_text)
            metrics_orig['avg_sentence_length'], metrics_orig['subordination_ratio'] = calculate_syntactic_complexity(original_text)
            metrics_orig['sentence_count'] = len(get_sentences(original_text))
        else:
            metrics_orig = {k: 0 for k in ['burstiness', 'ai_ism_freq', 'mtld', 'ttr', 'avg_sentence_length', 'subordination_ratio', 'sentence_count']}
            found_ai_isms_orig = []
        
        # Edited text metrics
        metrics_edited = {}
        if edited_text.strip():
            metrics_edited['burstiness'] = calculate_burstiness(edited_text)
            metrics_edited['ai_ism_freq'], found_ai_isms_edited = count_ai_isms(edited_text)
            metrics_edited['mtld'], metrics_edited['ttr'] = calculate_lexical_diversity(edited_text)
            metrics_edited['avg_sentence_length'], metrics_edited['subordination_ratio'] = calculate_syntactic_complexity(edited_text)
            metrics_edited['sentence_count'] = len(get_sentences(edited_text))
        else:
            metrics_edited = {k: 0 for k in ['burstiness', 'ai_ism_freq', 'mtld', 'ttr', 'avg_sentence_length', 'subordination_ratio', 'sentence_count']}
            found_ai_isms_edited = []
        
        # Metrics Dashboard
        st.markdown("---")
        st.subheader("📊 Metrics Dashboard")
        
        # Key metrics cards
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric(
                label="Burstiness Index",
                value=f"{metrics_edited['burstiness']:.2f}" if edited_text else "N/A",
                delta=f"{metrics_edited['burstiness'] - metrics_orig['burstiness']:+.2f}" if original_text and edited_text else None
            )
            if edited_text:
                if metrics_edited['burstiness'] < 1.0:
                    st.caption("🔴 AI-like uniformity")
                elif metrics_edited['burstiness'] > 1.5:
                    st.caption("🟢 Human-like variation")
                else:
                    st.caption("🟡 Moderate variation")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric(
                label="AI-ism Frequency",
                value=f"{metrics_edited['ai_ism_freq']:.2f}" if edited_text else "N/A",
                delta=f"{metrics_edited['ai_ism_freq'] - metrics_orig['ai_ism_freq']:+.2f}" if original_text and edited_text else None,
                delta_color="inverse"
            )
            if edited_text:
                st.caption("per 100 words")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col3:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric(
                label="Lexical Diversity (MTLD)",
                value=f"{metrics_edited['mtld']:.1f}" if edited_text else "N/A",
                delta=f"{metrics_edited['mtld'] - metrics_orig['mtld']:+.1f}" if original_text and edited_text else None
            )
            if edited_text:
                st.caption("Higher = more diverse")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col4:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric(
                label="Avg Sentence Length",
                value=f"{metrics_edited['avg_sentence_length']:.1f}" if edited_text else "N/A",
                delta=f"{metrics_edited['avg_sentence_length'] - metrics_orig['avg_sentence_length']:+.1f}" if original_text and edited_text else None
            )
            if edited_text:
                st.caption("words per sentence")
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Comparison visualization
        if original_text.strip() and edited_text.strip():
            st.markdown("---")
            st.subheader("📈 Visual Comparison")
            
            fig = create_comparison_chart(metrics_orig, metrics_edited)
            st.pyplot(fig)
            
            # Side-by-side text comparison with AI-ism highlighting
            st.markdown("---")
            st.subheader("🔍 Side-by-Side Text Comparison")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Original Text**")
                st.text_area("Original (read-only)", original_text, height=200, disabled=True, label_visibility="collapsed")
            
            with col2:
                st.markdown("**AI-Edited Text (AI-isms highlighted)**")
                highlighted_edited = highlight_ai_isms(edited_text)
                st.markdown(f'<div style="background-color: #f0f2f6; padding: 10px; border-radius: 5px; height: 200px; overflow-y: auto; font-family: Georgia, serif; font-size: 14px; line-height: 1.6;">{highlighted_edited}</div>', 
                           unsafe_allow_html=True)
            
            # AI-ism breakdown
            if found_ai_isms_edited:
                with st.expander("📋 AI-ism Breakdown in Edited Text", expanded=False):
                    cols = st.columns(3)
                    sorted_ai_isms = sorted(found_ai_isms_edited, key=lambda x: x[1], reverse=True)
                    for i, (ai_ism, count) in enumerate(sorted_ai_isms):
                        cols[i % 3].markdown(f"- **{ai_ism}**: {count} time(s)")
        
        # PDF Export
        st.markdown("---")
        st.subheader("📄 Export Report")
        
        if original_text.strip() or edited_text.strip():
            pdf_bytes = create_pdf_report(
                original_text, edited_text, 
                metrics_orig, metrics_edited,
                found_ai_isms_orig, found_ai_isms_edited
            )
            st.markdown(get_pdf_download_link(pdf_bytes), unsafe_allow_html=True)
    
    # Footer
    st.markdown("---")
    st.markdown(
        '<p style="text-align: center; color: #666; font-size: 0.9rem;">'
        'Built for ELT professionals | Open source on GitHub</p>',
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
