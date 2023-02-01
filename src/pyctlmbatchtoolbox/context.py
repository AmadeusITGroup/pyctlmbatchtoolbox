import logging

import os

class Context:
    """Keep context of passed parameters"""
    ctm_user = os.getenv('CTM_USER', None)
    ctm_pass = os.getenv('CTM_PASS', None)
    ctm_rest = os.getenv('CTM_REST_API', None)
    ctm_server = ''
    token = ''
    log_level = os.getenv('CTM_BATCH_LOG_LEVEL','INFO')


    def print(self):
        logging.info('Arguments parsed:')
        logging.info(f'User {self.ctm_user}')
        logging.info(f'Rest api {self.ctm_rest}')
        logging.info(f'Ctm server {self.ctm_server}')

    def validate(self):
        is_everything_ok = True
        if self.ctm_rest == None:
            logging.critical(f'Control M REST end point cant be None. Set it with CTM_REST_API')
            is_everything_ok = False
        if self.ctm_user == None:
            logging.critical(f'Control-M user cant be None. You can set it as command line option (see --help) or through environment variable CTM_USER')
            is_everything_ok = False
        if self.ctm_pass == None:
            logging.critical(f'Control-M pass cant be None. You can set it as command line option (see --help) or through environment variable CTM_USER')
            is_everything_ok = False
        if is_everything_ok == False:
            exit(1)
