# bandripper

Download albums from bandcamp using the command line.  
Only works for public tracks.  
Quality is limited to mp3 at 128 kbps.

## Installation

Install with:

```console
pip install bandripper
```

## Usage

##### Options

```console
> bandripper -h
Usage: bandripper [-h] [-n] [-o] [-nr] [str ...]

Positional Arguments:
  str                   The bandcamp url(s) for the album or artist. If the url is to an artists
                        main page, all albums will be downloaded. The tracks will be saved to a
                        subdirectory of your current directory. If a track can't be streamed (i.e.
                        private) it won't be downloaded. Multiple urls can be passed. (default: None)

Options:
  -h, --help            show this help message and exit
  -n, --no_track_number
                        By default the track number will be added to the front of the track title.
                        Pass this switch to disable the behavior. (default: False)
  -o, --overwrite       Pass this flag to overwrite existing files. Otherwise tracks that already
                        exist locally will not be downloaded. (default: False)
  -nr, --new_releases   Check urls in `discography_urls.txt` for new releases and download them. A
                        discography url is automatically added to the file when bandripper is used
                        on it. (default: False)
```

e.g.

```console
>bandripper https://blacklungwinter.bandcamp.com/releases
Downloading 5 tracks from Bodies of EarthHearts of Space by Blacklung Winter... ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100.00% 0s
>dir "./Blacklung Winter/Bodies of EarthHearts of Space"
03/22/2023  01:46 PM           228,335 Bodies of EarthHearts of Space.jpg
03/22/2023  01:46 PM         3,008,887 01 - Bodies of EarthHearts of Space.mp3
03/22/2023  01:46 PM         3,441,057 02 - Dead in the Water.mp3
03/22/2023  01:46 PM         2,792,802 03 - Yin and Yang.mp3
03/22/2023  01:46 PM         3,326,954 04 - Neurotoxin.mp3
03/22/2023  01:46 PM         3,836,446 05 - Uproot.mp3
```
