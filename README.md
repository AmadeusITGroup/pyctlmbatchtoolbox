
# Description
`pyctlmbatchtoolbox` is command line wrapper around [Control-M REST API](https://docs.bmc.com/docs/automation-api/918/services-783053199.html#Services-TopIntroduction). The goal is to provide a developer friendly 
command line tool easy to integrate with other tools.

# Install
```
pip install pyctlmbatchtoolbox --upgrade
```

# SRE toolbox included
Most of the tools include list/add/delete operations.

Tools included:
* batch_condition
* batch_conditionprofile
* batch_deploy
* batch_hostgroup
* batch_logs
* batch_status
* batch_token
* batch_order
```commandline
export CTM_USER=user
export CTM_PASS=***
export CTM_REST_API=https://<<controlm server instance>>:8443/automation-api
export CTM_BATCH_LOG_LEVEL=INFO

batch_order --controlm-server CTMSERVER --folder folder  
batch_logs --jobname JOBID 
batch_logs  --jobname JOBID
batch_condition --action GET --search-criteria 'name=*&server=CTMSERVER' 
batch_hostgroup --controlm-server CTMSERVER 
batch_hostgroup --controlm-server CTMSERVER --hostgroup HOSTGROUP1
```

