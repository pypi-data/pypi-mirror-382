from __future__ import annotations
from typing import List, Union, Dict, TYPE_CHECKING
import os
import psutil
import time

import sentencepiece as spm
import ctranslate2
import stanza
import pandas as pd

from abtranslate.config import CT2TranslatorConfig, CT2TranslationConfig
from abtranslate.config.constants import DEFAULT_CT2_CONFIG, DEFAULT_CT2_TRANSLATION_CONFIG, BATCH_SIZE
from abtranslate.utils.logger import logger
from abtranslate.utils.helper import generate_batch, expand_to_sentence_level, get_structure, apply_structure, restore_expanded_to_rows_level,  flatten_list
from abtranslate.utils.exception import InitializationError

if TYPE_CHECKING:
    from translator.package import ArgosPackage

class ArgosTranslator:
    def __init__(self, package: ArgosPackage, device:str ="cpu", translator_config: CT2TranslatorConfig = DEFAULT_CT2_CONFIG, optimized_config=False, lazy_load=True):
        if device == "gpu":
            translator_config == {}
            optimized_config = False
        self.translator_config = translator_config
        self.device = device
        self.pkg = package
        self.using_optimized_config = optimized_config
        
        self.translator = None
        if not lazy_load:
            self._initialize_models()

    def _initialize_models(
        self,
        sample_data=None
    ) -> ctranslate2.Translator:
        """
        Initialize all required models for translation.
        
        Args:
            compute_type: Computation type for CTranslate2
            inter_threads: Number of inter-threads
            intra_threads: Number of intra-threads
            
        Raises:
            ModelInitializationError: If any model fails to initialize
        """
        if (not self.translator) or self.using_optimized_config:
            try:
                model_path = self.pkg.get_model_path()
                if not os.path.exists(model_path):
                    dir_name = os.path.dirname(model_path)
                    list_dir = os.listdir(dir_name)
                    logger.warning(f"No model file found on package: {list_dir}")
                    raise FileNotFoundError(f"file {model_path} not exist")
                
                base_translator = ctranslate2.Translator(
                        model_path,
                        self.device,
                        **self.translator_config
                    ) 
            except Exception as e:
                logger.info(f"Model initialization error: {e}")
                raise InitializationError(f"Failed to initialize models: {e}")
        
            if (self.using_optimized_config and sample_data) == True:
                if len(sample_data) < BATCH_SIZE: # Only if sample data is sufficient, run the translator tuning.  
                    return base_translator
                try:
                    self.using_optimized_config=False
                    optimized_config = self.get_optimized_config(sample_data)
                    logger.info("Using translator config:", optimized_config)
                    self.apply_translator_config(device=self.device,
                                                 translator_config=optimized_config)
                except Exception as e:
                    logger.info(f"Failed to optimize translator. {e}")
                    self.translator = base_translator
                    self.using_optimized_config=False
            else:   
                self.translator = base_translator

        return self.translator

    def apply_translator_config(self, device, translator_config):
        self.translator = ctranslate2.Translator(
                        self.pkg.get_model_path(),
                        device,
                        **translator_config
                    ) 
        
    def _text_preprocessing(self, text: str) -> List[str]:
        tokenizer = self.pkg.tokenizer
        sentences = self.pkg.sentencizer.split_sentences(text) # stanza
        encoded_tokens = [tokenizer.encode(sentence) for sentence in sentences]  # SentencePiece
        return encoded_tokens
    
    def _parse_translation_result(self, ct2_outputs: ctranslate2.TranslationResult) -> List[str]:
        tokenizer = self.pkg.tokenizer
        translated_tokens = [output.hypotheses[0] for output in ct2_outputs]
        translations_detok = [tokenizer.decode(tokens) for tokens in translated_tokens]
        return translations_detok

    def translate(self, input_text:str, translation_config: CT2TranslationConfig = DEFAULT_CT2_TRANSLATION_CONFIG) -> str: 
        """
        Translate a sentence using CTranslate2 and shared SentencePiece model.

        Args:
            input (str): Source sentence to translate
            translator (ctranslate2.Translator): Loaded CTranslate2 model
            sp_model (sentencepiece.SentencePieceProcessor): Loaded shared SentencePiece model

        Returns:
            str: Translated sentence
        """
        translation_result = self.translate_batch([input_text], translation_config) 
        return  translation_result[0]

    def translate_batch(self, text_list: List[str] | pd.Series, translation_config: CT2TranslationConfig = DEFAULT_CT2_TRANSLATION_CONFIG, return_type = List) -> List[str]:
        """
        Translate a batch of text with comprehensive error handling.
        
        Args:
            text_list: List or Series of text to translate
            translation_config: Configuration for translation
            return_type: Expected return type (List or pd.Series)
        
        Returns:
            Translated text in the specified return type
        """
        logger.info(f"Starting translate_batch with {len(text_list) if hasattr(text_list, '__len__') else 'unknown'} items")
        
        try:
            # Step 1: Handle input type conversion
            try:
                if isinstance(text_list, pd.Series):
                    text_list = text_list.tolist()
                    return_type = pd.Series
                    logger.debug("Converted pandas Series to list")
            except Exception as e:
                logger.error(f"ERROR in input conversion: {type(e).__name__}: {e}")
                raise ValueError(f"Failed to convert input to list: {e}") from e

            # Store original length to ensure we return the same number of results
            original_length = len(text_list)
            logger.debug(f"Original input length: {original_length}")
            
            # Step 2: Handle empty/null inputs preprocessing
            try:
                processed_text_list = []
                empty_indices = []
                
                for i, text in enumerate(text_list):
                    if text is None or text == "" or (isinstance(text, str) and text.strip() == ""):
                        processed_text_list.append("")
                        empty_indices.append(i)
                    else:
                        processed_text_list.append(text)
                
                logger.debug(f"Found {len(empty_indices)} empty/null inputs at indices: {empty_indices[:10]}{'...' if len(empty_indices) > 10 else ''}")
            except Exception as e:
                logger.error(f"ERROR in input preprocessing: {type(e).__name__}: {e}")
                raise ValueError(f"Failed to preprocess input text: {e}") from e

            # Step 3: Initialize models
            try:
                translator = self._initialize_models(processed_text_list[:BATCH_SIZE])
                tokenizer = self.pkg.tokenizer
                sentencizer = self.pkg.sentencizer
                logger.debug("Successfully initialized translator, tokenizer, and sentencizer")
            except AttributeError as e:
                logger.error(f"ERROR in model initialization - missing attribute: {type(e).__name__}: {e}")
                raise AttributeError(f"Missing required component: {e}") from e
            except Exception as e:
                logger.error(f"ERROR in model initialization: {type(e).__name__}: {e}")
                raise RuntimeError(f"Failed to initialize translation models: {e}") from e

            # Step 4: Expand to sentence level
            try:
                expanded_rows = expand_to_sentence_level(processed_text_list, sentencizer, ignore_empty_paragraph=False, ignore_empty_row=False)
                logger.debug(f"Expanded to sentence level: {len(expanded_rows)} rows")
            except Exception as e:
                logger.error(f"ERROR in sentence expansion: {type(e).__name__}: {e}")
                logger.error(f"Failed on text sample: {processed_text_list[:3] if processed_text_list else 'empty list'}")
                raise RuntimeError(f"Failed to expand text to sentence level: {e}") from e

            # Step 5: Get structure
            try:
                structure = get_structure(expanded_rows, ignore_empty=False)
                logger.debug(f"Retrieved structure: {type(structure)} with length {len(structure) if hasattr(structure, '__len__') else 'N/A'}")
            except Exception as e:
                logger.error(f"ERROR in structure extraction: {type(e).__name__}: {e}")
                logger.error(f"Expanded rows sample: {expanded_rows[:3] if expanded_rows else 'empty'}")
                raise RuntimeError(f"Failed to extract text structure: {e}") from e

            # Step 6: Flatten sentences
            try:
                sentence_list = flatten_list(expanded_rows, str)
                logger.debug(f"Flattened to {len(sentence_list)} sentences")
            except Exception as e:
                logger.error(f"ERROR in sentence flattening: {type(e).__name__}: {e}")
                logger.error(f"Expanded rows type: {type(expanded_rows)}")
                raise RuntimeError(f"Failed to flatten sentences: {e}") from e
            
            # Handle case where all sentences are empty
            if not sentence_list or all(s == "" for s in sentence_list):
                logger.warning("All sentences are empty, returning empty results")
                result = [""] * original_length
                if return_type == pd.Series:
                    return pd.Series(result)
                return result
            
            # Step 7: Filter non-empty sentences
            try:
                non_empty_sentences = []
                sentence_indices = []
                
                for i, sentence in enumerate(sentence_list):
                    if sentence and sentence.strip():
                        non_empty_sentences.append(sentence)
                        sentence_indices.append(i)
                
                logger.info(f"Filtered to {len(non_empty_sentences)} non-empty sentences out of {len(sentence_list)} total")
                logger.debug(f"Sample sentences to translate: {non_empty_sentences[:3] if non_empty_sentences else 'none'}")
            except Exception as e:
                logger.error(f"ERROR in sentence filtering: {type(e).__name__}: {e}")
                raise RuntimeError(f"Failed to filter sentences: {e}") from e

            # Step 8: Tokenization and translation
            translated_sentences = [""] * len(sentence_list)
            
            if non_empty_sentences:
                # Tokenization
                try:
                    tokenized_sentences = tokenizer.encode_list(non_empty_sentences)
                    logger.debug(f"Successfully tokenized {len(tokenized_sentences)} sentences")
                except Exception as e:
                    logger.error(f"ERROR in tokenization: {type(e).__name__}: {e}")
                    logger.error(f"Sample sentences that failed: {non_empty_sentences[:3]}")
                    raise RuntimeError(f"Failed to tokenize sentences: {e}") from e

                # Translation config preparation
                try:
                    if not "max_batch_size" in translation_config.keys():
                        translation_config["max_batch_size"] = BATCH_SIZE
                    logger.debug(f"Translation config: {translation_config}")
                except Exception as e:
                    logger.error(f"ERROR in translation config setup: {type(e).__name__}: {e}")
                    raise ValueError(f"Invalid translation configuration: {e}") from e

                # Actual translation
                try:
                    translation_result = translator.translate_batch(
                        tokenized_sentences,
                        **translation_config
                    )
                    logger.debug(f"Translation completed, result type: {type(translation_result)}")
                except Exception as e:
                    logger.error(f"ERROR in translation execution: {type(e).__name__}: {e}")
                    logger.error(f"Translation config used: {translation_config}")
                    logger.error(f"Number of tokenized sentences: {len(tokenized_sentences)}")
                    raise RuntimeError(f"Translation failed: {e}") from e

                # Parse translation result
                try:
                    translated_non_empty = self._parse_translation_result(translation_result)
                    logger.debug(f"Parsed {len(translated_non_empty)} translation results")
                except Exception as e:
                    logger.error(f"ERROR in translation result parsing: {type(e).__name__}: {e}")
                    logger.error(f"Translation result type: {type(translation_result)}")
                    raise RuntimeError(f"Failed to parse translation results: {e}") from e
                
                # Reconstruct the full sentence list with translations
                try:
                    for i, translated in enumerate(translated_non_empty):
                        if i < len(sentence_indices):
                            translated_sentences[sentence_indices[i]] = translated
                        else:
                            logger.warning(f"Translation index {i} exceeds sentence_indices length {len(sentence_indices)}")
                    logger.debug("Successfully reconstructed sentence list with translations")
                except Exception as e:
                    logger.error(f"ERROR in sentence reconstruction: {type(e).__name__}: {e}")
                    logger.error(f"translated_non_empty length: {len(translated_non_empty)}, sentence_indices length: {len(sentence_indices)}")
                    raise RuntimeError(f"Failed to reconstruct translated sentences: {e}") from e

            # Step 9: Restore structure
            try:
                restored_structure = apply_structure(translated_sentences, structure)
                logger.debug(f"Applied structure successfully, result type: {type(restored_structure)}")
            except Exception as e:
                logger.error(f"ERROR in structure restoration: {type(e).__name__}: {e}")
                logger.error(f"Translated sentences length: {len(translated_sentences)}, structure type: {type(structure)}")
                raise RuntimeError(f"Failed to restore text structure: {e}") from e

            # Step 10: Restore to rows level
            try:
                translated_list = restore_expanded_to_rows_level(restored_structure)
                logger.debug(f"Restored to rows level: {len(translated_list)} items")
            except Exception as e:
                logger.error(f"ERROR in rows restoration: {type(e).__name__}: {e}")
                logger.error(f"Restored structure type: {type(restored_structure)}")
                raise RuntimeError(f"Failed to restore to original row structure: {e}") from e
            
            # Step 10.a: Removing unnecessary double-quotes
            

            # Step 11: Length validation and correction
            try:
                if len(translated_list) != original_length:
                    logger.warning(f"Length mismatch after translation: expected {original_length}, got {len(translated_list)}")
                    # Pad or truncate to match original length
                    if len(translated_list) < original_length:
                        padding_needed = original_length - len(translated_list)
                        translated_list.extend([""] * padding_needed)
                        logger.info(f"Padded result with {padding_needed} empty strings")
                    elif len(translated_list) > original_length:
                        translated_list = translated_list[:original_length]
                        logger.info(f"Truncated result to {original_length} items")
                else:
                    logger.debug("Length validation passed")
            except Exception as e:
                logger.error(f"ERROR in length validation: {type(e).__name__}: {e}")
                raise RuntimeError(f"Failed to validate/correct result length: {e}") from e
            
            # Step 12: Return type conversion
            try:
                if return_type == pd.Series:
                    result = pd.Series(translated_list)
                    logger.debug("Converted result to pandas Series")
                else:
                    result = translated_list
                    logger.debug("Returning result as list")
                
                logger.info(f"Translation completed successfully. Returned {len(result)} items")
                return result
                
            except Exception as e:
                logger.error(f"ERROR in return type conversion: {type(e).__name__}: {e}")
                raise RuntimeError(f"Failed to convert result to requested type: {e}") from e
                
        except Exception as e:
            # Catch-all error handler
            logger.error(f"CRITICAL ERROR in translate_batch: {type(e).__name__}: {e}")
            logger.error(f"Original input length: {original_length if 'original_length' in locals() else 'unknown'}")
            
            # Return safe fallback
            try:
                fallback_length = len(text_list) if hasattr(text_list, '__len__') else 0
                result = [""] * fallback_length
                if return_type == pd.Series:
                    return pd.Series(result)
                return result
            except Exception as fallback_error:
                logger.error(f"CRITICAL: Even fallback failed: {type(fallback_error).__name__}: {fallback_error}")
                # Last resort: return empty list
                return [] if return_type != pd.Series else pd.Series([])

    def get_optimized_config(self, sample_data: List[str]) -> ctranslate2.Translator:
        best_time = float('inf')
        prev_avg = float("inf") 
        patience_count = 0  # Added missing variable initialization

        translator_config = self.translator_config.copy()
        translator_config["compute_type"] = "int8_float32"
        translation_config = {  "beam_size": 1,
                                "num_hypotheses": 1, 
                                "replace_unknowns": False,}
        
        logical_cpu_count = psutil.cpu_count(logical=False)
        inter_intra_threads_pairs = [(1,                        0), 
                                    (1,                        logical_cpu_count),
                                    (logical_cpu_count//2,      2),
                                    ((logical_cpu_count//2)-1,  2),    
                                    (logical_cpu_count,        0),  
                                    (2,                        logical_cpu_count//2),
                                    (2,                        (logical_cpu_count//2)-1),
                                    (1,                        logical_cpu_count)]
        
        logger.info("Starting CPU allocation tuning")
        best_config = None
        for n_inter_threads, n_intra_threads in inter_intra_threads_pairs:
            translator_config["inter_threads"] = n_inter_threads
            translator_config["intra_threads"] = n_intra_threads
            logger.info(f"Testing translation with inter_threads:{n_inter_threads} intra_threads:{n_intra_threads}")
            try:
                self.apply_translator_config(device = self.device, translator_config=translator_config)
            except Exception as e:
                logger.info("Incompatible translator config: ", e)
                continue
            runtimes = []
            try:
                for _ in range(4):
                    start = time.perf_counter()
                    self.translate_batch(sample_data, translation_config)
                    end = time.perf_counter()
                    runtimes.append(end - start)
            except:
                raise Exception(f"Error during testing translator config{translator_config}")
            avg_time = sum(runtimes) / len(runtimes)
            logger.info(f"Translation finished, average time: {avg_time:.4f}s")

            if avg_time < best_time:
                best_time = avg_time
                best_config = translator_config.copy()
                logger.info("updating best config =>> ", best_config, "\n")
            
            if avg_time > prev_avg:
                patience_count +=1
            else:
                patience_count = 0
            prev_avg = avg_time
        return best_config