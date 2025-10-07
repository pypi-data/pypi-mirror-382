"""
Ray for Slurm
"""
import argparse
import subprocess
from time import sleep

import paramiko
from loguru import logger


def get_idle_node_info(partitions: list[str], black_list: list[str]) -> list[dict]:
    """
    Queues the idle nodes in the specified Slurm partitions and returns their names, CPU counts, and memory sizes.

    Parameters
    -----------
    partitions : list of str
        List of Slurm partition names to check for idle nodes.

    Returns
    -----------
    idle_nodes_info : list of dict
        each dict contains:
        {
            "node": node name,
            "cpus": CPUs,
            "mem_MB": memory in MB,
            "partition": partition name
        }
    """
    idle_nodes_info = []

    for partition in partitions:
        try:
            # sinfo cmd: -h remove header, -t idle only idle nodes, -N list by node, -o output node name, CPU, memory
            cmd = ["sinfo", "-h", "-t", "idle", "-p", partition, "-N", "-o", "%N %c %m"]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)

            for line in result.stdout.strip().split("\n"):
                if not line:
                    continue
                parts = line.split()
                if len(parts) != 3:
                    continue
                node_name, cpus, mem = parts
                if node_name in black_list:
                    print(f"Node {node_name} is in black list, skip ...")
                    continue
                idle_nodes_info.append(
                    {
                        "node": node_name,
                        "cpus": int(cpus),
                        "mem_MB": int(mem),
                        "partition": partition,
                    }
                )
        except subprocess.CalledProcessError as e:
            print("Error executing sinfo:", e, "partition:", partition)
    return idle_nodes_info


def main(partitions, max_nodes, black_list):
    idle_nodes = get_idle_node_info(partitions, black_list)
    if len(idle_nodes) > max_nodes:
        idle_nodes = idle_nodes[:max_nodes]  # limit to max_nodes
    print(f"Found {len(idle_nodes)} idle nodes.")
    for node_info in idle_nodes:
        print(f"Allocating node: {node_info['node']}")
        try:
            cmd = [
                "srun",
                "--job-name=ray_job",
                "-p",
                node_info["partition"],
                "-N1",
                "-w",
                node_info["node"],
                f'-n{node_info["cpus"]}',
                "--output=/dev/null",
                "--error=/dev/null",
                "bash",
                "-c",
                "sleep 24h",
            ]
            _ = subprocess.Popen(cmd)
            print(f"Node {node_info['node']} allocated.")
            sleep(5)  # wait a bit for the job to start
            ray_cmd = (
                "/flash/grp/gglab/xiacr/NicheAtlas/conda/bin/ray start --address='128.5.28.26:6379'"
            )
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            for i in range(5):  # retry 5 times
                try:
                    client.connect(node_info["node"], port=22)
                    print(f"SSH to {node_info['node']}...")
                    stdin, stdout, stderr = client.exec_command(ray_cmd)
                    print(stdout.read().decode())
                    print(stderr.read().decode())
                    client.close()
                    break
                except Exception as e:  # noqa
                    print(f"SSH to {node_info['node']} failed: {e}, retry time {i + 1}...")
                    sleep(3)
                    continue
            logger.success(f"Ray started on {node_info['node']}.")
        except Exception as e:  # noqa
            logger.error(f"Failed to allocate node {node_info['node']}: {e}")
        print("=" * 80)


def get_args():
    parser = argparse.ArgumentParser()

    df_partitions = ["dcu", "cpu1", "cpu2"]

    # partitions
    parser.add_argument(
        "--partitions",
        type=str,
        nargs="+",
        default=df_partitions,
        help="Slurm partition names to use.",
    )
    # max_nodes
    parser.add_argument(
        "--max_nodes", type=int, default=2, help="Maximum number of nodes to allocate."
    )
    # black_list
    parser.add_argument(
        "--black_list",
        type=str,
        nargs="+",
        default=[],
        help="List of node names to avoid allocation.",
    )
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    args = get_args()
    partitions = args.partitions
    max_nodes = args.max_nodes
    black_list = args.black_list
    main(partitions, max_nodes, black_list)
