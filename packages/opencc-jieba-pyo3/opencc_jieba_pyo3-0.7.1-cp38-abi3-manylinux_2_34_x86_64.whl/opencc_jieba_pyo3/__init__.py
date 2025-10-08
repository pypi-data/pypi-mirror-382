from .opencc_jieba_pyo3 import OpenCC as _OpenCC
from typing import List, Tuple


class OpenCC(_OpenCC):
    CONFIG_LIST = [
        "s2t", "t2s", "s2tw", "tw2s", "s2twp", "tw2sp", "s2hk", "hk2s",
        "t2tw", "tw2t", "t2twp", "tw2tp", "t2hk", "hk2t", "t2jp", "jp2t"
    ]

    def __init__(self, config="s2t"):
        self.config = config if config in self.CONFIG_LIST else "s2t"

    def set_config(self, config):
        """
        Set the conversion configuration.

        :param config: One of OpenCC.CONFIG_LIST
        """
        if config in self.CONFIG_LIST:
            self.config = config
        else:
            self.config = "s2t"

    def get_config(self):
        """
        Get the current conversion config.

        :return: Current config string
        """
        return self.config

    @classmethod
    def supported_configs(cls):
        """
        Return a list of supported conversion config strings.

        :return: List of config names
        """
        return cls.CONFIG_LIST

    def zho_check(self, input_text):
        """
        Heuristically determine whether input text is Simplified or Traditional Chinese.

        :param input_text: Input string
        :return: 0 = unknown, 2 = simplified, 1 = traditional
        """
        return super().zho_check(input_text)

    def convert(self, input_text, punctuation=False):
        """
        Automatically dispatch to the appropriate conversion method based on `self.config`.

        :param input_text: The string to convert
        :param punctuation: Whether to apply punctuation conversion
        :return: Converted string or error message
        """
        return super().convert(input_text, punctuation)

    def jieba_cut(self, input_text: str, hmm: bool = True) -> List[str]:
        """
        Perform word segmentation on the input text using Jieba.

        :param input_text: The input string to segment.
        :param hmm: Whether to enable the Hidden Markov Model (HMM) for new word discovery.
        :return: A list of segmented words.
        """
        return super().jieba_cut(input_text, hmm)

    def jieba_cut_and_join(self, input_text: str, delimiter: str = "/") -> str:
        """
        Perform word segmentation and join the words with a custom delimiter.

        :param input_text: The input string to segment.
        :param delimiter: Delimiter to use between segmented words.
        :return: A single string with segmented words joined by the delimiter.
        """
        return super().jieba_cut_and_join(input_text, delimiter)

    def jieba_keyword_extract_textrank(self, input_text: str, top_k: int) -> List[str]:
        """
        Extract top keywords using the TextRank algorithm.

        :param input_text: The input text to analyze.
        :param top_k: The number of top keywords to extract.
        :return: A list of top keywords.
        """
        return super().jieba_keyword_extract_textrank(input_text, top_k)

    def jieba_keyword_extract_tfidf(self, input_text: str, top_k: int) -> List[str]:
        """
        Extract top keywords using the TF-IDF algorithm.

        :param input_text: The input text to analyze.
        :param top_k: The number of top keywords to extract.
        :return: A list of top keywords.
        """
        return super().jieba_keyword_extract_tfidf(input_text, top_k)

    def jieba_keyword_weight_textrank(self, input_text: str, top_k: int) -> List[Tuple[str, float]]:
        """
        Extract top keywords with their weights using the TextRank algorithm.

        :param input_text: The input text to analyze.
        :param top_k: The number of top keywords to extract.
        :return: A list of (keyword, weight) tuples.
        """
        return super().jieba_keyword_weight_textrank(input_text, top_k)

    def jieba_keyword_weight_tfidf(self, input_text: str, top_k: int) -> List[Tuple[str, float]]:
        """
        Extract top keywords with their weights using the TF-IDF algorithm.

        :param input_text: The input text to analyze.
        :param top_k: The number of top keywords to extract.
        :return: A list of (keyword, weight) tuples.
        """
        return super().jieba_keyword_weight_tfidf(input_text, top_k)
