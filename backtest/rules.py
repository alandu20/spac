from classification import preprocess
from classification import document


def naive_rule(text: str) -> bool:
    """Given SEC document classify trade.

    For this naive rule, we simply look for LOI and business combination
    agreements while taking into account the number of redemptions.
    Args:
        text: String SEC document.
    Returns:
        Boolean of whether we should trade or not.
    """

    # Initialize document object.
    doc = document.Document(text)

    # Reject if too many votes against.
    votes = preprocess.parse_vote_results(text)
    votes_for, votes_against, votes_abstain, votes_broker_non_votes = votes
    votes_total = (votes_for + votes_against +
                   votes_abstain + votes_broker_non_votes)
    if votes_against / votes_total > 0.1:
        return False

    boolean_conditions = [
        doc.is_letter_of_intent(),
        doc.is_business_combination_agreement(),
        doc.is_consummation(),
        doc.is_extension(),
    ]
    return any(boolean_conditions)
