import re
from collections import Counter
from typing import List, Dict
from gplay_scraper.config import Config


DEFAULT_STOP_WORDS = {
    'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
    'from', 'up', 'about', 'into', 'through', 'during', 'before', 'after', 'above',
    'below', 'between', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
    'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should',
    'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those', 'i', 'you',
    'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them', 'my',
    'your', 'his', 'her', 'its', 'our', 'their', 'a', 'an', 'app'
}


class AsoAnalyzer:
    """App Store Optimization (ASO) analyzer for keyword and text analysis.
    
    Analyzes app descriptions, titles, and summaries to extract keywords,
    calculate readability scores, and identify competitive keywords.
    """
    
    def __init__(self):
        """Initialize ASO analyzer with stop words and competitive keyword sets."""
        self.default_stop_words = DEFAULT_STOP_WORDS
        # Categorized competitive keywords for different app aspects
        self.competitive_keywords = {
            'monetization': {
                'purchase', 'buy', 'subscription', 'premium', 'paid', 'upgrade', 'unlock', 'in-app purchase', 'offer', 'discount', 'free trial'
            },
            'engagement': {
                'interactive', 'personalized', 'challenge', 'task', 'daily reward', 'notification', 'reminder', 'streak', 'habit', 'goal'
            },
            'social': {
                'friends', 'share', 'invite', 'connect', 'community', 'chat', 'comment', 'like', 'follow', 'collaborate'
            },
            'progression': {
                'level', 'rank', 'badge', 'milestone', 'achievement', 'unlock', 'reward', 'track', 'progress', 'goal'
            },
            'usability': {
                'offline', 'fast', 'lightweight', 'easy', 'intuitive', 'responsive', 'secure', 'privacy', 'customizable', 'accessible'
            },
            'marketing': {
                'trending', 'popular', 'featured', 'top chart', 'recommended', 'exclusive', 'limited offer'
            }
        }

    def tokenize_text(self, text: str, min_length: int = 3, stop_words: set = None) -> List[str]:
        """Tokenize text into clean words for analysis.
        
        Args:
            text (str): Input text to tokenize
            min_length (int): Minimum word length to include
            stop_words (set): Set of stop words to exclude
            
        Returns:
            List[str]: List of cleaned, filtered words
        """
        if not text:
            return []
        stop_words = stop_words or self.default_stop_words
        # Remove punctuation and convert to lowercase
        text = re.sub(r'[^\w\s]', ' ', text.lower())
        words = text.split()
        # Filter by length and remove stop words
        return [word for word in words if len(word) >= min_length and word not in stop_words]

    def extract_ngrams(self, words: List[str], n: int = 2) -> List[str]:
        """Extract n-grams (phrases) from word list.
        
        Args:
            words (List[str]): List of words
            n (int): Number of words per phrase (2=bigrams, 3=trigrams)
            
        Returns:
            List[str]: List of n-gram phrases
        """
        if not words or n <= 0 or n > len(words):
            return []
        # Create sliding window of n words
        return [' '.join(words[i:i+n]) for i in range(len(words)-n+1)]

    def keyword_frequency(self, words: List[str], top_n: int = 20) -> Dict[str, int]:
        """Calculate frequency of words/phrases and return top results.
        
        Args:
            words (List[str]): List of words or phrases
            top_n (int): Number of top results to return
            
        Returns:
            Dict[str, int]: Dictionary of word/phrase frequencies
        """
        return dict(Counter(words).most_common(top_n))

    def analyze_competitive_keywords(self, text: str) -> Dict[str, List[str]]:
        """Identify competitive keywords by category in the text.
        
        Args:
            text (str): Text to analyze for competitive keywords
            
        Returns:
            Dict[str, List[str]]: Categories with found competitive keywords
        """
        text_lower = text.lower()
        # Find intersection of text words with each keyword category
        found = {cat: list(kws & set(text_lower.split())) 
                 for cat, kws in self.competitive_keywords.items()}
        # Return only categories that have matches
        return {cat: kws for cat, kws in found.items() if kws}

    def keyword_density(self, words: List[str], total_words: int) -> Dict[str, float]:
        """Calculate keyword density as percentage of total words.
        
        Args:
            words (List[str]): List of words to analyze
            total_words (int): Total word count for percentage calculation
            
        Returns:
            Dict[str, float]: Word densities as percentages
        """
        if total_words == 0:
            return {}
        freq = Counter(words)
        # Calculate percentage density for each word
        return {k: round((v / total_words) * 100, 2) for k, v in freq.items()}

    def calculate_readability(self, text: str) -> Dict[str, float]:
        """Calculate Flesch readability score and reading level.
        
        Args:
            text (str): Text to analyze for readability
            
        Returns:
            Dict[str, float]: Readability metrics including Flesch score and level
        """
        # Split text into sentences
        sentences = re.split(r'[.!?]+', text)
        sentences = [s for s in sentences if s.strip()]
        words = text.split()
        word_count = len(words)
        sentence_count = len(sentences)
        syllables = sum(self.count_syllables(w) for w in words)
        
        if sentence_count == 0 or word_count == 0:
            return {'flesch_score': 0, 'flesch_level': 'Unknown', 'avg_sentence_length': 0}

        # Calculate Flesch Reading Ease score
        score = 206.835 - 1.015 * (word_count / sentence_count) - 84.6 * (syllables / word_count)
        
        # Determine reading level based on score
        if score >= 90: level = 'Very Easy'
        elif score >= 80: level = 'Easy'
        elif score >= 70: level = 'Fairly Easy'
        elif score >= 60: level = 'Standard'
        elif score >= 50: level = 'Fairly Difficult'
        elif score >= 30: level = 'Difficult'
        else: level = 'Very Difficult'

        return {
            'flesch_score': round(score, 2),
            'flesch_level': level,
            'avg_sentence_length': round(word_count / sentence_count, 2)
        }

    def count_syllables(self, word: str) -> int:
        """Count syllables in a word using vowel patterns.
        
        Args:
            word (str): Word to count syllables for
            
        Returns:
            int: Number of syllables (minimum 1)
        """
        word = word.lower()
        vowels = 'aeiouy'
        count = 0
        prev_vowel = False
        
        # Count vowel groups (consecutive vowels = 1 syllable)
        for c in word:
            if c in vowels:
                if not prev_vowel:
                    count += 1
                prev_vowel = True
            else:
                prev_vowel = False
        
        # Silent 'e' at end doesn't count
        if word.endswith('e'):
            count -= 1
        
        # Every word has at least 1 syllable
        return max(1, count)

    def analyze_app_text(self, app_data: dict, top_n: int = None) -> dict:
        """Perform comprehensive ASO analysis on app text content.
        
        Args:
            app_data (dict): App data containing title, summary, description, etc.
            top_n (int): Number of top keywords/phrases to return (uses Config default if None)
            
        Returns:
            dict: Complete ASO analysis with keywords, readability, competitive analysis
        """
        # Use configuration default if not specified
        top_n = top_n or Config.ASO_TOP_KEYWORDS
        # Extract text fields with different importance weights
        text_fields = [
            ('title', app_data.get('title', '')),
            ('summary', app_data.get('summary', '')),
            ('description', app_data.get('description', '')),
            ('recent_changes', app_data.get('recentChanges', ''))
        ]

        # Weight title and summary more heavily for keyword analysis
        TITLE_WEIGHT = 3      # Title is most important for ASO
        SUMMARY_WEIGHT = 2    # Summary is second most important
        
        # Create weighted text by repeating important sections
        weighted_text = ' '.join(filter(None, 
            [text_fields[0][1]] * TITLE_WEIGHT + 
            [text_fields[1][1]] * SUMMARY_WEIGHT + 
            [f[1] for f in text_fields[2:]]
        ))
        
        # Tokenize and analyze the text
        words = self.tokenize_text(weighted_text)
        total_words = len(words)
        unique_count = len(set(words))
        
        # Generate frequency analysis
        word_freq = Counter(words)
        bigrams = self.extract_ngrams(words, 2)    # 2-word phrases
        trigrams = self.extract_ngrams(words, 3)   # 3-word phrases

        return {
            'total_words': total_words,
            'unique_keywords': unique_count,
            'top_keywords': dict(word_freq.most_common(top_n)),
            'top_bigrams': self.keyword_frequency(bigrams, top_n),
            'top_trigrams': self.keyword_frequency(trigrams, top_n),
            'keyword_density': {k: round((v / total_words) * 100, 2) for k, v in word_freq.items()} if total_words > 0 else {},
            'competitive_analysis': self.analyze_competitive_keywords(weighted_text),
            'readability': self.calculate_readability(weighted_text)
        }