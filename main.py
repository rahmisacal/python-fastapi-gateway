from fastapi import FastAPI, Depends, params
from typing import Annotated
from dotenv import load_dotenv
from auth import get_current_username
import os
import requests
import urllib3
from ratelimit import limits
import xmltodict
import json

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
app = FastAPI()
load_dotenv()

def ovirt_get_token(cluster: str, username: Annotated[str, Depends(get_current_username)]):
    urlToken = "https://" + cluster + ".turkcell.tgc/ovirt-engine/sso/oauth/token"
    reqToken = requests.request("POST", urlToken, verify=False, data = os.getenv(cluster), headers={"Content-Type":"application/x-www-form-urlencoded", "Accept":"application/json", "Authorization":"Basic Og==", "Cookie":"locale=en_US"})
    print("INFO: " + username + " has called " + urlToken)
    return reqToken.json()["access_token"]

@limits(calls=15, period=300)
@app.get("/ovirt-engine-version")
async def ovirtApiVersion(cluster: str, username: Annotated[str, Depends(get_current_username)]):
    url = "https://" + cluster + ".turkcell.tgc/ovirt-engine/api/v4"
    access_token = ovirt_get_token(cluster, username)
    req = requests.get(url, verify=False, headers={'Authorization': 'Bearer ' + access_token})
    print("INFO: " + username + " has called " + url)
    xpars = xmltodict.parse(req.text)
    reqjson = json.dumps(xpars)
    data = json.loads(reqjson)["api"]["product_info"]
    temp = []
    outjson = {'cluster' : cluster,
               'name' : data['name'],
               'version' : data['version'],
    }
    temp.append(outjson)
    return temp

@limits(calls=15, period=300)
@app.get("/ovirt-engine-hosts")
async def ovirtApiHosts(cluster: str, username: Annotated[str, Depends(get_current_username)]):
    url = "https://" + cluster + ".turkcell.tgc/ovirt-engine/api/hosts"
    access_token = ovirt_get_token(cluster, username)
    req = requests.get(url, verify=False, headers={'Authorization': 'Bearer ' + access_token})
    print("INFO: " + username + " has called " + url)
    xpars = xmltodict.parse(req.text)
    reqjson = json.dumps(xpars)
    data = json.loads(reqjson)["hosts"]["host"]
    temp = []
    for i in data:
        outjson = {'address' : i['address'],
                   'status' : i['status'],
                   'memory' : i['memory'],
                   'cpu' : i['cpu'],
                   'hardware_information' : i['hardware_information'],
        }
        temp.append(outjson)
    return temp

@limits(calls=15, period=300)
@app.get("/ovirt-engine-events")
async def ovirtApiEvents(cluster: str, username: Annotated[str, Depends(get_current_username)]):
    url = "https://" + cluster + ".turkcell.tgc/ovirt-engine/api/events?max=250"
    access_token = ovirt_get_token(cluster, username)
    req = requests.get(url, verify=False, headers={'Authorization': 'Bearer ' + access_token})
    print("INFO: " + username + " has called " + url)
    xpars = xmltodict.parse(req.text)
    reqjson = json.dumps(xpars)
    data = json.loads(reqjson)["events"]["event"]
    temp = []
    for i in data:
        outjson = {'time' : i['time'],
                   'description' : i['description'],
        }
        temp.append(outjson)
    return temp

@limits(calls=15, period=300)
@app.get("/ovirt-engine-events-remove-vm")
async def ovirtApiEventsRemoveVM(cluster: str, username: Annotated[str, Depends(get_current_username)]):
    url = "https://" + cluster + ".turkcell.tgc/ovirt-engine/api/events?search=code%3D10"
    access_token = ovirt_get_token(cluster, username)
    req = requests.get(url, verify=False, headers={'Authorization': 'Bearer ' + access_token})
    print("INFO: " + username + " has called " + url)
    xpars = xmltodict.parse(req.text)
    reqjson = json.dumps(xpars)
    data = json.loads(reqjson)["events"]["event"]
    temp = []
    for i in data:
        outjson = {'time' : i['time'],
                   'description' : i['description'],
        }
        temp.append(outjson)
    return temp

@limits(calls=15, period=300)
@app.get("/ovirt-engine")
async def ovirtApi(cluster: str, path_prefix: str, username: Annotated[str, Depends(get_current_username)]):
    url = "https://" + cluster + ".turkcell.tgc/ovirt-engine/api/" + path_prefix
    access_token = ovirt_get_token(cluster, username)
    req = requests.get(url, verify=False, headers={'Authorization': 'Bearer ' + access_token})
    print("INFO: " + username + " has called " + url)
    xpars = xmltodict.parse(req.text)
    reqjson = json.dumps(xpars)
    return json.loads(reqjson)

@limits(calls=15, period=300)
@app.get("/ocp-engine")
async def ocpApi(cluster: str, path_prefix: str, username: Annotated[str, Depends(get_current_username)]):
    url = "https://api." + cluster + ".tcs.turkcell.tgc:6443/" + path_prefix
    req = requests.get(url, verify=False, headers={'Authorization': 'Bearer ' + os.getenv(cluster)})
#    print(json.dumps(req.json(), indent=4, sort_keys=True))
    print("INFO: " + username + " has called " + url)
    return req.json()["items"]

@limits(calls=15, period=300)
@app.get("/ocp-clusterversion")
async def ocpClusterVersion(cluster: str, username: Annotated[str, Depends(get_current_username)]):
    url = "https://api." + cluster + ".tcs.turkcell.tgc:6443/apis/config.openshift.io/v1/clusterversions"
    req = requests.get(url, verify=False, headers={'Authorization': 'Bearer ' + os.getenv(cluster)})     
    data = req.json()['items']
    temp = []
    for i in data:
        outjson = {'cluster' : cluster,
                   'version' : i['status']['desired']['version'],
                   'info' : i['status']['desired']['url'],
        }
        temp.append(outjson)
    print("INFO: " + username + " has called " + url)
    return temp

@limits(calls=15, period=300)
@app.get("/ocp-users")
async def ocpUsers(cluster: str, username: Annotated[str, Depends(get_current_username)]):
    url = "https://api." + cluster + ".tcs.turkcell.tgc:6443/apis/user.openshift.io/v1/users"
    req = requests.get(url, verify=False, headers={'Authorization': 'Bearer ' + os.getenv(cluster)})     
    data = req.json()['items']
    temp = []
    for i in data:
        outjson = {'name' : i['metadata']['name'],
                   'identities' : i['identities'][0],
                   'creationtime' : i['metadata']['creationTimestamp']
        }
        temp.append(outjson)
    print("INFO: " + username + " has called " + url)
    return temp

@limits(calls=15, period=300)
@app.get("/ocp-user-rolebindings")
async def ocpRolebindings(cluster: str, username: Annotated[str, Depends(get_current_username)]):
    temp = []
    nsUrl = "https://api." + cluster + ".tcs.turkcell.tgc:6443/api/v1/namespaces"
    nsReq = requests.get(nsUrl, verify=False, headers={'Authorization': 'Bearer ' + os.getenv(cluster)})
    nsData = nsReq.json()['items']
    for ns in nsData:
        print(ns['metadata']['name'])
        if "openshift" in ns['metadata']['name'] or "kube" in ns['metadata']['name'] or "default" in ns['metadata']['name'] or "istio-system" in ns['metadata']['name']:
            continue
        url = "https://api." + cluster + ".tcs.turkcell.tgc:6443/apis/rbac.authorization.k8s.io/v1/namespaces/" + ns['metadata']['name'] +"/rolebindings"
        req = requests.get(url, verify=False, headers={'Authorization': 'Bearer ' + os.getenv(cluster)})     
        data = req.json()['items'] 
        for i in data:
            subjects = i['subjects']
            usertemp = []         
            for j in subjects:
                if j['kind'] != 'User':
                    continue
                user = {'kind' : j['kind'],
                        'name' : j['name']
                }
                usertemp.append(user)
            if not usertemp:
                continue
            outjson = {'namespace' : i['metadata']['namespace'],
                    'role_kind' : i['roleRef']['kind'],
                    'role_name' : i['roleRef']['name'],
                    'rolbinding_name' : i['metadata']['name'],
                    'user' : usertemp
            }
            temp.append(outjson)
        print("INFO: " + username + " has called " + url)
    return temp    