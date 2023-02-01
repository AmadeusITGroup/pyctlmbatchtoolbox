from pyctlmbatchtoolbox.common import *
import logging

class Command():
    description = HELP_STRING_COMMON + get_env_var_str()

    def main(self, ctx):
        logging.info(f"Current dir {os.getcwd()}")
        ctx.token = get_controlm_token(ctx.ctm_rest, ctx.ctm_user, ctx.ctm_pass)
        logging.debug(f'Authen token retrieved: {ctx.token[0:5]}xxxx ')
