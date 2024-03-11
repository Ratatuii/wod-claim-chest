from eth_account import Account
from web3 import Web3
from datetime import datetime
import requests
import time

# Connect to opBNB network
infura_url = 'https://opbnb-mainnet-rpc.bnbchain.org'
web3 = Web3(Web3.HTTPProvider(infura_url))


# Check connection
if not web3.is_connected():
    print("Not connected to Ethereum network")
    exit()

# URL to send the POST request to
url_collect_chest = 'https://worldofdypiansdailybonus.azurewebsites.net/api/CollectChest'

# Headers for the POST request
headers = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "uk,ru-RU;q=0.9,ru;q=0.8,en-US;q=0.7,en;q=0.6,bg;q=0.5,es;q=0.4",
    "Connection": "keep-alive",
    "Content-Type": "application/json",
    "Host": "worldofdypiansdailybonus.azurewebsites.net",
    "Origin": "https://www.worldofdypians.com",
    "Referer": "https://www.worldofdypians.com/",
    "Sec-Ch-Ua": "\"Not_A Brand\";v=\"8\", \"Chromium\";v=\"120\", \"Google Chrome\";v=\"120\"",
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": "\"Windows\"",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "cross-site",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# Read email and private keys from file
with open("info.txt", "r") as file:
    info_lines = file.readlines()

# Process for each line in info.txt
for line in info_lines:
    email, private_key = line.strip().split(':')

    # Create Ethereum account from private key
    account = Account.from_key(private_key)
    account_address = web3.to_checksum_address(account.address)
    recipient_address = web3.to_checksum_address('0xd600fbcf64da43ccbb4ab6da61007f5b1f8fe455')

    # Repeat process 10 times for each email and private key       
    for chestIndex in range(10):
        # Prepare the transaction with the method ID
        nonce = web3.eth.get_transaction_count(account_address)
        tx = {
            'to': recipient_address,
            'gas': 50000,
            'gasPrice': web3.to_wei('0.001', 'gwei'),
            'nonce': nonce,
            'data': '0x6f49a3c0',  # Method ID for openChest()
            'chainId': web3.eth.chain_id 
        }

        # Sign and send the transaction
        signed_tx = web3.eth.account.sign_transaction(tx, private_key)

        tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
        txn_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
        ht = str(tx_hash.hex())

        # Payload for the POST request
        payload = {
            "transactionHash": ht,
            "emailAddress": email,
            "chestIndex": chestIndex
        }

        # Sending the POST request
        response = requests.post(url_collect_chest, json=payload, headers=headers)
        # Check if the request was successful
        if response.status_code == 200:
            try:
                response_json = response.json()
                rewards = response_json.get("rewards", None)
                if rewards is not None:
                    print(f"Email: {email}, ChestIndex: {chestIndex}, Rewards: {rewards}")
                    date = datetime.now().strftime("%d %B %Y")
                    with open('result.txt', 'a+') as file:
                        date = datetime.now().strftime("%d %B %Y")
                        file.write(f'Date: {date}, Email: {email}, ChestIndex: {chestIndex}, Rewards: type rewards: {rewards[0]["rewardType"]} - {rewards[0]["reward"]}\n')
                else:
                    print("Rewards not found in the response.")
            except ValueError:
                print("Failed to parse response as JSON.")
        else:
            print("Status Code:", response.status_code, "Response:", response.text)
