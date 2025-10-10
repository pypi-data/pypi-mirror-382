import json
import re
import string
from collections.abc import Callable
from dataclasses import dataclass, field
from urllib.parse import ParseResult, urlparse

import argshell
import quickpool
from bs4 import BeautifulSoup, Tag  # type: ignore
from gruel import Response
from noiftimer import Timer
from pathier import Pathier
from printbuddies import ColorMap
from printbuddies.colormap import Tag as ColorTag
from requests import HTTPError
from rich.console import Console
from typing_extensions import Any

import bandripper.request

console = Console(style="pink1")
color = ColorMap()
root: Pathier = Pathier(__file__).parent
discog_urls = Pathier("discography_urls.txt")

# lazy way of treating the session object like a singleton, don't @ me
request: Callable[..., Any] = bandripper.request.get_session().get


@dataclass
class Colors:
    title: ColorTag = field(default_factory=lambda: color.a1)
    status: ColorTag = field(default_factory=lambda: color.br)
    highlight: ColorTag = field(default_factory=lambda: color.dp1)
    number: ColorTag = field(default_factory=lambda: color.bg)
    url: ColorTag = field(default_factory=lambda: color.t2)


colors = Colors()


@dataclass
class Track:
    title: str
    number: int
    url: str

    @property
    def file_name(self) -> str:
        """This track's title suffixed with `.mp3`."""
        return f"{self.title}.mp3"

    @property
    def numbered_file_name(self) -> str:
        """This track's numbered title suffixed with `.mp3`."""
        return f"{self.numbered_title}.mp3"

    @property
    def numbered_title(self) -> str:
        num = str(self.number)
        if len(num) == 1:
            num: str = "0" + num
        return f"{num} - {self.title}"

    def download(self) -> bytes | None:
        """Download this track and return the data."""
        response: Response = Response()
        fail_message = f"Download for {colors.url}{self.title}[/] failed"
        try:
            response = request(self.url)
            response.raise_for_status()
            return response.content
        except HTTPError as e:
            console.print(
                f"{fail_message} with status code {colors.status}{response.status_code}."
            )
        except Exception as e:
            console.print(f"{fail_message}:")
            console.print(e)


@dataclass
class Album:
    artist: str
    title: str
    tracks: list[Track]
    art_url: str | None = None

    def __repr__(self) -> str:
        return f"{self.title} by {self.artist}"

    @property
    def art_file_name(self) -> str:
        """Returns the album title with `.jpg` suffixed to it."""
        return f"{self.title}.jpg"

    @property
    def rich_str(self) -> str:
        """A rich tagged string for `"{self.title} by {self.artist}"`."""
        return f"{colors.title}{self.title}[/] by {colors.highlight}{self.artist}[/]"

    def download_art(self) -> bytes | None:
        """Download and return album art if this instance has an `art_url`."""
        if not self.art_url:
            console.print(f"No `art_url` provided for {self.rich_str}.")
            return None
        fail_message: str = f"Downloading album art for {self.rich_str} failed"
        response: Response = Response()
        try:
            response = request(self.art_url)
            response.raise_for_status()
            return response.content
        except HTTPError as e:
            console.print(
                f"{fail_message} with status code {colors.status}{response.status_code}."
            )
            raise e
        except Exception as e:
            console.print(f"{fail_message}:")
            console.print(e)


class AlbumParser:
    def __init__(self, html: str) -> None:
        """Parse album details from the html of a bandcamp album page."""
        self._soup = BeautifulSoup(html, "html.parser")

    @property
    def soup(self) -> BeautifulSoup:
        return self._soup

    def clean_string(self, text: str) -> str:
        """Remove punctuation and trailing spaces from text."""
        return re.sub(f"[{re.escape(string.punctuation)}]", "", text).strip()

    def get_album_art_url(self) -> str | None:
        """Returns the url for album art if there is one."""
        image_meta: Tag | None = self.soup.find(  # type:ignore
            "meta", attrs={"property": "og:image"}
        )
        if isinstance(image_meta, Tag):
            image_meta_content: Any = image_meta.get("content")  # type:ignore
            if isinstance(image_meta_content, str):
                return image_meta_content
        return None

    def get_album_data(self) -> dict[str, Any] | None:
        """Returns a dictionary containing album data if it's present."""
        for script in self.soup.find_all("script"):  # type:ignore
            if script.get("data-cart"):  # type:ignore
                return json.loads(script.attrs["data-tralbum"])  # type:ignore
        return None

    def parse(self) -> Album | None:
        """Parse album page and return `Album` object."""
        if data := self.get_album_data():
            artist: str = self.clean_string(data["artist"])
            title: str = self.clean_string(data["current"]["title"])
            tracks: list[Track] = [
                Track(
                    self.clean_string(track["title"]),
                    track["track_num"],
                    track["file"]["mp3-128"],
                )
                for track in data["trackinfo"]
                if track.get("file")
            ]
            art_url: str | None = self.get_album_art_url()
            return Album(artist, title, tracks, art_url)
        return None


class AlbumRipper:
    def __init__(
        self, album_url: str, no_track_number: bool = False, overwrite: bool = False
    ) -> None:
        """
        :param no_track_number: If True, don't add the track
        number to the front of the track title."""
        self.album_url: str = album_url
        self.no_track_number: bool = no_track_number
        self.overwrite: bool = overwrite
        self._save_path: Pathier | None = None
        self._failed_rips: list[Track] = []

    @property
    def failed_rips(self) -> list[Track]:
        """Returns a list of `Track` objects that failed to download."""
        return self._failed_rips

    @property
    def save_path(self) -> Pathier | None:
        """The path to save tracks to.
        Returns `None` if `self.make_save_path()` hasn't been called on an `Album` instance.
        """
        return self._save_path

    class NoSavePathError(RuntimeError):
        def __init__(self, album: Album | None = None) -> None:
            end_message = "Pass an `Album` instance to `self.make_save_path()` before doing what you just did."
            if not album:
                message: str = f"No save path set for this album."
            else:
                message: str = f"No save path set for {album.title} by {album.artist}."
            super().__init__(" ".join([message, end_message]))

    def get_album_page(self) -> str:
        """Make a request to `self.album_url` and return the text content."""
        response: Response = Response()
        try:
            response = request(self.album_url)
            response.raise_for_status()
        except HTTPError as e:
            console.print(f"Failed to retrieve page at {colors.url}{self.album_url}.")
            console.print(
                f"Failed with status code {colors.status}{response.status_code}."
            )
            raise e
        except Exception as e:
            console.print(f"Failed to retrieve page at {colors.url}{self.album_url}.")
            raise e
        return response.text

    def make_save_path(self, album: Album):
        """Create save path from album: `{current directory}/{artist}/{album}`"""
        self._save_path = Pathier.cwd() / album.artist / album.title
        self._save_path.mkdir(parents=True, exist_ok=True)

    def filter_existing_tracks(
        self, tracks: list[Track]
    ) -> tuple[list[Track], list[Track]]:
        """Splits `tracks` into a list of tracks that don't exist at the save location and a list of tracks that do.

        Return order is `(non_existing_tracks, existing_tracks)`."""
        non_existing_tracks: list[Track] = []
        existing_tracks: list[Track] = []
        for track in tracks:
            if self.track_exists(track):
                existing_tracks.append(track)
            else:
                non_existing_tracks.append(track)
        return non_existing_tracks, existing_tracks

    def get_track_download_list(self, album: Album) -> list[Track]:
        """Returns a list of tracks to download from an `Album` instance."""
        tracks_to_download: list[Track] = []
        existing_tracks: list[Track] = []
        if self.overwrite:
            tracks_to_download = album.tracks
        else:
            tracks_to_download, existing_tracks = self.filter_existing_tracks(
                album.tracks
            )
        if existing_tracks:
            if len(existing_tracks) == len(album.tracks):
                console.print(
                    f"Album {album.rich_str} already exists, skipping download."
                )
            else:
                for track in existing_tracks:
                    console.print(
                        f"Track {colors.title}{track.title}[/] already exists, skipping download."
                    )
            console.print(
                f"Rerun {colors.highlight}bandripper[/] command with the `{color.go1}-o[/]` flag to overwrite existing tracks."
            )
        return tracks_to_download

    def rip(self) -> Album:
        """Download and save the album tracks and album art."""
        album: Album | None = AlbumParser(self.get_album_page()).parse()
        if not album:
            raise RuntimeError(f"No album data was found on {self.album_url}.")
        num_tracks: int = len(album.tracks)
        if num_tracks == 0:
            console.print(f"No public tracks available for {album.rich_str}.")
            return album
        self.make_save_path(album)
        assert self.save_path
        self.save_album_art(album)

        tracks_to_download: list[Track] = self.get_track_download_list(album)
        if not tracks_to_download:
            return album

        num_tracks_to_download: int = len(tracks_to_download)
        quickpool.ThreadPool(
            [self.save_track] * num_tracks_to_download,
            [(track,) for track in tracks_to_download],
            max_workers=5,
        ).execute(
            description=f"Downloading {colors.number}{num_tracks_to_download}[/] tracks from {album.rich_str}..."
        )
        console.print("Download complete.")
        if self.failed_rips:
            console.print("The following tracks failed to download:")
            for track in self.failed_rips:
                console.print(f"  {colors.title}{track.title}")
        return album

    def save_album_art(self, album: Album) -> None:
        """Download and save album art if it has any."""
        if not self.save_path:
            raise self.NoSavePathError(album)
        if album.art_url:
            art: bytes | None = album.download_art()
            if art:
                (self.save_path / album.art_file_name).write_bytes(art)
        else:
            console.print(f"No album art detected for {album.rich_str}.")

    def save_track(self, track: Track) -> bool:
        """Save `track`.
        Returns whether the download was successful or not."""
        if not self.save_path:
            raise self.NoSavePathError()
        file_path: Pathier = self.save_path / (
            track.file_name if self.no_track_number else track.numbered_file_name
        )
        content: bytes | None = track.download()
        if content:
            file_path.write_bytes(content)
            return True
        self._failed_rips.append(track)
        return False

    def track_exists(self, track: Track) -> bool:
        """Return if a track already exists in `self.save_path`."""
        if not self.save_path:
            raise self.NoSavePathError()
        path: Pathier = self.save_path / (
            track.file_name if self.no_track_number else track.numbered_file_name
        )
        return path.exists()


class BandRipper:
    def __init__(
        self,
        band_url: str,
        no_track_number: bool = False,
        overwrite: bool = False,
        discography_page_html: str | None = None,
    ) -> None:
        self.band_url: str = band_url
        self.no_track_number: bool = no_track_number
        self.overwrite: bool = overwrite
        self.album_rippers: list[AlbumRipper] = []
        self.discography_page_html: str | None = discography_page_html

    def get_album_urls(self) -> list[str]:
        """Get album urls from the main bandcamp url."""
        if not self.discography_page_html:
            self.discography_page_html = self.get_discography_page()
        soup = BeautifulSoup(self.discography_page_html, "html.parser")
        grid: Tag | None = soup.find("ol", attrs={"id": "music-grid"})  # type:ignore
        assert isinstance(grid, Tag)
        parsed_url: ParseResult = urlparse(self.band_url)
        base_url: str = f"https://{parsed_url.netloc}"
        urls: list[str] = [  # type:ignore
            base_url + album.a.get("href")  # type:ignore
            for album in grid.find_all("li")  # type:ignore
        ]
        # Sometimes label pages link to a band's bandcamp instead of hosting the album
        # so we gotta fix double urls
        return [
            url if url.count("http") == 1 else url[url.find("http", 1) :]
            for url in urls
        ]

    def get_discography_page(self) -> str:
        url: str = f"{colors.url}{self.band_url}[/]"
        console.print(f"Fetching discography from {url}...")
        response: Response = Response()
        try:
            response = request(self.band_url)
            response.raise_for_status()
        except HTTPError as e:
            console.print(f"Failed to access {url}.")
            console.print(f"Status code: {colors.status}{response.status_code}")
            raise e
        except Exception as e:
            console.print(f"Failed to access {url}.")
            raise e
        return response.text

    def save_discog_url(self) -> None:
        """Add discog url to txt file if it isn't in there."""
        discog_urls.touch()
        urls: list[str] = discog_urls.split("utf-8")
        if self.band_url not in urls:
            urls.append(self.band_url)
        discog_urls.join(sorted(urls))

    def rip(self) -> list[Album]:
        """Rip all publicly available albums from the discography page.
        Returns a list of `Album` objects that were ripped."""
        console.print(f"Searching {colors.url}{self.band_url}[/] for albums...")
        for url in self.get_album_urls():
            self.album_rippers.append(
                AlbumRipper(url, self.no_track_number, self.overwrite)
            )
        # Save discography url to list after successfully getting albums from it
        self.save_discog_url()

        console.print(f"Found {colors.number}{len(self.album_rippers)}[/] albums.")
        console.print(f"Beginning rip...")
        timer = Timer(subsecond_resolution=True)
        timer.start()
        fails: list[tuple[AlbumRipper, Exception]] = []
        albums: list[Album] = []
        for ripper in self.album_rippers:
            try:
                album: Album = ripper.rip()
                albums.append(album)
            except Exception as e:
                fails.append((ripper, e))
        timer.stop()
        console.print(
            f"Finished downloading {colors.number}{len(self.album_rippers)}[/] albums in {colors.highlight}{timer.elapsed_str}."
        )
        if fails:
            console.print(f"The following downloads failed:")
            for fail in fails:
                console.print(
                    f"{colors.url}{fail[0].album_url}[/]: {colors.status}{fail[1]}"
                )
        return albums


def page_is_discography(url: str) -> str | None:
    """Returns the page text if `url` is a discography page.
    `None` if it isn't."""
    response: Response = request(url)
    response.raise_for_status()
    if '<ol id="music-grid"' in response.text:
        return response.text


def get_args() -> argshell.Namespace:
    parser = argshell.ArgumentParser()
    parser.add_argument(
        "urls",
        type=str,
        nargs="*",
        help=""" The bandcamp url(s) for the album or artist. 
        If the url is to an artists main page, all albums will be downloaded. 
        The tracks will be saved to a subdirectory of your current directory. 
        If a track can't be streamed (i.e. private) it won't be downloaded.
        Multiple urls can be passed.""",
    )
    parser.add_argument(
        "-n",
        "--no_track_number",
        action="store_true",
        help=""" By default the track number will be added to the front of the track title. 
        Pass this switch to disable the behavior.""",
    )
    parser.add_argument(
        "-o",
        "--overwrite",
        action="store_true",
        help=""" Pass this flag to overwrite existing files. 
        Otherwise tracks that already exist locally will not be downloaded.""",
    )
    parser.add_argument(
        "-nr",
        "--new_releases",
        action="store_true",
        help=""" Check urls in `discography_urls.txt` for new releases and download them.
        A discography url is automatically added to the file when bandripper is used on it.""",
    )
    args = parser.parse_args()
    args.urls = [url.strip("/") for url in args.urls]

    return args


def load_discog_urls() -> list[str]:
    if not discog_urls.exists():
        console.print(
            f"No `{colors.title}discography_urls.txt[/]` exists at this location."
        )
        return []
    return discog_urls.split("utf-8")


def main(args: argshell.Namespace | None = None):
    if not args:
        args = get_args()

    if args.new_releases:
        console.print("Loading previously accessed discography urls...")
        urls = load_discog_urls()
        if urls:
            console.print("Checking the following urls for new releases:")
            console.print(*[f"{colors.url}{url}" for url in urls], sep="\n")
            args.urls.extend(urls)

    for url in args.urls:
        if discography_page := page_is_discography(url):
            ripper = BandRipper(
                url, args.no_track_number, args.overwrite, discography_page
            )
        else:
            ripper = AlbumRipper(url, args.no_track_number, args.overwrite)
        ripper.rip()


if __name__ == "__main__":
    main(get_args())
