# Python Bitcoin Solo Miner
import requests
import socket
import threading
import json
import hashlib
import binascii
import logging
import random
import time
import traceback
import context as ctx
import psutil
import sys
from datetime import datetime
from signal import SIGINT, signal
from colorama import Back, Fore, Style
from tabulate import tabulate
from tqdm import tqdm

sock = None
best_difficulty = 0
best_hash = None
# Initialize difficulty outside the loop
difficulty = 0

# Initialize best share difficulty and hash
best_share_difficulty = float('inf')
best_share_hash = None

# Set the difficulty level
difficulty = 16

def show_loading_splash():
    ascii_art = """
⠀⠀⠀⠀⠀⠀⠀⠀⣀⣤⣴⣶⣾⣿⣿⣿⣿⣷⣶⣦⣤⣀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⣠⣴⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣦⣄⠀⠀⠀⠀⠀
⠀⠀⠀⣠⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⣄⠀⠀⠀
⠀⠀⣴⣿⣿⣿⣿⣿⣿⣿⠟⠿⠿⡿⠀⢰⣿⠁⢈⣿⣿⣿⣿⣿⣿⣿⣿⣦⠀⠀
⠀⣼⣿⣿⣿⣿⣿⣿⣿⣿⣤⣄⠀⠀⠀⠈⠉⠀⠸⠿⣿⣿⣿⣿⣿⣿⣿⣿⣧⠀
⢰⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡏⠀⠀⢠⣶⣶⣤⡀⠀⠈⢻⣿⣿⣿⣿⣿⣿⣿⡆
⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠃⠀⠀⠼⣿⣿⡿⠃⠀⠀⢸⣿⣿⣿⣿⣿⣿⣿⣷
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡟⠀⠀⢀⣀⣀⠀⠀⠀⠀⢴⣿⣿⣿⣿⣿⣿⣿⣿⣿
⢿⣿⣿⣿⣿⣿⣿⣿⢿⣿⠁⠀⠀⣼⣿⣿⣿⣦⠀⠀⠈⢻⣿⣿⣿⣿⣿⣿⣿⡿
⠸⣿⣿⣿⣿⣿⣿⣏⠀⠀⠀⠀⠀⠛⠛⠿⠟⠋⠀⠀⠀⣾⣿⣿⣿⣿⣿⣿⣿⠇
⠀⢻⣿⣿⣿⣿⣿⣿⣿⣿⠇⠀⣤⡄⠀⣀⣀⣀⣀⣠⣾⣿⣿⣿⣿⣿⣿⣿⡟⠀
⠀⠀⠻⣿⣿⣿⣿⣿⣿⣿⣄⣰⣿⠁⢀⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠟⠀⠀
⠀⠀⠀⠙⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠋⠀⠀⠀
⠀⠀⠀⠀⠀⠙⠻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠟⠋⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠉⠛⠻⠿⢿⣿⣿⣿⣿⡿⠿⠟⠛⠉⠀⠀⠀⠀⠀⠀⠀⠀
       WE ARE ALL SATOSHI
         B I T C O I N
    """
    # ANSI escape code for orange text
    orange_text = '\033[38;5;202m'
    # ANSI escape code to reset color
    reset_color = '\033[0m'

    print(orange_text + ascii_art + reset_color)

# Show loading Bitcoin
show_loading_splash()

# Show Block Found Splash
def block_found_splash(ascii_art):
    # ANSI escape code for green text
    green_text = '\033[38;5;46m'
    # ANSI escape code to reset color
    reset_color = '\033[0m'
    print(green_text + ascii_art + reset_color)

# Define your ASCII art for "Block Found" here
block_found_ascii_art = """
⠀⠀⠀⠀⠀⠀⠀⠀⣀⣤⣴⣶⣾⣿⣿⣿⣿⣷⣶⣦⣤⣀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⣠⣴⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣦⣄⠀⠀⠀⠀⠀
⠀⠀⠀⣠⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠿⣿⣿⣿⣿⣿⣿⣿⣿⣷⣄⠀⠀⠀
⠀⠀⣴⣿⣿⣿⣿⣿⣿⣿⠟⠿⠿⡿⠀⢰⣿⠁⢈⣿⣿⣿⣿⣿⣿⣿⣿⣦⠀⠀
⠀⣼⣿⣿⣿⣿⣿⣿⣿⣿⣤⣄⠀⠀⠀⠈⠉⠀⠸⠿⣿⣿⣿⣿⣿⣿⣿⣿⣧⠀
⢰⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡏⠀⠀⢠⣶⣶⣤⡀⠀⠈⢻⣿⣿⣿⣿⣿⣿⣿⡆
⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠃⠀⠀⠼⣿⣿⡿⠃⠀⠀⢸⣿⣿⣿⣿⣿⣿⣿⣷
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡟⠀⠀⢀⣀⣀⠀⠀⠀⠀⢴⣿⣿⣿⣿⣿⣿⣿⣿⣿
⢿⣿⣿⣿⣿⣿⣿⣿⢿⣿⠁⠀⠀⣼⣿⣿⣿⣦⠀⠀⠈⢻⣿⣿⣿⣿⣿⣿⣿⡿
⠸⣿⣿⣿⣿⣿⣿⣏⠀⠀⠀⠀⠀⠛⠛⠿⠟⠋⠀⠀⠀⣾⣿⣿⣿⣿⣿⣿⣿⠇
⠀⢻⣿⣿⣿⣿⣿⣿⣿⣿⠇⠀⣤⡄⠀⣀⣀⣀⣀⣠⣾⣿⣿⣿⣿⣿⣿⣿⡟⠀
⠀⠀⠻⣿⣿⣿⣿⣿⣿⣿⣄⣰⣿⠁⢀⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠟⠀⠀
⠀⠀⠀⠙⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠋⠀⠀⠀
⠀⠀⠀⠀⠀⠙⠻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠟⠋⠀⠀⠀⠀⠀
      B L O C K  F O U N D
          CHECK WALLET
"""


def timer():
    return datetime.now().time()

## Mining Address **Change Me**

address = sys.argv[1]
print(Back.BLUE, Fore.WHITE, 'SOLO ADDRESS:', Fore.GREEN, str(address), Style.RESET_ALL)

def handler(signal_received, frame):
    ctx.fShutdown = True
    print(Fore.MAGENTA, '[', timer(), ']', Fore.YELLOW, 'Force Close, Please Wait..')


# Define the logger with the desired format
logging.basicConfig(level=logging.INFO, filename="miner.log", format='%(asctime)s %(message)s')
logger = logging.getLogger("miner_logger")

# Update the logg function to use the logger
def logg(msg):
    logger.info(msg)


 ## This code is used to get the current block height of the Bitcoin network.
 ## The request is made to the blockchain.info API and the response is parsed to get the height field.
 ## The height is then converted to an integer and returned.
def get_current_block_height():
    r = requests.get('https://blockchain.info/latestblock')
    return int(r.json()['height'])


## This code is used to check if the mining context (ctx) is in shutdown mode.
## If the ctx.fShutdown flag is set to True, the ctx.listfThreadRunning list is updated with the current thread's index (n) and set to False.
## The thread's exit flag is also set to True to signal the thread to exit.
def check_for_shutdown(t):
    n = t.n
    if ctx.fShutdown:
        if n != -1:
            ctx.listfThreadRunning[n] = False
            t.exit = True

## This code is defining a custom thread class called ExitedThread which is a subclass of threading.Thread.
## The class has two attributes, exit and arg, and four methods,
## __init__, run, thread_handler and thread_handler2. The __init__ method is used to initialize the class and set the exit,
## arg and n attributes. The run method is used to call the thread_handler method with the arg and n attributes as parameters.
## The thread_handler method is used to check for shutdown and if the exit flag is set to True, the thread exits.
## The thread_handler2 method is used to be implemented by subclasses and is not implemented in this class.
## The check_self_shutdown and try_exit methods are used to check for shutdown and t
class ExitedThread(threading.Thread):
    def __init__(self, arg, n):
        super(ExitedThread, self).__init__()
        self.exit = False
        self.arg = arg
        self.n = n

    def run(self):
        self.thread_handler(self.arg, self.n)

    def thread_handler(self, arg, n):
        while True:
            check_for_shutdown(self)
            if self.exit:
                break
            ctx.listfThreadRunning[n] = True
            try:
                self.thread_handler2(arg)
            except Exception as e:
                logg("ThreadHandler()")
                print(Fore.MAGENTA, '[', timer(), ']', Fore.WHITE, 'ThreadHandler()')
                logg(str(e))
                print(Fore.GREEN, str(e))
            ctx.listfThreadRunning[n] = False
            time.sleep(2)

    def thread_handler2(self, arg):
        raise NotImplementedError("must implement this function")

    def check_self_shutdown(self):
        check_for_shutdown(self)

    def try_exit(self):
        self.exit = True
        ctx.listfThreadRunning[self.n] = False

 ## This code is defining a function called bitcoin_miner which is used to start and restart the bitcoin miner.
 ## If the miner is restarted, it will log and print that it has been restarted and sleep for 5 seconds.
 ## It will then log and print that the miner has started. It then runs a loop which checks if the miner thread is still alive and if the subscribe thread is running.
 ## If either of these conditions are not true, the loop will break. Otherwise,
 ## it will set the miner thread to be running, call the mining method on the miner thread, and set the miner thread to be not running.
 ## If an exception occurs, it is logged and the traceback is printed, and the loop breaks.
# Initialize best difficulty outside the loop
best_difficulty = 0  # Add this line to initialize best_difficulty
target = None
def bitcoin_miner(t, restarted=False):
    global best_share_difficulty, best_share_hash
    global target
    start_time = time.time()  # Start time for performance metrics
    total_hashes = 0  # Initialize total_hashes
    if restarted:
        logg('\n[*] Bitcoin Miner restarted')
        print(Fore.MAGENTA, '[', timer(), ']', Fore.YELLOW, 'Solo Miner Active')
        print(Fore.MAGENTA, '[', timer(), ']', Fore.BLUE, '[*] Bitcoin Miner Restarted')

    # Initialize share_difficulty outside the loop
    share_difficulty = 0

    # Initialize difficulty outside the loop
    difficulty = 0

    # Initialize best difficulty
    best_difficulty = 0  # Add this line to initialize best_difficulty

    ## This code is used to create a target (difficulty) and extranonce2 value for a mining context (ctx).
    ## The target is created by taking the last 3 bits of the nbits field from the context and appending '00' to the end of it ctx.nbits[2:] times.
    ## The extranonce2 value is a random number between 0 and 2^32-1, which is converted to hex and padded with zeros to match the length of the ctx.extranonce2_size.
    target = (ctx.nbits[2:] + '00' * (int(ctx.nbits[:2], 16) - 3)).zfill(64)
    extranonce2 = hex(random.randint(0, 2**32 - 1))[2:].zfill(2 * ctx.extranonce2_size)
    print(Fore.YELLOW, '[*] Target:', Fore.GREEN, '[', target, ']')
    print(Fore.YELLOW, '[*] Extranonce2:', Fore.GREEN, '[', extranonce2, ']')

    ## This code is used to create a coinbase hash from the mining context (ctx) and the extranonce2 value generated in the previous code.
    ## The coinbase is created by combining the ctx.coinb1, ctx.extranonce1, extranonce2 and ctx.coinb2 fields.
    ## The coinbase hash is then generated by taking the SHA-256 hash of the coinbase t
    coinbase = ctx.coinb1 + ctx.extranonce1 + extranonce2 + ctx.coinb2
    coinbase_hash_bin = hashlib.sha256(hashlib.sha256(binascii.unhexlify(coinbase)).digest()).digest()
    print(Fore.YELLOW, '[*] Coinbase Hash:', Fore.GREEN, '[', coinbase, ']')

    ## This code is used to generate a Merkle root from the mining context (ctx) and the coinbase hash generated in the previous code.
    ## The Merkle root is generated by looping through the ctx.merkle_branch list and combining the merkle_root and the current branch element in each iteration.
    ## The combined values are then hashed twice with SHA-256 to generate the new merkle_root.
    merkle_root = coinbase_hash_bin
    for h in ctx.merkle_branch:
        merkle_root = hashlib.sha256(hashlib.sha256(merkle_root + binascii.unhexlify(h)).digest()).digest()

    ## This code is used to convert the binary Merkle root generated in the previous code to a hexadecimal string.
    ## The binary merkle_root is converted to a hexadecimal string using the binascii.hexlify() function,
    ## and then the result is decoded to a string using the decode() method.
    merkle_root = binascii.hexlify(merkle_root).decode()
    print(Fore.YELLOW, '[*] Merkle Root:', Fore.YELLOW, '[', merkle_root, ']')

    ## This code is used to format the Merkle root generated in the previous code. The string is split into two-character substrings,
    ## and the result is reversed using the [::-1] slice notation.
    ## The work_on variable is used to get the current block height,
    ## and the ctx.nHeightDiff dictionary is updated with the new block height and a value of 0.
    merkle_root = ''.join([merkle_root[i] + merkle_root[i + 1] for i in range(0, len(merkle_root), 2)][::-1])
    work_on = get_current_block_height()
    ctx.nHeightDiff[work_on + 1] = 0

    ## This code is used to calculate the difficulty for the current block.
    ## The difficulty is calculated by taking the hex string "00000000FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF"
    ## and dividing it by the target value which is also in hex format. The result is the difficulty for the current block.
    ## Calculate the difficulty as you did in your original code
    _diff = int("00000000FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF", 16)

    # Print and log the difficulty value
    print(Fore.YELLOW, '[*] Diff:', Fore.YELLOW, '[', int(_diff), ']')
    logg('[*] Working to solve block at block height {}'.format(work_on + 1))
    print(Fore.MAGENTA, '[', timer(), ']', Fore.YELLOW, '[*] Working to solve block at ', Fore.GREEN, 'height {}'.format(work_on + 1))
    

    # Improved difficulty calculation
    def calculate_difficulty(target, hash_hex):
        hash_int = int(hash_hex, 16)
        target_int = int(target, 16)
        return target_int / max(hash_int, 1)  # Avoid division by zero

    # Enhanced metrics logging
    def log_metrics(start_time, nonce, hashes_computed, best_difficulty, best_hash):
        elapsed_time = time.time() - start_time
        hash_rate = hashes_computed / max(elapsed_time, 1)  # Avoid division by zero
        print(f"Nonce: {nonce}, Hash Rate: {hash_rate:.2f} hashes/sec")
        print(f"Hash Rate: {hash_rate:.2f} hashes/sec")
        print(f"Best Difficulty: {best_difficulty:.2f}")
        print(f"Best Hash: {best_hash}")

        # Initialize a variable to keep track of the previous progress percentage
        prev_progress_percentage = None

        # Initialize total_hashes before entering the mining loop
        total_hashes = 0

        # Initialize hash_rate
        hash_rate = 0.0

    progress = int(sys.argv[2])
    bits = 2 ** int(sys.argv[3])

    def make_packed_nonces(nonce):
        return hex(nonce)[2:].zfill(8)
    
    nonces = range(progress, bits)
    def make_block_headers(nonce):
        global ctx
        return ctx.version + ctx.prevhash + merkle_root + ctx.ntime + ctx.nbits + nonce + '000000800000000000000000000000000000000000000000000000000000000000000000000000000000000080020000'
    
    def make_hash(blockheader):
        return int(hashlib.sha256(hashlib.sha256(binascii.unhexlify(blockheader)).digest()).hexdigest(), 16)
    
    def check_hash(hash):
        global target
        return not hash < int(target, 16)

    while True:
        t.check_self_shutdown()
        if t.exit:
            break

        if ctx.prevhash != ctx.updatedPrevHash:
            logg('[*] NEW BLOCK {} DETECTED ON NETWORK'.format(ctx.prevhash))
            print(Fore.YELLOW, '[', timer(), ']', Fore.MAGENTA, '[*] New block {} detected on', Fore.BLUE,
                  ' network '.format(ctx.prevhash))
            logg('[*] Best difficulty previous block {} was {}'.format(work_on + 1, ctx.nHeightDiff[work_on + 1]))
            print(Fore.MAGENTA, '[', timer(), ']', Fore.GREEN, '[*] Best Diff Trying Block', Fore.YELLOW, ' {} ',
                  Fore.BLUE, 'was {}'.format(work_on + 1, ctx.nHeightDiff[work_on + 1]))
            ctx.updatedPrevHash = ctx.prevhash
            bitcoin_miner(t, restarted=True)
            print(Back.YELLOW, Fore.MAGENTA, '[', timer(), ']', Fore.BLUE, 'NEW BLOCK DETECTED - RESTARTING MINER...',
                  Style.RESET_ALL)
            continue

            ## This code is used to generate a blockheader from the mining context (ctx), the Merkle root,
            ## a random nonce, and the hash of the blockheader. The blockheader is created by combining the
            ## ctx.version, ctx.prevhash, merkle_root, ctx.ntime, ctx.nbits, nonce and,
            ## '000000800000000000000000000000000000000000000000000000000000000000000000000000000000000080020000'.
            ## The hash of the blockheader is then generated by taking the SHA-256 hash of the blockheader twice and getting the binary digest.
            ## The result is then converted to a hexadecimal string using the binascii.hexlify() function.
        
        
        packed_nonces = map(make_packed_nonces, nonces)

        blockheaders = map(make_block_headers, packed_nonces)
        hash = map(make_hash, blockheaders)

        ctx.total_hashes_computed += bits  # Increment total hash count
        #print(Fore.YELLOW + '[*] Nonce: ' + Fore.GREEN + str(nonce), end="\r")

        # Define the target difficulty as a hexadecimal string. 
        # The target difficulty represents the level of complexity required for a block to be considered valid.
        # It consists of leading zeros followed by a sequence of 'F' characters.
        # In hexadecimal format, it is represented as '0000000000000000FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF'.

        # Calculate the hash value of the current block as an integer.
        # The 'hash' variable contains the hash value of the block in hexadecimal format.
        # Converting it to an integer is useful for comparing it to the target difficulty.

        # Check if the current hash meets or exceeds the target difficulty
        # Check if this is the best difficulty so far
        if difficulty > best_difficulty:
            best_difficulty = difficulty
            best_hash = hash
            logg(f'[BEST HASH UPDATE] New best hash: {best_hash} with difficulty: {best_difficulty}')
            print(f'[BEST HASH UPDATE] New best hash: {best_hash} with difficulty: {best_difficulty}')

        # Update the difficulty for the current block in the context
        if ctx.nHeightDiff[work_on + 1] < difficulty:
            ctx.nHeightDiff[work_on + 1] = difficulty

        # Increment the total number of hashes computed
        total_hashes += bits
        
        # Calculate elapsed time
        elapsed_time = time.time() - start_time
        
        # Calculate hash rate
        hash_rate = total_hashes / elapsed_time
        
        # Display total hashes and hash rate on the same line with carriage return
        print(f"\rTotal Hashes: {total_hashes} | Hash Rate: {hash_rate:.2f} H/s", end='')

            ## This code is used to check if the hash of the blockheader is less than the target value.
            ## If the hash is less than the target, it means the block has been successfully solved and the ctx.solved flag is set to True.
        
        found_hash_iter = map(check_hash, hash)
        found_hash = not all(found_hash_iter)
        if found_hash:
            logg('[*] Share found for block {}.'.format(work_on + 1))
            hash = set(found_hash_iter)
            nonce = hash.index(True) + progress
            print(Fore.MAGENTA, '[', timer(), ']', Fore.YELLOW, '[*] Share found for block {}.'.format(work_on + 1))
            print(Fore.MAGENTA, '[', timer(), ']', Fore.YELLOW, 'Share:', hash.format(work_on + 1))
            logg('[*] Block hash: {}'.format(hash))
            print(Fore.YELLOW)
            print(Fore.MAGENTA, '[', timer(), ']', Fore.YELLOW, '[*] Block hash: {}'.format(hash))
            print(Fore.BLUE, '--------------~~( ', Fore.GREEN, 'BLOCK SOLVED CHECK WALLET!', Fore.ORANGE, ' )~~--------------')

            # Print nonce value when a new share is found
            logg('[*] Nonce Value: {}'.format(nonce))
            print(Fore.YELLOW, '[*] Nonce Value: {}'.format(nonce))

            payload = bytes('{"params": ["' + address + '", "' + ctx.job_id + '", "' + ctx.extranonce2 + '", "' + ctx.ntime + '", "' + nonce + '"], "id": 1, "method": "mining.submit"}\n', 'utf-8')
            logg('[*] Payload: {}'.format(payload))
            print(Fore.MAGENTA, '[', timer(), ']', Fore.BLUE, '[*] Payload:', Fore.GREEN, ' {}'.format(payload))
            sock.sendall(payload)
            ret = sock.recv(1024)
            logg('[*] Pool response: {}'.format(ret))
            print(Fore.MAGENTA, '[', timer(), ']', Fore.GREEN, '[*] Pool Response:', Fore.CYAN, ' {}'.format(ret))
            print(payload)
            block_found_splash(block_found_ascii_art)
            return True

        if difficulty >= 16:

            hash = set(found_hash_iter)
            nonce = hash.index(True) + progress
            # Construct JSON-RPC request for share submission
            share_payload = {
                "params": [address, ctx.job_id, ctx.extranonce2, ctx.ntime, nonce],
                "id": 1,
                "method": "mining.submit"
            }
            
            # Send the share payload to the pool's mining.submit endpoint
            share_payload = json.dumps(share_payload) + '\n'
            sock.sendall(share_payload.encode())
            
            # Receive and handle the pool's response
            response = sock.recv(1024).decode()
            
            # Log and print the response for monitoring purposes
            logg('[*] Pool response for share submission: {}'.format(response))
            print(Fore.MAGENTA, '[', timer(), ']', Fore.GREEN, '[*] Pool Response for share submission:', Fore.CYAN, ' {}'.format(response))

            # Calculate the difficulty for the current share
        progress += bits
        nonces = range(progress, progress + bits)
        # Check if this share is better than the best share
        # Update the difficulty for the current block in the context

         ## This code is used to set up a connection to the ckpool server and send a handle subscribe message.
         ## The response is parsed to get the ctx.sub_details, ctx.extranonce1 and ctx.extranonce2_size fields.
         ## Then an authorize message is sent with the address and password, and the response is read until the mining.notify message is received.

def block_listener(t) :
    # init a connection to ckpool
    sock = socket.socket(socket.AF_INET , socket.SOCK_STREAM)
    sock.connect(('solo.ckpool.org' , 3333))
    # send a handle subscribe message
    sock.sendall(b'{"id": 1, "method": "mining.subscribe", "params": []}\n')
    lines = sock.recv(1024).decode().split('\n')
    response = json.loads(lines[0])
    ctx.sub_details , ctx.extranonce1 , ctx.extranonce2_size = response['result']
    # send and handle authorize message
    sock.sendall(b'{"params": ["' + address.encode() + b'", "x"], "id": 2, "method": "mining.authorize"}\n')
    response = b''
    while response.count(b'\n') < 4 and not (b'mining.notify' in response) : response += sock.recv(1024)
    print(response)

    ## This code is used to parse the response from the ckpool server and get the necessary fields for the mining context (ctx).
    ## The response is split into individual lines and only lines that contain the 'mining.notify' string are parsed.
    ## The parsed results are then stored in the,
    ## ctx.job_id, ctx.prevhash, ctx.coinb1, ctx.coinb2, ctx.merkle_branch, ctx.version, ctx.nbits, ctx.ntime and ctx.clean_jobs fields.

    responses = [json.loads(res) for res in response.decode().split('\n') if
                 len(res.strip()) > 0 and 'mining.notify' in res]
    ctx.job_id , ctx.prevhash , ctx.coinb1 , ctx.coinb2 , ctx.merkle_branch , ctx.version , ctx.nbits , ctx.ntime , ctx.clean_jobs = \
        responses[0]['params']

    ## Do this one time, will be overwriten by mining loop when new block is detected

    ctx.updatedPrevHash = ctx.prevhash

    while True :
        t.check_self_shutdown()
        if t.exit :
            break

        ## This code is used to check if the previous hash in the response from the ckpool server is different from the previous hash,
        ## in the mining context (ctx). If the hashes are different, the response is parsed to get the necessary fields
        ## for the mining context and the fields are updated with the new values.

        response = b''
        while response.count(b'\n') < 4 and not (b'mining.notify' in response) : response += sock.recv(1024)
        responses = [json.loads(res) for res in response.decode().split('\n') if
                     len(res.strip()) > 0 and 'mining.notify' in res]

        if responses[0]['params'][1] != ctx.prevhash :

            ## New block detected on network
            ## update context job data

            # Update mining context with new work
            ctx.job_id, ctx.prevhash, ctx.coinb1, ctx.coinb2, ctx.merkle_branch, ctx.version, ctx.nbits, ctx.ntime, ctx.clean_jobs = responses[0]['params']

            # Call the splash screen function here
            show_loading_splash()

            # Log the new mining context
            logger.info(f"New Work Received from Pool:\n"
                         f"Job ID: {ctx.job_id}\n"
                         f"Previous Block Hash: {ctx.prevhash}\n"
                         f"Coinbase 1: {ctx.coinb1}\n"
                         f"Coinbase 2: {ctx.coinb2}\n"
                         f"Merkle Branch: {ctx.merkle_branch}\n"
                         f"Version: {ctx.version}\n"
                         f"nBits: {ctx.nbits}\n"
                         f"nTime: {ctx.ntime}\n"
                         f"Clean Jobs: {ctx.clean_jobs}")

    ## This code is defining a custom thread class called CoinMinerThread which is a subclass of ExitedThread.
    ## The class has two methods, __init__ and thread_handler2. The __init__ method is used to initialize the class and set the n attribute to 0.
    ## The thread_handler2 method calls the thread_bitcoin_miner method with the arg parameter. The thread_bitcoin_miner method is used to check for shutdown,
    ## and then calls the bitcoin_miner function with the current thread object as the parameter. The result of the bitcoin_miner function is logged to the console.

class CoinMinerThread(ExitedThread) :
    def __init__(self , arg = None) :
        super(CoinMinerThread , self).__init__(arg , n = 0)

    def thread_handler2(self , arg) :
        self.thread_bitcoin_miner(arg)

    def thread_bitcoin_miner(self , arg) :
        ctx.listfThreadRunning[self.n] = True
        check_for_shutdown(self)
        try :
            ret = bitcoin_miner(self)
            logg(Fore.MAGENTA , "[" , timer() , "] [*] Miner returned %s\n\n" % "true" if ret else "false")
            print(Fore.LIGHTCYAN_EX , "[*] Miner returned %s\n\n" % "true" if ret else "false")
        except Exception as e :
            logg("[*] Miner()")
            print(Back.WHITE , Fore.MAGENTA , "[" , timer() , "]" , Fore.BLUE , "[*] Miner()")
            logg(e)
            traceback.print_exc()
        ctx.listfThreadRunning[self.n] = False

    pass

    ## This code is defining a new class called NewSubscribeThread which is a subclass of ExitedThread. It has two methods,
    ## __init__ and thread_handler2. The __init__ method sets up the thread with the specified argument and sets the number of threads to 1.
    ## The thread_handler2 method calls the thread_new_block method with the specified argument.
    ## The thread_new_block method sets the thread to be running, checks for shutdown, and then calls the block_listener function. If an exception occurs,
    ## it is logged and the traceback is printed. Finally, the thread is set to be not running.

class NewSubscribeThread(ExitedThread) :
    def __init__(self , arg = None) :
        super(NewSubscribeThread , self).__init__(arg , n = 1)

    def thread_handler2(self , arg) :
        self.thread_new_block(arg)

    def thread_new_block(self , arg) :
        ctx.listfThreadRunning[self.n] = True
        check_for_shutdown(self)
        try :
            ret = block_listener(self)
        except Exception as e :
            logg("[*] Subscribe thread()")
            print(Fore.MAGENTA , "[" , timer() , "]" , Fore.YELLOW , "[*] Subscribe thread()")
            logg(e)
            traceback.print_exc()
        ctx.listfThreadRunning[self.n] = False

    pass

## This code is defining a function called StartMining which creates a thread for subscribing and one for mining.
## It first creates a new thread called subscribe_t which uses the NewSubscribeThread class.
## It then starts the thread and logs that the subscribe thread has been started.
## It then sleeps for 4 seconds and creates a new thread called miner_t which uses the CoinMinerThread class.
## It then starts the thread and logs that the Bitcoin solo miner has been started.

def StartMining() :
    subscribe_t = NewSubscribeThread(None)
    subscribe_t.start()
    logg("[*] Subscribe thread started.")
    print(Fore.MAGENTA , "[" , timer() , "]" , Fore.GREEN , "[*] Subscribe thread started.")

    time.sleep(1)

    miner_t = CoinMinerThread(None)
    miner_t.start()
    logg("[*]£££ Bitcoin Solo Miner Started £££")
    print(Fore.MAGENTA , "[" , timer() , '(', Fore.GREEN  , 'SOLO MINER STARTED' , Fore.BLUE , ' )~~--------------')
    print(Fore.BLUE , '--------------~~( ' , Fore.YELLOW , 'IN SATOSHI WE TRUST' , Fore.BLUE , ' )~~--------------')
    print(Fore.BLUE , '--------------~~( ' , Fore.GREEN  , 'DO NOT TRUST VERIFY' , Fore.BLUE , ' )~~--------------')


if __name__ == '__main__':
    # Initialize performance metrics in context
    ctx.total_hashes_computed = 0
    ctx.mining_time_per_block = []

    signal(SIGINT, handler)
    StartMining()
