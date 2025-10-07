import pandas as pd
from abtranslate.config import BOUNDARY, UNK_TOKEN

def extract_and_mask(col: pd.Series, filter_pattern, min_length: int = 1, ) -> pd.DataFrame:
    """
    Return a DataFrame with:
      • masked_text     : original text with non‑Chinese spans ≥ min_length → <UNK>
      • filter_pattern  : regex pattern of masking target
      • extracted_tokens: those spans (≥ min_length) joined by BOUNDARY
    
    Args:
        col: pandas Series containing text to process
        min_length: minimum length of non-Chinese text to mask (default: 1)
    
    Null and non‑string inputs become ''.
    """
    s = col.astype("string").fillna("")          # null‑safe → pandas StringDtype

    def extract_tokens(text):
        """Extract non-Chinese tokens that meet minimum length requirement"""
        matches = filter_pattern.findall(text)
        # Only include tokens that meet minimum length requirement
        filtered_matches = [match for match in matches if len(match.strip()) >= min_length]
        return BOUNDARY.join(filtered_matches)
    
    def mask_text(text):
        """Mask non-Chinese tokens that meet minimum length requirement"""
        def replace_match(match):
            token = match.group(1)
            # Only mask if token meets minimum length requirement
            if len(token.strip()) >= min_length:
                return UNK_TOKEN
            else:
                return token  # Keep original token if below minimum length
        
        return filter_pattern.sub(replace_match, text)

    extracted = s.apply(extract_tokens)
    masked = s.apply(mask_text)

    return pd.DataFrame(
        {"masked_text": masked.astype(str),
         "extracted_tokens": extracted.astype(str)}
    )

def restore_tokens(masked: pd.Series, extracted: pd.Series) -> pd.Series:
    """
    Restore original text by replacing UNK_TOKEN placeholders with extracted tokens.
    """
    m = masked.astype("string").fillna("")
    e = extracted.astype("string").fillna("")

    def rebuild(pair):
        masked_txt, extracted_txt = pair
        parts = masked_txt.split(UNK_TOKEN)
        tokens = extracted_txt.split(BOUNDARY) if extracted_txt else []
        return "".join(
            part + (tokens[i] if i < len(tokens) else "")
            for i, part in enumerate(parts)
        )

    return pd.Series(map(rebuild, zip(m, e)))

