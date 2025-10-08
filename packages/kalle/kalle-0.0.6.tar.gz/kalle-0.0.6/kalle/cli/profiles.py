from kalle.lib.util.ConfigManager import ConfigManager


def cli():
  config_manager = ConfigManager("kalle", "fe2", ".")

  for p in config_manager.config.profiles.keys():
    print(f"{p}")
