import subprocess
import os
import json
import hashlib

start_path = os.getcwd()
per_page = 5000
end_point_version = '/v3/'

######################################################################################################
# Generic command line functions.
######################################################################################################


def get_cf_response(url):
    if os.name == 'nt':
        # Need to escape the URL ampersands when running on Windows
        url = url.replace('&', '^&')
        p = subprocess.Popen(['cf.exe', 'curl', url],
                             stdout=subprocess.PIPE, shell=True)
    else:
        p = subprocess.Popen(['cf', 'curl', url], stdout=subprocess.PIPE)

    if p.returncode == 1:
        print("Can't find the CF CLI executable, is it installed?")
        sys.exit(1)

    output = p.communicate()[0]
    data = json.loads(output.decode('utf-8'))
    return data


def run_api_cmd_resources(url):
    all_data = {'resources': []}
    next_page = True

    while next_page:
        data = get_cf_response(url)
        for resource in data['resources']:
            all_data['resources'].append(resource)

        try:
            # if this element exists, a subsequent page exists so get the new URL and continue iteration
            url = data['pagination']['next']['href']
            index = url.find(end_point_version)
            url = url[index:]
        except:
            # break out of loop because this was the last page
            next_page = False

    return all_data


######################################################################################################
######################################################################################################
def obtain_cf_data_for_app(org_name, space_name, space_guid, app_guid, app_name):
    appjson = run_api_cmd_resources("/v3/apps/" + app_guid + "/processes")

    for d in appjson["resources"]:
        print(org_name + "," + space_name + "," + app_name + "," +
              str(d["instances"]) + "," + str(d["memory_in_mb"]) + "," + str(d["disk_in_mb"]))
    return

######################################################################################################
######################################################################################################


######################################################################################################
######################################################################################################
def obtain_cf_data_for_entire_space(org_name, space_guid, space_name):
    appsjson = run_api_cmd_resources(
        "/v3/apps?order_by=name&per_page=" + str(per_page) + "&space_guids="+space_guid)

    for d in appsjson["resources"]:
        obtain_cf_data_for_app(org_name, space_name,
                               space_guid, d["guid"], d["name"])

    return
######################################################################################################
######################################################################################################


######################################################################################################
######################################################################################################
def obtain_cf_data_for_entire_org(org_guid, org_name):
    spacesjson = run_api_cmd_resources(
        "/v3/spaces?order_by=name&per_page=" + str(per_page) + "&organization_guids="+org_guid)

    for d in spacesjson["resources"]:
        obtain_cf_data_for_entire_space(org_name, d["guid"], d["name"])

    return
######################################################################################################
######################################################################################################


######################################################################################################
# Starting point for script logic
######################################################################################################
print("")
print("")
print("==================================================================")
print("org name, space name, app name, instances, memory_in_mb, disk_in_mb")

orgjson = run_api_cmd_resources(
    "/v3/organizations?order_by=name&per_page=" + str(per_page) + "")

for d in orgjson["resources"]:
    obtain_cf_data_for_entire_org(d["guid"], d["name"])
