import re
import logging

logger = logging.getLogger(__name__)

SPACY_AVAILABLE = False
nlp = None
try:
    import spacy
    try:
        nlp = spacy.load("en_core_web_sm")
        SPACY_AVAILABLE = True
        logger.info("spaCy and en_core_web_sm loaded — using spaCy for disambiguation.")
    except Exception as e:
        logger.warning(
            "spaCy is installed but 'en_core_web_sm' could not be loaded. "
            "Install it with: python -m spacy download en_core_web_sm\n"
            f"spaCy error: {e}"
        )
        SPACY_AVAILABLE = False
except Exception:
    logger.info("spaCy not available — falling back to heuristics for ambiguous contractions.")
    

def expand_contractions(text: str, use_spacy: bool = True) -> dict:
    """
    Expand a broad set of English contractions in `text`.

    Returns a dict:
      {
        "expanded_text": <str>,
        "method": "spacy" or "heuristic",
        "replacements": [ {"original": ..., "expanded": ..., "count": int}, ... ]  # summary counts
      }

    If spaCy is available and use_spacy is True, spaCy is used to disambiguate
    ambiguous contractions such as "'s" and "'d". Otherwise heuristics are used.
    """
    if text is None:
        return {"expanded_text": None, "method": None, "replacements": []}

    original_text = text

    text = text.replace("’", "'").replace("‘", "'").replace("`", "'")

    def preserve_case(expansion: str, original: str) -> str:
        if not original:
            return expansion
        if original.isupper():
            return expansion.upper()
        if original[0].isupper():
            return expansion[0].upper() + expansion[1:]
        return expansion

    common_past_participles = set([
        "been", "gone", "seen", "done", "made", "taken", "given", "known", "felt",
        "said", "written", "found", "left", "put", "brought", "bought", "stolen",
        "driven", "eaten", "grown", "built", "kept", "heard", "become", "begun",
        "chosen", "shown", "shut", "lost", "met", "read", "run", "won", "held",
        "let", "set", "slept", "spoken", "spent", "understood", "worn", "won",
        "worked", "studied", "played", "attempted", "opened", "closed", "helped",
        "started", "stopped", "remembered", "forgotten", "changed", "called",
        "liked", "loved", "used", "believed", "seemed", "moved", "felt", "fell",
        "told", "sent", "begun", "caught", "kept", "built", "driven", "felt",
        "fixed", "solved", "learned", "taught", "thought", "fought", "walked",
        "talked", "lived", "died", "tried", "cried", "smiled", "laughed", "jumped",
        "climbed", "painted", "drawn", "written", "broken", "fallen", "risen",
        "frozen", "chosen", "woken", "spoken", "taken", "shaken", "mistaken",
    ])

    multiword_patterns = {
        r"\b(can't've)\b": "cannot have",
        r"\b(couldn't've)\b": "could not have",
        r"\b(mightn't've)\b": "might not have",
        r"\b(mustn't've)\b": "must not have",
        r"\b(shouldn't've)\b": "should not have",
        r"\b(wouldn't've)\b": "would not have",
        r"\b(ain't)\b": "is not", 
    }

    contractions = {
        "aren't": "are not",
        "can't": "cannot",
        "could've": "could have",
        "couldn't": "could not",
        "didn't": "did not",
        "doesn't": "does not",
        "don't": "do not",
        "hadn't": "had not",
        "hasn't": "has not",
        "haven't": "have not",
        "he'd've": "he would have",
        "how'd": "how did",
        "how'll": "how will",
        "how's": "how is",
        "i'd've": "i would have",
        "i'll": "i will",
        "i'm": "i am",
        "i've": "i have",
        "isn't": "is not",
        "it'd've": "it would have",
        "it'll": "it will",
        "it's": "it is",  
        "let's": "let us",
        "might've": "might have",
        "mightn't": "might not",
        "must've": "must have",
        "mustn't": "must not",
        "o'clock": "of the clock",
        "she'd've": "she would have",
        "she'll": "she will",
        "should've": "should have",
        "shouldn't": "should not",
        "that'll": "that will",
        "that's": "that is",
        "there's": "there is",
        "they'd've": "they would have",
        "they'll": "they will",
        "they're": "they are",
        "they've": "they have",
        "wasn't": "was not",
        "we'd": "we would",  
        "we'd've": "we would have",
        "we'll": "we will",
        "we're": "we are",
        "we've": "we have",
        "weren't": "were not",
        "when's": "when is",
        "where's": "where is",
        "why's": "why is",
        "won't": "will not",
        "would've": "would have",
        "wouldn't": "would not",
        "you'd've": "you would have",
        "you'll": "you will",
        "you're": "you are",
        "you've": "you have",
        "gonna": "going to",
        "gotta": "got to",
        "wanna": "want to",
        "gimme": "give me",
        "lemme": "let me",
        "outta": "out of",
        "kinda": "kind of",
        "sorta": "sort of",
        "dunno": "do not know",
        "y'all": "you all",
        "yall": "you all",
        "ma'am": "madam",
        "ne'er": "never",
        "'em": "them",
        "couldnt": "could not",
        "dont": "do not",
        "wont": "will not",
        "cant": "cannot",
    }

    replacements_counter = {}

    for pat, repl in multiword_patterns.items():
        def repl_fn(m, r=repl):
            original = m.group(0)
            replacements_counter[original] = replacements_counter.get(original, 0) + 1
            return preserve_case(r, original)
        text = re.sub(pat, repl_fn, text, flags=re.IGNORECASE)

    for contr, expansion in contractions.items():
        escaped = re.escape(contr)
        pattern = r'\b' + escaped + r'\b'
        def repl_base(m, e=expansion):
            orig = m.group(0)
            replacements_counter[orig] = replacements_counter.get(orig, 0) + 1
            return preserve_case(e, orig)
        text = re.sub(pattern, repl_base, text, flags=re.IGNORECASE)
    method_used = "heuristic"
    if use_spacy and SPACY_AVAILABLE:
        method_used = "spacy"

    def spaCy_next_info(subject_text, next_token_text):
        """
        Returns POS, TAG for next_token_text when parsed in context with subject_text.
        If spaCy isn't available or parsing fails, returns (None, None).
        """
        if not SPACY_AVAILABLE:
            return (None, None)
        try:
            s = f"{subject_text} {next_token_text}"
            doc = nlp(s)
            if len(doc) >= 2:
                t = doc[1]
                return (t.pos_, t.tag_)  
            elif len(doc) == 1:
                t = doc[0]
                return (t.pos_, t.tag_)
            else:
                return (None, None)
        except Exception:
            return (None, None)

    def replace_s(match):
        subject = match.group(1)
        apostrophe_s = match.group(2)  
        original_contraction = f"{subject}{apostrophe_s}"
        
        full_match = match.group(0)
        remainder = full_match[len(original_contraction):]
        
        match_end = match.end()
        remaining_text = text[match_end:] if match_end < len(text) else ""
        nxt = remaining_text.split()[0] if remaining_text.strip() else ""

        if method_used == "spacy":
            pos, tag = spaCy_next_info(subject, nxt) if nxt else (None, None)
            if tag == "VBN" or (pos == "VERB" and tag == "VBN"):
                out = f"{subject} has"
            else:
                possessive_indicators = {"the", "a", "an", "my", "your", "his", "her", "its", "our", "their", "this", "that", "these", "those"}
                if pos == "NOUN" or pos == "PRON" or nxt.lower() in possessive_indicators:
                    return original_contraction + remainder
                out = f"{subject} is"
        else:
            nxt_lower = nxt.lower() if nxt else ""
            determiners = {"the", "a", "an", "my", "your", "his", "her", "its", "our", "their", "this", "that", "these", "those"}
            
            possessive_nouns = {"book", "car", "house", "job", "work", "blog", "tech", "cloud", "migration", "company", "team", "project", "code", "data", "system"}
            if nxt_lower in common_past_participles:
                out = f"{subject} has"
            elif nxt_lower in determiners or nxt_lower in possessive_nouns:
                return original_contraction + remainder  
            else:
                out = f"{subject} is"

        replacements_counter[original_contraction] = replacements_counter.get(original_contraction, 0) + 1
        return out + remainder

    text = re.sub(r"\b([A-Za-z]+)('s)\b", replace_s, text, flags=re.IGNORECASE)


    def replace_d(match):
        subject = match.group(1)
        apostrophe_d = match.group(2)  
        original_contraction = f"{subject}{apostrophe_d}"
        
        full_match = match.group(0)
        remainder = full_match[len(original_contraction):]
        
        match_end = match.end()
        remaining_text = text[match_end:] if match_end < len(text) else ""
        nxt = remaining_text.split()[0] if remaining_text.strip() else ""

        if method_used == "spacy":
            pos, tag = spaCy_next_info(subject, nxt) if nxt else (None, None)
            if tag == "VBN" or (pos == "VERB" and tag == "VBN"):
                out = f"{subject} had"
            else:
                out = f"{subject} would"
        else:
            nxt_lower = nxt.lower() if nxt else ""
            infinitive_indicators = {"check", "probably", "just", "rather", "like", "prefer"}
            if nxt_lower in common_past_participles:
                out = f"{subject} had"
            elif nxt_lower in infinitive_indicators:
                out = f"{subject} would"
            else:
                out = f"{subject} would"

        replacements_counter[original_contraction] = replacements_counter.get(original_contraction, 0) + 1
        return out + remainder

    text = re.sub(r"\b([A-Za-z]+)('d)\b", replace_d, text, flags=re.IGNORECASE)

    def repl_ve(m):
        orig = m.group(0)
        replacements_counter[orig] = replacements_counter.get(orig, 0) + 1
        return preserve_case(m.group(1) + " have", orig)

    text = re.sub(r"\b([A-Za-z]+)('ve)\b", repl_ve, text, flags=re.IGNORECASE)

    def repl_re(m):
        orig = m.group(0)
        replacements_counter[orig] = replacements_counter.get(orig, 0) + 1
        return preserve_case(m.group(1) + " are", orig)

    text = re.sub(r"\b([A-Za-z]+)('re)\b", repl_re, text, flags=re.IGNORECASE)

    def repl_ll(m):
        orig = m.group(0)
        replacements_counter[orig] = replacements_counter.get(orig, 0) + 1
        return preserve_case(m.group(1) + " will", orig)

    text = re.sub(r"\b([A-Za-z]+)('ll)\b", repl_ll, text, flags=re.IGNORECASE)

    text = re.sub(r'\s{2,}', ' ', text).strip()

    replacements = [{"original": k, "count": v} for k, v in replacements_counter.items()]

    return {
        "expanded_text": text,
        "method": method_used,
        "replacements": replacements,
        "original_text": original_text
    }
    
def convert_words_to_dict(words):
    """Convert AssemblyAI Word objects to dictionaries and expand contractions per-word"""
    if not words:
        return None
    word_dicts = []
    for word in words:
        word_dict = word.__dict__.copy()
        if 'text' in word_dict and word_dict['text']:
            res = expand_contractions(word_dict['text'], use_spacy=False)
            word_dict['text_expanded'] = res["expanded_text"]
        else:
            word_dict['text_expanded'] = None
        word_dicts.append(word_dict)
    return word_dicts

def convert_utterances_to_dict(utterances):
    """Convert AssemblyAI Utterance objects to dictionaries"""
    if not utterances:
        return None
    return [utterance.__dict__ for utterance in utterances]