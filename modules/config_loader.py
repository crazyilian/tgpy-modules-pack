"""
    name: config_loader
    once: false
    origin: tgpy://module/config_loader
    priority: 1001
    save_locals: true
"""
import logging

from tgpy.utils import DATA_DIR
import yaml
from tgpy.main import console


class UniversalModuleConfig:
    filename = None
    config = {}

    def __init__(self, module_name, required_keys=None, init_funcs=None, default_dict=None):
        if required_keys is None:
            required_keys = []
        if init_funcs is None:
            init_funcs = [str] * len(required_keys)
        if default_dict is None:
            default_dict = {}

        self.filename = DATA_DIR / 'modules-config' / f'{module_name}_config.yml'

        self.load()
        correct_config = True
        for key, func in zip(required_keys, init_funcs):
            if key not in self.config:
                if correct_config:
                    correct_config = False
                    pretty_name = module_name.replace("_", " ").title()
                    console.print(f'[magenta bold] "{pretty_name}" module configuration is incomplete.')
                self.config[key] = func(console.input(f'│ Please enter "{key}": '))
        if not correct_config:
            console.print("| Configuration completed.")

        for key in default_dict:
            if key not in self.config:
                self.config[key] = default_dict[key]
        self.save()

    def save(self):
        with open(self.filename, 'w') as file:
            yaml.safe_dump(self.config, file)

    def load(self):
        try:
            with open(self.filename) as file:
                self.config = yaml.safe_load(file)
        except FileNotFoundError:
            self.config = {}

    def __getattr__(self, item):
        # logging.info(f"getattr {item}")
        return self.config[item]

    def __setattr__(self, key, value):
        if hasattr(self, key):
            super(UniversalModuleConfig, self).__setattr__(key, value)
        else:
            # logging.info(f"setattr {key}: {value}")
            self.config[key] = value
