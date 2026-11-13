import os

# safe-eth-py leaves `ethereum_node_url` as None when ETHEREUM_NODE_URL is not
# set, and the CLI commands under test need the node URL as an argument
os.environ.setdefault("ETHEREUM_NODE_URL", "http://localhost:8545")
