#!/usr/bin/env python3

import argparse
import sys
from pyctlmbatchtoolbox.context import Context
from pyctlmbatchtoolbox.command import Command
from pyctlmbatchtoolbox.common import *
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class ContextOrder(Context):
    """Keep context of passed parameters"""
    ctm_server = ''
    folder = None
    job = None
    sleep_before_status_seconds = 5
    max_retry_get_status = 3
    show_job_logs = False
    show_job_output = False

    def print(self):
        logging.info('Arguments parsed:')
        logging.info(f'User {self.ctm_user}')
        logging.info(f'Folder {self.folder}')
        logging.info(f'Job {self.job}')
        logging.info(f'Server{self.ctm_server}')
        logging.info(f'Show job logs {self.show_job_logs} {type(self.show_job_logs)}')
        logging.info(f'Show job output {self.show_job_output} {type(self.show_job_output)}')

    def validate(self):
        if self.job is None and self.folder is None:
            logging.error(f'Missing parameter: Job OR folder must be set')
            exit(1)

class CommandOrder(Command):
    description =  Command.description + """         Order a job (or folder) and show status and logs."""
    ctx = ContextOrder()

    def parse_arguments(self, sysargs, ctx):
        parser = argparse.ArgumentParser(description=self.description)
        parser.add_argument('--folder', dest='folder', required=False, default=None, help="Control-M simple folder")
        parser.add_argument('--job', dest='job', required=False, default=None, help="Job id. Ex: dAAATEST111")
        parser.add_argument('--controlm-server', dest='controlm_server', required=True, default=ctx.ctm_server, help="")
        parser.add_argument('--controlm-user', dest='controlm_user', required=False, default=None, help="")
        parser.add_argument('--controlm-password', dest='controlm_password', required=False, default=None, help="")
        parser.add_argument('--sleep-before-status', dest='sleep_before_status', required=False, default=5, help=f"Sleep before status in seconds (default {ctx.sleep_before_status_seconds})")
        parser.add_argument('--max-retry-get-status', dest='max_retry_get_status', required=False, default=5, help=f"Retry status (default {ctx.max_retry_get_status})")
        parser.add_argument('--show-job-logs', dest='show_job_logs', required=False, default=ctx.show_job_logs, help=f"Default {ctx.show_job_logs}")
        parser.add_argument('--show-job-output', dest='show_job_output', required=False, default=ctx.show_job_output, help=f"Default {ctx.show_job_output}")
        args = parser.parse_args(sysargs)

        if args.controlm_user:
            ctx.ctm_user = args.controlm_user
        if args.controlm_password:
            ctx.ctm_pass = args.controlm_password

        ctx.ctm_server = args.controlm_server
        ctx.folder = args.folder
        ctx.job = args.job
        ctx.sleep_before_status_seconds = int(args.sleep_before_status)
        ctx.max_retry_get_status = int(args.max_retry_get_status)

        if str(args.show_job_logs).lower() == 'true':
            ctx.show_job_logs = True

        if str(args.show_job_output).lower() == 'true':
            ctx.show_job_output = True

        ctx.print()
        ctx.validate()

    def main(self):
        ctx = self.ctx
        self.parse_arguments(sys.argv[1:], ctx)
        Command.main(self, self.ctx)

        # order the job and get JobId
        runid = order_folder_job(ctx.ctm_rest, ctx.token, ctx.ctm_server, ctx.folder, ctx.job)
        print(f'Control-M folder ordered: {ctx.folder} runid:{runid}')
        logging.info(f"Runid {runid}")

        current_retries = 0
        statuses = get_folder_status(ctx.ctm_rest, ctx.token, runid)
        while current_retries < ctx.max_retry_get_status and statuses == None:
            print(f"Retrieving status... try {current_retries}/{ctx.max_retry_get_status}")
            time.sleep(ctx.sleep_before_status_seconds)
            logging.info(f"Getting status for runId {runid}")
            statuses = get_folder_status(ctx.ctm_rest, ctx.token, runid)
            logging.debug(f"Get status {statuses}")
            current_retries +=1

        if statuses == None:
            logging.error(f'Status not found for runId {runid} max retry {ctx.max_retry_get_status} sleep {ctx.sleep_before_status_seconds}')
            exit(1)

        for s in statuses['statuses']:
            job = s['jobId']
            name = s['name']
            status = s['status']
            logs = s['logURI']
            output = s['outputURI']
            print(f"JobID {job} Name:{name} Status:{status}")
            if output != "Job did not run, it has no output" and ctx.show_job_output:
                output_text = get_log_or_output(output, ctx.token)
                print(f"===OUTPUT=== url {output}")
                print(output_text)

            if ctx.show_job_logs:
                logs_text = get_log_or_output(logs, ctx.token)
                print(f"===LOGS=== url {logs}")
                print(logs_text)
        logging.info("Finish")


def main():
    logging.basicConfig(level=os.getenv('CTM_BATCH_LOG_LEVEL', CTM_BATCH_LOG_LEVEL_DEFAULT))
    command = CommandOrder()
    command.main()
    exit(0)

if __name__ == '__main__':
    main()
    exit(0)

