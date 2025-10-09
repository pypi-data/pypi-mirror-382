# -*- coding: utf-8 -*-
"""

@author: ulysses
"""

import toml
import re
import json
import datetime
import requests
from pathlib import Path


def read_json(json_file):
    if json_file != None:
        pass
    else:
        return None
    with open(json_file,"r") as json_f:
        json_dict = json.load(json_f)
        return json_dict


def get_device_info_basic(base_url:str,timestamp:str,site:str,dev_type:str,dev_name='all') -> list:
    ## try using dev-tracker api
    deviceinfo = {}
    meta_dict_ls = []
    try:
       # url = f'{config_dict["basic_url"]}?date={timestamp}&site={site}&dev_type={dev_type}&dev_name={dev_name}'
        url = f'{base_url}?date={timestamp}&site={site}&dev_type={dev_type}&dev_name={dev_name}'
        metadata = requests.get(url).json()
        for c in metadata:
#            dev = metadata[f'{c}']['DEVICE']
#            camp = metadata[f'{c}']['HISTORY']['0']['pylarda_camp']
            meta_dict = metadata[f'{c}']
            meta_dict['timestamp'] = timestamp
            meta_dict_ls.append(meta_dict)
        return meta_dict_ls #deviceinfo 
    except Exception as e:
        print(f'Error: {e}')

def get_device_info(config_dict:dict,timestamp:str,site:str,dev_type:str,dev_name='all') -> list:
    ## try using dev-tracker api
    deviceinfo = {}
    meta_dict_ls = []
    try:
        url = f'{config_dict["basic_url"]}?date={timestamp}&site={site}&dev_type={dev_type}&dev_name={dev_name}'
        metadata = requests.get(url).json()
        for c in metadata:
#            dev = metadata[f'{c}']['DEVICE']
#            camp = metadata[f'{c}']['HISTORY']['0']['pylarda_camp']
            meta_dict = metadata[f'{c}']
            meta_dict['timestamp'] = timestamp
            meta_dict_ls.append(meta_dict)
        return meta_dict_ls #deviceinfo 
    except Exception as e:
        print(f'Error: {e}')

def get_campaign_ls(meta_dict:dict):
    #camp = meta_dict['history'][entry]['pylarda_camp']
    camp_ls = [entry["pylarda_camp"] for entry in meta_dict["history"].values()]
    return camp_ls

def get_device(meta_dict:dict):
    dev  = meta_dict['device']
    return dev

def get_data_base_dir_from_pylarda(config_dict:dict,meta_dict_ls:list,filetype_ls:list,camp=None,correct_system=None) -> dict:
    pylarda_basedir = config_dict['pylarda_basedir']
    all_campaigns_file = f'{pylarda_basedir}/larda-cfg/{config_dict["all_campaigns_file"]}'
    tomlcamp = toml.load(all_campaigns_file)

    data = {}
    for entry in meta_dict_ls:

        dev  = entry['device']
        dev_type  =entry['type']
        pid  = entry['pid']
        if camp is None:
            camp = entry['history']['0']['pylarda_camp']
        #print(camp)
        if correct_system is None:
            correct_system = entry['history']['0']['pylarda_system']
        timestamp = entry['timestamp']
        if len(camp) > 0:
            pass
        else:
            continue

        data[dev] = {}
        if dev in config_dict["device_dict"]:
            dev_translator = config_dict["device_dict"][dev]
        else:
            dev_translator = dev
#        print(dev)
#        print(dev_translator)
        param_file = tomlcamp[camp]['param_config_file']
        param_file = f'{pylarda_basedir}/larda-cfg/{param_file}'
        #print(param_file)
        tomldat = toml.load(param_file)
        
        ft_ls = []
        data[dev]['filetype'] = {}
        if len(correct_system) > 0:
            pass
        else:
            correct_system = ''
            for system in tomldat.keys():
                for file_type in tomldat[system]['path'].keys():
                    base_dir = tomldat[system]['path'][file_type]['base_dir']
                    if re.search(dev_translator, base_dir, re.IGNORECASE):
                        correct_system = system
                        break
                if len(correct_system) > 0:
                    connector_file = f'{pylarda_basedir}/larda-connectordump/{camp}/connector_{correct_system}.json'
                    print(connector_file)
                    try:
                        connector_file_json = open(connector_file)
                        connector_dict = json.load(connector_file_json)
                    except Exception:
                        connector_dict = ""
                        pass
                    if filetype_ls[0] in connector_dict.keys():
                        break
                    else:
                        continue

                #if len(correct_system) > 0:
                #    break
            if len(correct_system) == 0:
                print(f'could not find correct_system for {dev} in pylarda-campaign {camp}')
                data[dev]['system'] = ''
                return data
        print(correct_system)
#        print(filetype_ls)
        ft_ls = [i for i in tomldat[correct_system]['path'].keys()]
        connector_file = f'{pylarda_basedir}/larda-connectordump/{camp}/connector_{correct_system}.json'
        try:
            connector_file_json = open(connector_file)
            connector_dict = json.load(connector_file_json)
        except Exception:
            connector_dict = ""
            pass

#        data[dev][correct_system] = {}
        data[dev]['filetype'] = {}
        data[dev]['system'] = correct_system
        if len(filetype_ls) == 0:
            filetype_ls = ft_ls
        for ft in filetype_ls:
#           data[dev][correct_system][ft] = []
            data[dev]['filetype'][ft] = []

            if ft in connector_dict:
                filenames_ls = []
                for entry in connector_dict[ft]:
                    if dev_type == 'halo' and ft == 'sys_par': ## filter date for monthly file
                        timestamp_mod = f'{timestamp[0:6]}01'
                    else:
                        timestamp_mod = timestamp

                    entry_date = re.split(r'-',str(entry[0][0]))[0]
 
                    if timestamp_mod == entry_date:
                        filename = entry[1]
                        filename = re.split(r'^\.\/',filename)[1]
                        base_dir = tomldat[correct_system]['path'][ft]['base_dir']
                        full_filename = f"{base_dir}{filename}"
                        data[dev]['filetype'][ft].append(full_filename)
    return data


def find_correct_system(config_dict:dict,meta_dict:dict,camp=None,correct_system=None):
    pylarda_basedir = config_dict['pylarda_basedir']
    all_campaigns_file = f'{pylarda_basedir}/larda-cfg/{config_dict["all_campaigns_file"]}'
    tomlcamp = toml.load(all_campaigns_file)

    dev  = meta_dict['device']
    dev_type  =meta_dict['type']
    pid  = meta_dict['pid']
    if camp is None:
        camp = meta_dict['history']['0']['pylarda_camp']
    #print(camp)
    if correct_system is None:
        correct_system = meta_dict['history']['0']['pylarda_system']
    timestamp = meta_dict['timestamp']
    if len(camp) > 0:
        pass
    else:
        return None

    if dev in config_dict["device_dict"]:
        dev_translator = config_dict["device_dict"][dev]
    else:
        dev_translator = dev
#    print(dev)
#    print(dev_translator)
    param_file = tomlcamp[camp]['param_config_file']
    param_file = f'{pylarda_basedir}/larda-cfg/{param_file}'
    #print(param_file)
    tomldat = toml.load(param_file)
    
    if len(correct_system) > 0:
        pass
    else:
        correct_system = ''
        for system in tomldat.keys():
            #print(system)
            for file_type in tomldat[system]['path'].keys():
                base_dir = tomldat[system]['path'][file_type]['base_dir']
                if re.search(dev_translator, base_dir, re.IGNORECASE):
                    correct_system = system
                    #print(correct_system)
                    break
        if len(correct_system) == 0:
            print(f'could not find correct_system for {dev} in pylarda-campaign {camp}')
    return correct_system

def get_connectorfile(config_dict,camp,correct_system):
    if correct_system != None:
        pylarda_basedir = config_dict['pylarda_basedir']
        #camp = get_campaign_ls(meta_dict)
        connector_file = f'{pylarda_basedir}/larda-connectordump/{camp}/connector_{correct_system}.json'
    else:
        connector_file = None
    return connector_file

def get_paramfile_from_pylarda_connectorfile(config_dict,connectorfile):
    if connectorfile != None:
        pass
    else:
        return None
    pylarda_basedir = config_dict['pylarda_basedir']
    all_campaigns_file = f'{pylarda_basedir}/larda-cfg/{config_dict["all_campaigns_file"]}'
    tomlcamp = toml.load(all_campaigns_file)
    ## /home/larda3/larda-connectordump/GoSouth_II/connector_POLLYNET.json
    p = Path(connectorfile)

    filename = p.stem
    camp_dir = p.parent.name
    param_file = tomlcamp[camp_dir]['param_config_file']
    return param_file

def get_base_dir_from_paramfile(config_dict,system,param_file,system_key):
    if param_file != None or system != None:
        pass
    else:
        return None
    pylarda_basedir = config_dict['pylarda_basedir']
    tomlparam = toml.load(f'{pylarda_basedir}/larda-cfg/{param_file}')
    base_dir = tomlparam[system]['path'][system_key]['base_dir']
    return base_dir

def normalize_timestamp(ts: str, default_time: str = None) -> int:
    """
    Convert YYYYMMDD or YYYYMMDD-HHMMSS into int for comparison.
    If default_time is provided, append it when only date is given.
    """
    if "-" in ts:
        return int(ts.replace("-", ""))   # YYYYMMDDHHMMSS
    elif len(ts) == 8:  # just a date
        if default_time:
            return int(ts + default_time)
        else:
            return int(ts + "000000")
    else:
        raise ValueError(f"Invalid timestamp format: {ts}")

def get_system_from_connectorfile(connectorfile):
    p = Path(connectorfile)
    filename = p.stem
    campaign = p.parent.name
    system = re.split(r'connector_',filename)[-1]
    return system


def get_files_from_connectorfile(config_dict, connectorfile, system_key, start_date=None, end_date=None):
    if connectorfile != None:
        pass
    else:
        return None

    connector_dict = read_json(connectorfile)
    param_file = get_paramfile_from_pylarda_connectorfile(config_dict,connectorfile)
    system = get_system_from_connectorfile(connectorfile)
    base_dir = get_base_dir_from_paramfile(config_dict,system,param_file,system_key)
    results_dict = {}
    for (start, end), path in connector_dict.get(system_key, []):
        if start_date and end_date:
            qstart = normalize_timestamp(start_date, "000000")
            qend   = normalize_timestamp(end_date, "235959")
            fstart = normalize_timestamp(start)
            fend   = normalize_timestamp(end)
            if fstart <= qend and fend >= qstart:
                #print(start,path)
                #print(results_dict.keys())
                if start[0:8] in results_dict.keys():
                    results_dict[start[0:8]].append(str(Path(base_dir) / path))
                else:
                    results_dict[start[0:8]] = []
                    results_dict[start[0:8]].append(str(Path(base_dir) / path))
        else:
            if start[0:8] in results_dict.keys():
                results_dict[start[0:8]].append(str(Path(base_dir) / path))
            else:
                results_dict[start[0:8]] = []
                results_dict[start[0:8]].append(str(Path(base_dir) / path))

    return results_dict

def get_pylarda_campaign_from_connectorfile(connectorfile):
    p = Path(connectorfile)
    campaign = p.parent.name
    return campaign

def get_connectorfile_name_only(connectorfile):
    p = Path(connectorfile)
    filename = p.name
    return filename

def get_campaign_dir_from_connectorfile(connectorfile):
    p = Path(connectorfile)
    folder = p.parent
    return folder

def get_device_from_connectorfile_translator_dict(connectorfile_translator_dict,connectorfile):
    # revers indexing
    data = connectorfile_translator_dict
    reverse_index = {
    f: dev
    for dev_types in data.values()
    for devices in dev_types.values()
    for dev, files in devices.items()
    for f in files
    }
    return reverse_index[connectorfile]

def get_device_and_location_from_connectorfile_name_and_pylarda_campaign(metadata, connectorfile_name,camp):
    device = metadata.get("device")
    result = {}
    for _, subdict in metadata.get("history", {}).items():
        if connectorfile_name in subdict.get("pylarda_connectorfile") and subdict.get("pylarda_camp") == camp:
            result['device'] = device
            result['site'] = subdict.get("location")
            return result
    return None

def get_device_from_connectorfile(config_dict,connectorfile):
    ## still in experimental mode
    if connectorfile != None:
        pass
    else:
        return None
    connector_file_json = open(connectorfile)
    connector_dict = json.load(connector_file_json)
    pylarda_basedir = config_dict['pylarda_basedir']
#    connector_file = f'{pylarda_basedir}/larda-connectordump/{camp}/connector_{correct_system}.json'
    system = get_system_from_connectorfile(connectorfile)
    campaign = get_pylarda_campaign_from_connectorfile(connectorfile)
    #print(campaign,system)
    url = f'{config_dict["basic_url"]}?pid={campaign}'
    metadata = requests.get(url).json()
    #print(metadata)
    def comp_find(metadata, system_value):
        result = [
            devicename
            for devicename, info in metadata.items()
            if any(entry.get("pylarda_system") == system_value for entry in info.get("history", {}).values())
        ]
        if len(result) > 0:
            return result[0]
        else:
            return None
    device = comp_find(metadata, system)
    return device

