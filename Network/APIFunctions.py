from pathlib import Path
from os import path
import json

def getBinanceConfig(logger, test_net=False):
    with open(path.join(Path.home(), "binance.json")) as fp:
        b_config = json.loads(fp.read())
    
    if test_net:
        logger.info("running with binance TEST server")
        return {
            "url": "https://testnet.binance.vision/api", 
            "api_key": b_config["api_key_test"], 
            "api_secret":b_config["api_secret_test"]}
    else:
        logger.info("running with binance LIFE server")
        return {
            "url": "https://api.binance.com/api", 
            "api_key": b_config["api_key"], 
            "api_secret": b_config["api_secret"]}


