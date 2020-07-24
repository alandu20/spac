from typing import Dict
import re
import numpy as np


HEADER = (
    'financial accounting standards provided pursuant '
    'to section 13(a) of the exchange act'
)
FOOTER = (
    'pursuant to the requirements of '
    'the securities exchange act of 1934'
)
VOTE_HEADER = 'for against abstain broker non-votes'


def _search_text(txt: str, prefix: str, suffix: str) -> str:
    """Find text in between prefix and suffix.

    If suffix is "" find all text post prefix.
    Args:
        prefix: String prefix which parameterizes start index.
        suffix: String suffix which parameterizes end index.
    Return:
        String text in between suffix and prefix.
    """
    start = txt.index(prefix) + len(prefix)
    end = txt.index(suffix) if suffix is not "" else len(txt)
    return txt[start:end]


def preprocess_document(text: str) -> str:
    """Initial pre-processing for SEC text document.

    Given a string document, remove all new line characters, unicode characters
    and repeated spaces. Then lower case the text. Then remove the forward-looking
    statement section. Finally remove the header and footer of the doc.
    Args:
        text: String of document text.
    Returns:
        String for processed document text.
    """
    # Replace new line and tabs.
    text = text.replace('\n', ' ').replace('\t', ' ')
    # Replace unicode characters.
    unicode_replacements = {
        '\xa0': ' ', '\x93': '"', '”': '"', '“': '"'
    }
    for unicode, replacement in unicode_replacements.items():
        text = text.replace(unicode, replacement)

    # Remove extra spaces.
    text = re.sub(' +', ' ', text)
    text = text.lower()
    
    # Remove forward looking statement section.
    foward_start = 'forward-looking statements this current report on form 8-k'
    foward_end = 'undue reliance should not be placed upon the forward-looking statements'
    ind_start = text.find(foward_start)
    ind_end = text.find(foward_end)
    if ind_start!=-1 and ind_end!=-1:
        text = text[0:ind_start] + text[ind_end+len(foward_end):]

    # Remove everything in header and footer.
    text = _search_text(text, HEADER, FOOTER)
    return text


def parse_items_mapping(text: str) -> Dict[str, str]:
    """Get subheaders and associated subtext.

    Parse out all subheaders and create a mapping from subheader to its
    corresponding subtext. A subheader is of the form "item 7.01" and the
    associated subtext follows said subheader until the next item.
    Args:
        text: String SEC filing document, post preprocessing.
    Returns:
        Dictionary mapping subheader to subtext.
    """
    # Extract subheaders and get rid of duplicates
    subheaders = re.findall(r'item [0-9]+\.[0-9]+', text)
    subheaders = list(set(subheaders))
    subheaders.sort()

    # Map subheader to its associated text.
    item_mapping = {}
    for i, subheader in enumerate(subheaders):
        if i >= len(subheaders) - 1:
            subtext = _search_text(text, subheader, "")
        else:
            subtext = _search_text(text, subheader, subheaders[i + 1])
        item_mapping[subheader] = subtext
    return item_mapping


def parse_vote_results(text) -> (float, float, float, float):
    """Parse voting results.

    Given SEC document, parse out relevant voting results if they exist.
    Votes should be categorized into: votes for, votes against, votes abstain,
    and votes broker non-votes.
    Args:
        text: String SEC document, post preprocessing.
    Returns:
        Tuple of floats for (votes for, votes against, votes abstain,
        votes broker non-votes).
    """
    def convert_vote_count_to_int(vote_string) -> float:
        """Convert vote string to int."""
        # To indicate 0 votes, sometimes 8-K has dash (two types) instead of 0.
        if '—' in vote_string or '-' in vote_string:
            return 0.0
        try:
            votes = float(vote_string.replace(',', ''))
        except ValueError:
            return np.nan
        return votes

    vote_index = text.find(VOTE_HEADER)
    if vote_index == -1:
        return np.nan, np.nan, np.nan, np.nan
    else:
        vote_data = text[(vote_index + len(VOTE_HEADER)):].lstrip().split(' ')
        votes_for = convert_vote_count_to_int(vote_data[0])
        votes_against = convert_vote_count_to_int(vote_data[1])
        votes_abstain = convert_vote_count_to_int(vote_data[2])
        votes_broker_non_votes = convert_vote_count_to_int(vote_data[3])
        return (votes_for, votes_against,
                votes_abstain, votes_broker_non_votes)
