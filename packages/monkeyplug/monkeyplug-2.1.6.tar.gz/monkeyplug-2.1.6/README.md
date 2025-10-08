# monkeyplug

[![Latest Version](https://img.shields.io/pypi/v/monkeyplug)](https://pypi.python.org/pypi/monkeyplug/) [![VOSK Docker Images](https://github.com/mmguero/monkeyplug/workflows/monkeyplug-build-push-vosk-ghcr/badge.svg)](https://github.com/mmguero/monkeyplug/pkgs/container/monkeyplug) [![Whisper Docker Images](https://github.com/mmguero/monkeyplug/workflows/monkeyplug-build-push-whisper-ghcr/badge.svg)](https://github.com/mmguero/monkeyplug/pkgs/container/monkeyplug)

**monkeyplug** is a little script to censor profanity in audio files (intended for podcasts, but YMMV) in a few simple steps:

1. The user provides a local audio file (or a URL pointing to an audio file which is downloaded)
2. Either [Whisper](https://openai.com/research/whisper) ([GitHub](https://github.com/openai/whisper)) or the [Vosk](https://alphacephei.com/vosk/)-[API](https://github.com/alphacep/vosk-api) is used to recognize speech in the audio file
3. Each recognized word is checked against a [list](./src/monkeyplug/swears.txt) of profanity or other words you'd like muted
4. [`ffmpeg`](https://www.ffmpeg.org/) is used to create a cleaned audio file, muting or "bleeping" the objectional words

You can then use your favorite media player to play the cleaned audio file.

If provided a video file for input, **monkeyplug** will attempt to process the audio stream from the file and remultiplex it, copying the original video stream. 

**monkeyplug** is part of a family of projects with similar goals:

* 📼 [cleanvid](https://github.com/mmguero/cleanvid) for video files (using [SRT-formatted](https://en.wikipedia.org/wiki/SubRip#Format) subtitles)
* 🎤 [monkeyplug](https://github.com/mmguero/monkeyplug) for audio and video files (using either [Whisper](https://openai.com/research/whisper) or the [Vosk](https://alphacephei.com/vosk/)-[API](https://github.com/alphacep/vosk-api) for speech recognition)
* 📕 [montag](https://github.com/mmguero/montag) for ebooks

## Installation

Using `pip`, to install the latest [release from PyPI](https://pypi.org/project/monkeyplug/):

```
python3 -m pip install -U monkeyplug
```

Or to install directly from GitHub:


```
python3 -m pip install -U 'git+https://github.com/mmguero/monkeyplug'
```

## Prerequisites

[monkeyplug](./src/monkeyplug/monkeyplug.py) requires:

* [FFmpeg](https://www.ffmpeg.org)
* Python 3
    - [mutagen](https://github.com/quodlibet/mutagen)
    - a speech recognition library, either of:
        + [Whisper](https://github.com/openai/whisper)
        + [vosk-api](https://github.com/alphacep/vosk-api) with a VOSK [compatible model](https://alphacephei.com/vosk/models)

To install FFmpeg, use your operating system's package manager or install binaries from [ffmpeg.org](https://www.ffmpeg.org/download.html). The Python dependencies will be installed automatically if you are using `pip` to install monkeyplug, except for [`vosk`](https://pypi.org/project/vosk/) or [`openai-whisper`](https://pypi.org/project/openai-whisper/); as monkeyplug can work with both speech recognition engines, there is not a hard installation requirement for either until runtime.

## usage

```
usage: monkeyplug.py <arguments>

monkeyplug.py

options:
  -v, --verbose [true|false]
                        Verbose/debug output
  -m, --mode <string>   Speech recognition engine (whisper|vosk) (default: whisper)
  -i, --input <string>  Input file (or URL)
  -o, --output <string>
                        Output file
  --output-json <string>
                        Output file to store transcript JSON
  -w, --swears <profanity file>
                        text file containing profanity (default: "swears.txt")
  -a, --audio-params APARAMS
                        Audio parameters for ffmpeg (default depends on output audio codec)
  -c, --channels <int>  Audio output channels (default: 2)
  -s, --sample-rate <int>
                        Audio output sample rate (default: 48000)
  -f, --format <string>
                        Output file format (default: inferred from extension of --output, or "MATCH")
  --pad-milliseconds <int>
                        Milliseconds to pad on either side of muted segments (default: 0)
  --pad-milliseconds-pre <int>
                        Milliseconds to pad before muted segments (default: 0)
  --pad-milliseconds-post <int>
                        Milliseconds to pad after muted segments (default: 0)
  -b, --beep [true|false]
                        Beep instead of silence
  -h, --beep-hertz <int>
                        Beep frequency hertz (default: 1000)
  --beep-mix-normalize [true|false]
                        Normalize mix of audio and beeps (default: False)
  --beep-audio-weight <int>
                        Mix weight for non-beeped audio (default: 1)
  --beep-sine-weight <int>
                        Mix weight for beep (default: 1)
  --beep-dropout-transition <int>
                        Dropout transition for beep (default: 0)
  --force [true|false]  Process file despite existence of embedded tag

VOSK Options:
  --vosk-model-dir <string>
                        VOSK model directory (default: ~/.cache/vosk)
  --vosk-read-frames-chunk <int>
                        WAV frame chunk (default: 8000)

Whisper Options:
  --whisper-model-dir <string>
                        Whisper model directory (~/.cache/whisper)
  --whisper-model-name <string>
                        Whisper model name (base.en)
  --torch-threads <int>
                        Number of threads used by torch for CPU inference (0)
```

### Docker

Alternately, a [Dockerfile](./docker/Dockerfile) is provided to allow you to run monkeyplug in Docker. You can pull one of the following images:

* [VOSK](https://alphacephei.com/vosk/models)
    - oci.guero.org/monkeyplug:vosk-small
    - oci.guero.org/monkeyplug:vosk-large
* [Whisper](https://github.com/openai/whisper?tab=readme-ov-file#available-models-and-languages)
    - oci.guero.org/monkeyplug:whisper-tiny.en
    - oci.guero.org/monkeyplug:whisper-tiny
    - oci.guero.org/monkeyplug:whisper-base.en
    - oci.guero.org/monkeyplug:whisper-base
    - oci.guero.org/monkeyplug:whisper-small.en
    - oci.guero.org/monkeyplug:whisper-small
    - oci.guero.org/monkeyplug:whisper-medium.en
    - oci.guero.org/monkeyplug:whisper-medium
    - oci.guero.org/monkeyplug:whisper-large-v1
    - oci.guero.org/monkeyplug:whisper-large-v2
    - oci.guero.org/monkeyplug:whisper-large-v3
    - oci.guero.org/monkeyplug:whisper-large

then run [`monkeyplug-docker.sh`](./docker/monkeyplug-docker.sh) inside the directory where your audio files are located.

## Contributing

If you'd like to help improve monkeyplug, pull requests will be welcomed!

## Authors

* **Seth Grover** - *Initial work* - [mmguero](https://github.com/mmguero)

## License

This project is licensed under the BSD 3-Clause License - see the [LICENSE](LICENSE) file for details.
