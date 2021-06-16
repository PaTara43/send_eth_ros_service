#!/usr/bin/env python3
import logging
import rospy
import yaml
import rospkg

from send_eth.srv import send_eth_srv
from web3 import Web3
from web3.gas_strategies.time_based import medium_gas_price_strategy


def read_configuration(dirname: str) -> dict:
    """
    :param dirname: path to repo folder
    :return: dictionary, containing all the configuration info
    """
    config_path = dirname + "/config/config.yaml"
    logging.debug(config_path)

    try:
        with open(config_path) as f:
            content = f.read()
            config = yaml.load(content, Loader=yaml.FullLoader)
            logging.debug(f"Configuration dict: {content}")
            return config
    except Exception as e:
        while True:
            logging.error("Error in configuration file!")
            logging.error(e)
            exit()


def handle_send_eth(req, w3, config: dict) -> bool:
    """
    Send eth to required address

    :param config: dictionary, containing all the configuration info
    :param w3: instance of web3. Used to do stuff with eth by python
    :type w3: see docs
    :param req: request to handle
    :type req: see ../srv/send_eth_srv.srv
    :return: success or not
    """
    rospy.loginfo(f"Request to send {req.sum} ETH to {req.target_address}")

    nonce = w3.eth.getTransactionCount(req.source_address)
    tx = {
        'nonce': nonce,
        'to': req.target_address,
        'value': w3.toWei(req.sum, 'ether')
    }
    if config["general"]["testnet"]:
        tx.update({
            'gas': 200000,
            'gasPrice': w3.toWei('50', 'gwei')
        })
    else:
        w3.eth.setGasPriceStrategy(medium_gas_price_strategy)
        gas_price = w3.eth.generateGasPrice()
        rospy.loginfo(f"gas_price {gas_price}")
        tx.update({
            'gas': 21000,
            'gasPrice': gas_price
        })
    signed_tx = w3.eth.account.signTransaction(tx, req.private_key)
    tx_hash = w3.eth.sendRawTransaction(signed_tx.rawTransaction)
    rospy.loginfo(f"tx hash {tx_hash}")
    return True


def send_eth_server(config: dict) -> None:
    """
    Start server for handling requests

    :param config: dictionary, containing all the configuration info
    """

    rospy.init_node('send_eth_server')
    if config["general"]["testnet"]:
        provider = config["parameters"]["provider_testnet"]
        rospy.loginfo(f"Testnet")
    else:
        provider = config["parameters"]["provider"]
        rospy.loginfo(f"Mainnet")

    rospy.loginfo(f"Provider: {provider}")
    rospy.loginfo("Connecting to node")
    w3 = Web3(Web3.WebsocketProvider(provider))
    rospy.loginfo("Connected")

    handle_lambda = lambda x: handle_send_eth(x, w3, config)
    s = rospy.Service('send_eth', send_eth_srv, handle_lambda)
    rospy.loginfo(f"Ready send ETH.")
    rospy.spin()


if __name__ == "__main__":
    logging.debug("Reading configuration")
    rospack = rospkg.RosPack()
    packagePath = rospack.get_path("send_eth") + "/"
    config = read_configuration(packagePath)
    send_eth_server(config)
