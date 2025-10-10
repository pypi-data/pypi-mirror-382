'''

    This module is a main script for the flow jobs.
    It instanciates a JobWorkerSession and exexutes the job pointed by the env-var "KABARET_JOBS_FLOW_OID"


'''

from __future__ import print_function

import sys
import os
import traceback

from kabaret.app.session import KabaretSession
from kabaret.subprocess_manager import SubprocessManager
from libreflow.utils.kabaret.jobs import jobs_actor


def try_initialize_maya():
    try:
        import maya.standalone
    except ImportError:
        pass
    else:
        print('This looks like a maya pythong, let us initialize it.')
        try:
            maya.standalone.initialize()
        except:
            print('!!! Error initializing Maya:')
            traceback.print_exc()
            print('!!! Error initializing Maya.')
            sys.exit(-1)
        print('Maya initialization done.')


class JobsWorkerSession(KabaretSession):

    def __init__(self):
        super(JobsWorkerSession, self).__init__('JobsWorker')

        self.cmds.Cluster.connect_from_env()
        self.execute_job()

    def _create_actors(self):
        super(JobsWorkerSession, self)._create_actors()
        self.jobs_actor = jobs_actor.Jobs(self)
        subprocess_manager = SubprocessManager(self)

    def execute_job(self):
        self.jobs_actor.worker_execute_job()


if __name__ == '__main__':
    try_initialize_maya()
    JobsWorkerSession()