# Cloud Foundry Auditing Scripts

This repository contains miscellaneous scripts that can be used to audit various aspects of Cloud Foundry from an organization, space, or application-level perspective. At this time, the following main features/scripts are supported:
| Feature/Script| Description |
| --- | ----------- |
| Buildpack inspector| Obtains the AS-IS buildpack information for applications your account has access to. This includes identifying (and color coding/flag) applications using out of date buildpacks.|
| Configuration inspector| Obtains the AS-IS Cloud Foundry organization, space, application, and service information that your account has access to. Pair this with a previous version of the output and it will allow you to see changes to your environment which can really help with auditing activities.|
| Application resource inspector| Obtains AS-IS application-level settings including organization, space, application name, number of application instances, memory, and diskspace. |

## Reason for its creation

As part of the auditing responsibilities under our security plan, we needed a way to easily access and continually reassess our Cloud Foundry organization, space, and application setup. The various outputs from these scripts can be used to compare against baseline configurations to monitor configuration drift.

## Initial goals

 - Make the code simple to understand to instill trust in its usage (one reason we use the CLI vs. the CF API directly)
 - Avoid using 3rd party dependencies if possible (i.e., focus on using base Python features).
 - Provide a solution that can be easily enhanced as time allows.
 - Initially develop it as quickly as possible as the functionality was needed ASAP. 
 
## Scripts

## Buildpack inspector

Obtains the AS-IS buildpack information for applications your account has access to. This includes identifying (and color coding/flag) applications using out of date buildpacks. 

Note: This script could easily be setup using a GitHub Action, etc. to continually report out on the current buildpack usage. For my initial usage, I just needed a way to get the buildpack information on demand.

**Example usage:**
python cf_buildpack_inspector.py --report_file=C:\Users\Cooper\Desktop\2021-05-01.xlsx --cf_api_endpoint=https://api.fr.cloud.gov

**command line parameters**
 - **organization** - (optional) The organization name to filter the results by.
 - **space** - (optional) The space name to filter the results by.
 - **report_file** - file path to where to save the MS Excel based results.
 - **cf_api_endpoint** - The endpoint of the Cloud Foundry API that you're assessing.

## Configuration inspector

Obtains the AS-IS Cloud Foundry organization, space, application, and service information that your account has access to. Pair this with a previous version of the output and it will allow you to see changes to your environment which can really help with auditing activities.

We suggest that you create another private GitHub (or similar) version control repository to store the exported information. This will allow you to easily inspect the changes between runs using your preferred version control comparison tool. 

**Example usage:**
tbd

**command line parameters**
 - **tbd** - tbd

## Application resource inspector

Obtains AS-IS application-level settings including organization, space, application name, number of application instances, memory, and diskspace.

**Example usage:**
python cf_application_resource_inspector.py

**command line parameters**
 - None at this time, it just displays what your account has access to. Please submit an issue if additional functionality is needed.

## Disclaimer

The software is provided "as is", without warranty of any kind, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose and noninfringement. In no event shall the authors or copyright holders be liable for any claim, damages, or other liability, whether in an action of contract, tort or otherwise, arising from, out of or in connection with the software or the use or other dealings in the software.