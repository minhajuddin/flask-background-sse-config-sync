# number of processes
workers = 2
worker_class = "gevent"
# threads setting is ignored for gevent
#  threads = 8
spew = False
check_config = False
print_config = False
loglevel = "debug"
statsd_host = "localhost:8125"
dogstatsd_tags = "app:gunicorn"
statsd_prefix = "chaiclient"


def on_starting(server):
    server.log.info("Starting server, please wait...")


def on_reload(server):
    server.log.info("Reloading server, please wait...")


def when_ready(server):
    server.log.info("Server is ready.")


def pre_fork(server, worker):
    server.log.info("Pre-forking worker {0}".format(worker.pid))


def post_fork(server, worker):
    server.log.info("Post-forking worker {0}".format(worker.pid))


def post_worker_init(worker):
    worker.log.info("Post-worker-init worker {0}".format(worker.pid))


def worker_int(worker):
    worker.log.info("worker received INT or QUIT signal")


def worker_abort(worker):
    worker.log.info("worker received SIGABRT signal")


def pre_exec(server):
    server.log.info("About to exectue new binary")


def pre_request(worker, req):
    worker.log.info("Got request {0}".format(req.path))


def post_request(worker, req, environ):
    worker.log.info("Processed request {0}".format(req.path))


def child_exit(worker, status):
    worker.log.info("Worker exited with status {0}".format(status))


def worker_exit(_, worker):
    worker.log.info("Worker exited")


def nworkers_changed(server, new_value, old_value):
    server.log.info(
        "Number of workers changed from {0} to {1}".format(old_value, new_value)
    )


def on_exit(server):
    server.log.info("Exiting...")
