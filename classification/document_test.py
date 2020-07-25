from classification import document
import pytest
import glob
import os


@pytest.fixture
def document_data():
    """Aggregate test documents."""
    # Read in test data for letter of intent.
    pytest.loi_filepaths = glob.glob(
        os.path.join(os.path.dirname(__file__),
                     "data_test/loi/*.txt")
    )
    pytest.loi_text = [
        open(file, "r").read() for file in pytest.loi_filepaths
    ]

    # Read in test data for business combination agreement.
    pytest.bca_filepaths = glob.glob(
        os.path.join(os.path.dirname(__file__),
                     "data_test/bca/*.txt")
    )
    pytest.bca_text = [
        open(file, "r").read() for file in pytest.bca_filepaths
    ]

    # Read in test data for consummations.
    pytest.consummation_filepaths = glob.glob(
        os.path.join(os.path.dirname(__file__),
                     "data_test/consummation/*.txt")
    )
    pytest.consummation_text = [
        open(file, "r").read() for file in pytest.consummation_filepaths
    ]

    # Read in test data for extensions.
    pytest.extension_filepaths = glob.glob(
        os.path.join(os.path.dirname(__file__),
                     "data_test/extension/*.txt")
    )
    pytest.extension_text = [
        open(file, "r").read() for file in pytest.extension_filepaths
    ]


def test_loi_classification(document_data):
    """Test letter of intent classification function for documents."""
    for loi_text, loi_filepath in zip(pytest.loi_text, pytest.loi_filepaths):
        failure_message = "File failure %s" % loi_filepath
        doc = document.Document(loi_text)
        assert doc.is_letter_of_intent(), failure_message
        assert not doc.is_business_combination_agreement(), failure_message
        assert not doc.is_consummation(), failure_message


def test_bca_classification():
    """Test business combination agreement classification for documents."""
    for bca_text, bca_filepath in zip(pytest.bca_text, pytest.bca_filepaths):
        failure_message = "File failure %s" % bca_filepath
        doc = document.Document(bca_text)
        assert not doc.is_letter_of_intent(), failure_message
        assert doc.is_business_combination_agreement(), failure_message
        assert not doc.is_consummation(), failure_message


def test_consummation_classification():
    """Test business combination agreement classification for documents."""
    for consummation_text, consummation_filepath in zip(
            pytest.consummation_text, pytest.consummation_filepaths):
        failure_message = "File failure %s" % consummation_filepath
        doc = document.Document(consummation_text)
        assert not doc.is_letter_of_intent(), failure_message
        assert not doc.is_business_combination_agreement(), failure_message
        assert doc.is_consummation(), failure_message


def test_extension_classification():
    """Test business combination agreement classification for documents."""
    for extension_text, extension_filepath in zip(
            pytest.extension_text, pytest.extension_filepaths):
        failure_message = "File failure %s" % extension_filepath
        doc = document.Document(extension_text)
        assert not doc.is_letter_of_intent(), failure_message
        assert not doc.is_business_combination_agreement(), failure_message
        assert not doc.is_consummation(), failure_message
        assert doc.is_extension(), failure_message
