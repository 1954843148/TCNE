import os
import sys
import numpy as np
import pdb

from utils import common_tools as ct
from utils.data_handler import DataHandler as dh


def params_handler(params, info, pre_res, **kwargs):
    res = {}
    if ( "tag_walker" in pre_res ) and ( "walk_file" in pre_res["tag_walker"] ):
        params["walk_file"] = pre_res["tag_walker"]["walk_file"]
    else:
        params["walk_file"] = os.path.join(info["home_path"], params["walk_file"])
    if "model_path" in params["embedding_model"]:
        params["embedding_model"]["model_path"] = os.path.join(info["home_path"], params["embedding_model"]["model_path"])
    else:
        params["model_path"] = pre_res["optimize"]["model_path"]
    
    #if "dim" not in params["get_features"]:
    #    params["get_features"]["dim"] = params["tag_num"]
    gf_handler = __import__("get_features." + params["get_features"]["func"], fromlist = ["get_features"])
    features = gf_handler.get_features(params["get_features"], info)  # return numpy
    if "dim" not in params["get_features"]:
        params["get_features"]["dim"] = features.shape[1]

    params["embedding_model"]["aggregator"]["feature_num"] = params["get_features"]["dim"]
    res["entity_embedding_path"] = os.path.join(info["res_home"], "embeds.pkl")

    params["embedding_model"]["en_embed_size"] = info["en_embed_size"]
    params["embedding_model"]["tag_embed_size"] = info["tag_embed_size"]
    params["embedding_model"]["output_embed_size"] = info["output_embed_size"]
    params["embedding_model"]["res_home"] = info["res_home"]
    params["embedding_model"]["batch_size"] = params["batch_size"]
    params["embedding_model"]["show_num"] = params["show_num"]
    params["embedding_model"]["logger"] = info["logger"]
    
    G_entity = dh.load_entity_as_graph(os.path.join(info["network_folder"]["name"], info["network_folder"]["edge"]), \
            os.path.join(info["network_folder"]["name"], info["network_folder"]["mix_edge"]), \
            os.path.join(info["network_folder"]["name"], info["network_folder"]["entity"]), \
            os.path.join(info["network_folder"]["name"], info["network_folder"]["tag"]))
    G_tag = dh.load_edge_as_graph(params["walk_file"], \
            os.path.join(info["network_folder"]["name"], info["network_folder"]["tag"])) # walk file

    params["embedding_model"]["en_num"] = len(G_entity.nodes())
    params["embedding_model"]["tag_num"] = len(G_tag.nodes())
    info["en_num"] = params["embedding_model"]["en_num"]
    info["tag_num"] = params["embedding_model"]["tag_num"]


    return res, G_entity, G_tag, features

@ct.module_decorator
def infer(params, info, pre_res, **kwargs):
    res, G_entity, G_tag, features = params_handler(params, info, pre_res)
    
    
    model_handler = __import__("model." + params["embedding_model"]["func"], fromlist=["model"])
    model = model_handler.TagConditionedEmbedding(params["embedding_model"], features)
    bs_handler = __import__("batch_strategy." + params["batch_strategy"], fromlist=["batch_strategy"])
    bs = bs_handler.BatchStrategy(G_tag, G_entity, params)
    embeds = model.infer(bs.get_all(), params["embedding_model"]["model_path"])
    dh.save_as_pickle(embeds, res["entity_embedding_path"])

    return res
