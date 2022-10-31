#!/usr/bin/env python3
"load bins.json and install missing files"

import argparse, subprocess, json, dataclasses, logging, os, tarfile, re
from typing import Optional

logger = logging.getLogger(__name__)

def download(url):
    "run wget in subprocess"
    subprocess.run(['wget', url])
    logger.info('ok dl %s', url)

def install(bin_name, archive_name, dest):
    extensions = archive_name.split('.')
    if 'tar' in extensions or 'tgz' in extensions:
        tarfile.open(archive_name).extract(bin_name)
        subprocess.run(['sudo', 'install', bin_name, dest])
    else:
        raise ValueError('unknown extension type in', archive_name)

@dataclasses.dataclass
class Spec:
    name: str
    url: str
    version: str
    version_flag: str = '--version'
    version_regex: Optional[str] = None

    def dl_url(self):
        return self.url.format(version=self.version) \
            if '{version}' in self.url \
            else self.url

    def dl_target(self):
        return self.dl_url().split('/')[-1]

    def installed_version(self, dest: str):
        "return installed version of tool"
        if not os.path.exists(os.path.join(dest, self.name)):
            return None
        ret = subprocess.run([os.path.join(dest, self.name), self.version_flag], capture_output=True)
        return re.search(self.version_regex, ret.stdout.decode()).groups()[0] if self.version_regex else ret.stdout.strip()

LEVELS = {lev[0]: lev for lev in ('INFO', 'CRITICAL', 'DEBUG', 'ERROR', 'WARNING', 'FATAL', 'NOTSET')}

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--path', default='bins.json', help="path to conf file")
    p.add_argument('--dest', default='/usr/local/bin', help="destination folder for install")
    p.add_argument('--only', help="install only one tool")
    p.add_argument('--scratch', help="scratch download location")
    p.add_argument('--noinstall', action='store_true', help="just download, don't install")
    p.add_argument('--level', '-l', default='INFO', choices=tuple(LEVELS.keys()) + tuple(LEVELS.values()))
    p.add_argument('--clean', action='store_true', help="pass this to clean up downloaded archives")
    args = p.parse_args()

    logging.basicConfig(level=LEVELS.get(args.level, args.level))

    specs = [
        Spec(name=name, **raw)
        for name, raw in json.load(open(args.path)).items()
    ]
    logger.info('loaded %d specs', len(specs))
    if args.only:
        raise NotImplementedError('todo: support --only')
    if args.scratch:
        raise NotImplementedError('todo: makedirs() and chdir')
    for spec in specs:
        if spec.installed_version(args.dest) == spec.version:
            logger.debug('skipping already-installed %s:%s', spec.name, spec.version)
            continue
        if os.path.exists(spec.dl_target()):
            logger.debug('skipping dl existing %s:%s', spec.name, spec.version)
        else:
            download(spec.dl_url())
        if not args.noinstall:
            install(spec.name, spec.dl_target(), args.dest)
        if args.clean:
            raise NotImplementedError('todo: delete archives')

if __name__ == '__main__':
    main()