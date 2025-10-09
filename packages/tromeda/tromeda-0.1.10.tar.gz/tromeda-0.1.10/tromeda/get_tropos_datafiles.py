# -*- coding: utf-8 -*-
"""

@author: ulysses
"""

import argparse
import toml
import re
import json
import datetime
import requests
import tromeda_functions as tromeda

# Create the parser
my_parser = argparse.ArgumentParser(description='Show device of a TROPOS site at a specific timestamp')

# Add the arguments
my_parser.add_argument('--md_file', dest='md_file_input', metavar='markdown_file',
                       default='tropos_device_tracking_overview.md',
                       type=str,
                       help='the markdown file containing the device tracking informations')

my_parser.add_argument('--config_file',
                       default='config.json',
                       help='config file including base dirs etc.')

my_parser.add_argument('--site', dest='site', metavar='location',
                       default='all',
                       type=str,
                       help='the location to check; if set to \'all\' every location will be listed')

my_parser.add_argument('--timestamp', dest='timestamp', metavar='timestamp',
                       default='all',
                       type=str,
                       help='the date to look for; if set to \'all\' every timestamp will be listed')

my_parser.add_argument('--device_type', dest='device_type', metavar='type of device',
                       default='all',
                       type=str,
                       help='Here you can specify the type of the device - i.e. \'hatpro\' or \'polly\'. If left empty or set to \'all\' every device-type will be listet.')

my_parser.add_argument('--device_name', dest='device_name', metavar='name of device',
                       default='all',
                       type=str,
                       help='Here you can specify the device name you are looking for - i.e. \'Hatpro_LACROS\' or \'PollyXT_cpv\'. If left empty or set to \'all\' every device will be listet.')

my_parser.add_argument('--show_files', action='store_true',
                       help='switch: look for folder and files, where the measurement is stored.')

#valid_levels = ['level', 'level0', 'level1', 'level1a', 'level1b', 'level2']
#my_parser.add_argument('--datalevel', choices=valid_levels,
#                       default='level',
#                       help='choice of data level to scan for.')
my_parser.add_argument('--filetype',nargs='+',
                       default='',
                       help='choice of filetype, also reffering to the data level to scan for. Multiple entries are possbile, e.g. "hpl nc". Default is all types - meaning level0 to level1b.')



# Execute the parse_args() method
args = my_parser.parse_args()

def main():
    with open(args.config_file,"r") as con_file:
            config_dict = json.load(con_file)

    meta_dict_ls = tromeda.get_device_info(config_dict=config_dict, timestamp=args.timestamp, site=args.site, dev_type=args.device_type)
    #for entry in meta_dict_ls:
    #    print(entry['DEVICE'])

    if args.show_files:
        data = tromeda.get_data_base_dir_from_pylarda(config_dict=config_dict,meta_dict_ls=meta_dict_ls,filetype_ls=args.filetype)
        print(data)
        #for dev in data:
        #    print(dev)
        #    print(data[dev])


if __name__ == '__main__':
    main()

