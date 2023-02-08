# TGPy modules (by crazyilian)

## Installation

Clone repo and create symlinks to all directories you need. For example:

```bash
ln -s ~/tgpy-modules.git/modules ~/.config/tgpy/modules
ln -s ~/tgpy-modules.git/environments ~/.config/tgpy/environments
```

If you already have `modules` directory you can back up it, create symlink and copy all backed up modules to repo:

```bash
mv ~/.config/tgpy/modules ~/.config/tgpy/modules.backup
ln -s ~/tgpy-modules.git/modules ~/.config/tgpy/modules
cp -r ~/.config/tgpy/modules.backup ~/.config/tgpy/modules
```

Don't forget to copy `environments.json` manually if you use it.

