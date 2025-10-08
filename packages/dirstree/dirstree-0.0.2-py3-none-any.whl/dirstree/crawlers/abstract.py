from abc import ABC, abstractmethod
from typing import Generator
from pathlib import Path

from cantok import AbstractToken, DefaultToken


class AbstractCrawler(ABC):
    def __iter__(self) -> Generator[Path, None, None]:
        yield from self.go()

    def __add__(self, other: 'AbstractCrawler') -> 'AbstractCrawler':
        if not isinstance(other, AbstractCrawler):
            raise TypeError(f"Cannot add {type(self).__name__} and {type(other).__name__}.")

        from dirstree.crawlers.group import CrawlersGroup

        return CrawlersGroup([self, other])

    @abstractmethod
    def go(self, token: AbstractToken = DefaultToken()) -> Generator[Path, None, None]:
        ...  # pragma: no cover
