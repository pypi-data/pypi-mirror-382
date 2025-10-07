# ABTranslate

A translator wrapper for open-source translation models with batch optimization. Currently supports [ArgosTranslate](https://github.com/argosopentech/argos-translate) models and is designed for scalable deployment.

## Features

- ✅ Optimized translation for list or `pandas.Series` of text  
- 🛡️ Supports masking of specific patterns to exclude them from translation  
- ⚙️ Thread-tuned for multi-threaded deployment with `ctranslate2`  
- 📦 Compatible with ArgosTranslate model packages  

## Installation

```bash
pip install abtranslate
````

## Usage

```python
from abtranslate import load_argostranslate_model

# Load model from local path
model_package = load_argostranslate_model(model_path, package_dir=package_extraction_dir)

# Load translator with optional optimizations
translator = model_package.load_translator(optimized_config=True, lazy_load=False)

# Define translation quality settings (based on CTranslate2)
QUALITY_CONFIG = {
    "beam_size": 4,
    "num_hypotheses": 1,
    "replace_unknowns": True,
}

# Translate a batch of texts (e.g. pandas Series or list)
translated_texts = translator.translate_batch(df["input_text"], translation_config=QUALITY_CONFIG)
```

> 🔗 Refer to [CTranslate2 Translate Batch Parameters](https://opennmt.net/CTranslate2/python/ctranslate2.Translator.html) for more configuration options.

## Main Functions

* `load_argostranslate_model(model_path: str, package_dir: str) -> ModelPackage`:
  Loads and prepares an ArgosTranslate model for usage.

* `ModelPackage.load_translator(translator_config: dict, optimized_config: bool, lazy_load: bool) -> Translator`:
  Returns a translator instance with optional optimizations.

* `Translator.translate_batch(text_list: List[str] | pd.Series, translation_config: dict, return_type: any) -> List[str]`:
  Performs high-performance batch translation with support for multi-threading and tuning.

## License

MIT

## Author

Ichsan Takwa
[GitHub](https://github.com/Ichsan-T45/abtranslate)
