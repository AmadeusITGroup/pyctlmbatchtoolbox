#!/usr/bin/env python3


import argparse
import sys
#import logging
#import os
#import urllib3
from pyctlmbatchtoolbox.context import Context
from pyctlmbatchtoolbox.command import Command
from pyctlmbatchtoolbox.common import *

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class ContextDeploy(Context):
    """Keep context of passed parameters"""
    action = 'GET'
    app = ''
    execute = False
    export_format_xml = False

    def print(self):
        Context.print(self)
        logging.info("print ===================C")
        logging.info(f'Action {self.action}')
        logging.info(f'App {self.app}')
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
        parser.add_argument('--action', dest='action', required=False, default=ctx.action, help=f"GET, GENERATE_SHELL_SCRIPT_CREATE_AACS_HOSTGROUP. Default is {ctx.action}")
        parser.add_argument('--app', dest='app', required=False, default=ctx.app, help=f"Application (name of the Control-M simple folder.")
        parser.add_argument('--export-format-xml', dest='export_format_xml', required=False, action="store_true", help=f"Export to XML format instead of Json.")
        args = parser.parse_args(sysargs)

        if args.controlm_user:
            ctx.ctm_user = args.controlm_user
        if args.controlm_password:
            ctx.ctm_pass = args.controlm_password

        ctx.ctm_server = args.controlm_server
        ctx.action = args.action
        ctx.app = args.app
        ctx.export_format_xml = args.export_format_xml

#        if ctx.action not in ['GET', 'GENERATE_SHELL_SCRIPT_CREATE_AACS_HOSTGROUP']:
#            logging.critical(f"Action {ctx.action} not implemented yet")
#            exit(1)
        ctx.print()
        ctx.validate()



    def main(self):
        from datetime import datetime

        self.parse_arguments(sys.argv[1:], self.ctx)
        Command.main(self, self.ctx)
        ctx = self.ctx

        print(f'Getting deploy from {ctx.ctm_rest} {ctx.ctm_server} {ctx.obe} (may take a while)')
        deploy = []
        if ctx.action in ['GENERATE_SHELL_SCRIPT_CREATE_AACS_HOSTGROUP','GET']:
            deploy = get_controlm_deploy(ctx.ctm_rest, ctx.token, ctx.ctm_server, ctx.obe, export_format_xml=ctx.export_format_xml)

        if ctx.action == 'GENERATE_SHELL_SCRIPT_CREATE_AACS_HOSTGROUP':
            hostgroups = []
            for folder in deploy:
                logging.debug(f'Folder {folder}')
                if is_standard_folder(folder):
                    logging.debug(f"Starting standard folder:{folder}")
                    app = folder.split('-')[0]
                    phase = folder.split('-')[1]
                    simpl_folder = deploy[folder]
                    for k in simpl_folder:
                        logging.debug(f'Key of the json: {k}')
                        job = simpl_folder[k]
                        if is_jobscript(job):
                            host = job['Host']
                            if host.lower().find(ctx.obe.lower()) == -1:
                                logging.warning(f'Host {host} does not belong to obe specified as parameter {ctx.obe}')
                            else:
                                ulam = get_obe_ulam_component_binary(job)
                                if ulam == None:
                                    logging.warning(f"Ulam component not found for job:{job}")
                                else:
                                    peak = get_peak_from_job(job)
                                    hostgroup = {'agent': host,
                                                 'hostgroup': f'{ctx.obe}{phase.upper()}{peak.upper()}{ulam.upper()}', # ex hostgroup: APKDEVPK1YLD
                                                 'phase': phase}
                                    if hostgroup not in hostgroups:
                                        hostgroups.append(hostgroup)
                else:
                    logging.warning(f'Folder is non standard {folder}')

            filename = f'creation-hostgroup-{ctx.ctm_server}-{ctx.obe}.sh'
            with open(filename, "w") as f:
                f.write(f'# shell script generated from {ctx.ctm_rest} {ctx.ctm_server} {ctx.obe} on {str(datetime.today())}\n')
                for h in hostgroups:
                    agent = h['agent']
                    hostgroup = h['hostgroup']
                    command = """curl -k -H "Authorization: Bearer $token" -H "Content-Type: application/json" -X POST -d  "{\\"host\\": \\"%s\\", \\"tag\\": \\"OBE\\" }" %s/config/server/%s/hostgroup/%s/agent \n""" \
                                                                                                                               % (agent,               ctx.ctm_rest,   ctx.ctm_server, hostgroup)
                    f.write(command)
            print(f'Filename {filename} created.')
        exit(0)

def main():
    logging.basicConfig(level=os.getenv('CTM_BATCH_LOG_LEVEL', CTM_BATCH_LOG_LEVEL_DEFAULT))
    command = CommandDeploy()
    command.main()
    exit(0)


if __name__ == '__main__':
    main()
    exit(0)

