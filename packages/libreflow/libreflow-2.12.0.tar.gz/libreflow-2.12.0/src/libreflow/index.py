import os
import sys
import argparse
import time
import traceback
from datetime import datetime, timedelta

from .utils.search.actor import Search
from .session import BaseCLISession


def prefix_log():
    return f"[SEARCH INDEX SESSION - {datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')}]"


class SearchIndexSession(BaseCLISession):

    """
    For indexing entities coming from films and asset types
    to the Libreflow search.
    This CLI session runs once.
    """

    def __init__(self, index_uri, session_name=None, debug=False):
        self._index_uri = index_uri
        super(SearchIndexSession, self).__init__(session_name, debug)

    def _create_actors(self):
        Search(self, self._index_uri, True)
    
    def index_project(self, project_name):
        self.log_info(f'{prefix_log()} Indexing {project_name} started')
        
        self.cmds.Search.rebuild_project_index(project_name, f'/{project_name}/films', max_depth=7)
        self.cmds.Search.rebuild_project_index(project_name, f'/{project_name}/asset_types', max_depth=7)
        
        self.log_info(f'{prefix_log()} Indexing {project_name} completed')


def parse_remaining_args(args):
    parser = argparse.ArgumentParser(
        description='Libreflow Search Index Session Arguments'
    )
    parser.add_argument(
        '--index-uri', default=os.getenv('LIBREFLOW_SEARCH_INDEX_URI', None), dest='index_uri'
    )
    parser.add_argument(
        '-i', '--index-period', default=0, dest='period'
    )
    parser.add_argument(
        '-p', '--project', dest='project'
    )
    values, _ = parser.parse_known_args(args)
    return (
        values.index_uri,
        float(values.period),
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
    ) = SearchIndexSession.parse_command_line_args(argv)
    (
        index_uri,
        period,
        project_name
    ) = parse_remaining_args(remaining_args)
    session = SearchIndexSession(index_uri=index_uri,
                            session_name=session_name,
                            debug=debug,)
    session.cmds.Cluster.connect(host, port, cluster_name, db, password, read_replica_host, read_replica_port)

    TASK_COMPLETED = False
    while (TASK_COMPLETED is False):
        try:
            session.index_project(project_name)
            # Execute only once if no period argument
            if period == 0:
                TASK_COMPLETED = True
                return
            
            # Schedule next indexing
            schedule_date = datetime.now() + timedelta(seconds=period)
            session.log_info(
                f"{prefix_log()} Next indexing scheduled at {schedule_date.strftime('%Y-%m-%d %H:%M:%S')}"
            )
            time.sleep(period)
        except (Exception, KeyboardInterrupt) as e:
            if isinstance(e, KeyboardInterrupt):
                session.log_info(f'{prefix_log()} Indexing {project_name} manually stopped')
                break
            else:
                session.log_error(f"{prefix_log()} The following error occurred:")
                session.log_error(traceback.format_exc())
                session.log_error(f"{prefix_log()} Restart indexing...")
    
    session.close()


if __name__ == "__main__":
    main(sys.argv[1:])
