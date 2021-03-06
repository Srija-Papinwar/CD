import os, json, sys
import shutil
import subprocess
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
print(sys.version)
# sys.path.append("/home/venkatesh/Documents/oneview-python/examples")
from auto_loader import load_from_file


class executePythonResources():

    exe = []
    success_files = []
    failed_files = []

    """
    To Execute Python SDK.

    """
    config_rename_file = 'config-rename.json'
    config_rename_dummy_file = os.getcwd() + '/oneview-python/examples/config-rename_dummy.json'
    config_file = 'config.json'

    def __init__(self, resource_dict):
        self.auto_config = load_from_file("auto_config") 
        # if (os.path.isfile(self.config_rename_file)):
        #     shutil.copyfile(self.config_rename_file, self.config_rename_dummy_file)
        self.resource_dict = resource_dict
        self.exe = self.load_resources()
       

        
    def load_resources(self):
        """
        To load resources(examples) from external config file.
        """
        try:
            with open('../resource_list.txt', 'r') as resources_list:
                resources = resources_list.read().splitlines()
                print(str(resources))
                if not resources:
                    print("no data in file resourceslist")
                else:
                    for resource in resources:
                        if resource != '':
                            self.exe.append(self.resource_dict[resource])

        except IOError as e:
            print ("I/O error while loading resources from resources_list file({0}): {1}".format(e.errno, e.strerror))
            # remove files
            exit()
        except Exception as e:
            print("Unexpected error: {}".format(str(e)))
            # remove files
            exit()

        return self.exe

    def generate_config_values(self):
        check = self.check_validate_config(self.config_rename_file)
        print("==================")
        print(self.config_rename_file)
        print(os.getcwd())
        # if config-rename.json file is present, then rename and copy contents into renamed file.
        if check:
            # shutil.copyfile(self.config_rename_file, self.config_rename_dummy_file)
            os.rename(os.getcwd()+"/"+self.config_rename_file, os.getcwd()+"/"+self.config_file)
            print("==================")
            print(os.getcwd())
            print(self.config_file)
            try:
                # load credentials
                with open(self.config_file, 'r') as config:
                    json_object = json.load(config)
                    config1=open(self.config_file, 'w')
                    json_object["ip"] = self.auto_config["oneview_cred"]["oneview_ip"]
                    json_object["credentials"]["userName"] = self.auto_config["oneview_cred"]["user_name"]
                    json_object["credentials"]["password"] = self.auto_config["oneview_cred"]["password"]
                    json_object["credentials"]["authLoginDomain"] = self.auto_config["oneview_cred"]["domain_directory"]
                    json_object["image_streamer_ip"] = self.auto_config["oneview_cred"]["i3s_ip"]
                    json_object["api_version"] = self.auto_config["oneview_cred"]["api_version"]
                    json_object["server_certificate_ip"] = self.auto_config["python"]["server_certificate_ip"]
                    json_object["hypervisor_manager_ip"] = self.auto_config["python"]["hypervisor_manager_ip"]
                    json_object["hypervisor_user_name"] = self.auto_config["python"]["hypervisor_user_name"]
                    json_object["hypervisor_password"] = self.auto_config["python"]["hypervisor_password"]
                    json_object["storage_system_hostname"] = self.auto_config["python"]["storage_system_hostname"]
                    json_object["storage_system_username"] = self.auto_config["python"]["storage_system_username"]
                    json_object["storage_system_password"] = self.auto_config["python"]["storage_system_password"]
                    json_object["storage_system_family"] = self.auto_config["python"]["storage_system_family"]
                    json_object["enclosure_hostname"]=self.auto_config["sdk"]["enclosure_hostname"]
                    json_object["enclosure_username"]=self.auto_config["sdk"]["enclosure_username"]
                    json_object["enclosure_password"]=self.auto_config["sdk"]["enclosure_password"]
                    json_object["enclosure_password"]=self.auto_config["sdk"]["enclosure_password"]
                    json_object["enclosure_group_uri"]=self.auto_config["sdk"]["enclosure_group_uri"]
                    json_object["server_mpHostsAndRanges"]=self.auto_config["sdk"]["server_mpHostsAndRanges"]
                    json_object["server_hostname"]=self.auto_config["sdk"]["server_hostname"]
                    json_object["server_password"]=self.auto_config["sdk"]["server_password"]
                    json_object["power_device_hostname"]=self.auto_config["sdk"]["power_device_hostname"]
                    json_object["power_device_username"]=self.auto_config["sdk"]["power_device_username"]
                    json_object["power_device_password"]=self.auto_config["sdk"]["power_device_password"]
                    json_object["ssl_certificate"]=self.auto_config["sdk"]["ssl_certificate"]
                    json.dump(json_object, config1,indent=4)
            # if there is an exception thrown while updating credentials, revert all previous operations
            # to make it constant.
            except Exception as e:
                print("Error {} occurred while generating config files". format(str(e)))
                if self.check_validate_config(self.config_file):
                    os.remove(self.config_file)
                    shutil.copyfile(self.config_rename_dummy_file, self.config_rename_file)
                    exit()
        else:
            print("config-rename.json file was not found to update credentials")

    def check_validate_config(self, file_name):
        return os.path.isfile(file_name)

    def run_python_executor(self):
        """
        Executor for Python modules
        """
        cwd = os.getcwd()
        os.chdir('/home/venkatesh/Documents/oneview-python/examples')
        self.generate_config_values()
        for example in self.exe:
            try:
                print(os.getcwd())
                example_file = example + str('.py')
                print(">> Executing {}..".format(example))
                p1=subprocess.run(['python3',example_file],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
                # # print(p1.returncode)
                # # exec(compile(open(example_file).read(), example_file, 'exec'))
                print(p1.stdout.decode())
                if(p1.returncode==0):
                    print(p1.stdout.decode())
                    self.success_files.append(example)
                else:
                    print("output error:")
                    print(p1.stderr.decode())
                print(self.success_files)    
            except Exception as e:
                print("Failed to execute {} with exception {}".format(str(example),(str(e))))
                self.failed_files.append(example)
        # os.remove(self.config_file)
        # shutil.copyfile(self.config_rename_dummy_file, self.config_rename_file)
        # os.remove(self.config_rename_dummy_file)
        os.chdir(cwd)
        return self.success_files
