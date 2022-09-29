from configparser import ConfigParser

def get_config() -> ConfigParser:
    data = ConfigParser()
    data.read('config.conf')
    return data


def __getattr__(name: str):
    config = get_config()
    items = __dir__(True)   
    
    if name.lower() in items:
        return config[__dir__()[items.index(name.lower())]]

def __dir__(lower_case=False):
    return [f"{(i if not lower_case else i.lower())}" for i in get_config().keys()]