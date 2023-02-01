#!/usr/bin/env python3
import argparse
import sys
import urllib3
from pyctlmbatchtoolbox.common import *
from pyctlmbatchtoolbox.context import Context
from .command import Command
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class ContextCondition(Context):
    """Keep context of passed parameters"""
    action = 'GET'
    condition = None
    search = None

    def print(self):
        logging.info('Arguments parsed:')
        logging.info(f'Action {self.action}')
        logging.info(f'Condition {self.condition}')

class CommandCondition(Command):
    description =  Command.description + f"""        List, add, or delete Control-M conditions (used to pilot Agent registration). """
    ctx = ContextCondition()

    def parse_arguments(self, sysargs, ctx):

        parser = argparse.ArgumentParser(description=self.description)
        parser.add_argument('--controlm-server', dest='controlm_server', required=False, default=None, help="Control-M server. If not set, all conditions from all servers are returned.")
        parser.add_argument('--controlm-user', dest='controlm_user', required=False, default=None, help="")
        parser.add_argument('--controlm-password', dest='controlm_password', required=False, default=None, help="")
        parser.add_argument('--action', dest='action', required=False, default=ctx.action, help=f"GET, CREATE, DELETE")
        parser.add_argument('--condition', dest='condition', required=False, default=ctx.condition, help=f"The name of the condition")
        parser.add_argument('--search-criteria', dest='search', required=False, default=ctx.search, help=f"Search criteria. Only used with action=GET. Ex: 'name=A*&server=controlm'")
        args = parser.parse_args(sysargs)

        if args.controlm_user:
            ctx.ctm_user = args.controlm_user
        if args.controlm_password:
            ctx.ctm_pass = args.controlm_password

        ctx.search = args.search
        ctx.ctm_server = args.controlm_server
        ctx.search = args.search
        ctx.condition = args.condition

        ctx.action = args.action
        if ctx.action not in ['GET','CREATE', 'DELETE']:
            logging.critical(f"Action {ctx.action} not implemented yet")
            exit(1)

        if ctx.action in ['CREATE', 'DELETE']:
            if ctx.ctm_server is None or ctx.condition is None:
                logging.critical(f"Server ({ctx.ctm_server}) and condition ({ctx.condition}) are mandatory for action: {ctx.action}")
                exit(1)

        if ctx.ctm_user is None or ctx.ctm_pass is None:
            logging.critical("Mandatory parameter missing (user, pass)")
            exit(1)
        ctx.print()

    def main(self):
        ctx = self.ctx
        self.parse_arguments(sys.argv[1:], ctx)
        Command.main(self, self.ctx)

        if ctx.action == 'GET':
            # order the job and get JobId
            print(f'Getting conditions for criteria {ctx.search} ctm rest endpoint: {ctx.ctm_rest}' )
            conditions = get_conditions(ctx.ctm_rest, ctx.token, ctx.search)
            for condition in conditions:
                name = condition['name']
                ctm = condition['ctm']
                date = condition['date']
                print(f'Name:{name} ctm:{ctm} date:{date}')
            print(f'Conditions found: {len(conditions)}')
        elif ctx.action == 'CREATE':
            try:
                res = create_condition(ctx.ctm_rest, ctx.token, ctx.ctm_server, ctx.condition)
                print(f'Condition {ctx.condition} created res:{res} ')
            except:
                logging.error(f"Error creating condition! server:{ctx.ctm_server} condition:{ctx.condition}")
                exit(1)
        elif ctx.action == 'DELETE':
            res = delete_condition(ctx.ctm_rest, ctx.token, ctx.ctm_server, ctx.condition)
            print(f'Condition {ctx.condition} deleted res:{res} ')
        logging.info("Finish")


def main():
    logging.basicConfig(level=os.getenv('CTM_BATCH_LOG_LEVEL', CTM_BATCH_LOG_LEVEL_DEFAULT))
    command = CommandCondition()
    command.main()
    exit(0)

if __name__ == '__main__':
    main()
    exit(0)