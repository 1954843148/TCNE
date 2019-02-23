import os
import sys
import json
import argparse
import numpy as np
import networkx as nx
import random
from operator import itemgetter

from utils.env import *
from utils.data_handler import DataHandler as dh
from utils import common_tools as ct

import pdb

def init(args, params, whole_params):
    """
        1. Inject params configuration of model into info
        2. set logger
        3. set random seed
        4. set symlink for the newly results and log
    """
    info = {}
    for k, v in params.items():
        info[k] = v
    info['debug_level'] = args.level
    info['time'] = ct.get_time_str()
    info['whole_params'] = whole_params
    info["conf_name"] = args.conf
    info["res_home"] = os.path.join(os.path.join(RES_PATH, args.conf), info["time"])
    if not os.path.exists(info["res_home"]):
        os.makedirs(info["res_home"])
    info["data_path"] = DATA_PATH
    info["home_path"] = ROOT_PATH
    info["network_folder"] = params["network_folder"]
    info["network_folder"]["name"] = os.path.join(DATA_PATH, params["network_folder"]["name"])

    log_path = os.path.join(LOG_PATH, info["time"] + ".log")
    info["logger"] = ct.get_logger(log_filename=log_path)
    ct.symlink(log_path, os.path.join(LOG_PATH, "new_log"))

    ct.symlink(info["res_home"], os.path.join(RES_PATH, "new_res"))

    random.seed(info["random_seed"])
    np.random.seed(info["np_seed"])
    return info

def main():
    parser = argparse.ArgumentParser(formatter_class = argparse.RawTextHelpFormatter)
    parser.add_argument("--conf", type = str, default = "lc")
    parser.add_argument("--level", type = str, default = "INFO", help="log level = INFO | DEBUG")
    args = parser.parse_args()
    params = dh.load_json(os.path.join(CONF_PATH, args.conf + ".json"))
    info = init(args, params["static_info"], params)
    info["logger"].info("init finished! \n %s \n" %(info))
    info["logger"].debug("log level is DEBUG")

    res = {}
    for module in params["run_modules"]:
        mdl_name = module["func"]
        mdl_params = module["params"]
        print (mdl_name)
        if info["debug_level"] == 'DEBUG':
            pdb.set_trace()
        # if mdl_name in ["construct_graph", "tag_walker", ""]:
        #     continue
        mdl = __import__(mdl_name + "." + mdl_params["func"], fromlist=[mdl_name])
        res[mdl_name] = getattr(mdl, mdl_name)(mdl_params, info = info, pre_res = res, mdl_name = mdl_name)


if __name__ == "__main__":
    main()
