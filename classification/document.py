from classification import preprocess
# import nltk


class Document(object):

    def __init__(self, text):
        """Initialize document with raw SEC document text data."""
        # Apply initial preprocessing to remove unicode characters etc.
        self.text = preprocess.preprocess_document(text)

        # Parse out items in document.
        self.item_mapping = preprocess.parse_items_mapping(self.text)
        print('items:', list(self.item_mapping.keys()))

    # def _normalize_text(self):
    #     """Normalize text, get rid of stop words and stem words."""
    #     # Tokenize text.
    #     tokens = nltk.tokenize.RegexpTokenizer(r'\w+').tokenize(self.text)

    #     # Remove stop words (the, of, and etc).
    #     stop_words = set(nltk.corpus.stopwords.words('english'))
    #     tokens = [token for token in tokens if token not in stop_words]

    #     # Remove numbers and non-english characters.
    #     tokens = [token for token in tokens if token.encode('utf-8').isalpha()]

    #     # Stem the tokens.
    #     tokens = [
    #         nltk.stem.porter.PorterStemmer().stem(token) for token in tokens
    #     ]
    #     return ' '.join(tokens)

    def is_letter_of_intent(self) -> bool:
        """Check if document is a letter of intent."""
        loi_phrases = [
            'entry into a letter of intent',
            'entry into a non-binding letter of intent',
            'enter into a letter of intent',
            'enter into a non-binding letter of intent',
            'entered into a letter of intent',
            'entered into a non-binding letter of intent',
            'entering into a letter of intent',
            'entering into a non-binding letter of intent',
            'execution of a letter of intent',
            'execution of a non-binding letter of intent',
            'execute a letter of intent',
            'execute a non-binding letter of intent',
            'executed a letter of intent',
            'executed a non-binding letter of intent',
            'executing a letter of intent',
            'executing a non-binding letter of intent'
        ]
        return any(phrase in self.text for phrase in loi_phrases)

    def is_business_combination_agreement(self) -> bool:
        """Check if document is a business combination agreement."""
        bca_phrases = [
            '("business combination agreement")',
            '(the "business combination agreement")',
            '("business combination")',
            '(the "business combination")',
            'entry into a definitive agreement',
            'enter into a definitive agreement',
            'entered into a definitive agreement',
            'entering into a definitive agreement',
            'business combination proposal was approved'
        ]
        return any(phrase in self.text for phrase in bca_phrases)

    def is_consummation(self) -> bool:
        """"Check if document is a consummation."""
        consummation_phrases = [
            'announcing the consummation',
            'consummated the previously announced business combination'
        ]
        return any(phrase in self.text for phrase in consummation_phrases)

    def is_extension(self) -> bool:
        """Check if document is a extension."""
        extension_phrases = [
            '(the "extension")',
            '(the "extension amendment")',
            'extended the termination date',
            'extend the date by which the company must consummate',
            '(the "extension amendment proposal")'
        ]
        return any(phrase in self.text for phrase in extension_phrases)

    def is_trust(self) -> bool:
        """Check if document is a trust account."""
        trust_phrases = [
            'trust account'
        ]
        return any(phrase in self.text for phrase in trust_phrases)

    def is_ipo(self) -> bool:
        """"Check if document is a ipo."""
        ipo_phrases = [
            'consummated its initial public offering ("ipo")',
            'consummated its initial public offering (the "ipo")',
            'consummated an initial public offering ("ipo")',
            'consummated an initial public offering (the "ipo")',
            'consummated the initial public offering ("ipo")',
            'consummated the initial public offering (the "ipo")',
            'completed its initial public offering ("ipo")',
            'completed its initial public offering (the "ipo")',
            'in connection with its initial public offering ("ipo") was declared effective',
            'in connection with its initial public offering (the "ipo") was declared effective',
            'consummated the ipo',
            'in connection with the closing of the ipo'
        ]
        return any(phrase in self.text for phrase in ipo_phrases)

    def is_item_203(self) -> bool:
        """Check if document is a item 2.03."""
        item_phrases = [
            'item 2.03'
        ]
        return any(phrase in list(self.item_mapping.keys()) for phrase in item_phrases)

    # todo: add redemption
