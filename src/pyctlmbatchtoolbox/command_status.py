#!/usr/bin/env python3

import argparse
import sys
from pyctlmbatchtoolbox.context import Context
from pyctlmbatchtoolbox.command import Command
from pyctlmbatchtoolbox.common import *
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class ContextStatus(Context):
    """Keep context of passed parameters"""
    ctm_agentid = None
    ctm_status = 'Executing'

    def print(self):
        logging.info('Arguments parsed:')
        logging.info(f'Agent {self.ctm_agentid}')
        logging.info(f'Status{self.ctm_status}')

class CommandStatus(Command):
    description =  Command.description + """Get list of jobs filtered for a given status (ex: Executing)."""
    ctx = ContextStatus()

    def parse_arguments(self, sysargs, ctx):
        parser = argparse.ArgumentParser(description=self.description)
        parser.add_argument('--status', dest='status', required=False, default=ctx.ctm_status, help=f"Filter by status. Ex: Executing. Default is {ctx.ctm_status}")
        parser.add_argument('--agentid', dest='agentid', required=False, default=None, help="Filter by Agentid")
        parser.add_argument('--controlm-user', dest='controlm_user', required=False, default=None, help="")
        parser.add_argument('--controlm-password', dest='controlm_password', required=False, default=None, help="")
        args = parser.parse_args(sysargs)

        if args.controlm_user:
            ctx.ctm_user = args.controlm_user
        if args.controlm_password:
            ctx.ctm_pass = args.controlm_password

        ctx.ctm_status = args.status
        ctx.ctm_agentid = args.agentid
        ctx.print()

    def main(self):
        ctx = self.ctx
        self.parse_arguments(sys.argv[1:], ctx)
        Command.main(self, self.ctx)

        res = get_job_agent_status(ctx.ctm_rest, ctx.token, ctx.ctm_status, ctx.ctm_agentid)
        if res == None:
            logging.critical(f'Status not found for job {ctx.ctm_status} and agent {ctx.ctm_agentid}')
            exit(1)

        statuses = res['statuses']
        for status in statuses:
            jobid = status['jobId']
            name = status['name']
            folder = status['folder']
            starttime = status['startTime']
            endtime = status['endTime']
            numberRuns = status['numberOfRuns']
            print(f'Job: {name} running in agent:{ctx.ctm_agentid} with status:{ctx.ctm_status} jobId:{jobid} folder:{folder} starttime:{starttime} numerOfRuns:{numberRuns}')
        logging.info(f"Jobs found: {len(res)} with status: {ctx.ctm_status} for agent:{ctx.ctm_agentid}")


def main():
    logging.basicConfig(level=os.getenv('CTM_BATCH_LOG_LEVEL', CTM_BATCH_LOG_LEVEL_DEFAULT))
    command = CommandStatus()
    command.main()
    exit(0)

if __name__ == '__main__':
    main()
    exit(0)

