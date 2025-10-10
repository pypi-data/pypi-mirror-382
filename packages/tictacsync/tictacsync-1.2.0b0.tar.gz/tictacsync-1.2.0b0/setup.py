from setuptools import setup


with open("README.md", "rb") as f:
    long_descr = f.read().decode("utf-8")

long_description = 'CLI for syncing audio video \
	files containing an audio TicTacCode sync track.'

setup(
    name = "tictacsync",
    packages = ["tictacsync"],
    package_data={
      'tictacsync': ['tests/data/*'],
    },
    install_requires=[
        'sox>=1.4.1',
        'ffmpeg_python>=0.2.0',
        'loguru>=0.6.0',
        'matplotlib>=3.7.1',
        'numpy>=1.24.3',
        'rich>=10.12.0',
        'lmfit',
        'scikit-image',
        'scipy>=1.10.1',
        'platformdirs',
        ], 
    python_requires='>=3.10',
    entry_points = {
        "console_scripts": [
        'tictacsync = tictacsync.entry:main',
        'newmix = tictacsync.newmix:main',
        'mamsync = tictacsync.mamsync:main',
        'mamconf = tictacsync.mamconf:main',
        'multi2polywav = tictacsync.multi2polywav:main',
        ]
        },
    version = '1.2.0-beta',
    description = "commands for syncing audio video recordings",
    long_description_content_type='text/markdown',
    long_description = long_descr,
    include_package_data=True,
    zip_safe=False,
    author = "Raymond Lutz",
    author_email = "lutzrayblog@mac.com",
	url ='https://tictacsync.org/',
    classifiers=[
          'Development Status :: 4 - Beta',
          'Environment :: Console',
          'Intended Audience :: End Users/Desktop',
          'License :: OSI Approved :: MIT License',
          'Operating System :: MacOS',
          'Operating System :: Microsoft :: Windows',
          'Operating System :: POSIX',
          'Programming Language :: Python :: 3',
          'Topic :: Multimedia :: Sound/Audio',
          'Topic :: Utilities',
          'Topic :: Multimedia :: Sound/Audio :: Capture/Recording',
          'Topic :: Multimedia :: Video :: Non-Linear Editor',
      ], 
    )

