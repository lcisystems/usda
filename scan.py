import requests
import json
from jinja2 import Environment, BaseLoader

APIKEY='hawk.oQpIhNOxvte4q0uHvE4k.MXciFrmNUU4dip28SxkY'
ORGID = 'a8c24fcd-733d-4026-bbda-0ad30250da45'


def get_scan_result():
    
    url = "https://api.stackhawk.com/api/v1/auth/login"
    headers = {
        "accept": "application/json",
        "X-ApiKey": APIKEY
    }
    response = requests.get(url, headers=headers)
    token = json.loads(response.text)
    auth_token =  token['token']
    url = f"https://api.stackhawk.com/api/v1/app/{ORGID}/list"
    headers = {
        "accept": "application/json",
        "authorization": f"Bearer {auth_token}"
    }

    response = requests.get(url, headers=headers)
    data = json.loads(response.text)
    app_id = data['applications'][0]['applicationId']
    print(app_id)
    url = f"https://api.stackhawk.com/api/v1/scan/{ORGID}?appIds={app_id}&start=0&end=0&pageSize=10&pageToken=0&sortField=id&sortDir=desc"
    headers = {
        "accept": "application/json",
        "authorization": f"Bearer {auth_token}"
    }
    response = requests.get(url, headers=headers)
    scan_id_data = json.loads(response.text)
    scan_id = scan_id_data['applicationScanResults'][0]['scan']['id']
    url = f"https://api.stackhawk.com/api/v1/scan/{scan_id}/alerts"
    headers = {
        "accept": "application/json",
        "authorization": f"Bearer {auth_token}"
    }
    response = requests.get(url, headers=headers)
    
    json_data = json.loads(response.text)
    print(json_data)
    

    return json_data

    




def create_scan_document(json_data):
    
    template_str = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Application Scan Results</title>
        <style>
            body { font-family: Arial, sans-serif; }
            table { width: 100%; border-collapse: collapse; }
            th, td { padding: 8px; text-align: left; border-bottom: 1px solid #ddd; }
            th { background-color: #f2f2f2; }
            tr:hover { background-color: #f5f5f5; }
            ul, li { list-style-type: none; padding: 0; margin: 0; }
        </style>
    </head>
    <body>
        <h1>Application Scan Results</h1>
        {% for result in applicationScanResults %}
            <h2>Scan ID: {{ result.scan.id }}</h2> 
            <h2> Application Name {{ result.scan.applicationName }}</h2> 
            <h2> Environment {{ result.scan.env }}</h2> 
            <h2>({{ result.scan.status }})</h2>
            <p>Scan Duration: {{ result.scanDuration }} seconds</p>
            <p>URL Count: {{ result.urlCount }}</p>
            <p>URL Count: {{ result.urlCount }}</p>
            <p>Total Alerts: {{ result.alertStats.totalAlerts }}</p>
            
            <h3>Alert Statistics</h3>
            <p>Total Alerts: {{ result.alertStats.totalAlerts }}</p>
            <p>Unique Alerts: {{ result.alertStats.uniqueAlerts }}</p>
            <table>
                <thead>
                    <tr>
                        <th>Alert Status</th>
                        <th>Total Count</th>
                        <th>Severity: Low</th>
                        <th>Severity: Medium</th>
                    </tr>
                </thead>
                <tbody>
                    {% for status in result.alertStats.alertStatusStats %}
                    <tr>
                        <td>{{ status.alertStatus }}</td>
                        <td>{{ status.totalCount }}</td>
                        <td>{{ status.severityStats.Low }}</td>
                        <td>{{ status.severityStats.Medium }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
            <br><br/>
            <h3>Application Alerts</h3>
            <table>
                <thead>
                    <tr>
                        <th>Plugin ID</th>
                        <th>Name</th>
                        <th>Description</th>
                        <th>Severity</th>
                        <th>References</th>
                        <th>URI Count</th>
                        <th>CWE ID</th>
                    </tr>
                </thead>
                <tbody>
                    {% for alert in result.applicationAlerts %}
                    <tr>
                        <td>{{ alert.pluginId }}</td>
                        <td>{{ alert.name }}</td>
                        <td>{{ alert.description | striptags }}</td>
                        <td>{{ alert.severity }}</td>
                        <td>
                            <ul>
                                {% for ref in alert.references %}
                                <li><a href="{{ ref }}">{{ ref }}</a></li>
                                {% endfor %}
                            </ul>
                        </td>
                        <td>{{ alert.uriCount }}</td>
                        <td>{{ alert.cweId }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        {% endfor %}
    </body>
    </html>
    """

    # Create

    # Create a Jinja2 environment and compile the template
    env = Environment(loader=BaseLoader())
    template = env.from_string(template_str)

    # Render the template with JSON data
    html_output = template.render(applicationScanResults=json_data['applicationScanResults'])

    # The HTML output is ready to be saved to an HTML file or displayed as needed
    print(html_output)

    # The HTML output is ready to be saved to an HTML file or displayed as needed
    print(html_output)

    output_file_path = 'reports/scan_result.html'

    with open(output_file_path, 'x') as file:
        # Write the Scans DataFrame
        file.write(html_output)
        file.close()
 
create_scan_document(get_scan_result())
