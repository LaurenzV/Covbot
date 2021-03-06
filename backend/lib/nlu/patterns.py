from typing import List

from nltk import PorterStemmer
from spacy.matcher import DependencyMatcher
from spacy.tokens import Span
from lib.spacy_components.custom_spacy import CustomSpacy

_stemmer: PorterStemmer = PorterStemmer()


class Pattern:
    """Class that contains the necessary patterns for intent recognition."""
    _people_trigger_words: list = [_stemmer.stem(word) for word in ["human", "people", "person", "individual"]]
    _vaccine_trigger_words: list = [_stemmer.stem(word) for word in
                                    ["shot", "vaccine", "jab", "inoculation", "immunization",
                                     "administer"]]
    _cases_trigger_words: list = [_stemmer.stem(word) for word in ["case", "infection", "test", "positive", "negative"]]
    _covid_trigger_words: list = [_stemmer.stem(word) for word in ["covid", "covid-19", "covid19"]]

    human_pattern: List[dict] = [{
        "RIGHT_ID": "human_pattern",
        "RIGHT_ATTRS": {
            "_": {
                "stem": {
                    "IN": _people_trigger_words
                }
            }
        }
    }]

    covid_pattern: List[dict] = [{
        "RIGHT_ID": "covid_pattern",
        "RIGHT_ATTRS": {
            "_": {
                "stem": {
                    "IN": _covid_trigger_words
                }
            }
        }
    }]

    case_trigger_pattern: List[dict] = [{
        "RIGHT_ID": "case_trigger_pattern",
        "RIGHT_ATTRS": {
            "_": {
                "stem": {
                    "IN": _cases_trigger_words
                }
            }
        }
    }]

    country_pattern: List[dict] = [{
        "RIGHT_ID": "country_pattern",
        "RIGHT_ATTRS": {
            "LEMMA": {
                "IN": ["country", "nation"]
            }
        }
    }]

    how_pattern: List[dict] = [
        {
            "RIGHT_ID": "how_pattern",
            "RIGHT_ATTRS": {
                "LEMMA": "how"
            }
        }
    ]

    what_pattern: List[dict] = [
        {
            "RIGHT_ID": "what_pattern",
            "RIGHT_ATTRS": {
                "LEMMA": {
                    "IN": ["which", "what"]
                }
            }
        }
    ]

    when_pattern: List[dict] = [
        {
            "RIGHT_ID": "when_pattern",
            "RIGHT_ATTRS": {
                "LEMMA": "when"
            }
        }
    ]

    where_pattern: List[dict] = [
        {
            "RIGHT_ID": "where_pattern",
            "RIGHT_ATTRS": {
                "LEMMA": "where"
            }
        }
    ]

    number_pattern: List[dict] = [{
        "RIGHT_ID": "number_pattern",
        "RIGHT_ATTRS": {
            "LEMMA": {
                "IN": ["amount", "number"]
            }
        }
    }]

    most_pattern: List[dict] = [{
        "RIGHT_ID": "most_pattern",
        "RIGHT_ATTRS": {
            "LEMMA": {
                "IN": ["most"]
            }
        }
    }]

    least_pattern: List[dict] = [{
        "RIGHT_ID": "least_pattern",
        "RIGHT_ATTRS": {
            "LEMMA": {
                "IN": ["few", "least"]
            }
        }
    }]

    vaccine_trigger_pattern: List[dict] = [{
        "RIGHT_ID": "vaccine_trigger_pattern",
        "RIGHT_ATTRS": {
            "_": {
                "stem": {
                    "IN": _vaccine_trigger_words
                }
            }
        }
    }]

    covid_vaccine_pattern: List[dict] = covid_pattern + [{
        "LEFT_ID": "covid_pattern",
        "REL_OP": "<",
        "RIGHT_ID": "covid_vaccine_pattern",
        "RIGHT_ATTRS": {
            "_": {
                "stem": {
                    "IN": _vaccine_trigger_words
                }
            }
        }
    }]

    vaccine_covid_pattern: List[dict] = vaccine_trigger_pattern + [{
        "LEFT_ID": "vaccine_trigger_pattern",
        "REL_OP": ">>",
        "RIGHT_ID": "vaccine_covid_pattern",
        "RIGHT_ATTRS": {
            "_": {
                "stem": {
                    "IN": _covid_trigger_words
                }
            }
        }
    }]

    how_many_pattern: List[dict] = how_pattern + [
        {
            "LEFT_ID": "how_pattern",
            "REL_OP": "<",
            "RIGHT_ID": "how_many_pattern",
            "RIGHT_ATTRS": {
                "LEMMA": "many"
            }
        }]

    what_day_pattern: List[dict] = what_pattern + [
        {
            "LEFT_ID": "what_pattern",
            "REL_OP": "<<",
            "RIGHT_ID": "what_day_pattern",
            "RIGHT_ATTRS": {
                "LEMMA": {
                    "IN": ["day", "time", "date"]
                }
            }
        }
    ]

    what_country_pattern: List[dict] = what_pattern + [
        {
            "LEFT_ID": "what_pattern",
            "REL_OP": "<<",
            **country_pattern[0]
        }
    ]

    what_is_country_pattern: List[dict] = what_pattern + [
        {
            "LEFT_ID": "what_pattern",
            "REL_OP": "$++",
            **country_pattern[0]
        }
    ]

    number_of_pattern: List[dict] = number_pattern + [
        {
            "LEFT_ID": "number_pattern",
            "REL_OP": ">",
            "RIGHT_ID": "number_of_pattern",
            "RIGHT_ATTRS": {
                "LEMMA": "of"
            }
        }
    ]

    maximum_number_pattern: List[dict] = number_pattern + [
        {
            "LEFT_ID": "number_pattern",
            "REL_OP": ">",
            "RIGHT_ID": "maximum_number_pattern",
            "RIGHT_ATTRS": {
                "LEMMA": {
                    "IN": ["maximum", "maximal", "high", "peak"]
                }
            }
        }
    ]

    minimum_number_pattern: List[dict] = number_pattern + [
        {
            "LEFT_ID": "number_pattern",
            "REL_OP": ">",
            "RIGHT_ID": "minimum_number_pattern",
            "RIGHT_ATTRS": {
                "LEMMA": {
                    "IN": ["minimum", "minimal", "low"]
                }
            }
        }
    ]

    most_trigger_word_pattern: List[dict] = most_pattern + [
        {
            "LEFT_ID": "most_pattern",
            "REL_OP": "<<",
            "RIGHT_ID": "most_trigger_word_pattern",
            "RIGHT_ATTRS": {
                "_": {
                    "stem": {
                        "IN": _vaccine_trigger_words + _cases_trigger_words + _people_trigger_words
                    }
                }
            }
        }
    ]

    least_trigger_word_pattern: List[dict] = least_pattern + [
        {
            "LEFT_ID": "least_pattern",
            "REL_OP": "<<",
            "RIGHT_ID": "least_trigger_word_pattern",
            "RIGHT_ATTRS": {
                "_": {
                    "stem": {
                        "IN": _vaccine_trigger_words + _cases_trigger_words + _people_trigger_words
                    }
                }
            }
        }
    ]

    @staticmethod
    def has_valid_pattern(span: Span, pattern: list) -> bool:
        """Checks whether a given span matches a list of patterns."""
        matcher: DependencyMatcher = DependencyMatcher(CustomSpacy.get_spacy().vocab)

        matcher.add("pattern", pattern)
        result: list = matcher(span)

        return len(result) > 0
