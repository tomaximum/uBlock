#!/usr/bin/env python3

import os
import json
import sys
import codecs
from time import time
from shutil import rmtree
from collections import OrderedDict

if not sys.argv[1]:
    raise SystemExit('Build dir missing.')


def mkdirs(path):
    try:
        os.makedirs(path)
    finally:
        return os.path.exists(path)

pj = os.path.join
build_dir = os.path.abspath(sys.argv[1])

description = ''

# locales
locale_dir = pj(build_dir, '_locales')

for alpha2 in os.listdir(locale_dir):
    locale_path = pj(locale_dir, alpha2, 'messages.json')
    with codecs.open(locale_path, 'r', encoding='utf8') as f:
        string_data = json.load(f, object_pairs_hook=OrderedDict)

    if alpha2 == 'en':
        description = string_data['extShortDesc']['message']

    for string_name in string_data:
        string_data[string_name] = string_data[string_name]['message']

    rmtree(pj(locale_dir, alpha2))

    alpha2 = alpha2.replace('_', '-')
    locale_path = pj(locale_dir, alpha2 + '.json')

    mkdirs(pj(locale_dir))

    with codecs.open(locale_path, 'w', encoding='utf8') as f:
        json.dump(string_data, f, ensure_ascii=False)


# update Info.plist
proj_dir = pj(os.path.split(os.path.abspath(__file__))[0], '..')
chromium_manifest = pj(proj_dir, 'platform', 'chromium', 'manifest.json')

with codecs.open(chromium_manifest, encoding='utf8') as m:
    manifest = json.load(m)

manifest['buildNumber'] = int(time())
manifest['description'] = description

with codecs.open(pj(build_dir, 'Info.plist'), 'r+', encoding='utf8') as f:
    info_plist = f.read()
    f.seek(0)

    f.write(info_plist.format(**manifest))

# update Update.plist
update_plist = pj(proj_dir, 'platform', 'safari', 'Update.plist')
update_plist_build = pj(build_dir, '..', os.path.basename(update_plist))

with codecs.open(update_plist_build, 'w', encoding='utf8') as f:
    with codecs.open(update_plist, encoding='utf8') as u:
        update_plist = u.read()

    f.write(update_plist.format(**manifest))
