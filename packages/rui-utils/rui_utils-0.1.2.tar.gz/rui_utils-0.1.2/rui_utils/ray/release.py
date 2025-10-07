import argparse
import getpass
import subprocess
from time import sleep

from loguru import logger


def get_slurm_jobs(keyword="ray_") -> list[dict]:
    """
    Get all slurm jobs for current user with job name containing the keyword.
    """
    user = getpass.getuser()
    cmd = ["squeue", "-u", user, "-o", "%.18i %.20j %.20R"]
    result = subprocess.check_output(cmd, text=True).strip().split("\n")[1:]

    jobs = []
    for line in result:
        parts = line.split()
        if len(parts) >= 3:
            jobid, jobname, node = parts[0], parts[1], parts[2]
            if keyword in jobname.lower():
                jobs.append({"jobid": jobid, "jobname": jobname, "node": node})
    return jobs


def _node_is_idle(node):
    """
    Check if a node is idle: low CPU load & no user processes
    """
    user = getpass.getuser()
    try:
        # get load average
        load_str = (
            subprocess.check_output(
                [
                    "ssh",
                    "-o",
                    "StrictHostKeyChecking=no",
                    "-o",
                    "UserKnownHostsFile=/dev/null",
                    node,
                    "cat /proc/loadavg",
                ],
                text=True,
            )
            .strip()
            .split()[0]
        )
        load = float(load_str)
        print(f"Node {node} load: {load}")

        # check user processes
        ps_cmd = f"ps -u {user} -o pcpu= || true"
        cpu_list_str = (
            subprocess.check_output(
                [
                    "ssh",
                    "-o",
                    "StrictHostKeyChecking=no",
                    "-o",
                    "UserKnownHostsFile=/dev/null",
                    node,
                    ps_cmd,
                ],
                text=True,
            )
            .strip()
            .splitlines()
        )
        has_heavy_proc = any(float(v) > 30.0 for v in cpu_list_str if v.strip())
        print(f"Node {node} has heavy user process: {has_heavy_proc}")

        # consider idle if load < 1 and no heavy user process
        return load < 1 and not has_heavy_proc
    except Exception as e:  # noqa
        logger.error(f"[WARN] Failed to check node {node}: {e}")
        return False


def node_is_idle(node):
    # double check by _node_is_idle
    check1 = _node_is_idle(node)
    sleep(3)
    check2 = _node_is_idle(node)
    return check1 and check2


def cancel_job(jobid):
    """Cancel a specific job by jobid"""
    try:
        subprocess.run(["scancel", jobid], check=True)
        logger.warning(f"[INFO] Cancelled job {jobid}")
    except subprocess.CalledProcessError as e:
        logger.error(f"[ERROR] Failed to cancel job {jobid}: {e}")


def main(keyword, dry: bool = False):
    """Cancel all Ray jobs running on idle nodes."""
    jobs = get_slurm_jobs(keyword)
    while len(jobs) > 0:
        logger.info("Try release idle nodes")
        print(f"Found {len(jobs)} {keyword} jobs.")
        for job in jobs:
            node = job["node"]
            jobid = job["jobid"]
            if node_is_idle(node):
                logger.warning(f"Node {node} is idle, cancelling job {jobid} ...")
                if not dry:
                    cancel_job(jobid)
            else:
                logger.info(f"Node {node} is busy, keep job {jobid} running.")
        sleep(10)
        jobs = get_slurm_jobs(keyword)
    logger.success("All nodes released")


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--keyword", type=str, default="ray", help="Keyword to identify Ray jobs")
    parser.add_argument("--dry", action="store_true", help="Dry run without cancelling jobs")
    return parser.parse_args()


if __name__ == "__main__":
    args = get_args()
    main(args.keyword, args.dry)
