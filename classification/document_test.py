from classification import document
import pytest
import glob
import os


@pytest.fixture
def document_data():
    """Aggregate test documents."""
    # Read in test data for letter of intent.
    loi_filepaths = glob.glob(
        os.path.join(os.path.dirname(__file__),
                     "data_test/loi/*.txt")
    )
    pytest.loi_text = [
        open(file, "r").read() for file in loi_filepaths
    ]

    # Read in test data for business combination agreement.
    bca_filepaths = glob.glob(
        os.path.join(os.path.dirname(__file__),
                     "data_test/bca/*.txt")
    )
    pytest.bca_text = [
        open(file, "r").read() for file in bca_filepaths
    ]

    # Read in test data for consummations.
    consummation_filepaths = glob.glob(
        os.path.join(os.path.dirname(__file__),
                     "data_test/consummation/*.txt")
    )
    pytest.consummation_text = [
        open(file, "r").read() for file in consummation_filepaths
    ]

    # Read in test data for extensions.
    extension_filepaths = glob.glob(
        os.path.join(os.path.dirname(__file__),
                     "data_test/extension/*.txt")
    )
    pytest.extension_text = [
        open(file, "r").read() for file in extension_filepaths
    ]


def test_loi_classification(document_data):
    """Test letter of intent classification function for documents."""
    for loi_text in pytest.loi_text:
        doc = document.Document(loi_text)
        assert doc.is_letter_of_intent()
        assert not doc.is_business_combination_agreement()
        assert not doc.is_consummation()
        assert not doc.is_extension()


def test_bca_classification():
    """Test business combination agreement classification for documents."""
    for bca_text in pytest.bca_text:
        doc = document.Document(bca_text)
        assert not doc.is_letter_of_intent()
        assert doc.is_business_combination_agreement()
        assert not doc.is_consummation()
        assert not doc.is_extension()


def test_consummation_classification():
    """Test business combination agreement classification for documents."""
    for consummation_text in pytest.consummation_text:
        doc = document.Document(consummation_text)
        assert not doc.is_letter_of_intent()
        assert not doc.is_business_combination_agreement()
        assert doc.is_consummation()
        assert not doc.is_extension()


def test_extension_classification():
    """Test business combination agreement classification for documents."""
    for extension_text in pytest.extension_text:
        doc = document.Document(extension_text)
        assert not doc.is_letter_of_intent()
        assert not doc.is_business_combination_agreement()
        assert not doc.is_consummation()
        assert doc.is_extension()



