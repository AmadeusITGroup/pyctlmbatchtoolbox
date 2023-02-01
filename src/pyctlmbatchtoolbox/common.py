#!/usr/bin/env python3
import time

import requests
import logging
import os
import urllib3
import datetime

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
CTM_BATCH_LOG_LEVEL_DEFAULT='DEBUG'
HELP_STRING_COMMON = """
Log level can be set with env var CTM_BATCH_LOG_LEVEL (DEBUG, INFO, WARNING, ERROR, CRITICAL).
Control-M user and password can be specified in CTM_USER and CTM_PASS.
Control-M REST API endpoint must be set with CTM_REST_API.
To ignore SSL certificates (ex: local dev) set CTM_SSL_VERIFY=False
"""

ssl_verify = os.getenv('CTM_SSL_VERIFY',"TRUE").lower() == "true" # if not set -> TRUE. If set to TRUE -> TRUE. Else -> False

def check_arg_not_none(arg, string):
    if arg == None:
        logging.error(f'The setting {string} is needed. You can specify it on command line (see --help) or through environment variable "{string}"')
        exit(1)

def is_jobscript(content):
    type = 'Type'
    if type in content and (content[type] in ['Job:Script', 'Job:Command']):
            return True
    return False

def is_shell_command(arguments_list):
    if len(arguments_list)<4:
        return False
    if arguments_list[3] in ['/bin/', '/usr/bin/', '/', '/ama/CTLM/scripts/'] :
        return True
    return False

def get_env_var_str():
    """
    Return an string with the enviroments variables that can be used to customize the tool.
    """
    return f"""Env vars:
    CTM_BATCH_LOG_LEVEL={os.getenv('CTM_BATCH_LOG_LEVEL')}
    CTM_REST_API={os.getenv('CTM_REST_API')}
    CTM_USER={os.getenv('CTM_USER')}
    CTM_PASS=xxx (get from $CTM_PASS)
    CTM_SSL_VERIFY={os.getenv('CTM_SSL_VERIFY')}"""


def execute_request(method, url, headers, payload=None, verify=True, hide_log_payload=False):
    if method == 'POST':
        response = requests.post(url, headers=headers, data=payload, verify=ssl_verify)
    elif method == 'GET':
        response = requests.get(url, headers=headers, data=payload, verify=ssl_verify)
    elif method == 'DELETE':
        response = requests.delete(url, headers=headers, data=payload, verify=ssl_verify)
    else:
        raise Exception(f"Method {method} not supported")

    if response.status_code not in range(200, 299):
        logging.critical('Error requests 2')
        logging.error(get_env_var_str())
        logging.debug(url)
        logging.debug(response)
        logging.critical(response.text)
        if hide_log_payload==True:
            payload='xxxx'
        raise Exception(f"Status not expected! url={url} headers={headers} payload={payload} verify_ssl={verify}")
    else:
        return response

def get_controlm_token(url=None, user=None, password=None):
    """
    Returns an authenticated token from given user and password.
    """
    # curl -k -H "Content-Type: application/json" -X POST -d "${credentials}" "$controlm_rest/session/login"
    if url == None:
        url = os.getenv('CTM_REST_API',None)
        if url == None:
            logging.error(f'Url can not be None. Set the control M REST API endpoint through environment variable CTM_REST_API')
            exit(1)

    if user == None:
        user = os.getenv('CTM_USER', None)
        if user == None:
            logging.critical("User not found CTM_USER")
            exit(1)

    if password == None:
        password = os.getenv('CTM_PASS', None)
        if password == None:
            logging.critical("Pass not found")
            exit(1)

    url = url + '/session/login'
    payload = '{"username":"%s", "password":"%s" }' % (user, password)
    headers = {'Content-Type': 'application/json'}
    try:
      response = execute_request('POST',url=url, headers=headers, payload=payload, verify=ssl_verify, hide_log_payload=True)
    except:
      logging.critical('Error requests while login')
      logging.error(get_env_var_str())
      logging.debug(url)
      logging.critical('Login failed.')
      exit(1)

    token = response.json().get('token')
    return token

def order_folder_job(url, token, ctm_server, jobfolder, job=None):
    """
    Trigger a job of a folder.

    BMC documentation in https://docs.bmc.com/docs/automation-api/918/services-783053199.html#Services-runorder
    Curl:
    ```
    runId=$(curl -k -X POST -H "Authorization: Bearer $token" --header "Content-Type: application/json"
    --header "Accept: application/json" -d "{\"ctm\": \"${CONTROLM_SERVER}\",\"folder\": \"${CONTROLM_FOLDER}\"}"
    "$controlm_rest/run/order" | jq --raw-output '.runId' )
    ```
    """
    url = url + '/run/order'

    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json', 'Accept-Type': 'application/json'}
    if job == None:
        payload = """{"ctm":"%s", "folder":"%s"}""" % (ctm_server, jobfolder)
    else:
        payload = """{"ctm":"%s", "folder":"%s", "jobs":"%s"}""" % (ctm_server, jobfolder, job)
    response = execute_request('POST',url=url, headers=headers, payload=payload, verify=ssl_verify)
    runId = response.json().get('runId')
    return runId

def get_folder_status(url, token, runid):
    """
    Return the status of the run.
    BMC documentation in https://docs.bmc.com/docs/automation-api/918/services-783053199.html#Services-runstatus
    Curl:
    ```
    curl -k -H "Authorization: Bearer $token" "$controlm_rest/run/status/$runId"
    ```
    """
    url = url + f'/run/status/{runid}'

    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json', 'Accept-Type': 'application/json'}
    response = execute_request('GET',url=url, headers=headers, verify=ssl_verify)
    status = response.json()
    return status

def kill_jobid(url, token, jobid):
    """
    Kill a running job.
    BMC documentation: https://docs.bmc.com/docs/automation-api/918/services-783053199.html#Services-runjob::kill
    Curl:
    ```
    curl -H "Authorization: Bearer $token" -X POST "$endpoint/run/job/$jobId/kill"
    ```
    """
    logging.debug(f'Kill job:{jobid}')
    url = url + f'/run/job/{jobid}/kill'
    headers = {'Authorization': f'Bearer {token}'}
    response = execute_request('POST',url=url, headers=headers, verify=ssl_verify)
    res = response.json()
    return res

def create_condition(url, token, server, condition):
    """
    Create a condition.

    BMC documentation: https://docs.bmc.com/docs/automation-api/918/services-783053199.html#Services-event_managementEventManagement
    Curl:
    ```
    curl -H "Authorization: Bearer $token" -H "Content-Type: application/json"
        -X POST -d "{\"name\": \"newEvent\",\"date\":\"STAT\"}"
        "$controlm_rest/run/event/CTMSRV1P"
    ```
    """
    logging.debug(f'Set condition server:{server} condition:{condition}')
    url = url + f'/run/event/{server}'
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    payload = '{"name":"%s", "date":"STAT"}' % (condition)
    try:
        response = execute_request('POST',url=url, headers=headers, payload=payload, verify=ssl_verify)
        res = response.json()
    except:
        raise Exception(f"Error while creatig condition! url={url} headers={headers} payload={payload} verify_ssl={verify}")
    return res

def delete_condition(url, token, server, condition):
    """
    Delete a condition.

    BMC documentation: https://docs.bmc.com/docs/automation-api/9020100/run-service-990112953.html#Runservice-runeventdeleterunevent::delete

    Curl:
    ```
    curl -H "Authorization: Bearer $token" -X DELETE "$endpoint/run/event/$server/$name/$date"
    ```
    """
    logging.debug(f'Set condition server:{server} condition:{condition}')
    url = url + f'/run/event/{server}/{condition}/STAT'
    headers = {'Authorization': f'Bearer {token}'}
    response = execute_request('DELETE',url=url, headers=headers, verify=ssl_verify)
    res = response.json()
    return res

def get_conditions(url, token, search_criteria):
    """
    Retrieve conditions.

    BMC documentation: https://docs.bmc.com/docs/automation-api/9020100/run-service-990112953.html#Runservice-runevents::get

    Curl:
    ```
    curl -H "Authorization: Bearer $token" -X GET "$endpoint/run/events?$search_criteria"
    search_criteria="name=A*&server=controlm"
    ```
    """
    logging.info(f'Search criteria ->{search_criteria}<-')
    url = url + f'/run/events?{search_criteria}'
    headers = {'Authorization': f'Bearer {token}'}
    response = execute_request('GET',url=url, headers=headers, verify=ssl_verify)
    res = response.json()
    return res

def get_connection_profiles(url, token, server, agent, type):
    """
    BMC documentation: https://docs.bmc.com/docs/automation-api/9020100/deploy-service-990112951.html#Deployservice-deploy_cp_local_getdeployconnectionprofiles:local::get

    Curl:
    ```
    curl -k -X GET -H "Authorization: Bearer $t"
    https://<<control-m server>>:8443/automation-api/deploy/connectionprofiles/local?ctm=CTMSRV1P&agent=agentid&type=FileTransfer"
    ```
    """
    logging.info(f'Get connection profiles: server {server} agent {agent} type {type}')
    url = url + f'/deploy/connectionprofiles/local?ctm={server}&agent={agent}&type={type}'
    headers = {'Authorization': f'Bearer {token}'}
    response = execute_request('GET',url=url, headers=headers, verify=ssl_verify)
    res = response.json()
    return res

def get_controlm_deploy(url, token, server, folder=None, export_format_xml=False):
    """
    Returns the list of folders, with all jobs inside.

    BMC Documentation: https://docs.bmc.com/docs/automation-api/9020100/deploy-service-990112951.html#Deployservice-deployJobsGetdeployjobs::get
    Curl:
    """
    if folder == None:
        url += f'/deploy/jobs?&ctm={server}&folder=*'
        folder = 'all'
    else:
        url = url + f'/deploy/jobs?&ctm={server}&folder={folder}*'

    if export_format_xml:
        url += '&format=XML'

    headers = {'Authorization': f'Bearer {token}'}
    response = execute_request('GET', url=url, headers=headers, verify=ssl_verify)
    return response.text

def register_agent(url, token, server, agentid, hostgroup, condition=None):
    """
    BMC documentation: https://docs.bmc.com/docs/automation-api/9020100/config-service-990112957.html#Configservice-hostgroup_agents_getconfigserver:hostgroup:agents::get

    Curl:
    ```
    curl -H "Authorization: Bearer $token" -H "Content-Type: application/json"
         -X POST -d  "{\"host\":  \"agent-logical-id\",  \"hostgroupAgentParticipation\":{ \"event\": \"agent3Cond\", \"orderDate\": \"AnyDate\"}}" "
         $controlm_rest/config/server/MUCCT4T/hostgroup/APKDEVPK1GRP/agent"
    ```
    """
    url += f'/config/server/{server}/hostgroup/{hostgroup}/agent'
    headers = {'Authorization': f'Bearer {token}', 'Content-Type':'application/json'}
    if condition is None:
        payload = '{"host":"%s", "orderData":"AnyDate"}' % (agentid)
    else:
        payload = '{"host":"%s", "hostgroupAgentParticipation": { "event": "%s", "orderDate":"AnyDate"} }' % (agentid, condition)

    response = execute_request('POST',url=url, headers=headers, payload=payload, verify=ssl_verify)
    logging.debug(response.status_code)
    return True

def unregister_agent(url, token, server, agentid, hostgroup):
    """
    BMC Documentation: https://docs.bmc.com/docs/automation-api/9020100/config-service-990112957.html#Configservice-configserver:hostgroup:agent::delete
    Curl:
    ```
    curl -k -H "Authorization: Bearer $token" -X DELETE "$controlm_rest/config/server/CTMSRV1/hostgroup/HOSTGROUP/agent/agent-logical-id-2"
    ```
    """
    url += f'/config/server/{server}/hostgroup/{hostgroup}/agent/{agentid}'
    headers = {'Authorization': f'Bearer {token}'}
    response = execute_request('DELETE',url=url, headers=headers, verify=ssl_verify)
    return True

def get_controlm_hostgroups(url, token, server):
    """
    BMC Documentation: https://docs.bmc.com/docs/automation-api/9020100/config-service-990112957.html#Configservice-configserver:hostgroups::get
    Curl:
    ```
    curl -H "Authorization: Bearer $token" "$endpoint/config/server/$server/hostgroups"
    ```
    """
    url += f'/config/server/{server}/hostgroups'
    headers = {'Authorization': f'Bearer {token}'}
    response = execute_request('GET',url=url, headers=headers, verify=ssl_verify)
    return response.json()

def get_agents_in_hostgroups(url, token, server, group):
    """
    BMC Documentation: https://docs.bmc.com/docs/automation-api/9020100/config-service-990112957.html#Configservice-hostgroup_agents_getconfigserver:hostgroup:agents::get
    Curl:
    ```
    curl -H "Authorization: Bearer $token" "$endpoint/config/server/$server/hostgroup/$hostgroup/agents"
    ```
    """
    url += f'/config/server/{server}/hostgroup/{group}/agents'
    headers = {'Authorization': f'Bearer {token}'}
    response = execute_request('GET',url=url, headers=headers, verify=ssl_verify)
    return response.json()



def get_job_last_status(url, token, jobname, limit):
    """
    BMC Documentation: https://docs.bmc.com/docs/automation-api/9020100/run-service-990112953.html#Runservice-run_jobs_status_getrunjobs:status::get
    Curl:
    ```
    curl -k -H "Authorization: Bearer xx " 'https://<<control-m server>>>:8443/automation-api/run/jobs/status?jobname=JOBID&limit=1'
    ```
    """
    url += f'/run/jobs/status?jobname={jobname}&limit={limit}'
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json', 'Accept-Type': 'application/json'}
    response = execute_request('GET',url=url, headers=headers, verify=ssl_verify)
    json = response.json()
    return json

def get_job_agent_status(url, token, status=None, agentid=None):
    """
    BMC Documentation: https://docs.bmc.com/docs/automation-api/9020100/run-service-990112953.html#Runservice-run_jobs_status_getrunjobs:status::get
    Curl:
    ```
    curl -k -H "Authorization: Bearer xx " 'https://<<control-m server>>:8443/automation-api/run/jobs/status?status=Executing&host=AGENT'
    ```
    """
    url += f'/run/jobs/status'
    first = True
    if status != None:
        first = False
        url = url + f'?status={status}'
    if agentid != None:
        if first:
            url += '?'
            first = False
        else:
            url += '&'
        url += f'host={agentid}'

    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json', 'Accept-Type': 'application/json'}
    response = execute_request('GET',url=url, headers=headers, verify=ssl_verify)
    json = response.json()
    return json

def get_log_or_output(url, token):
    """
    Retrieve the logs or output from an URL.
    """
    headers = {'Authorization': f'Bearer {token}'}
    try:
        response = execute_request('GET',url=url, headers=headers, verify=ssl_verify)
    except:
        logging.info(f"I couldn't find the log or ouput from url={url}")
        return None
    text = response.text
    logging.debug(text)
    return text