Running SNAP
============

SNAP uses a single command line tool to run the node, described in the configuration file.

``run_snap`` command
--------------------

.. argparse::
   :filename: ../src/snap/node.py
   :func: get_parser
   :prog: run_snap

Status monitoring
-----------------

When run with the ``--status`` option, snap will add a simple server, which will report its status on every request.  The server runs on `zmq.REP` socket, and will reply ``b'OK'`` every time it receives a query. 

This simple check has multiple uses.
In the simple case the failure to report the status indicates that the application is down. 
In another case, if the processing steps can't keep up with the incoming data rate, more and more of the cpu time will be occupied processing.
As the status server operates within the same thread, it will respond to the status request only when other processing parts are idle, so a processing delay is proportional to the CPU load.
Analizing the delay between request and status report, a monitoring process can identify such processing problems.

A user-defined monitoring tool should use the :func:`snap.status.status_req` function.

.. autofunction:: snap.status.status_req
