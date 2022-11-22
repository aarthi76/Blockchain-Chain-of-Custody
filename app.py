from flask import Flask, redirect, render_template, request
from flask_sqlalchemy import SQLAlchemy
from DB import authenticate_user, insert_record
from Ipfs import ipfs_upload
from web3 import Web3
from Web3.deploy import compile_solidity
import solcx
from solcx import compile_standard
import json
solcx.install_solc('0.6.1')
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///market.db"
db = SQLAlchemy(app)
app.config["IMAGE_UPLOADS"] = "./static/img"


class User(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(length=30), unique=True, nullable=False)
    email = db.Column(db.String(length=50), unique=True, nullable=False)
    password = db.Column(db.String(length=60), nullable=False)

    def __repr__(self) -> str:
        return f"Username {self.username} Email {self.email} password {self.password}"


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        byte_name_arr = ""
        for char in str(request.form["username"]):
            byte_name_arr += str(ord(char))
        print(byte_name_arr)
        print(
            request.form["username"],
            request.form["password"],
            str(request.form["username"]) + str(request.form["password"]),
        )
        data = authenticate_user(
            str(request.form["username"]), str(request.form["password"])
        )
        if len(data) == 0:
            return render_template("login.html", error="Incorret Username or Password")
        return render_template("form.html")
    else:
        return render_template("login.html")



def get_abi_bytecode():
    with open("D:\\Aarthi\\MIT\\7th Sem\\BC\\Blockchain-Chain-of-Custody\\Web3\\Evidences.sol") as file:
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


def add_evidence_block(
    case_id,
    evd_no,
    evd_text1,
    evd_text2,
    evd_img_ipfs_hash,
    date,
    time,
):
    w3 = Web3(Web3.HTTPProvider("HTTP://127.0.0.1:7545"))
    chain_id = 1337
    my_address = "0x2cd75162Beb459d24177C082238F366307507aC3"
    private_key = "c77b1638b0f7ae6a4cbca39bdad9c9b8b74af1034d3c276c19ea2a182c5bb3a5"
    ABI, BYTECODE = get_abi_bytecode()
    EvidenceContract = w3.eth.contract(abi=ABI, bytecode=BYTECODE)
    nonce = w3.eth.getTransactionCount(my_address)
    EvidenceTransaction = EvidenceContract.constructor(
        case_id,
        evd_no,
        evd_img_ipfs_hash,
        evd_text1,
        evd_text2,
        date,
        time,
    ).build_transaction(
        {
            "gasPrice": w3.eth.gas_price,  # Remove the gas price field once it is deployed on the real ethereum network
            "chainId": chain_id,
            "from": my_address,
            "nonce": nonce,
        }
    )
    sign_transaction = w3.eth.account.sign_transaction(
        EvidenceTransaction, private_key=private_key
    )
    transaction_hash = w3.eth.send_raw_transaction(sign_transaction.rawTransaction)
    transaction_receipt = w3.eth.wait_for_transaction_receipt(transaction_hash)
    return ABI, nonce, transaction_receipt.contractAddress


def retrieve_evidence_block(contract_address, ABI):
    print(f"Retrieving the block at {contract_address} address")
    w3 = Web3(Web3.HTTPProvider("HTTP://127.0.0.1:7545"))
    EvidenceBlock = w3.eth.contract(address=str(contract_address), abi=ABI)
    print(f"Evidence Text 1 {EvidenceBlock.functions.getEvdtext1().call()}")
    print(f"Evidence Text 2 {EvidenceBlock.functions.getEvdtext2().call()}")
    print(f"Case ID {EvidenceBlock.functions.getCaseID().call()}")
    print(
        f"Evidence Image IPFS {EvidenceBlock.functions.getEvidenceIpfs().call()}"
    )
    print(f"Evidence Date {EvidenceBlock.functions.getDate().call()}")
    print(f"Evidence Time {EvidenceBlock.functions.getTime().call()}")


@app.route("/skin_consult", methods=["GET", "POST"])
def skin_consult():
    if request.method == "POST":
        print(request.form)
        img = request.files["img"]
        path_save = "./static/img/Evidences/" + img.filename
        img.save(path_save)
        ABI, nonce, contract_address = add_evidence_block(
            str(request.form["case_id"]),
            str(request.form["evd_no"]),
            str(request.form["evd_t1"]),
            str(request.form["evd_t2"]),
            str(ipfs_upload(path_save)),
            str(request.form["date"]),
            str(request.form["time"]),
        )
        print("Adding a new block ...")
        print(f"The new block number is {nonce}")
        print(f"The contract address {contract_address}")
        retrieve_evidence_block(contract_address, ABI)
        return "posted"
    else:
        return render_template("form.html")


if __name__ == "__main__":
    app.run(debug=True)
