import sys
import time
import argparse
import traceback

from datetime import datetime, timedelta
from kabaret.app.session import KabaretSession
from kabaret.app.actors.flow import Flow
from kabaret import flow


def prefix_log():
    return f"[SYNC JOBS CLEANER SESSION - {datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')}]"


class CleanSyncJobsSession(KabaretSession):

    def _create_actors(self):
        Flow(self)
    
    def clear_jobs(self, project_name, clear_before=1800):
        clear_action_oid = f'/{project_name}/admin/multisites/working_sites/clear_site_queues'

        try:
            valid_project = self.cmds.Flow.is_action(clear_action_oid)
        except (flow.MissingChildError, flow.MissingRelationError):
            valid_project = False
        
        if not valid_project:
            self.log_error('Invalid project !')
            return

        self.log_info(f'{prefix_log()} Clearing jobs...')
        self.cmds.Flow.set_value(oid=clear_action_oid+'/emitted_since', value=clear_before)
        self.cmds.Flow.run_action(oid=clear_action_oid, button='Clear')


def process_remaining_args(args):
    parser = argparse.ArgumentParser(
        description='Libreflow Sync Jobs Cleaner Session Arguments'
    )
    parser.add_argument(
        '-c', '--clear-period', default=0, dest='period'
    )
    parser.add_argument(
        '-t', '--elapsed-time', default=1800, dest='time'
    )
    parser.add_argument(
        '-p', '--project', dest='project'
    )
    values, remaining_args = parser.parse_known_args(args)
    
    return (float(values.period), float(values.time), values.project, remaining_args)


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
    ) = CleanSyncJobsSession.parse_command_line_args(argv)

    session = CleanSyncJobsSession(session_name=session_name, debug=debug)
    session.cmds.Cluster.connect(host, port, cluster_name, db, password, read_replica_host, read_replica_port)

    (
        period,
        elapsed_time,
        project_name,
        remaining_args
    ) = process_remaining_args(remaining_args)

    # Check project existence
    if not session.cmds.Flow.exists('/'+project_name):
        session.log_error(
            f'{prefix_log()} No project /{project_name} found on this cluster. ' \
            'Please specify an existing project name.'
        )
        return

    # Check project root type
    project_type_name = session.get_actor('Flow').get_project_qualified_type_name(project_name)

    TASK_COMPLETED = False
    while (TASK_COMPLETED is False):
        try:
            session.clear_jobs(project_name, clear_before=elapsed_time)
            # Execute only once if no period argument
            if period == 0:
                TASK_COMPLETED = True
                return
            
            # Schedule next cleaning
            schedule_date = datetime.now() + timedelta(seconds=period)
            session.log_info(
                f"{prefix_log()} Next cleaning scheduled at {schedule_date.strftime('%Y-%m-%d %H:%M:%S')}"
            )
            time.sleep(period)
        except (Exception, KeyboardInterrupt) as e:
            if isinstance(e, KeyboardInterrupt):
                session.log_info(f'{prefix_log()} Cleaner stopped. Exiting...')
                break
            else:
                session.log_error(f"{prefix_log()} The following error occurred:")
                session.log_error(traceback.format_exc())
                session.log_error(f"{prefix_log()} Restart jobs cleaner...")


if __name__ == "__main__":
    main(sys.argv[1:])