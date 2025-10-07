import sentencepiece as spm

from pathlib import Path
from typing import List

class Tokenizer:
    def encode(self, sentence: str) -> List[str]:
        raise NotImplementedError()
    
    def decode(self, tokens: List[str]) -> str:
        raise NotImplementedError()

class SentencePieceTokenizer(Tokenizer):
    def __init__(self, model_file: Path= None, src_file: Path = None, tgt_file: Path = None):
        if model_file and (src_file or tgt_file):
            raise ValueError("Provide either model_file or src_file/tgt_file, not both.")
        if not model_file and not (src_file and tgt_file):
            raise ValueError("Provide either model_file or both src_file and tgt_file.")
        if src_file and tgt_file:
            # Prefer src_file for model loading if both are provided
            self.src_file = src_file
            self.tgt_file = tgt_file
            self.is_single_tokenizer = False
        else:
            self.model_file = model_file
            self.is_single_tokenizer = True
        self.processor = None
        self.encoder : spm.SentencePieceProcessor = None
        self.decoder : spm.SentencePieceProcessor= None

    def lazy_processor(self) -> spm.SentencePieceProcessor:
        if self.is_single_tokenizer:
            self.processor = spm.SentencePieceProcessor(model_file=str(self.model_file)) 
            self.encoder = self.processor
            self.decoder = self.processor 
        else:
            if self.encoder is None:
                self.encoder = spm.SentencePieceProcessor(model_file=str(self.src_file))
            if self.decoder is None:
                self.decoder = spm.SentencePieceProcessor(model_file=str(self.tgt_file))
        
    def encode(self, sentence: str) -> List[str]:
        self.lazy_processor()
        tokens = self.encoder.encode(sentence, out_type=str)
        return tokens
    
    def encode_list(self, sentences) -> List[List[str]]:
        sentences_tokens = [self.encode(sentence) for sentence in sentences]
        return sentences_tokens  

    def decode(self, tokens: List[str]) -> str:
        self.lazy_processor()
        detokenized = self.decoder.decode(tokens)
        return detokenized.replace("▁", " ").lstrip()
    
    def decode_list(self, sentences_tokens: List[List[str]]) -> List[str]:
        sentences = [self.decode(tokens) for tokens in sentences_tokens]
        return sentences

class BPETokenizer(Tokenizer):
    def __init__(self, model_file: Path, from_code: str, to_code: str):
        self.model_file = model_file
        self.from_code = from_code
        self.to_code = to_code
        self.tokenizer = None
        self.detokenizer = None
        self.bpe_source = None

    def lazy_load(self):
        if self.tokenizer is None:
            from sacremoses.tokenize import MosesTokenizer, MosesDetokenizer
            from sacremoses.normalize import MosesPunctNormalizer

            self.tokenizer = MosesTokenizer(self.from_code)
            self.detokenizer = MosesDetokenizer(self.to_code)
            self.normalizer = MosesPunctNormalizer(self.from_code)

            from .apply_bpe import BPE
            with open(str(self.model_file), "r", encoding="utf-8") as f:
                self.bpe_source = BPE(f)

    def encode_list(self, sentences) -> List[List[str]]:
        sentences_tokens = [self.encode(sentence) for sentence in sentences]
        return sentences_tokens  

    def encode(self, sentence: str) -> List[str]:
        self.lazy_load()

        normalized = self.normalizer.normalize(sentence)
        tokenized = ' '.join(self.tokenizer.tokenize(normalized))
        segmented = self.bpe_source.segment_tokens(tokenized.strip('\r\n ').split(' '))
        return segmented
    
    def decode(self, tokens: List[str]) -> str:
        self.lazy_load()
        return self.detokenizer.detokenize(" ".join(tokens).replace("@@ ", "").split(" "))
    
    def decode(self, tokens: List[str]) -> str:
        detokenized = self.lazy_processor().Decode(tokens)
        return detokenized.replace("▁", " ").lstrip()