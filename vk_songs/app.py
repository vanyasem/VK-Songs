# -*- coding: utf-8 -*-
##
# Copyright (c) 2017 Ivan Semkin.
#
# This file is part of VK-Songs
# (see https://github.com/vanyasem/VK-Songs).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
##

from __future__ import print_function, unicode_literals
from colorama import Fore

import logging
import os

import requests
import vk_api
from vk_api.audio import VkAudio


class VkSong(object):
    """Helper class that defines a Song object"""
    def __init__(self, num, artist, title, url, album=None):
        self.num = num
        self.artist = artist
        self.title = title
        self.url = url
        self.album = album


class VkAlbum(object):
    """Helper class that defines an Album object"""
    def __init__(self, title, album_id, owner_id):
        self.title = title
        self.album_id = album_id
        self.owner_id = owner_id


class VkSongs(object):
    """VK-Songs downloads VK audio files"""
    def __init__(self):
        self.logger = VkSongs.get_logger(level=logging.DEBUG)  # TODO: Configurable log
        self.session = requests.Session()

        self.is_logged_in = False

        self.vk = None
        self.vk_audio = None

    def login(self, login_user, login_pass):
        """Logs in to VK"""
        vk_session = vk_api.VkApi(
            login_user, login_pass,
            auth_handler=self.two_factor_handler,
            captcha_handler=self.captcha_handler,
            app_id=6692066,
        )

        try:
            vk_session.auth()
        except vk_api.AuthError as error_msg:
            self.logger.error('Login failed for {0}. Reason: {1}'.format(login_user, error_msg))
            return

        self.vk = vk_session.get_api()
        self.vk_audio = VkAudio(vk_session)
        self.is_logged_in = True

    @staticmethod
    def two_factor_handler():
        key = input("♫ Enter authentication code: ")
        remember_device = True

        return key, remember_device

    @staticmethod
    def captcha_handler(captcha):
        #  TODO: Implement it using PyInquirer
        key = input("♫ Enter captcha code {0}: ".format(captcha.get_url())).strip()

        return captcha.try_again(key)

    @staticmethod
    def get_color(level):
        print(level)
        if level == 'ERROR':
            return Fore.RED
        elif level == 'WARNING':
            return Fore.YELLOW
        else:
            return ''

    @staticmethod
    def get_logger(level=logging.DEBUG):
        """Returns a logger"""
        logger = logging.getLogger(__name__)

        fh = logging.FileHandler('vk-songs.log', 'w')
        fh.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        fh.setLevel(level)
        logger.addHandler(fh)

        import sys
        sh = logging.StreamHandler(sys.stdout)
        sh.setFormatter(logging.Formatter(Fore.RED + '%(levelname)s: %(message)s'))
        sh.setLevel(logging.ERROR)
        logger.addHandler(sh)

        return logger

    def download(self, song, save_dir='./', tag=False):
        """Downloads the media file"""
        from pathvalidate import sanitize_filename
        import eyed3
        from eyed3.id3 import ID3_V2_4
        url = song.url
        base_name = '{0} - {1}.mp3'.format(song.artist.strip(), song.title.strip())  # TODO: Configurable file mask
        base_name = sanitize_filename(base_name, replacement_text='_')
        file_path = os.path.join(save_dir, base_name)

        if not os.path.isfile(file_path):
            import time
            with open(file_path, 'wb') as media_file:
                try:
                    content = self.session.get(url).content
                except requests.exceptions.ConnectionError:
                    time.sleep(5)
                    content = self.session.get(url).content

                media_file.write(content)

            file_time = time.time()
            os.utime(file_path, (file_time, file_time))

            if tag:
                audio_file = eyed3.load(file_path)
                eyed3.core.log.disabled = True
                eyed3.id3.log.disabled = True
                if audio_file:
                    if not audio_file.tag:
                        audio_file.initTag(version=ID3_V2_4)
                    audio_file.tag.artist = song.artist
                    audio_file.tag.album_artist = song.artist
                    audio_file.tag.title = song.title
                    if song.album is not None:
                        audio_file.tag.album = song.album
                    audio_file.tag.save(version=ID3_V2_4, encoding='utf_8')

            return True
        else:
            return False

    def search(self, query):
        search = self.vk_audio.search(q=query)  # TODO: Generator
        result = []
        for audio in search:
            audio['url'] = audio['url'].split('?', 1)[0]
            result.append(VkSong(num=audio['id'], artist=audio['artist'], title=audio['title'], url=audio['url']))
        if len(result) == 0:
            self.logger.error('No songs found')
        return result

    def search_user(self, owner_id, query):
        search = self.vk_audio.search_user(owner_id=owner_id, q=query)
        result = []
        for audio in search:
            audio['url'] = audio['url'].split('?', 1)[0]
            result.append(VkSong(num=audio['id'], artist=audio['artist'], title=audio['title'], url=audio['url']))
        if len(result) == 0:
            self.logger.error('No songs found')
        return result

    def get_albums(self, owner_id):
        albums = self.vk_audio.get_albums(owner_id=owner_id)  # TODO: Generator
        result = []
        for album in albums:
            result.append(VkAlbum(title=album['title'], album_id=album['id'], owner_id=album['owner_id']))
        if len(result) == 0:
            self.logger.error('No albums found')
        return result

    def get(self, owner_id=None, album_id=None, album_title=None):
        songs = self.vk_audio.get(owner_id=owner_id, album_id=album_id)  # TODO: Generator
        result = []
        for audio in songs:
            audio['url'] = audio['url'].split('?', 1)[0]
            result.append(VkSong(num=audio['id'], artist=audio['artist'],
                                 title=audio['title'], url=audio['url'], album=album_title))
        if len(result) == 0:
            self.logger.error('No songs found')
        return result

    @staticmethod
    def should_login(dict):
        # TODO: Implement user session caching
        return True

    @staticmethod
    def make_dst_dir(destination='./', artist='/'):
        """Creates the destination directory."""
        destination = destination + artist

        try:
            os.makedirs(destination)
        except OSError as err:
            import errno
            if err.errno == errno.EEXIST and os.path.isdir(destination):
                # Directory already exists
                pass
            else:
                # Target dir exists as a file, or a different error
                raise

        return destination


def print_initial(logged_in=False):
    from pyfiglet import Figlet
    f = Figlet()
    print(Fore.BLUE + f.renderText('VK Songs'))

    if not logged_in:
        print(Fore.YELLOW + "Visit https://vk.com/join if you don't have an account yet.")
        print()
    else:
        print(Fore.GREEN + '✔' + Fore.RESET + ' Connected to VK API')


def clear():
    if os.name == 'nt':
        _ = os.system('cls')
    else:
        _ = os.system('clear')


def main():
    from PyInquirer import prompt
    from colorama import init

    init(autoreset=True, convert=True)
    print_initial()

    vk_songs = VkSongs()
    while not vk_songs.is_logged_in:
        questions = [
            {
                'type': 'input',
                'name': 'username',
                'message': 'VK username:',
                'when': vk_songs.should_login,
            },
            {
                'type': 'password',
                'name': 'password',
                'message': 'VK password:',
                'when': vk_songs.should_login,
            },
        ]
        answers = prompt(questions, qmark='♫')
        if answers.get('username').strip() == '' or answers.get('password').strip() == '':
            vk_songs.logger.error('No username or password provided')
            # print('\033[3A', end='')  # TODO: Ditch print_initial
            print()
            continue
        vk_songs.login(answers.get('username').strip(), answers.get('password').strip())
        print()

    clear()
    print_initial(logged_in=True)
    print()

    while True:
        choices = [
            "Get user's / community's audios",
            "Get user's / community's albums",
            "Search in user's / community's audios",
            "Search global audios",
        ]
        questions = [
            {
                'type': 'list',
                'name': 'mode',
                'message': 'Select download mode:',
                'choices': choices,
            },
        ]
        mode = prompt(questions, qmark='♫')
        print()

        songs = []
        if choices.index(mode.get('mode')) == 0:
            while True:
                questions = [
                    {
                        'type': 'input',
                        'name': 'user',
                        'message': "Enter user's / community's id:",
                    },
                ]
                answers = prompt(questions, qmark='♫')
                if answers.get('user').strip() != '':  # TODO: Validate ID
                    # TODO: Add loading here
                    songs = vk_songs.get(owner_id=int(answers.get('user').strip()))  # TODO: ID Decoding
                    break
                else:
                    vk_songs.logger.error('No user id provided')
                print()

        if choices.index(mode.get('mode')) == 1:
            while True:
                questions = [
                    {
                        'type': 'input',
                        'name': 'user',
                        'message': "Enter user's / community's id:",
                    },
                ]
                answers = prompt(questions, qmark='♫')
                if answers.get('user').strip() != '':  # TODO: Validate ID
                    albums = vk_songs.get_albums(int(answers.get('user').strip()))  # TODO: ID Decoding
                    if albums and len(albums) > 0:
                        album_choices = []
                        questions = [
                            {
                                'type': 'checkbox',
                                'message': 'Select albums to download:',
                                'name': 'albums',
                                'choices': album_choices,
                            },
                        ]
                        for album in albums:
                            album_choices.append(
                                {
                                    'name': str(album.album_id) + '_' + str(album.owner_id) + '. ' + album.title,
                                },
                            )
                        answers = prompt(questions, qmark='♫')
                        selected = answers.get('albums')
                        # TODO: Place albums in separate folders
                        for selection in selected:
                            split = selection.split('.')[0].split('_')
                            songs += vk_songs.get(owner_id=int(split[1]), album_id=int(split[0]))
                    break
                else:
                    vk_songs.logger.error('No user id provided')
                print()

        if choices.index(mode.get('mode')) == 2:
            while True:
                questions = [
                    {
                        'type': 'input',
                        'name': 'user',
                        'message': "Enter user's / community's id:",
                    },
                ]
                answers = prompt(questions, qmark='♫')
                if answers.get('user').strip() != '':  # TODO: Validate ID
                    user_id = answers.get('user').strip()
                    while True:
                        questions = [
                            {
                                'type': 'input',
                                'name': 'query',
                                'message': 'Search query:',
                            },
                        ]
                        answers = prompt(questions, qmark='♫')
                        if answers.get('query').strip() != '':
                            songs = vk_songs.search_user(owner_id=int(user_id),  # TODO: ID Decoding
                                                         query=answers.get('query').strip())
                            break
                        else:
                            vk_songs.logger.error('No search query provided')
                        print()
                    break
                else:
                    vk_songs.logger.error('No user id provided')
                print()

        if choices.index(mode.get('mode')) == 3:
            while True:
                questions = [
                    {
                        'type': 'input',
                        'name': 'query',
                        'message': 'Search query:',
                    },
                ]
                answers = prompt(questions, qmark='♫')
                if answers.get('query').strip() != '':
                    songs = vk_songs.search(query=answers.get('query').strip())
                    break
                else:
                    vk_songs.logger.error('No search query provided')
                print()

        queue = []
        if songs and len(songs) > 0:
            song_choices = []
            questions = [
                {
                    'type': 'checkbox',
                    'message': 'Select songs to download:',
                    'name': 'songs',
                    'choices': song_choices,
                },
            ]
            for song in songs:
                song_choices.append(
                    {
                        'name': str(song.num) + '. ' + song.artist + ' - ' + song.title,
                    },
                )
            answers = prompt(questions, qmark='♫')
            selected = answers.get('songs')
            for selection in selected:
                for song in songs:
                    if song.num == int(selection.split('.')[0]):
                        queue.append(song)

        count = 0
        print()
        for song in queue:
            dst = VkSongs.make_dst_dir('./DOWNLOADS/')  # TODO: Configure destination directory
            print('\033[1A\033[2K' + '> {0} - {1}'.format(song.artist, song.title))
            print('♫' + Fore.GREEN + ' Downloading tracks [{0}/{1} - {2:.2f}%]:'.format(
                count, len(queue), 100 / len(queue) * count))
            result = vk_songs.download(song, dst, tag=True)  # TODO: Configure tag
            print('\033[2A\033[2K' + Fore.GREEN + '√' + Fore.RESET + ' {0} - {1}'.format(song.artist, song.title))
            if not result:
                print('\033[2K' + '  > Song already exists')
            count += 1
            print()

        print('\033[1A\033[2K' + Fore.GREEN + '√' + Fore.RESET + ' Finished downloading audios')
        print()


if __name__ == '__main__':
    main()
