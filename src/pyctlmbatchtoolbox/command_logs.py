#!/usr/bin/env python3

import argparse
import sys
from pyctlmbatchtoolbox.context import Context
from pyctlmbatchtoolbox.command import Command
from pyctlmbatchtoolbox.common import *
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class ContextLogs(Context):
    """Keep context of passed parameters"""
    jobname = ''
    show_job_logs = True
    show_job_output = True

    def print(self):
        logging.info('Arguments parsed:')
        logging.info(f'Show job logs {self.show_job_logs} {type(self.show_job_logs)}')
        logging.info(f'Show job output {self.show_job_output} {type(self.show_job_output)}')


class CommandLogs(Command):
    description =  Command.description + """      Get logs and stdout of the last job run."""
    ctx = ContextLogs()


    def parse_arguments(self, sysargs, ctx):
        parser = argparse.ArgumentParser(description=self.description)
        parser.add_argument('--jobname', dest='jobname', required=False, default=None, help="Jobname to get logs (ex: dAPKTEST222)")
        parser.add_argument('--controlm-user', dest='controlm_user', required=False, default=None, help="")
        parser.add_argument('--controlm-password', dest='controlm_password', required=False, default=None, help="")
        parser.add_argument('--show-job-logs', dest='show_job_logs', required=False, default=ctx.show_job_logs, help=f"Default {ctx.show_job_logs}")
        parser.add_argument('--show-job-output', dest='show_job_output', required=False, default=ctx.show_job_output, help=f"Default {ctx.show_job_output}")
        args = parser.parse_args(sysargs)

        if args.controlm_user:
            ctx.ctm_user = args.controlm_user
        if args.controlm_password:
            ctx.ctm_pass = args.controlm_password

        ctx.jobname = args.jobname

        if str(args.show_job_logs).lower() == 'true':
            ctx.show_job_logs = True

        if str(args.show_job_output).lower() == 'true':
            ctx.show_job_output = True

        ctx.print()

    def main(self):
        ctx = self.ctx
        self.parse_arguments(sys.argv[1:], self.ctx)
        Command.main(self, self.ctx)

        last_status = get_job_last_status(ctx.ctm_rest, ctx.token, ctx.jobname, 1)
        if last_status == None:
            logging.critical(f'Status not found for job {ctx.jobname}')
            exit(1)

        logging.debug(last_status)
        if 'statuses' not in last_status:
            logging.critical(f'Status not found for job {ctx.jobname}. Response {last_status}.')
            exit(0)
        status = last_status['statuses'][0]
        folder = status['folder']
        job_status = status['status']
        held = status['held']
        jobid = status['jobId']
        starttime = status['startTime']
        endtime = status['endTime']
        duration = -1
        application = status['application']
        output = status['outputURI']
        logs = status['logURI']
        if job_status not in ['Executing','Wait Condition','Wait Resource']:
            if len(endtime) > 0 and len(starttime) > 0:
              duration = int(endtime) - int(starttime)
        if output != "Job did not run, it has no output" and ctx.show_job_output:
            output_text = get_log_or_output(output, ctx.token)
            print(f"\n===OUTPUT=== url {output}\n")
            print(output_text)
        else:
            print(f'OUTPUT: Job {jobid} did not run, it has no output')

        if ctx.show_job_logs:
            logs_text = get_log_or_output(logs, ctx.token)
            print(f"\n===LOGS=== url {logs}\n")
            print(logs_text)

        print('-----------------')
        print(f'Application:[bold]{application}[/] Job:{jobid} folder:{folder} jobstatus:[underline]{job_status}[/] jobid:{jobid} duration:{duration} held:{held}')
        logging.info("Finish")


def main():
    logging.basicConfig(level=os.getenv('CTM_BATCH_LOG_LEVEL', CTM_BATCH_LOG_LEVEL_DEFAULT))
    command = CommandLogs()
    command.main()
    exit(0)

if __name__ == '__main__':
    main()
    exit(0)

