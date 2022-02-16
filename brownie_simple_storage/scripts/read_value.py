from brownie import SimpleStorage, accounts, config

def read_contract():
    # Access first deployment
    first_simple_storage = SimpleStorage[0]
    
    # Access lastest deployment
    simple_storage = SimpleStorage[-1]
    # We already updated the value to 15 when we deploy the contract
    print(simple_storage.retrieve())
    
    
def main():
    read_contract()
    