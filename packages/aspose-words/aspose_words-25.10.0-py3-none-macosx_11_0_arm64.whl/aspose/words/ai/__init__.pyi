﻿import aspose.words
import aspose.pydrawing
import datetime
import decimal
import io
import uuid
from typing import Iterable, List
from enum import Enum

class AiModel:
    """An abstract class representing the integration with various AI models within the Aspose.Words."""
    
    @overload
    def summarize(self, source_document: aspose.words.Document, options: aspose.words.ai.SummarizeOptions) -> aspose.words.Document:
        """Generates a summary of the specified document, with options to adjust the length of the summary.
        This operation leverages the connected AI model for content processing.
        
        :param source_document: The document to be summarized.
        :param options: Optional settings to control the summary length and other parameters.
        :returns: A summarized version of the document's content."""
        ...
    
    @overload
    def summarize(self, source_documents: List[aspose.words.Document], options: aspose.words.ai.SummarizeOptions) -> aspose.words.Document:
        """Generates summaries for an array of documents, with options to control the summary length and other settings.
        This method utilizes the connected AI model for processing each document in the array.
        
        :param source_documents: An array of documents to be summarized.
        :param options: Optional settings to control the summary length and other parameters
        :returns: A summarized version of the document's content."""
        ...
    
    def check_grammar(self, source_document: aspose.words.Document, options: aspose.words.ai.CheckGrammarOptions) -> aspose.words.Document:
        """Checks grammar of the provided document.
        This operation leverages the connected AI model for checking grammar of document.
        
        :param source_document: The document being checked for grammar.
        :param options: Optional settings to control how grammar will be checked.
        :returns: A new :class:`aspose.words.Document` with checked grammar."""
        ...
    
    def translate(self, source_document: aspose.words.Document, target_language: aspose.words.ai.Language) -> aspose.words.Document:
        """Translates the provided document into the specified target language.
        This operation leverages the connected AI model for content translating.
        
        :param source_document: The document to be translated.
        :param target_language: The language into which the document will be translated.
        :returns: A new :class:`aspose.words.Document` object containing the translated document."""
        ...
    
    def with_api_key(self, api_key: str) -> aspose.words.ai.AiModel:
        """Sets a specified API key to the model."""
        ...
    
    @staticmethod
    def create(model_type: aspose.words.ai.AiModelType) -> aspose.words.ai.AiModel:
        """Creates a new instance of :class:`AiModel` class."""
        ...
    
    def as_open_ai_model(self) -> aspose.words.ai.OpenAiModel:
        """Cast AiModel to :class:`OpenAiModel`."""
        ...
    
    def as_google_ai_model(self) -> aspose.words.ai.GoogleAiModel:
        """Cast AiModel to :class:`GoogleAiModel`."""
        ...
    
    def as_anthropic_ai_model(self) -> aspose.words.ai.AnthropicAiModel:
        """Cast AiModel to :class:`AnthropicAiModel`."""
        ...
    
    ...

class AnthropicAiModel(aspose.words.ai.AiModel):
    """An abstract class representing the integration with Anthropic’s AI models within the Aspose.Words."""
    
    @overload
    def summarize(self, source_document: aspose.words.Document, options: aspose.words.ai.SummarizeOptions) -> aspose.words.Document:
        """Generates a summary of the specified document, with options to adjust the length of the summary.
        This operation leverages the connected AI model for content processing.
        
        :param source_document: The document to be summarized.
        :param options: Optional settings to control the summary length and other parameters.
        :returns: A summarized version of the document's content."""
        ...
    
    @overload
    def summarize(self, source_documents: List[aspose.words.Document], options: aspose.words.ai.SummarizeOptions) -> aspose.words.Document:
        """Generates summaries for an array of documents, with options to control the summary length and other settings.
        This method utilizes the connected AI model for processing each document in the array.
        
        :param source_documents: An array of documents to be summarized.
        :param options: Optional settings to control the summary length and other parameters
        :returns: A summarized version of the document's content."""
        ...
    
    def translate(self, source_document: aspose.words.Document, target_language: aspose.words.ai.Language) -> aspose.words.Document:
        """Translates the provided document into the specified target language.
        This operation leverages the connected AI model for content translating.
        
        :param source_document: The document to be translated.
        :param target_language: The language into which the document will be translated.
        :returns: A new :class:`aspose.words.Document` object containing the translated document."""
        ...
    
    ...

class CheckGrammarOptions:
    """Allows to specify various options while checking grammar of a document using AI."""
    
    def __init__(self):
        ...
    
    @property
    def make_revisions(self) -> bool:
        """Allows to specify either final or revised document to be returned with proofed text.
        Default value is ``False``."""
        ...
    
    @make_revisions.setter
    def make_revisions(self, value: bool):
        ...
    
    @property
    def improve_stylistics(self) -> bool:
        """Allows to specify either AI will try to improve stylistics of the text being proofed.
        Default value is ``False``."""
        ...
    
    @improve_stylistics.setter
    def improve_stylistics(self, value: bool):
        ...
    
    @property
    def preserve_formatting(self) -> bool:
        """Allows to specify either :meth:`IAiModelText.check_grammar` will try to preserve
        layout and formatting of the original document, or not.
        Default value is ``True``.
        
        When the option is set to ``False``, the quality of grammar checking is higher
        than when this option is set to ``True``. However, the original formatting of the
        text is not preserved in this case."""
        ...
    
    @preserve_formatting.setter
    def preserve_formatting(self, value: bool):
        ...
    
    ...

class GoogleAiModel(aspose.words.ai.AiModel):
    """An abstract class representing the integration with Google’s AI models within the Aspose.Words."""
    
    @overload
    def summarize(self, doc: aspose.words.Document, options: aspose.words.ai.SummarizeOptions) -> aspose.words.Document:
        """Summarizes specified :class:`aspose.words.Document` object."""
        ...
    
    @overload
    def summarize(self, docs: List[aspose.words.Document], options: aspose.words.ai.SummarizeOptions) -> aspose.words.Document:
        """Summarizes specified :class:`aspose.words.Document` objects."""
        ...
    
    def translate(self, doc: aspose.words.Document, language: aspose.words.ai.Language) -> aspose.words.Document:
        """Translates a specified document."""
        ...
    
    ...

class IAiModelText:
    """The common interface for AI models designed to generate a variety of text-based content."""
    
    @overload
    def summarize(self, source_document: aspose.words.Document, options: aspose.words.ai.SummarizeOptions) -> aspose.words.Document:
        """Generates a summary of the specified document, with options to adjust the length of the summary.
        This operation leverages the connected AI model for content processing.
        
        :param source_document: The document to be summarized.
        :param options: Optional settings to control the summary length and other parameters.
        :returns: A summarized version of the document's content."""
        ...
    
    @overload
    def summarize(self, source_documents: List[aspose.words.Document], options: aspose.words.ai.SummarizeOptions) -> aspose.words.Document:
        """Generates summaries for an array of documents, with options to control the summary length and other settings.
        This method utilizes the connected AI model for processing each document in the array.
        
        :param source_documents: An array of documents to be summarized.
        :param options: Optional settings to control the summary length and other parameters
        :returns: A summarized version of the document's content."""
        ...
    
    def check_grammar(self, source_document: aspose.words.Document, options: aspose.words.ai.CheckGrammarOptions) -> aspose.words.Document:
        """Checks grammar of the provided document.
        This operation leverages the connected AI model for checking grammar of document.
        
        :param source_document: The document being checked for grammar.
        :param options: Optional settings to control how grammar will be checked.
        :returns: A new :class:`aspose.words.Document` with checked grammar."""
        ...
    
    def translate(self, source_document: aspose.words.Document, target_language: aspose.words.ai.Language) -> aspose.words.Document:
        """Translates the provided document into the specified target language.
        This operation leverages the connected AI model for content translating.
        
        :param source_document: The document to be translated.
        :param target_language: The language into which the document will be translated.
        :returns: A new :class:`aspose.words.Document` object containing the translated document."""
        ...
    
    ...

class OpenAiModel(aspose.words.ai.AiModel):
    """An abstract class representing the integration with OpenAI's large language models within the Aspose.Words."""
    
    @overload
    def summarize(self, source_document: aspose.words.Document, options: aspose.words.ai.SummarizeOptions) -> aspose.words.Document:
        """Generates a summary of the specified document, with options to adjust the length of the summary.
        This operation leverages the connected AI model for content processing.
        
        :param source_document: The document to be summarized.
        :param options: Optional settings to control the summary length and other parameters.
        :returns: A summarized version of the document's content."""
        ...
    
    @overload
    def summarize(self, source_documents: List[aspose.words.Document], options: aspose.words.ai.SummarizeOptions) -> aspose.words.Document:
        """Generates summaries for an array of documents, with options to control the summary length and other settings.
        This method utilizes the connected AI model for processing each document in the array.
        
        :param source_documents: An array of documents to be summarized.
        :param options: Optional settings to control the summary length and other parameters
        :returns: A summarized version of the document's content."""
        ...
    
    def translate(self, source_document: aspose.words.Document, target_language: aspose.words.ai.Language) -> aspose.words.Document:
        """Translates the provided document into the specified target language.
        This operation leverages the connected AI model for content translating.
        
        :param source_document: The document to be translated.
        :param target_language: The language into which the document will be translated.
        :returns: A new :class:`aspose.words.Document` object containing the translated document."""
        ...
    
    def with_organization(self, organization_id: str) -> aspose.words.ai.OpenAiModel:
        """Sets a specified Organization to the model."""
        ...
    
    def with_project(self, project_id: str) -> aspose.words.ai.OpenAiModel:
        """Sets a specified Project to the model."""
        ...
    
    ...

class SummarizeOptions:
    """Allows to specify various options for summarizing document content."""
    
    def __init__(self):
        """Initializes a new instances of :class:`SummarizeOptions` class."""
        ...
    
    @property
    def summary_length(self) -> aspose.words.ai.SummaryLength:
        """Allows to specify summary length.
        Default value is :attr:`SummaryLength.MEDIUM`."""
        ...
    
    @summary_length.setter
    def summary_length(self, value: aspose.words.ai.SummaryLength):
        ...
    
    ...

class AiModelType(Enum):
    """Represents the types of :class:`AiModel` that can be integrated into the document processing workflow.
    
    This enumeration is used to define which large language model (LLM) should be utilized for tasks
    such as summarization, translation, and content generation."""
    
    """GPT-4o generative model type."""
    GPT_4O: int
    
    """GPT-4o mini generative model type."""
    GPT_4O_MINI: int
    
    """GPT-4 Turbo generative model type."""
    GPT_4_TURBO: int
    
    """GPT-3.5 Turbo generative model type."""
    GPT_35_TURBO: int
    
    """Gemini 1.5 Flash generative model type."""
    GEMINI_15_FLASH: int
    
    """Gemini 1.5 Flash-8B generative model type."""
    GEMINI_15_FLASH_8B: int
    
    """Gemini 1.5 Pro generative model type."""
    GEMINI_15_PRO: int
    
    """Claude 3.5 Sonnet generative model type."""
    CLAUDE_35_SONNET: int
    
    """Claude 3.5 Haiku generative model type."""
    CLAUDE_35_HAIKU: int
    
    """Claude 3 Opus generative model type."""
    CLAUDE_3_OPUS: int
    
    """Claude 3 Sonnet generative model type."""
    CLAUDE_3_SONNET: int
    
    """Claude 3 Haiku generative model type."""
    CLAUDE_3_HAIKU: int
    

class Language(Enum):
    """Specifies the language into which the text will be translated using AI.
    ."""
    
    AFRIKAANS: int
    
    AFRIKAANS_SOUTH_AFRICA: int
    
    ALBANIAN: int
    
    ALBANIAN_ALBANIA: int
    
    ALSATIAN: int
    
    AMHARIC: int
    
    ARABIC: int
    
    ARABIC_ALGERIA: int
    
    ARABIC_BAHRAIN: int
    
    ARABIC_EGYPT: int
    
    ARABIC_IRAQ: int
    
    ARABIC_JORDAN: int
    
    ARABIC_KUWAIT: int
    
    ARABIC_LEBANON: int
    
    ARABIC_LIBYA: int
    
    ARABIC_MOROCCO: int
    
    ARABIC_OMAN: int
    
    ARABIC_QATAR: int
    
    ARABIC_SAUDI_ARABIA: int
    
    ARABIC_SYRIA: int
    
    ARABIC_TUNISIA: int
    
    ARABIC_UAE: int
    
    ARABIC_YEMEN: int
    
    ARMENIAN: int
    
    ARMENIAN_ARMENIA: int
    
    ASSAMESE: int
    
    AZERI: int
    
    AZERI_CYRILLIC: int
    
    AZERI_LATIN: int
    
    BASQUE: int
    
    BASQUE_BASQUE: int
    
    BELARUSIAN: int
    
    BELARUSIAN_BELARUS: int
    
    BENGALI: int
    
    BENGALI_BANGLADESH: int
    
    BOSNIAN_CYRILLIC: int
    
    BOSNIAN_LATIN: int
    
    BRETON: int
    
    BULGARIAN: int
    
    BULGARIAN_BULGARIA: int
    
    BURMESE: int
    
    CATALAN: int
    
    CATALAN_CATALAN: int
    
    CHEROKEE: int
    
    CHINESE_HONG_KONG: int
    
    CHINESE_MACAO: int
    
    CHINESE_CHINA: int
    
    CHINESE_SINGAPORE: int
    
    CHINESE_TAIWAN: int
    
    CHINESE_SIMPLIFIED: int
    
    CHINESE_TRADITIONAL: int
    
    CROATIAN: int
    
    CROATIAN_BOZNIA_AND_HERZEGOVINA: int
    
    CROATIAN_CROATIA: int
    
    CZECH: int
    
    CZECH_CZECH_REPUBLIC: int
    
    DANISH: int
    
    DANISH_DENMARK: int
    
    DIVEHI: int
    
    DIVEHI_MALDIVES: int
    
    DUTCH: int
    
    DUTCH_BELGIUM: int
    
    DUTCH_NETHERLANDS: int
    
    EDO: int
    
    ENGLISH: int
    
    ENGLISH_AUSTRALIA: int
    
    ENGLISH_BELIZE: int
    
    ENGLISH_CANADA: int
    
    ENGLISH_CARIBBEAN: int
    
    ENGLISH_HONG_KONG: int
    
    ENGLISH_INDIA: int
    
    ENGLISH_INDONESIA: int
    
    ENGLISH_IRELAND: int
    
    ENGLISH_JAMAICA: int
    
    ENGLISH_MALAYSIA: int
    
    ENGLISH_NEW_ZEALAND: int
    
    ENGLISH_PHILIPPINES: int
    
    ENGLISH_SINGAPORE: int
    
    ENGLISH_SOUTH_AFRICA: int
    
    ENGLISH_TRINIDAD_AND_TOBAGO: int
    
    ENGLISH_UK: int
    
    ENGLISH_US: int
    
    ENGLISH_ZIMBABWE: int
    
    ESTONIAN: int
    
    ESTONIAN_ESTONIA: int
    
    FAEROESE: int
    
    FAEROESE_FAROE_ISLANDS: int
    
    FILIPINO: int
    
    FINNISH: int
    
    FINNISH_FINLAND: int
    
    FRENCH: int
    
    FRENCH_BELGIUM: int
    
    FRENCH_CAMEROON: int
    
    FRENCH_CANADA: int
    
    FRENCH_CONGO: int
    
    FRENCH_COTE_D_IVOIRE: int
    
    FRENCH_FRANCE: int
    
    FRENCH_HAITI: int
    
    FRENCH_LUXEMBOURG: int
    
    FRENCH_MALI: int
    
    FRENCH_MONACO: int
    
    FRENCH_MOROCCO: int
    
    FRENCH_REUNION: int
    
    FRENCH_SENEGAL: int
    
    FRENCH_SWITZERLAND: int
    
    FRENCH_WEST_INDIES: int
    
    FRISIAN_NETHERLANDS: int
    
    FULFULDE: int
    
    GAELIC_SCOTLAND: int
    
    GALICIAN: int
    
    GALICIAN_GALICIAN: int
    
    GEORGIAN: int
    
    GEORGIAN_GEORGIA: int
    
    GERMAN: int
    
    GERMAN_AUSTRIA: int
    
    GERMAN_GERMANY: int
    
    GERMAN_LIECHTENSTEIN: int
    
    GERMAN_LUXEMBOURG: int
    
    GERMAN_SWITZERLAND: int
    
    GREEK: int
    
    GREEK_GREECE: int
    
    GUARANI: int
    
    GUJARATI: int
    
    GUJARATI_INDIA: int
    
    HAUSA: int
    
    HAWAIIAN: int
    
    HEBREW: int
    
    HEBREW_ISRAEL: int
    
    HINDI: int
    
    HINDI_INDIA: int
    
    HUNGARIAN: int
    
    HUNGARIAN_HUNGARY: int
    
    IBIBIO: int
    
    ICELANDIC: int
    
    ICELANDIC_ICELAND: int
    
    IGBO: int
    
    INDONESIAN: int
    
    INDONESIAN_INDONESIA: int
    
    INUKTITUT: int
    
    INUKTITUT_LATIN_CANADA: int
    
    IRISH_IRELAND: int
    
    ITALIAN: int
    
    ITALIAN_ITALY: int
    
    ITALIAN_SWITZERLAND: int
    
    JAPANESE: int
    
    JAPANESE_JAPAN: int
    
    KANNADA: int
    
    KANNADA_INDIA: int
    
    KANURI: int
    
    KASHMIRI: int
    
    KASHMIRI_ARABIC: int
    
    KAZAKH: int
    
    KAZAKH_KAZAKHSTAN: int
    
    KHMER: int
    
    KISWAHILI: int
    
    KISWAHILI_KENYA: int
    
    KONKANI: int
    
    KONKANI_INDIA: int
    
    KOREAN: int
    
    KOREAN_KOREA: int
    
    KYRGYZ: int
    
    KYRGYZ_KYRGYZSTAN: int
    
    LAO: int
    
    LATIN: int
    
    LATVIAN: int
    
    LATVIAN_LATVIA: int
    
    LITHUANIAN: int
    
    LITHUANIAN_LITHUANIA: int
    
    LUXEMBOUGISH_LUXEMBURG: int
    
    MACEDONIAN: int
    
    MACEDONIAN_FYROM: int
    
    MALAY: int
    
    MALAY_MALAYSIA: int
    
    MALAY_BRUNEI_DARUSSALAM: int
    
    MALAYALAM: int
    
    MALTESE: int
    
    MANIPURI: int
    
    MAORI: int
    
    MAPUDUNGUN_CHILE: int
    
    MARATHI: int
    
    MARATHI_INDIA: int
    
    MOHAWK_MOHAWK: int
    
    MONGOLIAN: int
    
    MONGOLIAN_CYRILLIC: int
    
    MONGOLIAN_MONGOLIAN: int
    
    NEPALI: int
    
    NEPALI_INDIA: int
    
    NORWEGIAN: int
    
    NORWEGIAN_BOKMAL: int
    
    NORWEGIAN_NYNORSK: int
    
    ORIYA: int
    
    OROMO: int
    
    PAPIAMENTU: int
    
    PASHTO: int
    
    PERSIAN: int
    
    PERSIAN_IRAN: int
    
    POLISH: int
    
    POLISH_POLAND: int
    
    PORTUGUESE: int
    
    PORTUGUESE_BRAZIL: int
    
    PORTUGUESE_PORTUGAL: int
    
    PUNJABI: int
    
    PUNJABI_INDIA: int
    
    PUNJABI_PAKISTAN: int
    
    QUECHUA_BOLIVIA: int
    
    QUECHUA_ECUADOR: int
    
    QUECHUA_PERU: int
    
    ROMANIAN: int
    
    ROMANIAN_MOLDOVA: int
    
    ROMANIAN_ROMANIA: int
    
    ROMANSH_SWITZERLAND: int
    
    RUSSIAN: int
    
    RUSSIAN_MOLDOVA: int
    
    RUSSIAN_RUSSIA: int
    
    SAMI_INARI_FINLAND: int
    
    SAMI_LULE_NORWAY: int
    
    SAMI_LULE_SWEDEN: int
    
    SAMI_NORTHERN_FINLAND: int
    
    SAMI_NORTHERN_NORWAY: int
    
    SAMI_NOTHERN_SWEDEN: int
    
    SAMI_SKOLT_FINLAND: int
    
    SAMI_SOUTHERN_NORWAY: int
    
    SAMI_SOUTHERN_SWEDEN: int
    
    SANSKRIT: int
    
    SANSKRIT_INDIA: int
    
    SEPEDI: int
    
    SERBIAN: int
    
    SERBIAN_CYRILLIC_BOSNIA_AND_HERZEGOVINA: int
    
    SERBIAN_CYRILLIC_SERBIA_AND_MONTENEGRO: int
    
    SERBIAN_LATIN_BOSNIA_AND_HERZEGOVINA: int
    
    SERBIAN_LATIN_SERBIA_AND_MONTENEGRO: int
    
    SINDHI: int
    
    SINDHI_DEVANAGARIC: int
    
    SINHALESE: int
    
    SLOVAK: int
    
    SLOVAK_SLOVAKIA: int
    
    SLOVENIAN: int
    
    SLOVENIAN_SLOVENIA: int
    
    SOMALI: int
    
    SORBIAN: int
    
    SPANISH: int
    
    SPANISH_ARGENTINA: int
    
    SPANISH_BOLIVIA: int
    
    SPANISH_CHILE: int
    
    SPANISH_COLOMBIA: int
    
    SPANISH_COSTA_RICA: int
    
    SPANISH_DOMINICAN_REPUBLIC: int
    
    SPANISH_ECUADOR: int
    
    SPANISH_EL_SALVADOR: int
    
    SPANISH_GUATEMALA: int
    
    SPANISH_HONDURAS: int
    
    SPANISH_MEXICO: int
    
    SPANISH_NICARAGUA: int
    
    SPANISH_PANAMA: int
    
    SPANISH_PARAGUAY: int
    
    SPANISH_PERU: int
    
    SPANISH_PUERTO_RICO: int
    
    SPANISH_SPAIN_MODERN_SORT: int
    
    SPANISH_SPAIN_TRADITIONAL_SORT: int
    
    SPANISH_URUGUAY: int
    
    SPANISH_VENEZUELA: int
    
    SUTU: int
    
    SWEDISH: int
    
    SWEDISH_FINLAND: int
    
    SWEDISH_SWEDEN: int
    
    SYRIAC: int
    
    SYRIAC_SYRIA: int
    
    TAJIK: int
    
    TAMAZIGHT: int
    
    TAMAZIGHT_LATIN: int
    
    TAMIL: int
    
    TAMIL_INDIA: int
    
    TATAR: int
    
    TATAR_RUSSIA: int
    
    TELUGU: int
    
    TELUGU_INDIA: int
    
    THAI: int
    
    THAI_THAILAND: int
    
    TIBETAN_BUTAN: int
    
    TIBETAN_CHINA: int
    
    TIGRIGNA_ERITREA: int
    
    TIGRIGNA_ETHIOPIA: int
    
    TSONGA: int
    
    TSWANA: int
    
    TURKISH: int
    
    TURKISH_TURKEY: int
    
    TURKMEN: int
    
    UKRAINIAN: int
    
    UKRAINIAN_UKRAINE: int
    
    URDU: int
    
    URDU_PAKISTAN: int
    
    URDU_INDIAN: int
    
    UZBEK: int
    
    UZBEK_CYRILLIC: int
    
    UZBEK_LATIN: int
    
    VENDA: int
    
    VIETNAMESE: int
    
    VIETNAMESE_VIETNAM: int
    
    WELSH: int
    
    XHOSA: int
    
    YI: int
    
    YIDDISH: int
    
    YORUBA: int
    
    ZULU: int
    

class SummaryLength(Enum):
    """Enumerates possible lengths of summary."""
    
    """Try to generate 1-2 sentences."""
    VERY_SHORT: int
    
    """Try to generate 3-4 sentences."""
    SHORT: int
    
    """Try to generate 5-6 sentences."""
    MEDIUM: int
    
    """Try to generate 7-10 sentences."""
    LONG: int
    
    """Try to generate 11-20 sentences."""
    VERY_LONG: int
    

