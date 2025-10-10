from .bandripper import (
    Album,
    AlbumParser,
    AlbumRipper,
    BandRipper,
    Track,
    page_is_discography,
)

__version__ = "0.3.1"
__all__ = [
    "BandRipper",
    "AlbumRipper",
    "Track",
    "Album",
    "AlbumParser",
    "page_is_discography",
]
