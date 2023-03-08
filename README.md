# TGPy modules by crazyilian

Modules pack for [TGpy](https://github.com/tm-a-t/TGPy).

## Installation

Clone repo and create symlink to modules directory. For example:

```bash
git clone https://github.com/crazyilian/tgpy-modules-pack.git
ln -s tgpy-modules-pack.git/modules ~/.config/tgpy/modules
```

If you already have `modules` directory in your TGPy config you can back it up, create symlink and copy all backed up modules to repo:
```bash
mv ~/.config/tgpy/modules ~/.config/tgpy/modules.backup
ln -s tgpy-modules-pack.git/modules ~/.config/tgpy/modules
cp -r ~/.config/tgpy/modules.backup ~/.config/tgpy/modules
```
Alternatively, you can fork repo and change or add your own modules.

## Updating

To update modules you can send to any telegram chat two messages:
```bash
.sh
cd path/to/tgpy-modules-pack.git
git pull
```
and then
```python
restart()
```
