import os
import re

# Regular expressions are matched against file paths.

# Path separator must be escaped in case we're running on Windows.
sep = re.escape(os.sep)

checksums = r'\.(?i:sfv|md5)$'

extras = (
    r'(?i:'
    # Directory named "extras".
    rf'{sep}extras{sep}'
    r'|'
    # Anything with the word "extras" with another word in front of it. This
    # should exclude the show "Extras".
    rf'{sep}.+[\. ]extras[\. ]'
    r'|'
    # Numbered extras (e.g. "Foo.S01.Extra1.mkv", "Foo.S01.Extra.2.mkv", .etc)
    rf'{sep}.+[\. ]extra[\. ]?\d+[\.]'
    r')'
)

images = r'\.(?i:png|jpg|jpeg)$'

nfo = r'\.(?i:nfo)$'

samples = (
    r'(?i:'
    # Sample directory
    rf'{sep}[!_0-]?sample{sep}'
    r'|'
    # Sample file name starts with release name
    rf'[^{sep}][\.\-_ ]sample\.mkv'
    r'|'
    # Sample file name ends with release name
    rf'{sep}sample[\!\-_].+\.mkv'
    r'|'
    # Sample file name starts with release name and ends with "sample-RLSGRP.mkv"
    r'[\.\-_!]?sample-[a-zA-Z0-9]+\.mkv'
    r'|'
    # Sample file name starts with "<characters that top-sort>sample"
    rf'{sep}[!#$%&*+\-\.]?sample\.mkv'
    r')'
)

subtitles = r'\.(?i:srt|idx|sub)$'
