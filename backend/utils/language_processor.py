"""
Language Processor for ServiceLink AI
Handles multi-language support: Urdu, Roman Urdu, and English
Extracts service types and locations from natural language
"""

from typing import Dict, Optional, List, Tuple
import re
from langdetect import detect, LangDetectException
from deep_translator import GoogleTranslator

class LanguageProcessor:
    """
    Multi-language NLP processor for service requests
    Supports: Urdu, Roman Urdu (Urdu in Latin script), English
    """

    def __init__(self):
        pass  # deep-translator doesn't need initialization

        # Service type mappings (English, Urdu, Roman Urdu)
        self.service_mappings = {
            # AC Repair
            'ac repair': ['ac', 'air conditioner', 'ac repair', 'ac service', 'ac maintenance',
                         'ایئر کنڈیشنر', 'اے سی', 'ac theek', 'ac ka masla', 'ac thanda nahi'],

            # Plumbing
            'plumbing': ['plumber', 'plumbing', 'pipe', 'drain', 'water tank', 'bathroom',
                        'پلمبر', 'نل', 'پائپ', 'paani ka masla', 'pipe leak', 'nal theek'],

            # Electrician
            'electrician': ['electrician', 'electric', 'wiring', 'light', 'fan', 'switch',
                           'بجلی', 'الیکٹریشن', 'bijli ka masla', 'light theek', 'fan repair'],

            # Home Cleaning
            'home cleaning': ['cleaning', 'clean', 'maid', 'house cleaning', 'deep clean',
                             'صفائی', 'کلینگ', 'ghar ki safai', 'cleaning service', 'safai'],

            # Carpenter
            'carpenter': ['carpenter', 'carpentry', 'furniture', 'wood', 'door', 'cabinet',
                         'بڑھئی', 'لکڑی', 'furniture theek', 'darwaza repair', 'lakri ka kaam'],

            # Painter
            'painter': ['painter', 'painting', 'paint', 'wall paint', 'color',
                       'پینٹر', 'رنگ', 'paint karna', 'deewar ka rang', 'painting service']
        }

        # Location keywords (Islamabad areas)
        self.location_keywords = [
            # Sectors
            'f-6', 'f-7', 'f-8', 'f-10', 'f-11',
            'g-6', 'g-7', 'g-8', 'g-9', 'g-10', 'g-11', 'g-13',
            'i-8', 'i-9', 'i-10',
            'e-7', 'e-11',
            # Areas
            'blue area', 'bahria town', 'dha', 'pwd', 'gulberg',
            'islamabad', 'rawalpindi', 'pindi',
            # Markaz
            'markaz', 'market', 'super market'
        ]

        # Urgency keywords
        self.urgency_keywords = {
            'emergency': ['emergency', 'urgent', 'abhi', 'فوری', 'jaldi', 'turant', 'immediately'],
            'high': ['high priority', 'important', 'zaruri', 'ضروری', 'jald'],
            'normal': ['normal', 'regular', 'aam', 'عام']
        }

    def detect_language(self, text: str) -> str:
        """
        Detect language of input text

        Args:
            text: Input text

        Returns:
            Language code: 'en' (English), 'ur' (Urdu), 'roman_urdu' (Roman Urdu)
        """
        try:
            # Check for Urdu script
            if self._contains_urdu_script(text):
                return 'ur'

            # Try language detection
            lang = detect(text)

            # Check for Roman Urdu patterns (Urdu words in Latin script)
            if lang == 'en' and self._is_roman_urdu(text):
                return 'roman_urdu'

            return lang

        except LangDetectException:
            # Default to English if detection fails
            return 'en'

    def _contains_urdu_script(self, text: str) -> bool:
        """Check if text contains Urdu/Arabic script"""
        urdu_range = range(0x0600, 0x06FF)
        return any(ord(char) in urdu_range for char in text)

    def _is_roman_urdu(self, text: str) -> bool:
        """
        Detect if text is Roman Urdu (Urdu written in Latin script)
        Checks for common Roman Urdu patterns and words
        """
        roman_urdu_patterns = [
            'theek', 'karna', 'chahiye', 'masla', 'hai', 'ka', 'ki',
            'abhi', 'jaldi', 'zaruri', 'ghar', 'paani', 'bijli',
            'safai', 'kaam', 'service', 'repair', 'nahi', 'ho', 'raha'
        ]

        text_lower = text.lower()
        matches = sum(1 for pattern in roman_urdu_patterns if pattern in text_lower)

        # If 2 or more Roman Urdu words found, classify as Roman Urdu
        return matches >= 2

    def translate_to_english(self, text: str, source_lang: str = None) -> str:
        """
        Translate text to English

        Args:
            text: Input text
            source_lang: Source language code (auto-detect if None)

        Returns:
            Translated English text
        """
        if not source_lang:
            source_lang = self.detect_language(text)

        # Already English
        if source_lang == 'en':
            return text

        try:
            # Translate Urdu to English
            if source_lang == 'ur':
                translator = GoogleTranslator(source='ur', target='en')
                return translator.translate(text)

            # Roman Urdu - try to translate common phrases
            if source_lang == 'roman_urdu':
                # Replace common Roman Urdu words with English equivalents
                translated = self._translate_roman_urdu(text)
                return translated

            # Other languages - translate to English
            translator = GoogleTranslator(source='auto', target='en')
            return translator.translate(text)

        except Exception as e:
            print(f"⚠️ Translation error: {e}")
            return text  # Return original text if translation fails

    def _translate_roman_urdu(self, text: str) -> str:
        """
        Translate common Roman Urdu phrases to English
        """
        replacements = {
            'theek karna': 'repair',
            'theek': 'fix',
            'masla': 'problem',
            'hai': 'is',
            'nahi': 'not',
            'chahiye': 'need',
            'abhi': 'now',
            'jaldi': 'quickly',
            'zaruri': 'urgent',
            'ghar': 'home',
            'paani': 'water',
            'bijli': 'electricity',
            'safai': 'cleaning',
            'kaam': 'work',
            'service': 'service',
            'repair': 'repair'
        }

        text_lower = text.lower()
        for roman, english in replacements.items():
            text_lower = text_lower.replace(roman, english)

        return text_lower

    def extract_service_type(self, text: str) -> Optional[str]:
        """
        Extract service type from natural language text

        Args:
            text: Input text (any language)

        Returns:
            Service type or None if not found
        """
        # Translate to English first
        lang = self.detect_language(text)
        if lang != 'en':
            text_english = self.translate_to_english(text, lang)
        else:
            text_english = text

        text_lower = text_english.lower()

        # Check against service mappings
        for service_type, keywords in self.service_mappings.items():
            for keyword in keywords:
                if keyword.lower() in text_lower or keyword.lower() in text.lower():
                    return service_type

        return None

    def extract_location_from_text(self, text: str) -> Optional[str]:
        """
        Extract location/area from text

        Args:
            text: Input text

        Returns:
            Location string or None if not found
        """
        text_lower = text.lower()

        # Check for location keywords
        for location in self.location_keywords:
            if location.lower() in text_lower:
                return location

        # Try to extract sector pattern (e.g., G-13, F-10)
        sector_pattern = r'\b[a-zA-Z]-\d{1,2}\b'
        sector_match = re.search(sector_pattern, text, re.IGNORECASE)
        if sector_match:
            return sector_match.group(0).upper()

        return None

    def extract_urgency(self, text: str) -> str:
        """
        Extract urgency level from text

        Args:
            text: Input text

        Returns:
            Urgency level: 'emergency', 'high', or 'normal'
        """
        text_lower = text.lower()

        # Check for emergency keywords
        for keyword in self.urgency_keywords['emergency']:
            if keyword.lower() in text_lower:
                return 'emergency'

        # Check for high priority keywords
        for keyword in self.urgency_keywords['high']:
            if keyword.lower() in text_lower:
                return 'high'

        return 'normal'

    def extract_contact_info(self, text: str) -> Dict[str, Optional[str]]:
        """
        Extract contact information (phone, email) from text

        Args:
            text: Input text

        Returns:
            Dict with phone and email (None if not found)
        """
        # Phone pattern (Pakistani format)
        phone_pattern = r'(\+92|0)?[-\s]?3\d{2}[-\s]?\d{7}'
        phone_match = re.search(phone_pattern, text)

        # Email pattern
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        email_match = re.search(email_pattern, text)

        return {
            'phone': phone_match.group(0) if phone_match else None,
            'email': email_match.group(0) if email_match else None
        }

    def parse_service_request(self, text: str) -> Dict:
        """
        Parse complete service request from natural language

        Args:
            text: Input text (any language)

        Returns:
            Dict with extracted information
        """
        # Detect language
        language = self.detect_language(text)

        # Translate to English for processing
        text_english = self.translate_to_english(text, language)

        # Extract all information
        service_type = self.extract_service_type(text)
        location = self.extract_location_from_text(text)
        urgency = self.extract_urgency(text)
        contact_info = self.extract_contact_info(text)

        return {
            'original_text': text,
            'detected_language': language,
            'translated_text': text_english,
            'service_type': service_type,
            'location': location,
            'urgency': urgency,
            'phone': contact_info['phone'],
            'email': contact_info['email']
        }

    def format_response(self, response: str, target_language: str = 'en') -> str:
        """
        Format response in target language

        Args:
            response: Response text in English
            target_language: Target language code

        Returns:
            Formatted response in target language
        """
        if target_language == 'en':
            return response

        try:
            if target_language == 'ur':
                translation = self.translator.translate(response, src='en', dest='ur')
                return translation.text

            # For Roman Urdu, keep English (most users prefer English responses)
            return response

        except Exception as e:
            print(f"⚠️ Response translation error: {e}")
            return response
