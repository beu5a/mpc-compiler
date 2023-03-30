
import time
from multiprocessing import Process, Queue

import pytest

from expression import Scalar, Secret
from protocol import ProtocolSpec
from server import run
import time
import statistics
import matplotlib.pyplot as plt
import numpy as np
import sys

import seaborn as sns
from tqdm import tqdm

import os
import numpy as np
import time
from sympy import symbols, Secret, Scalar
from sympy.utilities.iterables import multiset_permutations
from sympy.printing.str import StrPrinter
from sympy.printing.latex import LatexPrinter

from smc_party import SMCParty


def smc_client(client_id, prot, value_dict, queue):
    cli = SMCParty(
        client_id,
        "localhost",
        5000,
        protocol_spec=prot,
        value_dict=value_dict
    )
    res = cli.run()
    queue.put(res)
    print(f"{client_id} has finished!")


def smc_server(args):
    run("localhost", 5000, args)


def run_processes(server_args, *client_args):
    queue = Queue()

    server = Process(target=smc_server, args=(server_args,))
    clients = [Process(target=smc_client, args=(*args, queue)) for args in client_args]

    server.start()
    time.sleep(3)
    for client in clients:
        client.start()

    results = list()
    for client in clients:
        client.join()

    for client in clients:
        results.append(queue.get())

    server.terminate()
    server.join()

    # To "ensure" the workers are dead.
    time.sleep(2)

    print("Server stopped.")

    return results


def suite(parties, expr):
    participants = list(parties.keys())

    prot = ProtocolSpec(expr=expr, participant_ids=participants)
    clients = [(name, prot, value_dict) for name, value_dict in parties.items()]

    results = run_processes(participants, *clients)
    return results



def print_metrics(metrics):
    # Check if file exists
    if not os.path.exists('metrics.txt'):
        with open('metrics.txt', 'w') as f:
            f.write('\\begin{table}[ht]\n')
            f.write('\\centering\n')
            f.write('\\begin{tabular}{c c c c}\n')
            f.write('\\hline\n')
            f.write('Num Scalar Additions & Sent (bytes) & Received (bytes) & Time (s) \\\\ \n')
            f.write('\\hline\n')
            f.write('\\end{tabular}\n')
            f.write('\\caption{Performance metrics for nkadd}\n')
            f.write('\\label{tab:nkadd_metrics}\n')
            f.write('\\end{table}\n')

    # Append metrics to file
    with open('metrics.txt', 'a') as f:
        f.write('\\begin{table}[ht]\n')
        f.write('\\centering\n')
        f.write('\\begin{tabular}{c c c c}\n')
        f.write('\\hline\n')
        f.write('Num Scalar Additions & Sent (bytes) & Received (bytes) & Time (s) \\\\ \n')
        f.write('\\hline\n')
        for d in metrics['sent']:
            index = d['index']
            f.write(f"{metrics['num'][index]} & {d['mean']:.4f} $\\pm$ {d['std']:.4f} & ")
            f.write(f"{metrics['recv'][index]['mean']:.4f} $\\pm$ {metrics['recv'][index]['std']:.4f} & ")
            f.write(f"{metrics['time'][index]['mean']:.4f} $\\pm$ {metrics['time'][index]['std']:.4f} \\\\ \n")
        f.write('\\hline\n')
        f.write('\\end{tabular}\n')
        f.write('\\end{table}\n')





def nparties():

    alice_secret = Secret()
    bob_secret = Secret()
    charlie_secret = Secret()

    parties = {
        "Alice": {alice_secret: 3},
        "Bob": {bob_secret: 14},
        "Charlie": {charlie_secret: 2}
    }

    num_runs = 10
    num_clients_list = [1, 5, 10, 20, 50, 75, 100]

    metrics = {
        'sent': [],
        'recv': [],
        'ttp': [],
        'time': []
    }

    for num_clients in num_clients_list:
        benchmark_parties = dict()
        for i in range(num_clients):
            benchmark_parties[f"Party {i}"] = {Secret(): i}

        parties.update(benchmark_parties)

        expr = (alice_secret + bob_secret + charlie_secret)
        run_times = []
        sent_bytes = []
        recv_bytes = []
        ttp_bytes = []
        for i in range(num_runs):
            start_time = time.time()
            x = suite(parties, expr)
            end_time = time.time()
            elapsed_time = end_time - start_time
            run_times.append(elapsed_time)

            sent_bytes_run = 0
            recv_bytes_run = 0
            ttp_bytes_run = 0
            for result in x:
                sent_bytes_run += result[1]['sent']
                recv_bytes_run += result[1]['recv']
                ttp_bytes_run += result[1]['ttp']
            sent_bytes.append(sent_bytes_run / len(x))
            recv_bytes.append(recv_bytes_run / len(x))
            ttp_bytes.append(ttp_bytes_run / len(x))

        metrics['sent'].append({'num': num_clients, 'mean': np.mean(sent_bytes), 'std': np.std(sent_bytes)})
        metrics['recv'].append({'num': num_clients, 'mean': np.mean(recv_bytes), 'std': np.std(recv_bytes)})
        metrics['ttp'].append({'num': num_clients, 'mean': np.mean(ttp_bytes), 'std': np.std(ttp_bytes)})
        metrics['time'].append({'num': num_clients, 'mean': np.mean(run_times), 'std': np.std(run_times)})

    # Print the results
    for metric, data in metrics.items():
        print(metric)
        for d in data:
            print(f"Num clients: {d['num']}, Mean: {d['mean']:.4f}, Std: {d['std']:.4f}")
        print()



def nadd():
    alice_secret = Secret()
    bob_secret = Secret()
    charlie_secret = Secret()

    parties = {
        "Alice": {alice_secret: 3},
        "Bob": {bob_secret: 14},
        "Charlie": {charlie_secret: 2}
    }

    num_runs = 10
    num_add_list = [10, 100, 200, 500]

    metrics = {
        'sent': [],
        'recv': [],
        'ttp': [],
        'time': []
    }

    for num_additions in num_add_list:

        expr = alice_secret
        for i in range(num_additions - 1):
            expr *= bob_secret
        expr *= charlie_secret

        run_times = []
        sent_bytes = []
        recv_bytes = []
        ttp_bytes = []
        for i in range(num_runs):
            start_time = time.time()
            x = suite(parties, expr)
            end_time = time.time()
            elapsed_time = end_time - start_time
            run_times.append(elapsed_time)

            sent_bytes_run = 0
            recv_bytes_run = 0
            ttp_bytes_run = 0
            for result in x:
                sent_bytes_run += result[1]['sent']
                recv_bytes_run += result[1]['recv']
                ttp_bytes_run += result[1]['ttp']
            sent_bytes.append(sent_bytes_run / len(x))
            recv_bytes.append(recv_bytes_run / len(x))
            ttp_bytes.append(ttp_bytes_run / len(x))

        metrics['sent'].append({'num': num_additions, 'mean': np.mean(sent_bytes), 'std': np.std(sent_bytes)})
        metrics['recv'].append({'num': num_additions, 'mean': np.mean(recv_bytes), 'std': np.std(recv_bytes)})
        metrics['ttp'].append({'num': num_additions, 'mean': np.mean(ttp_bytes), 'std': np.std(ttp_bytes)})
        metrics['time'].append({'num': num_additions, 'mean': np.mean(run_times), 'std': np.std(run_times)})

    # Print the results
    for metric, data in metrics.items():
        print(metric)
        for d in data:
            print(f"Num Additions: {d['num']}, Mean: {d['mean']:.4f}, Std: {d['std']:.4f}")
        print()


def nmul():

    alice_secret = Secret()
    bob_secret = Secret()
    charlie_secret = Secret()

    parties = {
        "Alice": {alice_secret: 3},
        "Bob": {bob_secret: 14},
        "Charlie": {charlie_secret: 2}
    }

    num_runs = 10
    num_add_list = [10, 100, 200, 500]

    metrics = {
        'sent': [],
        'recv': [],
        'ttp': [],
        'time': []
    }

    for num_multip in num_add_list:

        expr = alice_secret
        for i in range(num_multip - 1):
            expr += bob_secret
        expr += charlie_secret

        run_times = []
        sent_bytes = []
        recv_bytes = []
        ttp_bytes = []
        for i in range(num_runs):
            start_time = time.time()
            x = suite(parties, expr)
            end_time = time.time()
            elapsed_time = end_time - start_time
            run_times.append(elapsed_time)

            sent_bytes_run = 0
            recv_bytes_run = 0
            ttp_bytes_run = 0
            for result in x:
                sent_bytes_run += result[1]['sent']
                recv_bytes_run += result[1]['recv']
                ttp_bytes_run += result[1]['ttp']
            sent_bytes.append(sent_bytes_run / len(x))
            recv_bytes.append(recv_bytes_run / len(x))
            ttp_bytes.append(ttp_bytes_run / len(x))

        metrics['sent'].append({'num': num_multip, 'mean': np.mean(sent_bytes), 'std': np.std(sent_bytes)})
        metrics['recv'].append({'num': num_multip, 'mean': np.mean(recv_bytes), 'std': np.std(recv_bytes)})
        metrics['ttp'].append({'num': num_multip, 'mean': np.mean(ttp_bytes), 'std': np.std(ttp_bytes)})
        metrics['time'].append({'num': num_multip, 'mean': np.mean(run_times), 'std': np.std(run_times)})

    # Print the results
    for metric, data in metrics.items():
        print(metric)
        for d in data:
            print(f"Num Multiplications: {d['num']}, Mean: {d['mean']:.4f}, Std: {d['std']:.4f}")
        print()




def nkadd():
    alice_secret = Secret()
    bob_secret = Secret()
    charlie_secret = Secret()
    k = Scalar(1)

    parties = {
        "Alice": {alice_secret: 3},
        "Bob": {bob_secret: 14},
        "Charlie": {charlie_secret: 2}
    }

    num_runs = 10
    num_add_list = [10, 100, 200, 500]

    metrics = {
        'sent': [],
        'recv': [],
        'ttp': [],
        'time': []
    }

    for num_kmul in num_add_list:

        expr = alice_secret
        for i in range(num_kmul - 1):
            expr += k
        expr += charlie_secret

        run_times = []
        sent_bytes = []
        recv_bytes = []
        ttp_bytes = []
        for i in range(num_runs):
            start_time = time.time()
            x = suite(parties, expr)
            end_time = time.time()
            elapsed_time = end_time - start_time
            run_times.append(elapsed_time)

            sent_bytes_run = 0
            recv_bytes_run = 0
            ttp_bytes_run = 0
            for result in x:
                sent_bytes_run += result[1]['sent']
                recv_bytes_run += result[1]['recv']
                ttp_bytes_run += result[1]['ttp']
            sent_bytes.append(sent_bytes_run / len(x))
            recv_bytes.append(recv_bytes_run / len(x))
            ttp_bytes.append(ttp_bytes_run / len(x))

        metrics['sent'].append({'num': num_kmul, 'mean': np.mean(sent_bytes), 'std': np.std(sent_bytes)})
        metrics['recv'].append({'num': num_kmul, 'mean': np.mean(recv_bytes), 'std': np.std(recv_bytes)})
        metrics['ttp'].append({'num': num_kmul, 'mean': np.mean(ttp_bytes), 'std': np.std(ttp_bytes)})
        metrics['time'].append({'num': num_kmul, 'mean': np.mean(run_times), 'std': np.std(run_times)})

    # Print the results
    for metric, data in metrics.items():
        print(metric)
        for d in data:
            print(f"Num Scalar Additions: {d['num']}, Mean: {d['mean']:.4f}, Std: {d['std']:.4f}")
        print()


def nkmul():
    alice_secret = Secret()
    bob_secret = Secret()
    charlie_secret = Secret()
    k = Scalar(2)

    parties = {
        "Alice": {alice_secret: 3},
        "Bob": {bob_secret: 14},
        "Charlie": {charlie_secret: 2}
    }

    num_runs = 10
    num_add_list = [10, 100, 200, 500]

    metrics = {
        'sent': [],
        'recv': [],
        'ttp': [],
        'time': []
    }

    for num_kmul in num_add_list:

        expr = alice_secret
        for i in range(num_kmul - 1):
            expr *= k
        expr *= charlie_secret

        run_times = []
        sent_bytes = []
        recv_bytes = []
        ttp_bytes = []
        for i in range(num_runs):
            start_time = time.time()
            x = suite(parties, expr)
            end_time = time.time()
            elapsed_time = end_time - start_time
            run_times.append(elapsed_time)

            sent_bytes_run = 0
            recv_bytes_run = 0
            ttp_bytes_run = 0
            for result in x:
                sent_bytes_run += result[1]['sent']
                recv_bytes_run += result[1]['recv']
                ttp_bytes_run += result[1]['ttp']
            sent_bytes.append(sent_bytes_run / len(x))
            recv_bytes.append(recv_bytes_run / len(x))
            ttp_bytes.append(ttp_bytes_run / len(x))

        metrics['sent'].append({'num': num_kmul, 'mean': np.mean(sent_bytes), 'std': np.std(sent_bytes)})
        metrics['recv'].append({'num': num_kmul, 'mean': np.mean(recv_bytes), 'std': np.std(recv_bytes)})
        metrics['ttp'].append({'num': num_kmul, 'mean': np.mean(ttp_bytes), 'std': np.std(ttp_bytes)})
        metrics['time'].append({'num': num_kmul, 'mean': np.mean(run_times), 'std': np.std(run_times)})

    # Print the results
    for metric, data in metrics.items():
        print(metric)
        for d in data:
            print(f"Num Scalar Multiplications: {d['num']}, Mean: {d['mean']:.4f}, Std: {d['std']:.4f}")
        print()

if __name__== "__main__" :
    sys.setrecursionlimit(5000)
    nparties()
    nadd()
    nmul()
    nkadd()
    nkmul()



