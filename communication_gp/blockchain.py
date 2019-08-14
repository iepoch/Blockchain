# Paste your version of blockchain.py from the client_mining_p
# folder here
# Paste your version of blockchain.py from the basic_block_gp
# folder here
import hashlib
import json
from time import time
from uuid import uuid4

from flask import Flask, jsonify, request

from urllib.parse import urlparse


class Blockchain(object):
    def __init__(self):
        self.chain = []
        self.current_transactions = []
        self.nodes = set()

        # create the genesis_block
        if len(self.chain) == 0:
            self.create_genesis_block()

    def create_genesis_block(self):
        self.new_block(proof=5981, previous_hash=1)

    def new_block(self, proof, previous_hash=None):
        """
        Create a new Block in the Blockchain
        :param proof: <int> The proof given by the Proof of Work algorithm
        :param previous_hash: (Optional) <str> Hash of previous Block
        :return: <dict> New Block
        """

        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
        }

        # Reset the current list of transactions
        self.current_transactions = []

        self.chain.append(block)
        return block

    def new_transaction(self, sender, recipient, amount):
        """
        Creates a new transaction to go into the next mined Block
        :param sender: <str> Address of the Recipient
        :param recipient: <str> Address of the Recipient
        :param amount: <int> Amount
        :return: <int> The index of the BLock that will hold this transaction
        """

        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
        })

        return self.last_block['index'] + 1

    @staticmethod
    def hash(block):
        """
        Creates a SHA-256 hash of a Block
        :param block": <dict> Block
        "return": <str>
        """

        # We must make sure that the Dictionary is Ordered,
        # or we'll have inconsistent hashes

        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    @property
    def last_block(self):
        return self.chain[-1]

    # def proof_of_work(self, last_proof):
    #     """
    #     Simple Proof of Work Algorithm
    #     Find a number p such that hash(last_block_string, p) contains 6 leading
    #     zeroes
    #     """
    #     proof = 0
    #     # for block 1, hash(1,p) = 000000x
    #     while self.valid_proof(last_proof, proof) is False:
    #         proof += 1

    #     return proof

    @staticmethod
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

    def register_node(self, address):

        parsed_url = urlparse(address)

        self.nodes.add(parsed_url.netloc)

    def brodcast_new_block(self, block):
        neighbors = self.nodes
        post_data = {'block': block}

        for node in neighbors:
            r = request.post(f'http://{node}/block/new', json=post_data)

            if response.status_code != 200:
                # TODO:  Error handling

    def valid_chain(self, chain):
        """
        Determine if a given blockchain is valid
        :param chain: <list> A blockchain
        :return: <bool> True if valid, False if not
        """

        last_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]
            print(f'{last_block}')
            print(f'{block}')
            print("\n-------------------\n")
            # Check that the hash of the block is correct
            # TODO: Return false if hash isn't correct
            last_block_hash = self.hash(last_block)

            if block['previous_hash'] != last_block_hash:
                return False
            # Check that the Proof of Work is correct
            # TODO: Return false if proof isn't correct

            if not self.valid_proof(last_block['proof'], block['proof'], last_block_hash):
                return False

            last_block = block
            current_index += 1

        return True


# Instantiate our Node
app = Flask(__name__)

# Generate a globally unique address for this node
node_identifier = str(uuid4()).replace('-', '')

# Instantiate the Blockchain
blockchain = Blockchain()


@app.route('/mine', methods=['POST', 'GET'])
def mine():
    # We run the proof of work algorithm to get the next proof...
    values = request.get_json()
    required = ['proof']
    print(required)
    if not all(k in values for k in required):
        return 'Missing Values', 400

    print(f'This is the proof', values)
    if not blockchain.valid_proof(blockchain.last_block['previous_hash'], values['proof']):
        print("ERROR")
        response = {'message': "The proof is invalid. May have already been submitted"
                    }
        return jsonify(response),
        # We must receive a reward for finding the proof.
        # The sender is "0" to signify that this node has mine a new coin
        # The recipient is the current node, it did the mining!
        # The amount is 1 coin as a reward for mining the next block
    blockchain.new_transaction(0, node_identifier, 1)

    # Forge the new Block by adding it to the chain
    block = blockchain.new_block(
        values['proof'], blockchain.hash(blockchain.last_block))
    blockchain.brodcast_new_block(block)
    # Send a response with the new block
    response = {
        'message': "New Block Forged",
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
    }
    return jsonify(response), 200


@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.get_json()

    # Check that the required fields are in the POST'ed data
    required = ['sender', 'recipient', 'amount']
    if not all(k in values for k in required):
        return 'Missing Values', 400

    # Create a new Transaction
    index = blockchain.new_transaction(values['sender'],
                                       values['recipient'],
                                       values['amount'])

    response = {'message': f'Transaction will be added to Block {index}'}
    return jsonify(response), 201


@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        # TODO: Return the chain and its current length
        'currentChain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200


@app.route('/last_block_string', methods=['GET'])
def last_block_string():
    response = {
        # TODO: Return the the proof
        'last_block_string': blockchain.last_block
    }
    return jsonify(response), 200


@app.route('/nodes_register', methods=['POST'])
def register_nodes():
    values = request.get_json()
    nodes = values['nodes']

    if nodes is None:
        return "Error, please supply node info", 400
    for n in nodes:
        blockchain.register_node(n)

    response = {
        'message': "New nodes have been added successfully",
        'total_nodes': list(blockchain.nodes)
    }


@app.route('/block/new', method=['POST'])
def receive_block():
    values = request.get_json()

    new_last_block = values['block']
    old_last_block = blockchain.last_block

    if new_last_block['index'] == old_last_block['index'] + 1:
        if new_last_block['previous_hash'] == blockchain.hash(old_last_block):
            block_string = json.dump(old_last_block, sort_keys=True).encode()
            if blockchain.valid_proof(block_string, new_last_block['proof']):
                print("New Block added!")
                blockchain.add(new_last_block)
                return 'Block Accepted', 200
            else:
                # TODO Proof of work is invalid
        else:
            # TODO Previous has is invalid
    else:
        # TODO Indexes are not consecutive

            # Run the program on port 5000
if __name__ == '__main__':
    app.run(host='localhost', port=5000, debug=True)
