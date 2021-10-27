from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from bitcoinlib.wallets import Wallet, wallet_delete
from bitcoinlib.services.litecoind import LitecoindClient
from bitcoinlib.services import authproxy
from bitcoinlib.mnemonic import Mnemonic
import os

#global vars
db_uri = 'mysql://corepay:18781875Core@localhost:3306/corepay_ltc'
rpc = authproxy.AuthServiceProxy("http://%s:%s@127.0.0.1:18332"%("corepay","18781875Core"))

# base_url = 'http://user:password@server_url:18332'
# bdc = LitecoindClient(base_url=base_url)
# txid = 'e0cee8955f516d5ed333d081a4e2f55b999debfff91a49e8123d20f7ed647ac5'
# rt = bdc.getrawtransaction(txid)
# print("Raw: %s" % rt)

# init app
app = Flask(__name__)
# app.config["MYSQL_HOST"]="localhost"
# app.config["MYSQL_USER"]="corepay"


@app.route('/wallet/create', methods=['POST'])
def create_wallet():
    owner = request.json['owner']
    name = request.json['name']
    # create a Mnemonic
    passphrase = Mnemonic().generate()
    w = Wallet.create(name, keys=passphrase, network='litecoin_testnet', db_uri=db_uri, owner=owner)
    w = Wallet(name,db_uri=db_uri)
    return jsonify({'passphrase':passphrase,'info':w.as_json()})

@app.route('/wallet/balance',methods=['GET'])
def get_balance():
    wallet_name = request.json['wallet_name']
    # open the wallet
    w = Wallet(wallet_name,db_uri=db_uri)

    # scan for uxto's
    w.scan(network='litecoin_testnet')
    
    return jsonify({'balance': w.balance(network='litecoin_testnet')})


@app.route('/wallet/get-address', methods=['GET'])
def get_address():
    wallet_name = request.json['wallet_name']
    #open the wallet
    w = Wallet(wallet_name,db_uri=db_uri)
    # get the wallet key
    key = w.get_key(network='litecoin_testnet')

    #use the key to create a payment address
    return jsonify({'address':key.address})

@app.route('/wallet/send', methods=['POST'])
def send_to():
    wallet_name = request.json['wallet_name']
    reciever_address = request.json['reciever_address']
    amount = request.json['amount']
    #open wallet
    w = Wallet(wallet_name,db_uri=db_uri)
    t = t = w.send_to(reciever_address, amount ,network='litecoin_testnet',offline=True)
    return jsonify({t.info()})

@app.route('/wallet/tx/satus',methods=['GET'])
def tx_status():
    # wallet = request.json['wallet']
    address = request.json['address']
    #rescan blockchain
    if rpc.rescanblockchain():
        last_tx = rpc.listrecievedbyaddress(1,True,True,address)
        return last_tx
# start server
if __name__ == '__main__':
    app.run(debug=True)
