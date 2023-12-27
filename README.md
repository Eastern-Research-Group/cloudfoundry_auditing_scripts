  

# Cloud Foundry Auditing Scripts

  

This repository contains miscellaneous scripts that can be used to audit various aspects of Cloud Foundry from an organization, space, or application-level perspective. At this time, the following main features/scripts are supported:

| Feature/Script| Description |
| --- | ----------- |
| Buildpack inspector| Obtains the AS-IS buildpack information for applications your account has access to. This includes identifying (and color coding/flag) applications using out of date buildpacks.|
| Configuration inspector| Obtains the AS-IS Cloud Foundry organization, space, application, and service information that your account has access to. Pair this with a previous version of the output and it will allow you to see changes to your environment which can really help with auditing activities. <br><br>Pair this with the results from our [Cloud Foundry Audit Events](https://github.com/Eastern-Research-Group/cloudfoundry_audit_events) script and you’ll obtain complete visibility into all the actions that took place from the baseline resulting in the latest configuration.|
| Application resource inspector| Obtains AS-IS application-level settings including organization, space, application name, number of application instances, memory, and diskspace. |
| Service account key check| Obtains AS-IS information about service keys (e.g., last update date) to help teams determine if keys need to be rotated (i.e. 60 or 90 day policy). |
| Log Drain service check| Identify applications that have a log drain service bound to them.  This script enables you to perform regular audits against your Cloud Foundry environment to ensure applications are configured to drain information to an external logging endpoint (e.g., Splunk). Typically to meet M-21-31 requirements. |

## Reason for its creation

  

As part of the auditing responsibilities under our security plan, we needed a way to easily assess and then continually reassess our Cloud Foundry organization, space, and application setup. The various outputs from these scripts can be used to compare against baseline configurations, monitor configuration drift, and check policy compliance (e.g., service key rotation taking place, applications configured to drain to external endpoint, etc.).

  

## Initial goals

  

- Make the code simple to understand to instill trust in its usage (one reason we use the CLI vs. the CF API directly)

- Avoid using 3rd party dependencies if possible (i.e., focus on using base Python features).

- Provide a solution that can be easily enhanced as time allows.

- Initially develop it as quickly as possible as the functionality was needed ASAP.

## Scripts

  

---

## Buildpack inspector

  

Obtains the AS-IS buildpack information for applications your account has access to. This includes identifying (and color coding/flag) applications using out of date buildpacks.

  

Note: This script could easily be setup using a GitHub Action, etc. to continually report out on the current buildpack usage. For my initial usage, I just needed a way to get the buildpack information on demand.

  

**Example usage:**

python cf_buildpack_inspector.py --report_file=C:\Users\Cooper\Desktop\2021-05-01.xlsx --cf_api_endpoint=https://api.fr.cloud.gov

  

**command line parameters**

-  **organization** - (optional) The organization name to filter the results by.

-  **space** - (optional) The space name to filter the results by.

-  **report_file** - file path to where to save the MS Excel based results.

-  **cf_api_endpoint** - The endpoint of the Cloud Foundry API that you're assessing.

  

---

## Configuration inspector

  

Obtains the AS-IS Cloud Foundry organization, space, application, and service information that your account has access to. Pair this with a previous version of the output and it will allow you to see changes to your environment which can really help with auditing activities.

  

Pair this with the results from our [Cloud Foundry Audit Events](https://github.com/Eastern-Research-Group/cloudfoundry_audit_events) script and you’ll obtain complete visibility into all the actions that took place from the baseline resulting in the latest configuration.

  

We suggest that you create another private GitHub (or similar) version control repository to store the exported information. This will allow you to easily inspect the changes between runs using your preferred version control comparison tool.

  

The script attempts to remove any sensitive information (user account running the script and environmental values (hashes its key/value pairs)). This makes comparing the baseline against the new run less noisy. In addition, data is saved in JSON (from the CF API) and TEXT (from the CLI) formats for completeness. When I do my auditing, I typically only review the .txt files for changes and if there is something off, I then look at the .json files and also the audit events from [Cloud Foundry Audit Events](https://github.com/Eastern-Research-Group/cloudfoundry_audit_events) script. The main difference, the .txt files don’t contain values that frequently change (e.g., timestamps from routine restage events, etc.) which can be rather noisy when trying to identify changes.

  

**Example usage:**

python cf_configuration_inspector.py --data_folder=C:\Cooper\cf_test_org\data --remove_data_folder=true

  

**command line parameters**

-  **data_folder** - file path to where to save the extracted Cloud Foundry configuration information.

-  **remove_data_folder** - Whether the existing **data_folder** location should be removed before running. This can help with auditing as it will show which files were deleted vs. just modified after the run.

  

---

## Application resource inspector

  

Obtains AS-IS application-level settings including organization, space, application name, number of application instances, memory, and diskspace.

  

**Example usage:**

python cf_application_resource_inspector.py

  

**command line parameters**

- None at this time, it just displays what your account has access to. Please submit an issue if additional functionality is needed.

---

## Service account key check

  

Obtains AS-IS information about service keys (e.g., last update date) to help teams determine if keys need to be rotated (i.e. 60 or 90 day policy).

  

**Example usage:**

python cf_service_account_key_check.py --cf_api_endpoint=https://api.fr.cloud.gov --report_file=C:\Users\BCooper\Desktop\service_key_check.xlsx --binding_type=key

  

**command line parameters**

-  **cf_api_endpoint** - Cloud Foundry API endpoint location.

-  **report_file** - Local path and filename output should be saved to.

-  **binding_type** - Values {app or key} or just don't use this parameter. Cloud Foundry applications and service_accounts bind to services, this allows you to filter which ones get included into the report_file.

---
  
## Log Drain check

 Identify applications that have a log drain service bound to them.  This script enables you to perform regular audits against your Cloud Foundry environment to ensure applications are configured to drain information to an external logging endpoint (e.g., Splunk). Typically to meet M-21-31 requirements.

**Example usage:**

python cf_log_drain_check.py --log_drain_url="syslog-tls://splunk.erg.com:1234" --report_file="C:\Users\BCooper\Desktop\2024-01-Log_drain_check.xlsx"

  
**command line parameters**

-  **log_drain_url** - The full URL/hyperlink (with protocol and port) to external drain service. This should match the URL/hyperlink used when your log drain service was configured.

-  **report_file** - Local path and filename output should be saved to.


---

## Disclaimer

  

The software is provided "as is", without warranty of any kind, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose and noninfringement. In no event shall the authors or copyright holders be liable for any claim, damages, or other liability, whether in an action of contract, tort or otherwise, arising from, out of or in connection with the software or the use or other dealings in the software.
