from rephorm.utility.is_set import is_set
footnote_counter = 0

def generate_footnote_numbers(footnotes):
    """
    Generate list of numbers for the footnotes
    Uses a global counter.
    """
    global footnote_counter
    references = []
    if is_set(footnotes):
        for _ in footnotes:
            footnote_counter += 1
            references.append(str(footnote_counter))
    return references
