#!/usr/bin/env python3

'''

 Code to handle command line usage of this module
 eg `python -m metadata_xml my_record.yaml`

 Creates an XML file with same base name as Yaml file
 (eg, record.yaml -> record.xml)

'''


from datetime import date
import os
import argparse
import pathlib
import yaml
from jinja2 import Environment, FileSystemLoader

dir_path = os.path.dirname(os.path.realpath(__file__))
this_directory = pathlib.Path(__file__).parent.absolute()
schema_path = f'{this_directory }/iso19115-cioos-template'


def normalize_datestring(datestring, format_='default'):
    """groks date string into ISO8601
       Adopted from Pygeometa https: // github.com/geopython/pygeometa/blob/master/pygeometa/core.py
    """

    try:
        if isinstance(datestring, date):
            if datestring.year < 1900:
                datestring2 = '{0.day:02d}.{0.month:02d}.{0.year:4d}'.format(
                    datestring)
            else:
                datestring2 = datestring.strftime('%Y-%m-%dT%H:%M:%SZ')
            if datestring2.endswith('T00:00:00Z'):
                datestring2 = datestring2.replace('T00:00:00Z', '')
            return datestring2
        elif isinstance(datestring, int) and len(str(datestring)) == 4:  # year
            return str(datestring)
    except AttributeError:
        raise RuntimeError('Invalid datestring: {}'.format(datestring))
    return datestring


def list_all_languages_in_record(record):
    '''So that we can list all languages used in the otherLocale section of XML'''
    def list_keys_in_dict(d, all_keys=[]):
        # recursive function, works on nested dict for example
        for k, v in d.items():
            if isinstance(v, dict):
                all_keys.append(k)
                list_keys_in_dict(v, all_keys)
            else:
                all_keys.append(k)
        return set(all_keys)

    keys_in_record = list_keys_in_dict(record)

    two_character_keys = list(
        filter(lambda x: (len(x) == 2) and (x != 'id'), keys_in_record))
    return two_character_keys


if __name__ == '__main__':

    parser = argparse.ArgumentParser(prog='metadata_xml',
                                     description="Convert yaml into CIOOS xml")

    parser.add_argument(
        '-f', type=str, dest="yaml_file",
        help="Enter filename of yaml file.", required=True)

    args = parser.parse_args()
    filename = args.yaml_file

    with open(args.yaml_file) as stream:
        record = yaml.safe_load(stream)

    basename = os.path.basename(filename)
    print("Input filename as: "+basename)

    template_loader = FileSystemLoader(searchpath=schema_path)
    template_env = Environment(loader=template_loader, trim_blocks=True,
                               lstrip_blocks=True)

    template_env.globals.update(
        list_all_languages_in_record=list_all_languages_in_record)
    template_env.filters['normalize_datestring'] = normalize_datestring
    template = template_env.get_template('main.j2')

    xml = template.render({"record": record})

    pre, ext = os.path.splitext(filename)
    yaml_filename = f'{pre}.xml'
    file = open(yaml_filename, "w")
    file.write(xml)
    print("Wrote " + file.name)
