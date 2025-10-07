from transformation_test import *
from translation_test import *
from text_processing_test import *
from abtranslate.config.settings import log_level
import logging
log_level = logging.DEBUG


## TRANSFORMATION TEST FUNCTION
test_expand_to_sentence_level()
test_flatten_sentences()
test_tokenized_sentences()
test_detokenized_sentences()
test_get_structure()
test_apply_structure()

# ## TRANSLATION TEST FUNCTION
test_translation()
test_batch_translation()
test_udf_translation()

# TEXT PROCESSING TEST
# test_extract_and_mask_udf()
# test_restore_masked_udf