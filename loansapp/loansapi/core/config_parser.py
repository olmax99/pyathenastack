import os
import pathlib
import configparser


def read_config(mode='DEV'):
    parser = configparser.ConfigParser()
    project_path = pathlib.Path(__file__).parents[2]
    config_file = os.path.join(project_path, '.config.ini')
    if os.path.isfile(config_file):
        try:
            parser.read(config_file)
            return config_section_map(parser, mode)
        except configparser.ParsingError as e:
            print(e)
    else:
        raise FileNotFoundError


def config_section_map(parser, section):
    dict1 = {}
    options = parser.options(section)
    for option in options:
        try:
            dict1[option] = parser.get(section, option)
        except:
            print(f"exception on {option}!")
            dict1[option] = None
    return dict1
