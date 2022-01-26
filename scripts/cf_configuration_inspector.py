import sys
import subprocess
import os
import shutil
import json
import hashlib
from urllib.parse import unquote


######################################################################################################
# Globals setup and directory location initiation
######################################################################################################

start_path = os.getcwd()
os.chdir("..")
data_folder_path = os.getcwd() + "\\data"
end_point_version = '/v3/'
per_page = 5000

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


def run_cmd_suppress_output(cmd, args):
    subprocess.call([cmd, args], stdout=open(
        os.devnull, "w"), stderr=subprocess.STDOUT)
    return


def run_cli_cmd(cmd, filename):
    p1 = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    output = p1.communicate()[0]
    output2 = ""

    for line in output.splitlines():
        line = line.decode()
        if(line.endswith("...")) and " as " in line:
            index = line.find(" as ")
            line = line[:index] + " as 'USER INFOMATION REDACTED'..."
        output2 = output2 + line + "\n"

    f = open(filename + ".txt", "w")
    print(output2, file=f)
    f.close()
    return


def run_quota_cmd_api(url, cmd, filename):
    output = get_cf_response(url)
    try:
        # if this element exists, a subsequent page exists so get the new URL and continue iteration
        quota_url = output['links']['quota']['href']
        index = quota_url.find(end_point_version)
        quota_url = quota_url[index:]
        output = get_cf_response(quota_url)
        f = open(filename + ".json", "w")
        print(json.dumps(output, indent=4), file=f)
        f.close()
        quota_name = output["name"]
        run_cli_cmd(["cf", cmd, quota_name], filename)
    except:
        # break out of loop because this was the last page
        f = open(filename + ".json", "w")
        print('{ "message": "No quota set." }', file=f)
        f.close()
        f = open(filename + ".txt", "w")
        print("No quota set.", file=f)
        f.close()

    return


def run_api_cmd(url, filename):
    output = get_cf_response(url)
    f = open(filename + ".json", "w")
    print(json.dumps(output, indent=4), file=f)
    f.close()
    return


def run_api_cmd_resources(url, filename):
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

    f = open(filename + ".json", "w")
    print(json.dumps(all_data, indent=4), file=f)
    f.close()


def run_api_cmd_and_hash_output_txt(cmd, hash_statement, json_attrib, filename):
    p1 = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    output = p1.communicate()[0]
    json_data = json.loads(output)

    text = ""
    if "CF-NotAuthorized" in output.decode():
        text = "Not authorized to perform action around this action."
        hash_statement = text
        print(text + " " + '/'.join(cmd))
    elif json_attrib != None and json_attrib not in output.decode():
        text = "There is no " + json_attrib + " in the results of this action."
        hash_statement = text
    elif json_attrib == None:
        text = json_data
    else:
        text = json_data[json_attrib]

    hash_object = hashlib.md5(json.dumps(text).encode('utf-8'))
    f = open(filename + ".txt", "w")
    print(hash_statement + ": " + hash_object.hexdigest(), file=f)
    f.close()
    return

######################################################################################################
######################################################################################################


def obtain_cf_data_for_app(space_folder, org_name, space_name, space_guid, app_guid, app_name):
    print("")
    print("==================================================================")
    print("Obtaining apps data for app " + app_name)
    print("==================================================================")
    os.chdir(space_folder)
    cur_app_folder = space_folder + "\\apps\\" + app_name
    os.makedirs(cur_app_folder, exist_ok=True)
    os.chdir(cur_app_folder)

    # APP Details (avoiding anything about current memory usage to avoid false positives related to changes)
    run_api_cmd_resources("/v3/apps?per_page=" + str(per_page) + "&names=" +
                          app_name + "&space_guids=" + space_guid, "app-details")
    # Routes
    run_api_cmd_resources("/v3/apps/" + app_guid +
                          "/routes?order_by=created_at&per_page=" + str(per_page), "app-routes")
    # Processes
    run_api_cmd_resources("/v3/apps/" + app_guid +
                          "/processes?order_by=created_at&per_page=" + str(per_page), "app-processes")
    # Packages
    run_api_cmd_resources("/v3/apps/" + app_guid +
                          "/packages?order_by=created_at&per_page=" + str(per_page), "app-packages")
    # Tasks
    run_api_cmd_resources("/v3/apps/" + app_guid +
                          "/tasks?order_by=created_at&per_page=" + str(per_page), "app-tasks")
    # Droplets
    run_api_cmd("/v3/apps/" + app_guid +
                "/droplets/current?order_by=created_at&per_page=" + str(per_page), "app-droplets")
    # features
    run_api_cmd_resources("/v3/apps/" + app_guid +
                          "/features?order_by=created_at&per_page=" + str(per_page), "app-features")
    # Revisions
    run_api_cmd_resources("/v3/apps/" + app_guid +
                          "/revisions?order_by=created_at&per_page=" + str(per_page), "app-revisions")
    # Revisions Deployed
    run_api_cmd_resources("/v3/apps/" + app_guid +
                          "/revisions/deployed?order_by=created_at&per_page=" + str(per_page), "app-revisions-deployed")
    # enviroment variables
    hash_statement = "Hashed for security reasons"
    run_api_cmd_and_hash_output_txt(["cf", "curl", "/v3/apps/" + app_guid +
                                     "/environment_variables?order_by=name&per_page=" + str(per_page)], hash_statement, "var", "app-env-var")

    return

######################################################################################################
######################################################################################################


######################################################################################################
######################################################################################################
def obtain_cf_data_for_entire_space(org_folder, org_name, space_guid, space_name):
    print("")
    print("==================================================================")
    print("Obtaining space data for org: " +
          org_name + " space: " + space_name)
    print("==================================================================")
    os.system("cf target -o " + org_name + " -s " + space_name)
    os.chdir(org_folder)
    cur_space_folder = org_folder + "\\spaces\\" + space_name
    os.makedirs(cur_space_folder, exist_ok=True)
    os.chdir(cur_space_folder)

    # SPACE INFO
    run_cli_cmd(["cf", "space", space_name], "space")
    run_api_cmd(
        "/v3/spaces/" + space_guid, "space")
    run_api_cmd(
        "/v3/spaces/" + space_guid + "/features", "space-features")
    # QUOTAS
    run_quota_cmd_api(
        "/v3/spaces/" + space_guid, "space-quota", "space-quota")
    # SPACE-USERS
    run_cli_cmd(["cf", "space-users", org_name,
                 space_name], "space-users")
    # NETWORK POLICIES
    run_cli_cmd(["cf", "network-policies"], "network-policies")
    # APPS
    run_cli_cmd(["cf", "apps"], "apps")
    run_api_cmd_resources("/v3/apps?order_by=name&per_page=" + str(per_page) + "&space_guids=" +
                          space_guid, "apps")
    # SERVICES
    run_cli_cmd(["cf", "services"], "services")
    run_api_cmd_resources("/v3/service_instances?order_by=name&per_page=" + str(per_page) + "&space_guids=" +
                          space_guid, "service-instances")

    with open("apps.json") as json_data_file:
        data = json.load(json_data_file)
        for d in data["resources"]:
            obtain_cf_data_for_app(
                cur_space_folder, org_name, space_name, space_guid, d["guid"], d["name"])

    return
######################################################################################################
######################################################################################################


######################################################################################################
######################################################################################################
def obtain_cf_data_for_entire_org(org_guid, org_name):
    print("")
    print("==================================================================")
    print("Obtaining organization wide data for: " + org_name)
    print("==================================================================")
    os.system("cf target -o " + org_name)
    os.chdir(data_folder_path)
    cur_org_folder = data_folder_path + "\\orgs\\" + org_name
    os.makedirs(cur_org_folder, exist_ok=True)
    os.chdir(cur_org_folder)

    # ORG INFORMATION
    run_cli_cmd(["cf", "org", org_name], "org")
    run_api_cmd(
        "/v3/organizations/" + org_guid, "org")
    # ORG-USERS
    run_cli_cmd(["cf", "org-users", org_name], "org-users")
    # SPACES
    run_api_cmd_resources(
        "/v3/spaces?order_by=name&per_page=" + str(per_page) + "&organization_guids="+org_guid, "spaces")
    run_cli_cmd(["cf", "spaces"], "spaces")
    # QUOTAS
    run_cli_cmd(["cf", "space-quotas"], "space-quotas")
    run_api_cmd_resources(
        "/v3/space_quotas?order_by=created_at&per_page=" + str(per_page) + "&organization_guids="+org_guid, "space-quotas")
    run_quota_cmd_api(
        "/v3/organizations/" + org_guid, "org-quota", "org-quota")
    # DOMAINS
    run_cli_cmd(["cf", "domains"], "domains")
    run_api_cmd_resources(
        "/v3/domains?order_by=created_at&per_page=" + str(per_page) + "&organization_guids="+org_guid, "domains")

    with open("spaces.json") as json_data_file:
        data = json.load(json_data_file)
        for d in data["resources"]:
            obtain_cf_data_for_entire_space(
                cur_org_folder, org_name, d["guid"], d["name"])

    return
######################################################################################################
######################################################################################################


######################################################################################################
# Starting point for script logic
######################################################################################################
print("")
print("")
print("==================================================================")
print("Set things up.")
print("==================================================================")

if os.path.exists(data_folder_path):
    print("")
    print("Its recommended that you delete the data folder before continuning.")
    Fl = ''
    while True:
        print("")
        query = input('Should the data folder be deleted? ')
        Fl = query[0].lower()
        if query == '' or not Fl in ['y', 'n']:
            print('Please answer with y or n.')
        else:
            break

    if Fl == 'y':
        shutil.rmtree(data_folder_path)
        os.mkdir(data_folder_path)
else:
    os.mkdir(data_folder_path)

os.chdir(data_folder_path)

print("")
print("==================================================================")
print("Obtaining high-level subscription data")
print("==================================================================")

# Getting ORGS that user has access to
run_cli_cmd(["cf", "orgs"], "organizations")
run_api_cmd_resources("/v3/organizations?order_by=name&per_page=" + str(per_page),
                      "organizations")

# Platform Feature Flags
run_cli_cmd(["cf", "feature-flags"], "feature-flags")
run_api_cmd_resources("/v3/feature_flags?order_by=name&per_page=" + str(per_page),
                      "feature-flags")
# Platform Buildpacks
run_cli_cmd(["cf", "buildpacks"], "buildpacks")
run_api_cmd_resources("/v3/buildpacks?order_by=position&per_page=" + str(per_page),
                      "buildpacks")


with open("organizations.json") as json_data_file:
    data = json.load(json_data_file)
    for d in data["resources"]:
        obtain_cf_data_for_entire_org(d["guid"], d["name"])

print("")
print("")
print("==================================================================")
print("Script completed.")
print("==================================================================")
