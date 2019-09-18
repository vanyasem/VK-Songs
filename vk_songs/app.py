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
    def __init__(self, num, artist, title, url):
        self.num = num
        self.artist = artist
        self.title = title
        self.url = url


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

    def download(self, song, save_dir='./'):
        """Downloads the media file"""
        url = song.url
        base_name = '{0} - {1}.mp3'.format(song.artist, song.title)  # TODO: Configurable file mask
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
            self.logger.error('Nothing found')
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

    init(autoreset=True)

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
        answers = prompt(questions, qmark='♫')
        print()

        songs = []
        if choices.index(answers.get('mode')) == 3:
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
            choices = []
            questions = [
                {
                    'type': 'checkbox',
                    'message': 'Select songs to download:',
                    'name': 'songs',
                    'choices': choices,
                },
            ]
            for song in songs:
                choices.append(
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
        import sys
        for song in queue:
            # TODO: Show live progress
            # char = ' '
            # while True:
            #     if char == ' ':
            #         char = '♫'
            #     else:
            #         char = ' '
            #     print('\r' + '♫' + Fore.GREEN + ' Downloading tracks [{0}/{1} - {2:.2f}%]:'.format(
            #         count, len(queue), 100 / len(queue) * count))
            dst = VkSongs.make_dst_dir('./DOWNLOADS/')  # TODO: Configure destination directory
            sys.stdout.write('\r> {0} - {1}'.format(song.artist, song.title))
            result = vk_songs.download(song, dst)
            sys.stdout.write('\r' + Fore.GREEN + '√' + Fore.RESET + ' {0} - {1}'.format(song.artist, song.title))
            if not result:
                sys.stdout.write('\n  > Song already exists')
            count += 1
            print()

        print(Fore.GREEN + '√' + Fore.RESET + ' Finished downloading audios')
        print()


if __name__ == '__main__':
    main()
