# Paste your version of miner.py from the clinet_mining_p
# folder here
import hashlib
import requests

import sys


# TODO: Implement functionality to search for a proof
def proof_of_work(last_block_string):
    """
    Simple Proof of Work Algorithm
    Find a number p such that hash(last_block_string, p) contains 6 leading
    zeroes
    """
    print("Starting work on a new proof...")
    proof = 0
    # for block 1, hash(1,p) = 000000x
    while valid_proof(last_block_string, proof) is False:
        proof += 1
    print("This is work done")
    return proof


def valid_proof(last_block_string, proof):
    """
    Validates the Proof:
    Does hash(block_string, proof)
    contain 6 leading zeroes?
    """
    # build string to hash
    guess = f'{last_block_string}{proof}'.encode()
    # use hash function
    guess_hash = hashlib.sha256(guess).hexdigest()
    # check if 6 leading 0's
    beg = guess_hash[0:6]  # [:6]
    if beg == "000000":
        return True
    else:
        return False


if __name__ == '__main__':
    # What node are we interacting with?
    if len(sys.argv) > 1:
        node = sys.argv[1]
    else:
        node = "http://localhost:5000"

    coins_mined = 0
    # Run forever until interrupted
    while True:
        # TODO: Get the last proof from the server and look for a new one
        r = requests.get(node+'/last_block_string')
        data = r.json()
        last_block_string = data['last_block_string']['previous_hash']
        print(last_block_string)
        # Look for a new one
        new_proof = proof_of_work(last_block_string)

        # TODO: When found, POST it to the server {"proof": new_proof}

        # TODO: We're going to have to research how to do a POST in Python
        # Do a POST in python
        proof_data = {'proof': new_proof}
        print('proof_data:', proof_data)
        r = requests.post(url=f'{node}/mine', json=proof_data)
        # HINT: Research `requests` and remember we're sending our data as JSON
        # TODO: If the server responds with 'New Block Forged'
        # add 1 to the number of coins mined and print it.  Otherwise,
        # print the message from the server.
        data = r.json()
        if data.get('message') == "New Block Forged":
            coins_mined += 1
            print(f'You have mined: {coins_mined} coins')
        print(data.get('message'))
