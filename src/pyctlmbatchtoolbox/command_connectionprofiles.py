#!/usr/bin/env python3

import argparse
import sys

import urllib3
from pyctlmbatchtoolbox.context import Context
from pyctlmbatchtoolbox.command import Command
from pyctlmbatchtoolbox.common import *
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class ContextConnectionProfile(Context):
    """Keep context of passed parameters"""
    action = 'GET'
    connectionprofile = None
    agent = None
    type = 'FileTransfer'

    def print(self):
        logging.info('Arguments parsed:')
        logging.info(f'Action {self.action}')
        logging.info(f'Connection profile {self.connectionprofile}')
        logging.info(f'Agent id {self.agent}')
        logging.info(f'Type {self.type}')

class CommandConnectionProfile(Command):
    description =  Command.description + """List, add, or delete Control-M hostgroups. Can [un]register agent with conditions into a hostgroup."""
    ctx = ContextConnectionProfile()

    def parse_arguments(self, sysargs, ctx):
        parser = argparse.ArgumentParser(description=self.description)
        parser.add_argument('--controlm-server', dest='controlm_server', required=True, default=None, help="Ex: MUCACS1D, MUCCT4T")
        parser.add_argument('--controlm-user', dest='controlm_user', required=False, default=None, help="")
        parser.add_argument('--controlm-password', dest='controlm_password', required=False, default=None, help="")
        parser.add_argument('--agent', dest='agent', required=True, default=ctx.agent, help=f"Agent id used to retrieve connection profiles.")
        parser.add_argument('--type', dest='type', required=False, default=ctx.type, help=f"Type of the connection profile. Default is {ctx.type}.")
        args = parser.parse_args(sysargs)

        if args.controlm_user:
            ctx.ctm_user = args.controlm_user
        if args.controlm_password:
            ctx.ctm_pass = args.controlm_password

        ctx.ctm_server = args.controlm_server
        ctx.agent = args.agent
        ctx.print()

    def main(self):
        ctx = self.ctx
        self.parse_arguments(sys.argv[1:], ctx)
        Command.main(self, self.ctx)

        print(f'Getting connection profiles for ctm server {ctx.ctm_server} agent: {ctx.agent} type {ctx.type} ctm rest endpoint: {ctx.ctm_rest}' )
        connection_profiles = get_connection_profiles(ctx.ctm_rest, ctx.token, ctx.ctm_server, ctx.agent, ctx.type)
        for cp in connection_profiles:
            print(f'Connection profile: {cp}: {connection_profiles[cp]}')
        print(f'Coonnection profiles found: {len(connection_profiles)}')
        logging.info("Finish")

def main():
    logging.basicConfig(level=os.getenv('CTM_BATCH_LOG_LEVEL', CTM_BATCH_LOG_LEVEL_DEFAULT))
    command = CommandConnectionProfile()
    command.main()
    exit(0)

if __name__ == '__main__':
    main()
    exit(0)

