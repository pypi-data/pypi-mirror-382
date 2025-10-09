# coding=utf-8
# Copyright (c) 2025 Jifeng Wu
# Licensed under the MIT License. See LICENSE file in the project root for full license information.
import sys
from textcompat import text_to_stdout_str, stdin_str_to_text
from typing import Text

if sys.version_info < (3,):
    def unicode_raw_input(prompt=u''):
        # type: (Text) -> Text
        return stdin_str_to_text(raw_input(text_to_stdout_str(prompt)))
else:
    def unicode_raw_input(prompt=u''):
        # type: (Text) -> Text
        return input(prompt)