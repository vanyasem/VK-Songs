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

from setuptools import setup, find_packages

requires = [
    'vk_api',
    'BeautifulSoup4',
    'requests',
    'pyfiglet',
    'PyInquirer',
    'prompt_toolkit==1.0.14',
    'colorama',
    'pathvalidate',
    'python-magic-bin ; platform_system=="Windows"',
    'python-magic-bin ; platform_system=="Darwin"',
    'python-magic ; platform_system=="Linux"',
]

setup(
    name='VK-Songs',
    version='0.1.0',
    description='',
    url='https://github.com/vanyasem/VK-Songs',
    download_url='https://github.com/vanyasem/VK-Songs/archive/v0.1.0.tar.gz',
    author='Ivan Semkin',
    author_email='ivan@semkin.ru',
    license='GPL-3.0',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Topic :: Multimedia :: Sound/Audio',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    packages=find_packages(exclude=['tests']),
    install_requires=requires,
    dependency_links=['https://github.com/Sixshaman/eyeD3/tarball/master#egg=eyeD3-0.8.11'],
    entry_points={
        'console_scripts': [
            'vk-songs=vk_songs.app:main',
        ],
    },
    keywords=['vk', 'vkontakte', 'music', 'download', 'media', 'audio', 'song'],
)
