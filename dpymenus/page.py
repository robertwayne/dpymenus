# -*- coding: utf-8 -*-
"""
The MIT License (MIT)

Copyright (c) 2020 Rob Wagner

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from typing import Callable, Optional

from discord import Embed


class Page:
    """Represents a single page inside a menu.

    Attributes:
        name: The page name.
        embed: A Discord.Embed object; used for displaying the page.
        func: Reference to a function called when the page loads. Should be None on the last page.
    """
    __slots__ = ('name', 'embed', 'func')

    def __init__(self, name: str, embed: Embed, func: Optional[Callable]):
        self.name = name
        self.embed = embed
        self.func = func
