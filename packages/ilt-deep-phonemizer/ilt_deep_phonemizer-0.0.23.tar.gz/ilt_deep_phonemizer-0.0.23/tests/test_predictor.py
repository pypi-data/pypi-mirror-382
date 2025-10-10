import unittest
from typing import Any, Dict, Tuple
from unittest.mock import patch

import torch

from deep_phonemizer.model.model import Model
from deep_phonemizer.model.predictor import Predictor
from deep_phonemizer.preprocessing.text import Preprocessor


class ModelMock:

    def generate(
        self, batch: Dict[str, Any], **kwargs
    ) -> Tuple[torch.tensor, torch.tensor]:
        """Return input and ones as probs"""
        tokens = batch["text"]
        probs = torch.ones(tokens.size())
        return tokens, probs


@patch.object(Model, "generate", new_callable=ModelMock)
class TestPredictor(unittest.TestCase):

    def test_call_with_model_mock(self, model_mock: Model) -> None:
        config = {
            "preprocessing": {
                "text_symbols": "abcd",
                "phoneme_symbols": "abcd",
                "char_repeats": 1,
                "languages": ["de"],
                "lowercase": False,
            },
        }
        preprocessor = Preprocessor.from_config(config)
        predictor = Predictor(model_mock, preprocessor)
        texts = ["ab", "cde"]

        result = predictor(texts, lang="de", batch_size=8)
        self.assertEqual(2, len(result))
        self.assertEqual("ab", result[0].word)
        self.assertEqual("ab", result[0].phonemes)
        self.assertEqual("cd", result[1].phonemes)

        result = predictor(texts, lang="de", batch_size=1)
        self.assertEqual(2, len(result))
        self.assertEqual("ab", result[0].phonemes)
        self.assertEqual("cd", result[1].phonemes)

        texts = ["/"]
        result = predictor(texts, lang="de", batch_size=1)
        self.assertEqual(1, len(result))
        self.assertEqual("", result[0].phonemes)
        self.assertEqual([], result[0].phoneme_tokens)
