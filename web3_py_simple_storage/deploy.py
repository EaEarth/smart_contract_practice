from solcx import compile_standard, install_solc
import json
import os
from web3 import Web3
from dotenv import load_dotenv

load_dotenv()

with open("./SimpleStorage.sol","r") as file:
    simple_storage_file = file.read()
    
install_solc("0.6.0")
compiled_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"SimpleStorage.sol": {"content": simple_storage_file}},
        "settings": {
            "outputSelection": {
                "*": {
                    "*": ["abi", "metadata", "evm.bytecode", "evm.sourceMap"]
                }
            }
        }
    },
    solc_version="0.6.0"
)

with open("compiled_code.json","w") as file:
    json.dump(compiled_sol, file)
    
# get bytecode
bytecode = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["evm"]["bytecode"]["object"]

#get abi
abi = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["abi"]

# connecting to ganache (simulated/local blockchain)
w3 = Web3(Web3.HTTPProvider("HTTP://127.0.0.1:7545"))
chain_id = 1337
my_address = "0x6328AA3eEb9779122205f98DE593b60e769Ec161"
private_key = os.getenv("PRIVATE_KEY")

# Create the contract
SimpleStorage = w3.eth.contract(abi=abi, bytecode=bytecode)
# Get lastest transaction
nonce = w3.eth.getTransactionCount(my_address)

# Deploy the contract = make a state change
# we need to follow these steps 
# 1. Build a transaction
# 2. Sign a transaction
# 3. Send a transaction

# 1.
transaction = SimpleStorage.constructor().buildTransaction({"gasPrice": w3.eth.gas_price, "chainId": chain_id, "from": my_address, "nonce": nonce})

#2.
signed_txn = w3.eth.account.sign_transaction(transaction, private_key=private_key)

#3.
print("Deploying Contract...")
tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
# Waiting for confirmation
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
print("Deployed!")

# Requirement from working with contract
# Contract address
# ContraCt ABI
simple_storage = w3.eth.contract(address=tx_receipt.contractAddress, abi=abi)

# Test the contract
# There are two ways to interact with the contract
# Call -> Simulate making the call and getting the return value. Don't make state changes. 
# Transact -> Actully Make state changes

# Initial value of favorite number
print(simple_storage.functions.retrieve().call())

# Simulate. Doesn't make real transaction
print(simple_storage.functions.store(15).call())

# Make real transaction.
print("Making transaction...")
store_transaction = simple_storage.functions.store(15).buildTransaction(
    {"gasPrice": w3.eth.gas_price, "chainId": chain_id, "from": my_address, "nonce": nonce+1}
)
signed_store_txn = w3.eth.account.sign_transaction(store_transaction, private_key=private_key)
send_store_tx = w3.eth.send_raw_transaction(signed_store_txn.rawTransaction)
store_tx_receipt = w3.eth.wait_for_transaction_receipt(send_store_tx)
print(simple_storage.functions.retrieve().call())
print("Made transaction!")