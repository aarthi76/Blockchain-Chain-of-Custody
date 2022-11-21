# Importing solidity compiler and web 3 library
from solcx import compile_standard
import json
from web3 import Web3 as w3

# This converts the solidity program code- into Application Binary Interface and Bytecode
def compile_solidity():

    # Open and Read the Solidity File
    with open("D:\\Aarthi\\MIT\\7th Sem\\BC\\Blockchain-Chain-of-Custody\\Web3\\Patient.sol") as file:
        Evidences = file.read()

    # Compile the code by converting into JSON file
    compiled_sol = compile_standard(
        {
            "language": "Solidity",
            "sources": {"Evidences.sol": {"content": Evidences}},
            "settings": {
                "outputSelection": {
                    "*": {"*": ["abi", "metadata", "evm.bytecode", "evm.sourceMap"]}
                }
            },
        },
        solc_version="0.6.1",
    )

    # Open the JSON file
    with open("compiled_code.json", "w") as file:
        json.dump(compiled_sol, file)

    # Read the ABI and bytecode from the JSON file
    bytecode = compiled_sol["contracts"]["Evidences.sol"]["Evidences"]["evm"]["bytecode"][
        "object"
    ]
    abi = compiled_sol["contracts"]["Evidences.sol"]["Evidences"]["abi"]
    return abi, bytecode


def create_evidence_transaction(EvidenceDetails, nonce):

    # Collect the evidence details
    case_id = int(input("Enter the Case ID :"))
    evd_no = int(input("Enter the Evidence No :"))
    evd_t1 = input("Enter Evidence Text 1 :")
    evd_t2 = input("Enter Evidence Text 2 :")

    # Create the transaction with chain_ID, from Address
    transaction = EvidenceDetails.constructor(
        case_id, evd_no, evd_t1, evd_t2
    ).build_transaction(
        {
            "gasPrice": w3.eth.gas_price,  # Remove the gas price field once it is deployed on the real ethereum network
            "chainId": 1337,
            "from": "0xFb7eaeE42D9e83195d17eb2228139Ff24Ee32409",
            "to": "0xf9C3f3a6E596cA6123bA1D95E604f6A2582260cC",
            "nonce": nonce,
        }
    )
    return transaction


def add_patient_record(private_key, transaction):

    # Sign, Send the transaction and return the transaction receipt
    sign_trns = w3.eth.account.sign_transaction(transaction, private_key=private_key)
    tran_hash = w3.eth.send_raw_transaction(sign_trns.rawTransaction)
    trans_receipt = w3.eth.wait_for_transaction_receipt(tran_hash)
    return trans_receipt.contractAddress


def retrieve_evidence_record(block_address):

    # Retrieving the Patient details from their respective block address
    print(f"Retrieving the block at {block_address} address")
    ABI, BYTECODE = compile_solidity()
    Evidence = w3.eth.contract(address=str(block_address), abi=ABI)
    print("Case ID", Evidence.functions.getCaseID().call())
    print("Evidence No.", Evidence.functions.getEvdNo().call())
    print("Evidence Text 1", Evidence.functions.getEvdtext1().call())
    print("Evidence Text 2", Evidence.functions.getEvdtext2().call())
    print("The block address is retrieved successfully !")


def get_transaction_list(w3, address):
    transaction_hash = w3.eth.get_block(98).transactions
    print(transaction_hash, type(transaction_hash), w3.eth.get_block_number())
    print(w3.eth.get_transaction(transaction_hash[0]))
    print(
        "The number of transaction made by the this address is",
        w3.eth.get_transaction_count("0xf9C3f3a6E596cA6123bA1D95E604f6A2582260cC"),
    )


def get_abi_bytecode():
    with open("./compiled_code.json", "r") as j:
        json_data = json.loads(j.read())
    ABI = json_data["contracts"]["Evidences.sol"]["Evidences"]["abi"]
    BYTECODE = json_data["contracts"]["Evidences.sol"]["Evidences"]["evm"]["bytecode"][
        "object"
    ]
    print(ABI, BYTECODE)


if __name__ == "__main__":
    get_abi_bytecode()
    # Change the URL once deployment on real ethereum network
    # w3 = Web3(Web3.HTTPProvider("HTTP://127.0.0.1:7545"))
    # # Change the chainId = 1 for RinkeBy Network, Change the address, Change the Private Key

    # chain_id = 1337
    # my_address = "0x7f21EF7f1185aA02fb597B7F77C1255E27137B63"
    # private_key = "0xf8c8ab49ddd90558a152e48a925c42a4b41a8a2ed7b3f1d5f6446f960938eb0a"

    # # Create an instance of Patient Smart Contract
    # PatientDetails = w3.eth.contract(abi=abi, bytecode=bytecode)
    # # Get the last block in blockchain to link the new block
    # nonce = w3.eth.getTransactionCount(my_address)

    # # Trigger the transaction and add a new block
    # transaction = create_patient_transaction(PatientDetails, nonce)
    # block_address = add_patient_record(private_key, transaction)

    # # Retrieve the data from the respective block addres
    # print("Adding a new block ...")
    # print(f"The new block number is {nonce}")
    # print(f"The block address is {block_address}")
    # print(f"Block Addedd Successfully!")
    # retrieve_patient_record(block_address)
