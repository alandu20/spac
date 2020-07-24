from classification import preprocess


def naive_rule(text: str) -> bool:
    """Given SEC document classify trade.

    For this naive rule, we simply look for LOI and business combination
    agreements while taking into account the number of redemptions.
    Args:
        text: String SEC document.
    Returns:
        Boolean of whether we should trade or not.
    """
    text = preprocess.preprocess_document(text)
    item_mapping = preprocess.parse_items_mapping(text)

    # Reject if too many votes against.
    votes = preprocess.parse_vote_results(text)
    votes_for, votes_against, votes_abstain, votes_broker_non_votes = votes
    votes_total = (votes_for + votes_against +
                   votes_abstain + votes_broker_non_votes)
    if votes_against / votes_total > 0.1:
        return False

    keywords = [
        'letter intent', 'enter definit agreement',
        '(the "business combination agreement")', '("business combination")',
        '(the "extension")', 'announcing the consummation'
    ]
    if (any(word in text for word in keywords)
            and "item 2.03" in item_mapping.keys()):
        return True

    return False