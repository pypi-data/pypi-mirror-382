#import tromeda.tromeda_functions as tromeda
import tromeda_functions as tromeda
import re
from pathlib import Path
import json
import argparse
import requests

## Create the parser
my_parser = argparse.ArgumentParser(description='LARP connectorfiles to db converter')

my_parser.add_argument('-sd','--startdate', dest='startdate',
                               type=str,
                                                      help='the startdate to look for')
my_parser.add_argument('-ed','--enddate', dest='enddate',
                               type=str,
                                                      help='the enddate to look for')
my_parser.add_argument('-s','--site', dest='site',
                               type=str,
                                                      help='the site to look for')
my_parser.add_argument('-t','--dev_type', dest='dev_type',
                               type=str,
                                                      help='the device_type to look for')
my_parser.add_argument('-d','--device', dest='device',
                               nargs='+',
                                                      help='the polly-device to look for, e.g.: pollyxt-lacros, pollyxt_arielle, pollyxt_cpv, ...; if not parsed as argument, all devices will be scanned.')
my_parser.add_argument('-c','--config', dest='config',
                               type=str,
                                                      help='the tromeda config file')

## Execute the parse_args() method
args = my_parser.parse_args()

def read_json(json_file):
    if json_file != None:
        pass
    else:
        return None
    with open(json_file,"r") as json_f:
        json_dict = json.load(json_f)
        return json_dict

#config_file = '/lacroshome/lacroswww/src/quicklooks/tromeda_config.json'
config_file = args.config 
connectorfile_translator = "/lacroshome/lacroswww/src/LARP/tromeda_device_connectorfile_translator.json"

connectorfile_translator_dict = read_json(connectorfile_translator)

config_dict = read_json(config_file)
start_date = args.startdate
end_date = args.enddate
site = args.site
if args.device:
    device = args.device[0]
dev_type = args.dev_type
if start_date == None and end_date == None:
    date = 'all'
else:
    date = f'{start_date}:{end_date}'
#meta_dict_ls = tromeda.get_device_info(config_dict=config_dict, timestamp=date, site=site, dev_type=dev_type, dev_name=device)

#print(meta_dict_ls)
#print(len(meta_dict_ls))
#exit()
#print(f'dev_name: {device}')
#for entry in meta_dict_ls:
#    device_meta = tromeda.get_device(entry)
#    if device_meta == device:
#        pass
#    else:
#        continue
#    print(f'device_name_meta: {device_meta}')
#    camp_ls = tromeda.get_campaign_ls(entry)
#    sdate_ls = [e["startdate"] for e in entry["history"].values()]
#    edate_ls = [e["enddate"] for e in entry["history"].values()]
#    for n,camp in enumerate(camp_ls):
#        print(f'pylarda_campaign: {camp}')
#        print(sdate_ls[n],edate_ls[n])
#        correct_system = tromeda.find_correct_system(config_dict=config_dict,meta_dict=entry,camp=camp,correct_system=None)
#        #print(correct_system)
#        connectorfile = tromeda.get_connectorfile(config_dict,camp,correct_system)
#        print(connectorfile)
#exit()

#con_ls = ['/home/larda3/larda-connectordump/caro_limassol/connector_POLLYNET.json','/home/larda3/larda-connectordump/caro_limassol/connector_POLLYNETprofiles.json','/home/larda3/larda-connectordump/caro_limassol/connector_POLLYraw.json','/home/larda3/larda-connectordump/cge/connector_POLLYNET.json','/home/larda3/larda-connectordump/cge/connector_POLLYNETprofiles.json','/home/larda3/larda-connectordump/cge/connector_POLLYraw.json','/home/larda3/larda-connectordump/cloudlab/connector_POLLYNET.json','/home/larda3/larda-connectordump/cloudlab/connector_POLLYNETprofiles.json','/home/larda3/larda-connectordump/cloudlab/connector_POLLYraw.json','/home/larda3/larda-connectordump/cloudlab_II/connector_POLLYNET.json','/home/larda3/larda-connectordump/cloudlab_II/connector_POLLYNETprofiles.json','/home/larda3/larda-connectordump/cloudlab_II/connector_POLLYraw.json','/home/larda3/larda-connectordump/cloudlab_III/connector_POLLYNET.json','/home/larda3/larda-connectordump/cloudlab_III/connector_POLLYNETprofiles.json','/home/larda3/larda-connectordump/cloudlab_III/connector_POLLYraw.json','/home/larda3/larda-connectordump/coala/connector_POLLYNET_24h.json','/home/larda3/larda-connectordump/coala/connector_POLLYNET.json','/home/larda3/larda-connectordump/coala/connector_POLLYNETprofiles.json','/home/larda3/larda-connectordump/coala/connector_POLLYraw.json','/home/larda3/larda-connectordump/cv_oscm/connector_POLLYNET.json','/home/larda3/larda-connectordump/cv_oscm/connector_POLLYNETprofiles.json','/home/larda3/larda-connectordump/cv_oscm/connector_POLLYraw.json','/home/larda3/larda-connectordump/cyp/connector_POLLYNET.json','/home/larda3/larda-connectordump/cyp/connector_POLLYNETprofiles.json','/home/larda3/larda-connectordump/cyp/connector_POLLYraw.json','/home/larda3/larda-connectordump/fmi/connector_POLLYNET.json','/home/larda3/larda-connectordump/fmi/connector_POLLYNETprofiles.json','/home/larda3/larda-connectordump/fmi/connector_POLLYraw.json','/home/larda3/larda-connectordump/GoSouth_II/connector_POLLYNET.json','/home/larda3/larda-connectordump/GoSouth_II/connector_POLLYNETprofiles.json','/home/larda3/larda-connectordump/GoSouth_II/connector_POLLYraw2.json','/home/larda3/larda-connectordump/lacros_accept/connector_POLLY.json','/home/larda3/larda-connectordump/lacros_accept/connector_POLLYNET.json','/home/larda3/larda-connectordump/lacros_accept/connector_POLLYNETprofiles.json','/home/larda3/larda-connectordump/lacros_accept/connector_POLLYraw.json','/home/larda3/larda-connectordump/lacros_cycare/connector_POLLY.json','/home/larda3/larda-connectordump/lacros_cycare/connector_POLLYNET.json','/home/larda3/larda-connectordump/lacros_cycare/connector_POLLYNETprofiles.json','/home/larda3/larda-connectordump/lacros_cycare/connector_POLLYraw.json','/home/larda3/larda-connectordump/lacros_dacapo/connector_POLLY.json','/home/larda3/larda-connectordump/lacros_dacapo/connector_POLLYNET.json','/home/larda3/larda-connectordump/lacros_dacapo/connector_POLLYNETprofiles.json','/home/larda3/larda-connectordump/lacros_dacapo/connector_POLLYNETprofilesNR.json','/home/larda3/larda-connectordump/lacros_dacapo/connector_POLLYNETprofilesOC.json','/home/larda3/larda-connectordump/lacros_dacapo/connector_POLLYraw.json','/home/larda3/larda-connectordump/lacros_dacapo_gpu/connector_POLLYNET.json','/home/larda3/larda-connectordump/lacros_dacapo_gpu/connector_POLLYNETprofiles.json','/home/larda3/larda-connectordump/lacros_dacapo_gpu/connector_POLLYraw.json','/home/larda3/larda-connectordump/lacros_leipzig/connector_POLLY.json','/home/larda3/larda-connectordump/lacros_leipzig/connector_POLLYNET2.json','/home/larda3/larda-connectordump/lacros_leipzig/connector_POLLYNET.json','/home/larda3/larda-connectordump/lacros_leipzig/connector_POLLYNETprofiles2.json','/home/larda3/larda-connectordump/lacros_leipzig/connector_POLLYNETprofiles.json','/home/larda3/larda-connectordump/lacros_leipzig/connector_POLLYraw2.json','/home/larda3/larda-connectordump/lacros_leipzig/connector_POLLYraw.json','/home/larda3/larda-connectordump/lidars_leipzig_ceilo_calib_historical/connector_POLLYNET_arielle.json','/home/larda3/larda-connectordump/lidars_leipzig/connector_POLLYNET_arielle.json','/home/larda3/larda-connectordump/lidars_leipzig/connector_POLLYNET_cyp.json','/home/larda3/larda-connectordump/lidars_leipzig/connector_POLLYNETprofiles_arielle.json','/home/larda3/larda-connectordump/lidars_leipzig/connector_POLLYNETprofiles_cyp.json','/home/larda3/larda-connectordump/lidars_leipzig/connector_POLLYNETprofiles_TROPOS.json','/home/larda3/larda-connectordump/lidars_leipzig/connector_POLLYNET_TROPOS.json','/home/larda3/larda-connectordump/lostecca/connector_POLLYNET.json','/home/larda3/larda-connectordump/lostecca/connector_POLLYNETprofiles.json','/home/larda3/larda-connectordump/lostecca/connector_POLLYNETprofilesNR.json','/home/larda3/larda-connectordump/lostecca/connector_POLLYraw.json','/home/larda3/larda-connectordump/martha/connector_POLLYNET.json','/home/larda3/larda-connectordump/martha/connector_POLLYNETprofiles.json','/home/larda3/larda-connectordump/martha/connector_POLLY_QUICKLOOKS.json','/home/larda3/larda-connectordump/martha/connector_POLLYraw.json','/home/larda3/larda-connectordump/mosaic/connector_POLLYNET.json','/home/larda3/larda-connectordump/mosaic/connector_POLLYNETprofiles.json','/home/larda3/larda-connectordump/noa/connector_POLLYNET.json','/home/larda3/larda-connectordump/noa/connector_POLLYNETprofiles.json','/home/larda3/larda-connectordump/noa/connector_POLLYraw.json','/home/larda3/larda-connectordump/oceanet_atlantic/connector_POLLYNET.json','/home/larda3/larda-connectordump/oceanet_atlantic/connector_POLLYNETprofiles.json','/home/larda3/larda-connectordump/oceanet_M207/connector_POLLYNET.json','/home/larda3/larda-connectordump/oceanet_M207/connector_POLLYNETprofiles.json','/home/larda3/larda-connectordump/oceanet_pascal/connector_POLLYNET.json','/home/larda3/larda-connectordump/oceanet_pascal/connector_POLLYNETprofiles.json','/home/larda3/larda-connectordump/oceanet_sonne/connector_POLLYNET.json','/home/larda3/larda-connectordump/oceanet_sonne/connector_POLLYNETprofiles.json','/home/larda3/larda-connectordump/polly_1v2/connector_POLLYNET.json','/home/larda3/larda-connectordump/polly_1v2/connector_POLLYNETprofiles.json','/home/larda3/larda-connectordump/polly_1v2/connector_POLLY_QUICKLOOKS.json','/home/larda3/larda-connectordump/polly_1v2/connector_POLLYraw.json','/home/larda3/larda-connectordump/polly_1v2_leipzig/connector_POLLYNET.json','/home/larda3/larda-connectordump/polly_1v2_leipzig/connector_POLLYNETprofiles.json','/home/larda3/larda-connectordump/polly_1v2_tirana/connector_POLLYNET.json','/home/larda3/larda-connectordump/polly_1v2_tirana/connector_POLLYNETprofiles.json','/home/larda3/larda-connectordump/polly_arielle_leipzig/connector_POLLYNET.json','/home/larda3/larda-connectordump/polly_arielle_leipzig/connector_POLLYNETprofiles.json','/home/larda3/larda-connectordump/polly_ift_leipzig/connector_POLLYNET.json','/home/larda3/larda-connectordump/polly_ift_leipzig/connector_POLLYNETprofiles.json','/home/larda3/larda-connectordump/pollyxt_arielle/connector_POLLYNET.json','/home/larda3/larda-connectordump/pollyxt_arielle/connector_POLLYNETprofiles.json','/home/larda3/larda-connectordump/pollyxt_arielle/connector_POLLY_QUICKLOOKS.json','/home/larda3/larda-connectordump/pollyxt_arielle/connector_POLLYraw.json','/home/larda3/larda-connectordump/pollyxt_cge/connector_POLLYNET.json','/home/larda3/larda-connectordump/pollyxt_cge/connector_POLLYNETprofiles.json','/home/larda3/larda-connectordump/pollyxt_cge/connector_POLLY_QUICKLOOKS.json','/home/larda3/larda-connectordump/pollyxt_cge/connector_POLLYraw.json','/home/larda3/larda-connectordump/pollyxt_cpv/connector_POLLYNET.json','/home/larda3/larda-connectordump/pollyxt_cpv/connector_POLLYNETprofiles.json','/home/larda3/larda-connectordump/pollyxt_cpv/connector_POLLY_QUICKLOOKS.json','/home/larda3/larda-connectordump/pollyxt_cpv/connector_POLLYraw.json','/home/larda3/larda-connectordump/pollyxt_cyp/connector_POLLYNET.json','/home/larda3/larda-connectordump/pollyxt_cyp/connector_POLLYNETprofiles.json','/home/larda3/larda-connectordump/pollyxt_cyp/connector_POLLY_QUICKLOOKS.json','/home/larda3/larda-connectordump/pollyxt_cyp/connector_POLLYraw.json','/home/larda3/larda-connectordump/pollyxt_dwd/connector_POLLYNET.json','/home/larda3/larda-connectordump/pollyxt_dwd/connector_POLLYNETprofiles.json','/home/larda3/larda-connectordump/pollyxt_dwd/connector_POLLY_QUICKLOOKS.json','/home/larda3/larda-connectordump/pollyxt_dwd/connector_POLLYraw.json','/home/larda3/larda-connectordump/pollyxt_fmi/connector_POLLYNET.json','/home/larda3/larda-connectordump/pollyxt_fmi/connector_POLLYNETprofiles.json','/home/larda3/larda-connectordump/pollyxt_fmi/connector_POLLY_QUICKLOOKS.json','/home/larda3/larda-connectordump/pollyxt_fmi/connector_POLLYraw.json','/home/larda3/larda-connectordump/pollyxt_lacros2/connector_POLLYNET.json','/home/larda3/larda-connectordump/pollyxt_lacros2/connector_POLLYNETprofiles.json','/home/larda3/larda-connectordump/pollyxt_lacros2/connector_POLLY_QUICKLOOKS.json','/home/larda3/larda-connectordump/pollyxt_lacros2/connector_POLLYraw.json','/home/larda3/larda-connectordump/pollyxt_lacros/connector_POLLYNET.json','/home/larda3/larda-connectordump/pollyxt_lacros/connector_POLLYNETprofiles.json','/home/larda3/larda-connectordump/pollyxt_lacros/connector_POLLY_QUICKLOOKS.json','/home/larda3/larda-connectordump/pollyxt_lacros/connector_POLLYraw.json','/home/larda3/larda-connectordump/pollyxt_noa/connector_POLLYNET.json','/home/larda3/larda-connectordump/pollyxt_noa/connector_POLLYNETprofiles.json','/home/larda3/larda-connectordump/pollyxt_noa/connector_POLLY_QUICKLOOKS.json','/home/larda3/larda-connectordump/pollyxt_noa/connector_POLLYraw.json','/home/larda3/larda-connectordump/pollyxt_tau/connector_POLLYNET.json','/home/larda3/larda-connectordump/pollyxt_tau/connector_POLLYNETprofiles.json','/home/larda3/larda-connectordump/pollyxt_tau/connector_POLLY_QUICKLOOKS.json','/home/larda3/larda-connectordump/pollyxt_tau/connector_POLLYraw.json','/home/larda3/larda-connectordump/pollyxt_tjk/connector_POLLYNET.json','/home/larda3/larda-connectordump/pollyxt_tjk/connector_POLLYNETprofiles.json','/home/larda3/larda-connectordump/pollyxt_tjk/connector_POLLY_QUICKLOOKS.json','/home/larda3/larda-connectordump/pollyxt_tjk/connector_POLLYraw.json','/home/larda3/larda-connectordump/pollyxt_tropos_cadex/connector_POLLYNET.json','/home/larda3/larda-connectordump/pollyxt_tropos_cadex/connector_POLLYNETprofiles.json','/home/larda3/larda-connectordump/pollyxt_tropos/connector_POLLYNET.json','/home/larda3/larda-connectordump/pollyxt_tropos/connector_POLLYNETprofiles.json','/home/larda3/larda-connectordump/pollyxt_tropos/connector_POLLY_QUICKLOOKS.json','/home/larda3/larda-connectordump/pollyxt_tropos/connector_POLLYraw.json','/home/larda3/larda-connectordump/pollyxt_tropos_haifa/connector_POLLYNET.json','/home/larda3/larda-connectordump/pollyxt_tropos_haifa/connector_POLLYNETprofiles.json','/home/larda3/larda-connectordump/pollyxt_tropos_kuopio/connector_POLLYNET.json','/home/larda3/larda-connectordump/pollyxt_tropos_kuopio/connector_POLLYNETprofiles.json','/home/larda3/larda-connectordump/pollyxt_tropos_kuopio/connector_POLLY_QUICKLOOKS.json','/home/larda3/larda-connectordump/pollyxt_tropos_kuopio/connector_POLLYraw.json','/home/larda3/larda-connectordump/pollyxt_uw/connector_POLLYNET.json','/home/larda3/larda-connectordump/pollyxt_uw/connector_POLLYNETprofiles.json','/home/larda3/larda-connectordump/pollyxt_uw/connector_POLLY_QUICKLOOKS.json','/home/larda3/larda-connectordump/pollyxt_uw/connector_POLLYraw.json','/home/larda3/larda-connectordump/rsd_leipzig/connector_POLLYNET_arielle.json','/home/larda3/larda-connectordump/rsd_leipzig/connector_POLLYNET_pollyxt_lacros.json','/home/larda3/larda-connectordump/rsd_leipzig/connector_POLLYraw_arielle.json','/home/larda3/larda-connectordump/rsd_leipzig/connector_POLLYraw_pollyxt_lacros.json','/home/larda3/larda-connectordump/tau/connector_POLLYNET.json','/home/larda3/larda-connectordump/tau/connector_POLLYNETprofiles.json','/home/larda3/larda-connectordump/tau/connector_POLLYraw.json','/home/larda3/larda-connectordump/tjk/connector_POLLYNET.json','/home/larda3/larda-connectordump/tjk/connector_POLLYNETprofiles.json','/home/larda3/larda-connectordump/tjk/connector_POLLYraw.json'
#        ]
con_ls = [
#connectorfile = "/home/larda3/larda-connectordump/GoSouth_II/connector_POLLYraw2.json"
#connectorfile = "/home/larda3/larda-connectordump/pollyxt_arielle/connector_POLLYNET.json"
#"/home/larda3/larda-connectordump/rsd_leipzig/connector_POLLYNET_arielle.json",
"/home/larda3/larda-connectordump/rsd_leipzig/connector_POLLYraw_arielle.json",
"/home/larda3/larda-connectordump/rsd_leipzig/connector_POLLYNET_pollyxt_lacros.json",
]
meta_dict_ls = tromeda.get_device_info(config_dict=config_dict, timestamp=date, site=site, dev_type=dev_type)
#print(meta_dict_ls)
for connectorfile in  con_ls:
    connectorfile_name_only = tromeda.get_connectorfile_name_only(connectorfile)
    campaign = tromeda.get_pylarda_campaign_from_connectorfile(connectorfile)
    print(connectorfile_name_only)
    print(campaign)
#print(meta_dict_ls)
#exit()
    for metadata_entry in meta_dict_ls:
        device_site_result = tromeda.get_device_and_location_from_connectorfile_name_and_pylarda_campaign(metadata_entry,connectorfile_name_only,campaign)
        if device_site_result != None:
            device = device_site_result['device']
            site = device_site_result['site']
            site = re.split(r' \(',site)[0].lower()
            print(connectorfile)
            print(device,site,campaign)
            system = tromeda.get_system_from_connectorfile(connectorfile)
            folder = tromeda.get_campaign_dir_from_connectorfile(connectorfile)
            #print(system)
            #print(folder)
            if 'POLLYraw'.lower() in system.lower():
                filetype = 'source_files'
                system_key = "nc"
                qu_files = None
            elif 'POLLYNET'.lower() in system.lower() :
                filetype = 'processed_files'
                system_key = "attbsc"
                qu_filetype = 'polly_quicklook'
                qu_system_key = 'polly'
                if device == 'arielle':
                    qu_system_key = f'pollyxt_{device}'
                else:
                    qu_system_key = device
                qu_connectorfile = Path(folder,f'connector_POLLY_QUICKLOOKS.json')
                if qu_connectorfile:
                    qu_files = tromeda.get_files_from_connectorfile(config_dict, qu_connectorfile, system_key=qu_system_key, start_date=start_date, end_date=end_date)
                else:
                    qu_files = None
            files = tromeda.get_files_from_connectorfile(config_dict, connectorfile, system_key=system_key, start_date=start_date, end_date=end_date)
            print(filetype)
            print(files)
            print(qu_files)
exit()
#url = f'{config_dict["basic_url"]}?pid={campaign}'
#metadata = requests.get(url).json()
#for entry in metadata.keys():
#    if dev_type in metadata[entry]['type']:
#        device = entry
device = tromeda.get_device_from_connectorfile_translator_dict(connectorfile_translator_dict,connectorfile)
source_files = tromeda.get_files_from_connectorfile(config_dict, connectorfile, system_key="nc", start_date=start_date, end_date=end_date)
print(source_files)
print(device)
connectorfile = "/home/larda3/larda-connectordump/GoSouth_II/connector_POLLYNET.json"
processed_files = tromeda.get_files_from_connectorfile(config_dict, connectorfile, system_key="attbsc", start_date=start_date, end_date=end_date)
device = tromeda.get_device_from_connectorfile_translator_dict(connectorfile_translator_dict,connectorfile)
print(device)
#for d in processed_files.keys():
#    print(d,processed_files[d])

connectorfile = "/home/larda3/larda-connectordump/GoSouth_II/connector_RSD_QUICKLOOKS.json"
quicklook_files = tromeda.get_files_from_connectorfile(config_dict, connectorfile, system_key="polly", start_date=start_date, end_date=end_date)
#for d in quicklook_files.keys():
#    print(d,quicklook_files[d])
exit()
for d in source_files.keys():
    print(d)
    print(source_files[d])
    if d in processed_files.keys():
        print(processed_files[d])
    else:
        print(f'no processed entry for {d}')
    if d in quicklook_files.keys():
        print(quicklook_files[d])
    else:
        print(f'no quicklook entry for {d}')



#start_date = '20250918'
#end_date = '20250918'
#start_date = None
#end_date = None

#end_date = start_date
print(date)
#site = 'invercargill'
#site = 'leipzig'
#dev_type = 'halo'
#dev_type = 'ceilo'
#dev_type = 'polly'
#meta_dict_ls = tromeda.get_device_info(config_dict=config_dict, timestamp='20231207', site='eriswil', dev_type='halo')
#print(meta_dict_ls)
#meta_dict_ls = tromeda.get_device_info(config_dict=config_dict, timestamp='20250410', site='leipzig', dev_type='polly')


for entry in meta_dict_ls:
    device = tromeda.get_device(entry)
    print(device)
    #print(meta_dict_ls)
    #exit()
    campaign = tromeda.get_campaign(entry)
    print(campaign)
    correct_system = tromeda.find_correct_system(config_dict,entry)
    print(correct_system)
    #correct_system = 'POLLYNET'
    connectorfile = tromeda.get_connectorfile(config_dict,entry,correct_system)
    print(connectorfile)
    device = tromeda.get_device_from_connectorfile(config_dict,connectorfile)
#    continue
#    exit()
    param_file = tromeda.get_paramfile_from_pylarda_connectorfile(config_dict,connectorfile)
    #print(param_file)
#    system_key = 'nc_lvl0'
    system_key = 'attbsc'
#    system_key = 'nc'
#    system_key = 'scans'
    base_dir = tromeda.get_base_dir_from_paramfile(config_dict,correct_system,param_file,system_key)
    #print(base_dir)
    connector_dict = read_json(connectorfile)
    #print(connector_dict)

    if date == 'all':
        date = None
    print(system_key)
    processed_files= tromeda.files_query(connector_dict, system_key, start_date, end_date, basedir=base_dir)
    ## levle0-files
    correct_system = 'POLLYraw2'
    connectorfile = tromeda.get_connectorfile(config_dict,entry,correct_system)
    param_file = tromeda.get_paramfile_from_pylarda_connectorfile(config_dict,connectorfile)
    system_key = 'nc'
    base_dir = tromeda.get_base_dir_from_paramfile(config_dict,correct_system,param_file,system_key)
    connector_dict = read_json(connectorfile)

    if date == 'all':
        date = None
    print(system_key)
    source_files = tromeda.files_query(connector_dict, system_key, start_date, end_date, basedir=base_dir)

    correct_system = 'RSD_QUICKLOOKS'
    connectorfile = tromeda.get_connectorfile(config_dict,entry,correct_system)
    param_file = tromeda.get_paramfile_from_pylarda_connectorfile(config_dict,connectorfile)
    system_key = 'polly'
    base_dir = tromeda.get_base_dir_from_paramfile(config_dict,correct_system,param_file,system_key)
    connector_dict = read_json(connectorfile)

    if date == 'all':
        date = None
    print(system_key)
    quicklook_files = tromeda.files_query(connector_dict, system_key, start_date, end_date, basedir=base_dir)

    for d in source_files.keys():
        print(d,source_files[d])
    for d in processed_files.keys():
        print(d,processed_files[d])
    for d in quicklook_files.keys():
        print(d,quicklook_files[d])
