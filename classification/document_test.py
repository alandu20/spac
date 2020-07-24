from classification import document
import pytest
import glob
import os


@pytest.fixture
def document_data():
    """Aggregate test documents."""
    loi_filepaths = glob.glob(
        os.path.join(os.path.dirname(__file__),
                     "data_test/loi/*.txt")
    )
    pytest.loi_text = [
        open(file, "r").read() for file in loi_filepaths
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
    assert True




