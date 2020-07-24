from classification import preprocess
import nltk


class Document(object):

    def __init__(self, text):
        """Initialize document with raw SEC document text data."""
        # Apply initial preprocessing to remove unicode characters etc.
        self.text = preprocess.preprocess_document(text)

        # Parse out items in document.
        self.item_mapping = preprocess.parse_items_mapping(self.text)

        # Normalize text.
        self.normalized_text = self._normalize_text()

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
        loi_phrases = ['letter intent', 'entri definit agreement']
        return any(phrase in self.normalized_text for phrase in loi_phrases)

    def is_business_combination_agreement(self) -> bool:
        """Check if document is a business combination agreement."""
        return False

    def is_consummation(self) -> bool:
        """"Check if document is a consummation."""
        return False

    def is_extension(self) -> bool:
        """Check if document is a extension."""
        return False