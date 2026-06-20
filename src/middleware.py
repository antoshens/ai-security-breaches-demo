from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine, OperatorConfig
from presidio_analyzer import PatternRecognizer, Pattern
from presidio_anonymizer.entities import OperatorConfig
from presidio_analyzer import AnalyzerEngine
from presidio_analyzer.nlp_engine import NlpEngineProvider

analyzer = AnalyzerEngine()
anonymizer = AnonymizerEngine()

def secure_output_middleware(agent_response: str) -> str:
    # 1. Scan text for PII (Email, Phone, Credit Card)
    results = analyzer.analyze(text=agent_response, language="en")
    
    # 2. Anonimyzing
    anonymized_text = anonymizer.anonymize(text=agent_response, analyzer_results=results)
    return anonymized_text.text


def custom_secure_output_middleware(agent_response: str) -> str:
    # 1. Regex for our custom ID
    dk_id_pattern = Pattern(
        name="dk_id_pattern", 
        regex=r"\bDK-\d{3,10}\b", 
        score=0.85 # The model's confidence that this is a PII (0 to 1)
    )

    # 2. Initialize the PatternRecognizer
    dk_recognizer = PatternRecognizer(
        supported_entity="DK_INTERNAL_ID", 
        patterns=[dk_id_pattern]
    )

    # 3. Register it in our analyzer engine
    analyzer.registry.add_recognizer(dk_recognizer)

    results = analyzer.analyze(text=agent_response, language="en")
    
    anonymized_text = anonymizer.anonymize(text=agent_response, analyzer_results=results)
    return anonymized_text.text


def custom_secure_output_middleware_with_mask(agent_response: str) -> str:
    # 1. Regex for our custom ID
    dk_id_pattern = Pattern(
        name="dk_id_pattern", 
        regex=r"\bDK-\d{3,10}\b", 
        score=0.85 # The model's confidence that this is a PII (0 to 1)
    )

    # 2. Initialize the PatternRecognizer
    dk_recognizer = PatternRecognizer(
        supported_entity="DK_INTERNAL_ID", 
        patterns=[dk_id_pattern]
    )

    # Setting up a masking operator for credit cards
    # We want to replace the numbers with '*', but leave the last 4 characters visible
    crypto_mask_config = {
        "type": "mask",
        "masking_char": "*",
        "chars_to_mask": 15,
        "from_end": False
    }

    operators_custom = {
        "CREDIT_CARD": OperatorConfig("mask", crypto_mask_config),
        "DK_INTERNAL_ID": OperatorConfig("replace", {"new_value": "[REDACTED_ID]"})
    }

    # 3. Register it in our analyzer engine
    analyzer.registry.add_recognizer(dk_recognizer)

    results = analyzer.analyze(text=agent_response, language="en")
    
    anonymized_text = anonymizer.anonymize(text=agent_response, analyzer_results=results, operators=operators_custom)
    return anonymized_text.text

def custom_secure_output_middleware_multiple_lang(agent_response: str) -> str:
    # 1. We describe the configuration for an NLP engine (e.g. spaCy)
    # We specify which local language models to use
    configuration = {
        "nlp_engines": [{
            "name": "spacy", # Can be other (e.g. Flair)
            "model_names": [
                {"lang_code": "en", "model_name": "en_core_web_lg"},
                {"lang_code": "uk", "model_name": "uk_core_news_trf"} # If we need Ukrainian region support
            ]
        }]
    }

    # 2. Create a provider and load the analyzer
    provider = NlpEngineProvider(nlp_configuration=configuration)
    multi_lang_analyzer = AnalyzerEngine(nlp_engine=provider.create_engine())

    # 3. Now we can dynamically switch context during analysis:
    results = multi_lang_analyzer.analyze(text=agent_response, language="uk")

    anonymized_text = anonymizer.anonymize(text=agent_response, analyzer_results=results)
    return anonymized_text.text
