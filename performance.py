
import time
from multiprocessing import Process, Queue

import pytest

from expression import Scalar, Secret
from protocol import ProtocolSpec
from server import run
import time
import statistics
import matplotlib.pyplot as plt


import seaborn as sns
from tqdm import tqdm

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




def nparties():

    alice_secret = Secret()
    bob_secret = Secret()
    charlie_secret = Secret()

    parties = {
        "Alice": {alice_secret: 3},
        "Bob": {bob_secret: 14},
        "Charlie": {charlie_secret: 2}
    }

    times = []
    num_clients_list = [1,5, 10, 20, 50, 75, 100]

    for num_clients in num_clients_list:
        benchmark_parties = dict()
        for i in range(num_clients):
            benchmark_parties[f"Party {i}"] = {Secret(): i}

        parties.update(benchmark_parties)

        expr = (alice_secret + bob_secret + charlie_secret)
        start_time = time.time()
        suite(parties, expr)
        end_time = time.time()
        elapsed_time = end_time - start_time
        times.append(elapsed_time)

    # Plot the results
    sns.set(style="darkgrid")
    sns.set_palette("husl")
    plt.figure(figsize=(8, 6))
    plt.errorbar(num_clients_list, times, fmt='o-', markersize=8, capsize=5)
    plt.xlabel("Number of Parties")
    plt.ylabel("Time (Seconds)")
    plt.savefig("nparties.png")
    plt.show()


def nadd():
    alice_secret = Secret()
    bob_secret = Secret()
    charlie_secret = Secret()

    parties = {
        "Alice": {alice_secret: 3},
        "Bob": {bob_secret: 14},
        "Charlie": {charlie_secret: 2}
    }

    times = []
    num_additions_list = [10, 100, 500]

    # Warmup runs
    for i in range(3):
        expr = alice_secret + bob_secret + charlie_secret
        suite(parties, expr)

    for num_additions in num_additions_list:
        expr = alice_secret
        for i in range(num_additions - 1):
            expr += bob_secret
        expr += charlie_secret

        run_times = []
        for i in range(5):
            start_time = time.time()
            suite(parties, expr)
            end_time = time.time()
            elapsed_time = end_time - start_time
            run_times.append(elapsed_time)

        mean_time = statistics.mean(run_times)
        std_dev = statistics.stdev(run_times)
        times.append(mean_time)

    # Plot the results
    sns.set(style="darkgrid")
    sns.set_palette("husl")
    plt.figure(figsize=(8, 6))
    plt.errorbar(num_additions_list, times, fmt='o-', markersize=8, capsize=5)
    plt.xlabel("Number of Additions")
    plt.ylabel("Time (Seconds)")
    plt.show()



def nmul():
    alice_secret = Secret()
    bob_secret = Secret()
    charlie_secret = Secret()

    parties = {
        "Alice": {alice_secret: 3},
        "Bob": {bob_secret: 14},
        "Charlie": {charlie_secret: 2}
    }

    times = []
    num_additions_list = [10, 20, 50, 75, 100, 150, 200, 250]

    # Warmup runs
    for i in range(3):
        expr = alice_secret + bob_secret + charlie_secret
        suite(parties, expr)

    for num_additions in num_additions_list:
        expr = alice_secret
        for i in range(num_additions - 1):
            expr *= bob_secret
        expr *= charlie_secret

        run_times = []
        for i in range(5):
            start_time = time.time()
            suite(parties, expr)
            end_time = time.time()
            elapsed_time = end_time - start_time
            run_times.append(elapsed_time)

        mean_time = statistics.mean(run_times)
        std_dev = statistics.stdev(run_times)
        times.append(mean_time)

    # Plot the results
    sns.set(style="darkgrid")
    sns.set_palette("husl")
    plt.figure(figsize=(8, 6))
    plt.errorbar(num_additions_list, times, fmt='o-', markersize=8, capsize=5)
    plt.xlabel("Number of Multiplications")
    plt.ylabel("Time (Seconds)")
    plt.show()




def nkadd():
    alice_secret = Secret()
    bob_secret = Secret()
    charlie_secret = Secret()

    parties = {
        "Alice": {alice_secret: 3},
        "Bob": {bob_secret: 14},
        "Charlie": {charlie_secret: 2}
    }

    times = []
    num_additions_list = [10, 20, 50, 75, 100, 150, 200, 250]
    k = Scalar(1)
    # Warmup runs
    for i in range(3):
        expr = alice_secret + bob_secret + charlie_secret
        suite(parties, expr)

    for num_additions in num_additions_list:
        expr = alice_secret
        for i in range(num_additions - 1):
            expr += k
        expr += charlie_secret

        run_times = []
        for i in range(5):
            start_time = time.time()
            suite(parties, expr)
            end_time = time.time()
            elapsed_time = end_time - start_time
            run_times.append(elapsed_time)

        mean_time = statistics.mean(run_times)
        std_dev = statistics.stdev(run_times)
        times.append(mean_time)

    # Plot the results
    sns.set(style="darkgrid")
    sns.set_palette("husl")
    plt.figure(figsize=(8, 6))
    plt.errorbar(num_additions_list, times, fmt='o-', markersize=8, capsize=5)
    plt.xlabel("Number of Scalar Additions")
    plt.ylabel("Time (Seconds)")
    plt.show()


def nkmul():
    alice_secret = Secret()
    bob_secret = Secret()
    charlie_secret = Secret()

    parties = {
        "Alice": {alice_secret: 3},
        "Bob": {bob_secret: 14},
        "Charlie": {charlie_secret: 2}
    }

    times = []
    num_additions_list = [10, 20, 50, 75, 100, 150, 200, 250]
    k = Scalar(1)
    # Warmup runs
    for i in range(3):
        expr = alice_secret + bob_secret + charlie_secret
        suite(parties, expr)

    for num_additions in num_additions_list:
        expr = alice_secret
        for i in range(num_additions - 1):
            expr *= k
        expr += charlie_secret

        run_times = []
        for i in range(5):
            start_time = time.time()
            suite(parties, expr)
            end_time = time.time()
            elapsed_time = end_time - start_time
            run_times.append(elapsed_time)

        mean_time = statistics.mean(run_times)
        std_dev = statistics.stdev(run_times)
        times.append(mean_time)

    # Plot the results
    sns.set(style="darkgrid")
    sns.set_palette("husl")
    plt.figure(figsize=(8, 6))
    plt.errorbar(num_additions_list, times, fmt='o-', markersize=8, capsize=5)
    plt.xlabel("Number of Scalar Multiplications")
    plt.ylabel("Time (Seconds)")
    plt.show()

if __name__== "__main__" :
    nadd()



