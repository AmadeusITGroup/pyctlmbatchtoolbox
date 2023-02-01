#!/usr/bin/env python3

import argparse
import sys
import urllib3
from pyctlmbatchtoolbox.common import *
from pyctlmbatchtoolbox.context import Context
from pyctlmbatchtoolbox.command import Command
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class CommandToken(Command):
    description =  Command.description + """Get security token for auth from Control M."""
    ctx = Context()

    def parse_arguments(self, sysargs, ctx):
        description = f"""
    """ + HELP_STRING_COMMON + get_env_var_str()
        parser = argparse.ArgumentParser(description=description)
        parser.add_argument('--controlm-user', dest='controlm_user', required=False, default=None, help="")
        parser.add_argument('--controlm-password', dest='controlm_password', required=False, default=None, help="")
        args = parser.parse_args(sysargs)

        if args.controlm_user:
            ctx.ctm_user = args.controlm_user
        if args.controlm_password:
            ctx.ctm_pass = args.controlm_password

        ctx.print()
        ctx.validate()


    def main(self):
        ctx = self.ctx
        self.parse_arguments(sys.argv[1:], ctx)
        ctx.token = get_controlm_token(ctx.ctm_rest, ctx.ctm_user, ctx.ctm_pass)
        print(ctx.token)

def main():
    logging.basicConfig(level=os.getenv('CTM_BATCH_LOG_LEVEL', CTM_BATCH_LOG_LEVEL_DEFAULT))
    command = CommandToken()
    command.main()
    exit(0)


if __name__ == '__main__':
    main()
    exit(0)

