#!/usr/bin/env python3
import argparse
import sys
from pyctlmbatchtoolbox.context import Context
from pyctlmbatchtoolbox.command import Command
from pyctlmbatchtoolbox.common import *

class ContextHostgroup(Context):
    action = 'GET'
    hostgroup = None
    agentid = None
    condition = None

    def print(self):
        Context.print(self)
        logging.info("print ===================C")
        logging.info(f'Action {self.action}')
        logging.info(f'Hostgroup {self.hostgroup}')
        logging.info(f'Agent id {self.agentid}')
        logging.info(f'Condition {self.condition}')
        logging.info("print ===================C")

    def validate(self):
        Context.validate(self)
        logging.info("validate ===================C")
        if self.action not in ['GET', 'ADD_AGENT', 'DELETE_AGENT']:
            logging.critical(f"Action {self.action} not implemented.")
            exit(1)
        logging.info("validate ===================C")


class CommandHostgroup(Command):
    description =  Command.description + """     List, add, or delete Control-M hostgroups. Can [un]register agent with conditions into a hostgroup."""
    ctx = ContextHostgroup()

    def parse_arguments(self, sysargs, ctx):
        parser = argparse.ArgumentParser(description=self.description)
        parser.add_argument('--controlm-server', dest='controlm_server', required=True, default=None,
                            help="Ex: CTMSRVP1, CTMSRVT1")
        parser.add_argument('--controlm-user', dest='controlm_user', required=False, default=None, help="")
        parser.add_argument('--controlm-password', dest='controlm_password', required=False, default=None, help="")
        parser.add_argument('--action', dest='action', required=False, default=ctx.action, help=f"GET, ADD_AGENT, DELETE_AGENT. Default is {ctx.action}")
        parser.add_argument('--hostgroup', dest='hostgroup', required=False, default=ctx.hostgroup, help=f"Hostgroup to list. If absent all groups will be listed. Needed to list the content.")
        parser.add_argument('--agentid', dest='agentid', required=False, default=ctx.agentid, help=f"Agent id to register into the hostgroup. Can specify a condition.")
        parser.add_argument('--condition', dest='condition', required=False, default=ctx.condition, help=f"Condition to add to the agent registration.")
        args = parser.parse_args(sysargs)

        if args.controlm_user:
            ctx.ctm_user = args.controlm_user
        if args.controlm_password:
            ctx.ctm_pass = args.controlm_password

        ctx.ctm_server = args.controlm_server
        ctx.hostgroup = args.hostgroup
        ctx.agentid = args.agentid
        ctx.condition = args.condition
        ctx.action = args.action

        ctx.print()
        ctx.validate()

    def main(self):
        self.parse_arguments(sys.argv[1:], self.ctx)
        Command.main(self, self.ctx)
        ctx = self.ctx
        # order the job and get JobId
        print(f'Getting hostgroups for ctm server {ctx.ctm_server} ctm rest endpoint: {ctx.ctm_rest}' )
        if self.ctx.hostgroup == None:
            hostgroups = get_controlm_hostgroups(ctx.ctm_rest, ctx.token, ctx.ctm_server)
            for hostgroup in hostgroups:
                print(hostgroup)
            print(f'Hostgroups found: {len(hostgroups)}')
        else:
            if ctx.action == 'GET':
                agents = get_agents_in_hostgroups(ctx.ctm_rest, ctx.token, ctx.ctm_server, ctx.hostgroup)
                print(f'Hostgroup:{ctx.hostgroup} ctm:{ctx.ctm_server}')
                for agent in agents:

                    print(f'{agent}')
                print(f'Agents found: {len(agents)}')
            elif ctx.action == 'ADD_AGENT':
                logging.info(f'Adding agent {ctx.agentid} condition {ctx.condition} server:{ctx.ctm_server}')
                res = register_agent(ctx.ctm_rest,ctx.token,ctx.ctm_server,ctx.agentid,ctx.hostgroup,ctx.condition)
                if res:
                    print(f"Agent {ctx.agentid} registered to group {ctx.hostgroup} with condition {ctx.condition}")
            elif ctx.action == 'DELETE_AGENT':
                logging.info(f'Removing agent {ctx.agentid} hostgroup:{ctx.hostgroup} server:{ctx.ctm_server}')
                res = unregister_agent(ctx.ctm_rest, ctx.token, ctx.ctm_server, ctx.agentid, ctx.hostgroup)
                if res:
                    print(f"Agent {ctx.agentid} unregistered from group {ctx.hostgroup} with condition {ctx.condition}")
                    logging.info(f"Agent removed")
            else:
                logging.critical(f"Action not found {ctx.action}")
                exit(1)

        logging.info("Finish")

def main():
    logging.basicConfig(level=os.getenv('CTM_BATCH_LOG_LEVEL', CTM_BATCH_LOG_LEVEL_DEFAULT))
    command = CommandHostgroup()
    command.main()
    exit(0)


if __name__ == '__main__':
    main()
    exit(0)

