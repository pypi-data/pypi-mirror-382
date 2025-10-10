import os
import sys
import argparse
import time
import datetime
import traceback

from .session import BaseCLISession


def log(msg):
    print("[SYNC SESSION - %s] %s" % (
        datetime.datetime.fromtimestamp(time.time()).strftime('%y-%m-%d %H:%M:%S'),
        msg
    ))


def parse_remaining_args(args):
    parser = argparse.ArgumentParser(
        description='Libreflow Synchronization Session Arguments'
    )
    parser.add_argument(
        '-s', '--site', default=os.getenv('LIBREFLOW_SITE', 'lfs'), dest='site'
    )
    parser.add_argument(
        '-p', '--project', dest='project'
    )
    values, _ = parser.parse_known_args(args)

    return (
        values.site,
        values.project
    )


def main(argv):
    (
        session_name,
        host,
        port,
        cluster_name,
        db,
        password,
        debug,
        read_replica_host,
        read_replica_port,
        remaining_args,
    ) = BaseCLISession.parse_command_line_args(argv)

    session = BaseCLISession(
        session_name=session_name, debug=debug,
    )
    session.cmds.Cluster.connect(host, port, cluster_name, db, password, read_replica_host, read_replica_port)

    (
        site,
        project
    ) = parse_remaining_args(remaining_args)

    session.cmds.Flow.call(
        "/" + project,
        "ensure_runners_loaded",
        args={}, kwargs={}
    )

    if site:
        os.environ["KABARET_SITE_NAME"] = site
    
    site_oid = f"/{project}/admin/multisites/working_sites/{site}"
    sync_action_oid = f"/{project}/synchronization/synchronize_files"

    root_dir = session.cmds.Flow.call(
        "/" + project, "get_root",
        args={}, kwargs={}
    )
    if not root_dir or not os.path.isdir(root_dir):
        print(f"Root dir not found: '{root_dir}' (must be defined in the current site settings)")
        sys.exit(1)

    exchange_site = session.cmds.Flow.call(
        "/" + project, "get_exchange_site",
        args={}, kwargs={}
    )
    
    get_waiting_jobs = lambda site_oid: session.cmds.Flow.call(
        site_oid, "get_jobs", args={}, kwargs=dict(status=['WAITING'])
    )
    synchronize_job = lambda job: session.cmds.Flow.call(
        sync_action_oid, "process", args={job}, kwargs={}
    )
    set_revision_sync_status = lambda oid, status, site_name=None: session.cmds.Flow.call(
        oid, "set_sync_status", args={status}, kwargs=dict(site_name=site_name)
    )
    touch = lambda oid: session.cmds.Flow.call(
        oid, "touch", args={}, kwargs={}
    )

    while (True):
        try:
            jobs = get_waiting_jobs(site_oid)
            num_wait = len(jobs)
            num_proc = 0
            log(f"Processing {num_wait} waiting jobs...")
            for job in jobs:
                synchronize_job(job)
                if job.status.get() != "PROCESSED":
                    continue

                if job.type.get() == "Download":
                    set_revision_sync_status(job.emitter_oid.get(), "Available")
                elif job.type.get() == "Upload":
                    set_revision_sync_status(job.emitter_oid.get(), "Available", exchange_site.name())
                touch(session.cmds.Flow.resolve_path(job.emitter_oid.get() + "/..")) # update revision map
                touch(session.cmds.Flow.resolve_path(sync_action_oid + "/..")) # update synchronization
                num_proc += 1
            log(f"Processed jobs: {num_proc}/{num_wait}")
            time.sleep(10)
        except (Exception, KeyboardInterrupt) as e:
            if isinstance(e, KeyboardInterrupt):
                print("Synchronization stopped")
                break
            else:
                print("The following error occurred:")
                print(traceback.format_exc())
                print("Restart synchronization...")


if __name__ == "__main__":
    main(sys.argv[1:])
