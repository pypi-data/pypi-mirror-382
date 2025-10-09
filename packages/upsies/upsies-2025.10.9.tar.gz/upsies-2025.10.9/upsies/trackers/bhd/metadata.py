import re

sources = {
    'Blu-ray': re.compile(r'(?i:blu-?ray|bd(?:25|50|66|100))'),  # (UHD) BluRay|BD(25|50|66|100) (Remux)
    'HD-DVD': re.compile(r'(?i:hd-?dvd)'),  # HD(-)DVD
    'WEB': re.compile(r'^(?i:web)'),  # WEB(-DL|Rip)
    'HDTV': re.compile(r'(?:hd-?|)(?i:tv)'),  # HD(-)TV
    'DVD': re.compile(r'^(?i:dvd)'),  # DVD(5|9|...)
}
