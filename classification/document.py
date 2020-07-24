from classification import preprocess


class Document(object):

    def __init__(self, text):
        """Initialize document with raw SEC document text data."""
        # Apply initial preprocessing to remove unicode characters etc.
        self.text = preprocess.preprocess_document(text)

        # Parse out items in document.
        self.item_mapping = preprocess.parse_items_mapping(self.text)

    def is_letter_of_intent(self) -> bool:
        """"""
        return False

    def is_business_combination_agreement(self) -> bool:
        """"""
        return False

    def is_consummation(self) -> bool:
        """"""
        return False

    def is_extension(self) -> bool:
        """"""
        return False