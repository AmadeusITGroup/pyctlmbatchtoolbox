#!/usr/bin/env python3

import argparse
import sys
from pyctlmbatchtoolbox.context import Context
from pyctlmbatchtoolbox.command import Command
from pyctlmbatchtoolbox.common import *
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class ContextDeploy(Context):
    """Keep context of passed parameters"""
    action = 'GET'
    folder = ''
    execute = False
    export_format_xml = False

    def print(self):
        Context.print(self)
        logging.info("print ===================C")
        logging.info(f'Action {self.action}')
        logging.info(f'Folder {self.folder}')
        logging.info(f'Execute {self.execute}')
        logging.info(f'Export format XML {self.export_format_xml}')
        logging.info("print ===================C")

    def validate(self):
        Context.validate(self)
#        logging.info("validate ===================C")
#        if self.action not in ['GET', 'ADD_AGENT', 'DELETE_AGENT']:
#            logging.critical(f"Action {self.action} not implemented.")
#            exit(1)
#        logging.info("validate ===================C")


class CommandDeploy(Command):
    description =  Command.description + """     List Control-M deployments."""
    ctx = ContextDeploy()

    def parse_arguments(self, sysargs, ctx):
        parser = argparse.ArgumentParser(description=self.description)
        parser.add_argument('--controlm-server', dest='controlm_server', required=True, default=None, help="Ex: MUCACS1D, MUCCT4T")
        parser.add_argument('--controlm-user', dest='controlm_user', required=False, default=None, help="")
        parser.add_argument('--controlm-password', dest='controlm_password', required=False, default=None, help="")
        parser.add_argument('--action', dest='action', required=False, default=ctx.action, help=f"GET. Default is {ctx.action}")
        parser.add_argument('--folder', dest='folder', required=False, default=ctx.folder, help=f"Folder.")
        parser.add_argument('--export-format-xml', dest='export_format_xml', required=False, action="store_true", help=f"Export to XML format instead of Json.")
        args = parser.parse_args(sysargs)

        if args.controlm_user:
            ctx.ctm_user = args.controlm_user
        if args.controlm_password:
            ctx.ctm_pass = args.controlm_password

        ctx.ctm_server = args.controlm_server
        ctx.action = args.action
        ctx.folder = args.folder
        ctx.export_format_xml = args.export_format_xml

        ctx.print()
        ctx.validate()

    def main(self):
        from datetime import datetime

        self.parse_arguments(sys.argv[1:], self.ctx)
        Command.main(self, self.ctx)
        ctx = self.ctx

        print(f'Getting deploy from {ctx.ctm_rest} {ctx.ctm_server} {ctx.folder} (may take a while)')
        response = get_controlm_deploy(ctx.ctm_rest, ctx.token, ctx.ctm_server, ctx.folder, export_format_xml=ctx.export_format_xml)

        # write deploy to file
        extension = 'xml' if ctx.export_format_xml else 'json'
        filename = f'{ctx.ctm_server}-{ctx.folder}-deploy.{extension}'
        print(f'Writting file with deploys for {ctx.ctm_server} {ctx.folder} {filename}')
        with open(filename, "w") as f:
            f.write(response)
        print(f'Done!')
        exit(0)

def main():
    logging.basicConfig(level=os.getenv('CTM_BATCH_LOG_LEVEL', CTM_BATCH_LOG_LEVEL_DEFAULT))
    command = CommandDeploy()
    command.main()
    exit(0)


if __name__ == '__main__':
    main()
    exit(0)

