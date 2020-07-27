from classification import preprocess
import nltk


class Document(object):

    def __init__(self, text):
        """Initialize document with raw SEC document text data."""
        # Apply initial preprocessing to remove unicode characters etc.
        self.text = preprocess.preprocess_document(text)

        # Parse out items in document.
        self.item_mapping = preprocess.parse_items_mapping(self.text)

    def _normalize_text(self):
        """Normalize text, get rid of stop words and stem words."""
        # Tokenize text.
        tokens = nltk.tokenize.RegexpTokenizer(r'\w+').tokenize(self.text)

        # Remove stop words (the, of, and etc).
        stop_words = set(nltk.corpus.stopwords.words('english'))
        tokens = [token for token in tokens if token not in stop_words]

        # Remove numbers and non-english characters.
        tokens = [token for token in tokens if token.encode('utf-8').isalpha()]

        # Stem the tokens.
        tokens = [
            nltk.stem.porter.PorterStemmer().stem(token) for token in tokens
        ]
        return ' '.join(tokens)

    def is_letter_of_intent(self) -> bool:
        """Check if document is a letter of intent."""
        loi_phrases = [
            'letter of intent', 'entry into a definitive agreement',
            'enter into a definitive agreement',
            'entering into a definitive agreement',
            'entered into a definitive agreement',
            'definitive agreement will be entered into'
        ]
        return any(phrase in self.text for phrase in loi_phrases)

    def is_business_combination_agreement(self) -> bool:
        """Check if document is a business combination agreement."""
        bca_phrases = [
            '(the "business combination agreement")',
            '("business combination")',
            '"business combination proposal"'
        ]
        return any(phrase in self.text for phrase in bca_phrases)

    def is_consummation(self) -> bool:
        """"Check if document is a consummation."""
        consummation_phrases = [
            'announcing the consummation',
        ]
        return any(phrase in self.text for phrase in consummation_phrases)

    def is_extension(self) -> bool:
        """Check if document is a extension."""
        extension_phrases = ['(the "extension")', 'the "extension amendment"']
        return any(phrase in self.text for phrase in extension_phrases)
