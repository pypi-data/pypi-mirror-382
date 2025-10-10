import os
import sys
import ast
import time
from pprint import pprint

from libreflow.session import BaseCLISession


def main(args):
    runner = args[0]
    oid = args[1]
    function_name = args[2]

    try:
        function_args = ast.literal_eval(args[3])
    except:
        raise Exception(f"\n\nInvalid arguments '{args[3]}': "
        "it must be a valid Python list\n\n")
    
    try:
        function_kwargs = ast.literal_eval(args[4])
    except:
        raise Exception(f"\n\nInvalid keyword arguments '{args[4]}': "
        "it must be a valid Python dictionary")

    session = BaseCLISession(
        session_name="%s(pid=%i)" % (
            runner, os.getpid()
        ),
        debug=False,
    )
    
    session.cmds.Cluster.connect_from_env()
    session.cmds.Flow.call(oid, function_name, args=function_args, kwargs=function_kwargs)
    session.close()


if __name__ == "__main__":
    main(sys.argv[1:])
