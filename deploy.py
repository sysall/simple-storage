import json
from solcx import compile_standard, install_solc
from web3 import Web3
import os
from dotenv import load_dotenv

load_dotenv()

#1: read the solidity file 
with open("./SimpleStorage.sol", "r") as file:
    simple_storage_file = file.read()

#2: Compile our Solidity
install_solc("0.6.0")
compiled_sol = compile_standard(
    {
        "language": "Solidity",
        "sources" : {"SimpleStorage.sol": {"content": simple_storage_file}},
        "settings": {
            "outputSelection": {
                "*": {"*": ["abi", "metadata", "evm.bytecode", "evm.sourceMap"]}
            }
        }
    },
    solc_version = "0.6.0"
)
#print(compiled_sol)
with open("compile_code.json", "w") as file:
    json.dump(compiled_sol, file)

# get bytecode
bytecode = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["evm"]["bytecode"]["object"]

# get abi
abi = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["abi"]

# Connnecting to Ganache
#w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
# Connecting to ethereum testnest
w3 = Web3(Web3.HTTPProvider("https://sepolia.infura.io/v3/7e206c5589564950abe83bc42de908e0"))
#chain_id = 1337
#change testnest chainID https://chainid.network/
chain_id = 11155111
my_address = "0x529461ED5cbD65b5ebdA8a7d8C4c69e301fbe570"
# create .env file for the keys : source .env
private_key = os.getenv("PRIVATE_KEY")
gasPrice = w3.eth.gas_price
print(gasPrice)

#Create the contract in python
SimpleStorage = w3.eth.contract(abi=abi, bytecode=bytecode)

# Get the latest transactions
nonce = w3.eth.get_transaction_count(my_address) 

#  Deploy our contract
# 1. Build Transaction
# 2. Sign a transaction
# 3. Send a transaction
transaction = SimpleStorage.constructor().build_transaction(
    {"chainId": chain_id, "gasPrice": gasPrice, "from": my_address, "nonce": nonce}
)
signed_txn = w3.eth.account.sign_transaction(transaction, private_key=private_key)
#Send this sign transaction
print("Deploying contract ....")
tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
print("Deployed!")
# Working with the contract w/ contract address and contract ABI
simple_storage = w3.eth.contract(address=tx_receipt.contractAddress, abi=abi)
# Call -> Simulate making call and getting a return value
#print(simple_storage.functions.retrieve().call())
# Transact -> Actually make a state change
# Call function just simulate the function but don't make any state change
#print(simple_storage.functions.store(15).call())
print("Updating Contract .....")
store_tx = simple_storage.functions.store(20).build_transaction(
    {"chainId": chain_id, "from": my_address, "nonce": nonce + 1}
)
signed_store_tx = w3.eth.account.sign_transaction(store_tx, private_key=private_key)
send_store_tx = w3.eth.send_raw_transaction(signed_store_tx.rawTransaction)
store_tx_receipt = w3.eth.wait_for_transaction_receipt(send_store_tx)
print("Updated!")
print(simple_storage.functions.retrieve().call())

#install node, yarn to use ganache cli instead of ui 
# to get the same addresses use the command ganache-cli --deterministic to run it instead of only ganache-cli

#so far we deploy the contract on local blockchain and testnet using infura.