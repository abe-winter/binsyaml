# binsyaml

Tool to download + install binaries according to a declarative spec. Use this like a mini package manager for random tools you download from github releases.

Uses json not yaml (despite the name).

See `bins-sample.json` in this repo for an example of the file format.

## getting started

### install

We're not on pypi, install using normal `git+https://...`.

Test the command with `binsyaml -h`.

### set up download

Assume the base case here is downloading from github releases.

First worry about the initial download step. Add a minimal bins.json entry like:

```json
{
  "gopass": {
    "version": "1.15.2",
    "url": "https://github.com/gopasspw/gopass/releases/download/v{version}/gopass-{version}-linux-amd64.tar.gz"
  }
}
```

Note the `{version}` wildcard in the url.

Run `binsyaml --dest bin -l DEBUG`. It should download and install gopass in your bin folder.

### setup up version detection

The tool wants to be smart and not redownload existing versions, but to do that, you have to tell it how to read the binary's version.

If you run the command again now, you'll get:

```sh
$ binsyaml --dest bin -l DEBUG
INFO:bins:loaded 1 specs
DEBUG:bins:skipping dl existing gopass:1.15.2
DEBUG:bins:installing gopass in bin from archive gopass-1.15.2-linux-amd64.tar.gz
```

It didn't re-download, because the tgz file wasn't cleaned up (pass `--clean` for cleanup), but it would have.

`gopass -v` prints `gopass 1.15.2 go1.19.4 linux amd64`, so add these keys to bins.json:

```json
{
  "gopass": {
    "# existing stuff": "# already exists",
    "version_flag": "-v",
    "version_regex": "\\w+ ([^\\s]+)"
  }
}
```

Now it will detect the installed version:

```sh
$ binsyaml --dest bin -l DEBUG
INFO:bins:loaded 1 specs
DEBUG:bins:skipping already-installed gopass:1.15.2
```

## tools I should investigate instead of this

- [asdf](https://asdf-vm.com/guide/introduction.html#why-use-asdf)

## roadmap

- [ ] mechanism for checking latest version in release folder
