from re import search, IGNORECASE
from SSHLibrary import SSHLibrary
import json
import platform, os, sys
import time
import netifaces

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
print("4")
print(BASE_DIR)
print(sys.path.append(BASE_DIR))
from auto_loader import load_from_file

import logging
logging.basicConfig(level=logging.INFO)


class dcs(object):
    def __init__(self, ipv6="", vmInterface="", user="", userpwd=""):
        """
	Constructor method to RestAppliance.
        We compute the correct API-Version for REST calls.
		
        Parameters
        ----------
        ipv6 : str
            Ipv6 of the dcs vm to connect. 
	vmInterface: str
		Interface of the ubuntu VM. 
                IPv6 address starts with fe80:: i.e. it's a link-local address, reachable only in the network segment it's directly connected to.
                Using the NIC that connects to that segment specifically.
	user: str
		Username of the DCS VM name
	userpwd: str
		DCS VM password
        """
        # builds endpoint
        self.ipv6Endpoint = ipv6 + "%" + vmInterface

        self.sshlib = SSHLibrary()
        self.stdout = None
        self.sshlib.open_connection(self.ipv6Endpoint)
        self.sshlib.login(username=user, password=userpwd)

        # sets API version
        self.api_version = self.get_api_version()
        logging.debug("The API Version utilized is {0}.".format(
            self.api_version))
        print(self.api_version)

        # header information
        self._header = "-H \"X-API-Version: {0}\" -H \"Content-Type: application/json\"".format(
            self.api_version)
        self._secure_header = None

    def get_api_version(self):
        """
        Helper method get_api_version
        Gets latest API verisons supported from the appliance.
        On failure, sets api_verison to 120

        Parameters
        ----------
        none
        """
        api_command = "curl --request GET https://localhost/rest/version"
        apiversions, exit_code = self.sshlib.execute_command(
            command=api_command, return_rc=True)
        if exit_code == 0:
            api_version = json.loads(apiversions)
            return api_version["currentVersion"]
        else:
            logging.warning(
                "The API Version utilized is 120 as get_api_version return exit code 1"
            )
            return "120"

    def build_command(self, url, request_type, payload={}, *options):
        """
        Helper method build_command
        creates the curl command along with headers for GEt and POST call to the appliance.

        Parameters:       
        ----------
        url: str
            URL location of the endpoint.

        request_type: str
            specifies the type of REST request. For isntance, Get, Post.

        payload: dict
            data to be sent to the appliance, only applicable when making a post call.

        *options: list of strings
            any arguments that needs to be concatinated with the curl command. For instance, "-i", "-s"
        """
        url = "https://localhost" + url
        if request_type == "GET":
            command = "curl -X {0} {1} {2}".format(request_type, self._header,
                                                   url)
            if self._secure_header != None:
                command = "curl -X {0} {1} {2}".format(request_type,
                                                       self._secure_header,
                                                       url)
        elif request_type == "POST":
            payload = '{0}'.format(json.dumps(payload).replace("'", '"'))
            command = 'curl -X {0} {1} -d \'{2}\' {3}'.format(
                request_type, self._header, payload, url)
            if self._secure_header != None:
                command = 'curl -X {0} {1} -d \'{2}\' {3}'.format(
                    request_type, self._secure_header, payload, url)
        if options:
            option = ""
            for op in options:
                option = option + " " + op
                command = "curl{0} -X {1} {2} -d '{3}' {4}".format(
                    option, request_type, self._header, payload, url)
            if self._secure_header != None:
                command = "curl{0} -X {1} {2} -d '{3}' {4}".format(
                    option, request_type, self._secure_header, payload, url)
                logging.info('Executing URI {0} Request Type: {1}'.format(
                    url, request_type))
        return command

    def accept_eula_once(self, service_access="yes"):
        """On initial communication with the appliance, the end user service agreement (EULA) must be accepted.
        This only needs to occur once.  Additional calls will not change the status of the EULA nor the status of the service access.
        If a change to the service access is required, see the function change_service_access()
        If the appliance returns an error status (anything outside of the 100 or 200 range), an error is raised.
        No authentication on the appliance is required.
        Parameters
        ----------
        service_access (optional): str
            "yes" will accept service access
            "no" will not allow service access
             empty value will default to "yes"
        """
        url = '/rest/appliance/eula/status'
        eula_command = self.build_command(url, "GET")
        json_result, exit_code = self.sshlib.execute_command(eula_command,
                                                             return_rc=True)
        if not json_result:  # if False, eula acceptance has already occurred.
            logging.warning('EULA does not need to be saved.')
        if exit_code != 0 or json_result:
            logging.debug(
                'Call EULA Acceptance with enable service access={0}'.format(
                    service_access))
            url = '/rest/appliance/eula/save'
            payload = {"supportAccess": service_access}
            save_eula_command = self.build_command(url, "POST", payload)
            logging.warning(save_eula_command)
            save_success, exit_code = self.sshlib.execute_command(
                save_eula_command, return_rc=True)
            if exit_code == 0:
                logging.info('EULA Response {0}'.format(save_success))
            else:
                raise Exception('accept_eula failed. JSON Response {0}'.format(
                    json.dumps(save_success)))

    def change_administrator_password(self):
        """On initial logon, the administrator's password has to be changed from the default value.
        The call to the administrator password change is attempted.
        If the change administrator password call fails, then we attempt to login with the administrator password.
        If successful, we log a message and the accurate administrator password.
        If the administrator login is not successful, an error is raised.
        The administrator data is pulled from the dictionary in this file.  This needs to be moved to a more formal location.
        Parameters
        ----------
        none
        """
        url = "/rest/users/changePassword"
        payload = {
            "userName": "Administrator",
            "oldPassword": "admin",
            "newPassword": "admin123"
        }
        change_pass_command = self.build_command(url, "POST", payload)
        status, success = self.sshlib.execute_command(
            command=change_pass_command, return_rc=True)

        if success == 0:
            logging.info('Administrator password change was accepted.')
        else:
            raise Exception(
                'change_administrator_password failed. JSON Response: {0}'.
                format(json.dumps(status)))

    def get_secure_headers(self):
        """Helper method to appliance_request().
        Gives header information required by the appliance with authentication information.
        Return
        ------
        _secure_header: dict. Dictionary containing X-API-Verions, Content-Type, and Auth.  The Auth parameter value is a sessionID.
        """
        # Once _secure_header is defined, we can use it over and over again for the duration of its life.
        # Note, the header is only good for that user (administrator), 24 hours, and until the next reboot.

        if self._secure_header != None:
            return self._secure_header
        payload = {"userName": "Administrator", "password": "admin123"}
        url = '/rest/login-sessions'

        authentication_command = self.build_command(url, "POST", payload)
        status, exit_code = self.sshlib.execute_command(
            command=authentication_command, return_rc=True)
        if exit_code != 0:
            raise Exception(
                "There was an issue with the HTTP Call to get headers. Exception message: {0}"
                .format(status))
        try:
            safe_json = json.loads(status)
            self._secure_header = self._header
            if 'sessionID' not in safe_json:
                raise Exception(
                    'Auth token for the header is undefined.  No Session ID available. Status: {0}.'
                    .format(status))
            self._secure_header = self._header + ' -H "Auth: {0}"'.format(
                safe_json['sessionID'])
            return self._secure_header
        except:
            raise Exception(
                'Failure to access the sessionID from the response. JSON: {0}'.
                format(status))

    def get_mac(self):
        """
        Helper method get_mac
        Used when creating the payload for setting the ip address of the oneview dcs appliance.
        returns mac address of the oneview dcs appliance. 

        Parameters:
        ----------
        none
        """
        url = "/rest/appliance/network-interfaces"
        self.get_secure_headers()
        mac_command = self.build_command(url, "GET")
        data, exit_code = self.sshlib.execute_command(command=mac_command,
                                                      return_rc=True)
        if exit_code != 0:
            raise Exception(
                'Failure to get mac address of the interface: {0}'.format(
                    data))
        data = json.loads(data)
        try:
            return data["applianceNetworks"][0]["macAddress"]
        except:
            raise Exception('Failure to fetch macAddress from the reponse')

    def change_ovDcs_ip(self, app1Ipv4Addr, app2Ipv4Addr, virtIpv4Addr,
        ipv4Gateway, ipv4Subnet, ):
        """Changes the Ip address of the oneview dcs appliance.

        Parameters:
        ----------
        app1Ipv4Addr: str
             Node1 IPv4 address in a two-node cluster

        app2Ipv4Addr: str
             Node2 IPv4 address in a two-node cluster.

        virtIpv4Addr: str
            Virtual IPv4 address. Oneview dcs will be reachable from this IP.

        ipv4Gateway: str
             IPv4 gateway address.
             
        ipv4Subnet: str
            IPv4 subnet mask or CIDR bit count.
        """
        url = "/rest/appliance/network-interfaces"
        macAddress = self.get_mac()
        payload = {
            "applianceNetworks": [{
                "activeNode": 1,
                "app2Ipv4Addr": app2Ipv4Addr,
                "app1Ipv4Addr": app1Ipv4Addr,
                "confOneNode": True,
                "hostname": "ThisIsAutomated.com",
                "networkLabel": "Managed devices network",
                "interfaceName": "Appliance",
                "device": "eth0",
                "ipv4Gateway": ipv4Gateway,
                "ipv4Subnet": ipv4Subnet,
                "ipv4Type": "STATIC",
                "ipv6Type": "UNCONFIGURE",
                "macAddress": macAddress,
                "overrideIpv4DhcpDnsServers": False,
                "unconfigure": False,
                "slaacEnabled": "yes",
                "virtIpv4Addr": virtIpv4Addr
            }]
        }

        changeIp_command = self.build_command(url, "POST", payload, "-i")
        data, exit_code = self.sshlib.execute_command(command=changeIp_command,
                                                      return_rc=True)
        x = json.dumps(data)
        time.sleep(2)
        uri =  search('Location: (.+?)\r\nCache-Control', x)

        print(uri, x)
        if uri != None:
            task_uri = uri.group(1)

            if (self.get_task(task_uri)):
                logging.info("Oneview Ip is set to: {0}".format(virtIpv4Addr))
        f = open('ipaddress.txt', 'w')
        f.write(str(virtIpv4Addr))
        return None

    def get_task(self, uri):
        """Gets the task corresponding to a given task ID.
        Will wait until the task is not completed. 
        No failure will rasie an exception. 
        On successful completion will return True

        Parameters:
        ----------
        uri: str
            Uri of the task
        """
        self.get_secure_headers()
        task_command = self.build_command(uri, "GET")
        data, exit_code = self.sshlib.execute_command(command=task_command,
                                                      return_rc=True)
        if exit_code == 0:
            task_data = json.loads(data)
            while task_data["taskState"] == "Running":
                logging.info("task \"{0}\" is running...".format(uri))
                time.sleep(10)
                data, exit_code = self.sshlib.execute_command(command=task_command,
                                                              return_rc=True)
                task_data = json.loads(data)
            if task_data["taskState"] == "Completed":
                logging.info("task \"{0}\" completed".format(uri))
                return True
            else:
                logging.warning(
                    "Unexpected failure. Task ended with state {0}, URI:{1}".
                    format(task_data["taskState"], uri))
        return None

    def search_task(self, param):
        """Gets all the tasks based upon filters provided. Note: filters are optional.
        iterate through all the task collected and calls get_task() to check the status.
        Used while running hardware discovery

        Parameters:
        ----------
        param: str
            Filters for the finding the task uris. For example: ?filter="'name' = 'alertMax'"
            filters are concatenated with the URI
        """
        self.get_secure_headers()
        uri = "/rest/tasks" + param
        task_command = self.build_command(uri, "GET")
        data, exit_code = self.sshlib.execute_command(command=task_command,
                                                      return_rc=True)
        all_members = json.loads(data)
        for i in all_members["members"]:
            self.get_task(i["uri"])

    def execute_command_in_dcs_and_verify(self, dcs_command, expected_output):
        '''Execute the given Command in DCS and verify the response with Expected output.
        Example
            Execute Command In DCS And Verify | <dcs_command> | <expected_output> |
        :param dcs_command: Command that need to be executed in DCS vm
        :param expected_output: expected output from the DCS command executed
        :raises  AssertionError if output does not match with expected output
        :return stdout: return response obtained after command execution
        '''
        logging.info("executing {0}".format(dcs_command))
        self.stdout = self.sshlib.execute_command(dcs_command,
                                                  return_stdout=True)
        if search(expected_output, self.stdout, IGNORECASE) is None:
            raise AssertionError(
                "DCS command output is not as expected: {} found: {}".format(
                    expected_output, self.stdout))
        return self.stdout

    def change_dcs_schematic(self, dcs_commands):
        '''Changes DCS schematic to given schematic
        Example
            Change DCS Schematic | <dcs_commands> |
        :param dcs_commands: DCS commands to be executed along with its expected output for changing the schematic
                             ex:[["dcs stop", "DCS is Stopped"]]
        '''
        for cmd in dcs_commands:
            self.execute_command_in_dcs_and_verify(cmd[0], cmd[1])
            time.sleep(60)

    def dcs_hardware_setup(self):
        '''Performs Hardware Setup in DCS appliance

        Parameters:
        none
        '''
        logging.info("executing appliance set up")
        status, exit_code = self.sshlib.execute_command(
            command=
            "curl -i -s -o /dev/nul -I -w '%{http_code}\n' -X POST -H \"X-API-Version: "
            + str(self.api_version) +
            "\" https://localhost/rest/appliance/tech-setup",
            return_rc=True)
        if exit_code != 0:
            raise AssertionError(
                "Failed to Invoke Sever Hardware discovery with status:{} and exit code:{}"
                .format(status, exit_code))
        elif status == "202":
            self.search_task(
                "?filter=\"'name'='Discover%20hardware'\"&sort=created:descending&count=1"
            )

    def dcs_network_configuration(self, app1Ipv4Addr, app2Ipv4Addr,
                                  virtIpv4Addr, ipv4Gateway, ipv4Subnet):
        """Changes the passwordthe dcs appliance and sets new Ip of the appliamce.

        Parameters:
         app1Ipv4Addr: str                                                               
              Node1 IPv4 address in a two-node cluster
 
         app2Ipv4Addr: str
              Node2 IPv4 address in a two-node cluster.
 
         virtIpv4Addr: str
             Virtual IPv4 address. Oneview dcs will be reachable from this IP.
 
         ipv4Gateway: str
              IPv4 gateway address.
              
         ipv4Subnet: str
             IPv4 subnet mask or CIDR bit count.
       """
        self.accept_eula_once()
        self.change_administrator_password()
        self.change_ovDcs_ip(app1Ipv4Addr, app2Ipv4Addr, virtIpv4Addr,
                             ipv4Gateway, ipv4Subnet)

    def dcs_schematic_configuration(self, dcs_commands):
        '''Change DCS schematic then perform Hardware setup
        :param dcs_commands: Sequence of DCS commands to be executed along with its expected output for changing the schematic
                             ex:[["dcs stop", "DCS is Stopped"]]
        '''
        # need to check if the surnning schematic is 3endl_demo then skip this step
        self.change_dcs_schematic(dcs_commands)
        self.dcs_hardware_setup()
        self.sshlib.close_connection()


dcs_commands = [
    ["dcs status", "dcs is running"],
    ["dcs stop", "dcs is stopped"],
    ["dcs status", "dcs is not running"],
    ["dcs start /dcs/schematic/synergy_3encl_demo cold", "DCS httpd daemon started"],
    [
        "dcs status",
        "DCS is Running\n  Schematic used:  /dcs/schematic/synergy_3encl_demo",
    ],
]


def ping(hosts):
    """
    Returns True if host (str) responds to a ping request.
    """
    host=hosts.strip()
    # operating_sys = platform.system().lower()
    exit_code = os.system("ping6 "+host+"%"+interfaces[0]+" -c 5")
    # print("ping6 "+hosts+"%"+interfaces[0]+" -c 5")
    if exit_code == 0:
        return True
    return False


interfaces = list(filter(lambda x: "ens" in x, netifaces.interfaces()))
config = load_from_file("auto_config")["fts"]
if __name__ == "__main__":
    if len(interfaces) > 0:
        f=open("ipv6.txt")
        ipv6=f.readline()
        while ipv6:
            if ping(ipv6):
                ipv6=ipv6.strip()
                dcs_inst = dcs(ipv6, interfaces[0] , sys.argv[1], sys.argv[2])
                dcs_inst.dcs_network_configuration(sys.argv[3], sys.argv[4], sys.argv[5],
                                                   sys.argv[6], sys.argv[7])
                dcs_inst.dcs_schematic_configuration(dcs_commands)
                break
            else:
                ipv6=f.readline()
        
