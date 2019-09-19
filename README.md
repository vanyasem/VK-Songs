VK Songs
========
![Python 3.5, 3.6, 3.7](https://img.shields.io/pypi/pyversions/vk_songs.svg)
[![GitHub License](https://img.shields.io/badge/license-GPLv3-blue.svg)](https://raw.githubusercontent.com/vanyasem/VK-Songs/master/LICENSE)
[![PyPI](https://img.shields.io/pypi/v/vk-songs.svg)](https://pypi.python.org/pypi/VK-Songs)
[![Travis](https://img.shields.io/travis/vanyasem/VK-Songs.svg)](https://travis-ci.org/vanyasem/VK-Songs)

vk-songs is a command-line application written in Python that downloads VK audio files. Use responsibly.

Features
--------
- Scrape user's music
- Scrape community's music
- Scrape albums
- Embedding support

Install
-------

#### Arch GNU/Linux
For the stable version:

    $ trizen -S vk-songs

For the git version:

    $ trizen -S vk-songs-git

#### Other distros
For the stable version:

    $ pip3 install vk-songs --upgrade --user

For the git version:

    $ pip3 install git+https://github.com/vanyasem/VK-Songs.git --upgrade --user

Usage
-----
Just run the app, it's interactive

    $ vk-songs

**Note:** If running from PyCharm, make sure to check "Emulate terminal in output console" in your Run configuration.

Contributing
------------
1. Check open issues or open a new one to start a discussion around
   your idea or a bug you found
2. Fork the repository and make your changes
3. Send a pull request

Futurelog
---------
- Qt5 GUI
- Embedding how-to
- Configuration (file mask, log level, destination, ID3 tagging)
- Session caching
- User ID decoding
- Download albums to separate folders
