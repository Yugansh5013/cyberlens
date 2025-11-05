import spacy

# Load spaCy small English model
nlp = spacy.load("en_core_web_sm")

def extract_named_entities(text: str):
    """
    Extract named entities such as PERSON, ORG, and GPE (locations)
    from OCR or text input.
    Returns: list of {type, value}
    """
    doc = nlp(text)
    entities = []
    for ent in doc.ents:
        if ent.label_ in ["PERSON", "ORG", "GPE"]:
            entities.append({"type": ent.label_, "value": ent.text})
    return entities
