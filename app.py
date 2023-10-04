import base64
import hashlib
from time import sleep
import re
import xml.etree.ElementTree as ET
#install
from flask import Flask, request, render_template, jsonify ,redirect , url_for
import requests
import argparse
import colorama
from colorama import Fore, Back, Style
colorama.init(autoreset=True)


W = Fore.WHITE
R = Fore.RED
Y = Fore.YELLOW
G = Fore.GREEN
C = Fore.CYAN
B = Fore.BLUE
M = Fore.MAGENTA
BM = Back.MAGENTA
BY = Back.YELLOW
BW = Back.WHITE
BG = Back.GREEN
BR = Back.RED
SB = Style.BRIGHT

app = Flask(__name__)


print(f'{SB}{W}+-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-+')  
print(f"{SB}{W}|{G}███████╗██╗  ██╗   ██╗{Y}██████╗ {G}██████╗  ██████╗ ██╗  ██╗{W}|")
print(f"{SB}{W}|{G}██╔════╝██║  ╚██╗ ██╔╝{Y}╚════██╗{G}██╔══██╗██╔═══██╗╚██╗██╔╝{W}|")
print(f"{SB}{W}|{G}█████╗  ██║   ╚████╔╝ {Y} █████╔╝{G}██████╔╝██║   ██║ ╚███╔╝ {W}|")
print(f"{SB}{W}|{G}██╔══╝  ██║    ╚██╔╝  {Y}██╔═══╝ {G}██╔══██╗██║   ██║ ██╔██╗ {W}|")
print(f"{SB}{W}|{G}██║     ███████╗██║   {Y}███████╗{G}██████╔╝╚██████╔╝██╔╝ ██╗{W}|")
print(f"{SB}{W}|{G}╚═╝     ╚══════╝╚═╝   {Y}╚══════╝{G}╚═════╝  ╚═════╝ ╚═╝  ╚═╝{W}|")
print(f'{SB}{W}+-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-+')
print(f"{SB}{W}|                                                       |")
print(f"{SB}{W}|                 {W}.: Version: {G}1.0.0 {W}:.",f"{SB}{W}                 |")                                    
print(f"{SB}{W}|               {W}.: Author : {BG}{W}!AZERTY9!", f"{SB}{W}:.", f"{SB}{W}               |")                                    
print(f'{SB}{W}+-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-+')  





def parse_xml(xml_data):
    root = ET.fromstring(xml_data)
    data = {}
    for elem in root:
        data[elem.tag] = elem.text
    return data

# var MACRO_LOGIN = '1';
# var MACRO_LOGOUT = '2';    
def get_error_message(error_code):
    error_messages = {
        "100002": "ERROR_SYSTEM_NO_SUPPORT",
        "100003": "ERROR_SYSTEM_NO_RIGHTS",
        "100004": "ERROR_SYSTEM_BUSY",
        "108001": "ERROR_LOGIN_USERNAME_WRONG",
        "108002": "ERROR_LOGIN_PASSWORD_WRONG",
        "108003": "ERROR_LOGIN_ALREADY_LOGIN",
        "108006": "ERROR_LOGIN_USERNAME_PWD_WRONG",
        "108007": "ERROR_LOGIN_USERNAME_PWD_ORERRUN",
        "108008": "ERROR_LOGIN_SSID2_FORBIDDEN",
        "108901": "ERROR_LOGIN_USERNAME_PWD_WRONG_ONE_TIME",
        "108902": "ERROR_LOGIN_USERNAME_PWD_WRONG_TWO_TIME",
        "120001": "ERROR_VOICE_BUSY",
        "125001": "ERROR_WRONG_TOKEN",
        "125002": "ERROR_WRONG_SESSION_ID",
        "125003": "ERROR_WRONG_SESSION_TOKEN",
    }   
    return error_messages.get(error_code, "Unknown Error")


def login_state(client, getawey):
    url = "http://%s/api/user/state-login" % getawey
    response = client.get(url)
    #<Username>admin</Username>
    if "<State>0</State><" in response.text:
        #print(f"{SB}{B}[info]{W}Already logged in.")
        return True
    return False
    
    
def hash(password):
    try:
        hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest()
        hashed_password = hashed_password.replace("-", "").lower()
        password_bytes = bytes(hashed_password, 'ascii')
        encoded_password = base64.b64encode(password_bytes).decode('ascii')
        return encoded_password
    except Exception as x:
        print(f'{SB}{R}[Error]{W} Hash: ', f'{SB}{R}{x}')

  
def get_csrf_token(client, getawey):
    url = "http://%s/api/webserver/SesTokInfo" % getawey
    response = client.get(url)
    root = ET.fromstring(response.text)
    csrf_token = root.findall('TokInfo')[0].text
    sleep(1)
    #print("[Token]", csrf_token)
    
    # url = "http://%s/" % getawey
    # response = client.get(url)
    # csrf_token_pattern = r'<meta name="csrf_token" content="(.*?)">'
    # match = re.search(csrf_token_pattern, response.text)

    # if match:
        # csrf_token = match.group(1)
        # return csrf_token
    # else:
        # print("[info*]", "csrf_token not found.")
    # return False
    return csrf_token
    
    
def setup_session(client, server):
    """ SETUP SESSION COOKIE """
    url = "http://%s/" % server
    response = client.get(url)
    response.raise_for_status()
    sleep(1)


def logout(client, getawey):
    try:
        if login_state(client, getawey):
            url = "http://%s/api/user/logout" % getawey
            csrf_token = get_csrf_token(client, getawey)
            headers = {'__RequestVerificationToken': csrf_token} 
            logout_payload = '<?xml version="1.0" encoding="UTF-8"?><request><Logout>1</Logout></request>'
            response = client.post(url, data=logout_payload, headers=headers)
            if response.status_code==200 :
                if "<response>OK</response>" in response.text:
                    print(f"{SB}{B}[info]{W} Logout.")
                    return True
        
    except Exception as x :
        print(f'{SB}{R}[Error] {W}Logout: {R}{x}' )


    return
     

def login(client, getawey, username, password):
    try:
        
        if login_state(client, getawey):
            return True
        else:
            print(f'{SB}{BR}Login.')
            setup_session(client, getawey)
            url = "http://%s/api/user/login" % getawey
            csrf_token = get_csrf_token(client, getawey)
            KEY = hash(password)
            hashed_password = hash(f"{username}{KEY}{csrf_token}")
            print(f"{SB}{C}[USER] {W}{username} \n{C}[*KEY] {W}{KEY} \n{C}[*TOKEN] {W}{csrf_token} ") 

            login_payload = f'<?xml version "1.0" encoding="UTF-8"?><request><Username>{username}</Username><Password>{hashed_password}</Password><password_type>4</password_type></request>'
            headers = {'__RequestVerificationToken': csrf_token} 
            response = client.post(
                    url, data=login_payload, headers=headers)
            if response.status_code==200 :
                if "<response>OK</response>" in response.text:
                    global csrf_token1
                    csrf_token1 = csrf_token
                    print(f"{SB}{B}[info]{W} Logged in.")
                    return True
                elif "<error>" in response.text :
                    global error_code_holder
                    root = ET.fromstring(response.text)
                    error_code = root.find('code').text
                    error_message = get_error_message(error_code)
                    print(f'{SB}{R}[Error]', error_message)
                    error_code_holder = error_message
                    if '<waittime>' in response.text:
                        timeout = root.find('waittime').text
                        print(f'{SB}{Y}[warning]', f'{SB}{W}You have attempted to log in three consecutive times unsuccessfully.')
                        print(f'{SB}{Y}[warning]', f'{SB}{W}Please try again after %smn.' % timeout)
                        error_code_holder = 'please try again after %smn.' % timeout
                        #Router Blocked,
                    return False
                    exit()     
                        
                    
        return False    
    except Exception as x :
        print(f"{SB}{R}[Error]{W} Login: ", x)
        return False


def reboot(client, getawey, username, password):
    """ REBOOT """
    try: 
        if login(client, getawey, username, password):
            url = "http://%s/api/device/control" % getawey
            csrf_token = get_csrf_token(client, getawey)
            headers = {'__RequestVerificationToken': csrf_token} 
            reboot_payload = '<?xml version:"1.0" encoding="UTF-8"?><request><Control>1</Control></request>'
            response = client.post(url, data='<?xml version:"1.0" encoding="UTF-8"?><request><Control>1</Control></request>', headers=headers)
            if response.status_code==200 :
                if "<response>OK</response>" in response.text:
                    print(f"{SB}{B}[info]{W} Roboted.")
                    return True
            
        
    except Exception as x :
        print("[Error] Reboot: ", x)


def current_network(client, getawey, username, password):
    if login(client, getawey, username, password):
            url = "http://%s/api/net/net-mode" % getawey
            get_net_mode = client.get(url)
            if "800C5" in get_net_mode.text:
                print(f"{SB}{B}[info]{W} NetworkMode: ", f"{SB}{G}4G FDD")
                return "4G FDD"  
            elif "7A000000000" in get_net_mode.text:
                print(f"{SB}{B}[info]{W} NetworkMode: ", f"{SB}{G}4G TDD")
                return "4G TDD"
            return False
            
            
def net_mode(client, getawey, username, password):
    """ CHANGE NET MODE """
    current_network = None
    FDD_Payload='<?xml version="1.0" encoding="UTF-8"?><request><NetworkMode>03</NetworkMode><NetworkBand>3FFFFFFF</NetworkBand><LTEBand>800C5</LTEBand></request>'
    TDD_Payload='<?xml version="1.0" encoding="UTF-8"?><request><NetworkMode>03</NetworkMode><NetworkBand>3FFFFFFF</NetworkBand><LTEBand>7A000000000</LTEBand></request>'
    try:
        if login(client, getawey, username, password):
            url = "http://%s/api/net/net-mode" % getawey
            get_net_mode = client.get(url)
            csrf_token = get_csrf_token(client, getawey)
            headers = {'__RequestVerificationToken': csrf_token} 
            if "800C5" in get_net_mode.text:
                set_net_mode = client.post(url, data=TDD_Payload, headers=headers)
                current_network = "4G TDD"
                
            elif "7A000000000" in get_net_mode.text:
                set_net_mode = client.post(url, data=FDD_Payload, headers=headers)
                current_network = "4G FDD"
            
            if set_net_mode.status_code==200 :
                if "<response>OK</response>" in set_net_mode.text:
                    print(f"{SB}{B}[info]{W} NetworkMode: ", f"{SB}{G}{current_network}" )
                    return True
            return False 
    except Exception as x:
        print(f'{SB}{R}[Error]{W} Net mode: {R}{x}')
        

def device_information(client, getawey, username, password):
    """ GET IPADDRESS """
    try:
        if login(client, getawey, username, password):
            url = "http://%s/api/device/information" % getawey
            while(True):
                response = client.get(url)
                root = ET.fromstring(response.text)
                ip = root.findall('WanIPAddress')[0]
                if ip.text :
                    element_to_replace = root.find("ProductFamily")
                    element_to_replace.text = 'azerty9'
                    modified_xml = ET.tostring(root, encoding="utf-8").decode()
                    return(modified_xml)
                    break
    except Exception as x:
        print(f'{SB}{R}[Error]{W} Get ipaddess: {R}{x}')
        
      
def convert_bytes(bytes):
    bytes = int(bytes)
    if bytes >= 1099511627776:  # Terabytes
        return f'{bytes / 1099511627776:.2f} TB'
    elif bytes >= 1073741824:  # Gigabytes
        return f'{bytes / 1073741824:.2f} GB'
    elif bytes >= 1048576:  # Megabytes
        return f'{bytes / 1048576:.2f} MB'
    elif bytes >= 1024:  # Kilobytes
        return f'{bytes / 1024:.2f} KB'
    else:  # Bytes
        return f'{bytes} Bytes'


def get_ip(client, getawey, username, password):
    xml_data = device_information(client, getawey, username, password)
    #parsed_data = parse_xml(xml_data)
    root = ET.fromstring(xml_data)   
    WanIPAddress = root.find('WanIPAddress').text 
    print(f'{SB}{B}[info]{W} WanIPAddress:', f'{SB}{G}{WanIPAddress}')
    #ProductFamily = root.find('ProductFamily').text    
    return WanIPAddress


def status_info(username, password):
    
    """ GET IP/NetworkMode """
    WanIPAddress = get_ip(client, getawey, username, password)
    current_net_mode = current_network(client, getawey, username, password)
    
    """ GET WIFI USER """
    #print()
    status_path = "http://%s/api/monitoring/status" % getawey
    xml_data = client.get(status_path)
    root = ET.fromstring(xml_data.text)   
    current_wifi_user = root.find('CurrentWifiUser').text 
    print(f"{SB}{B}[info]{W} CurrentWifiUser:", f"{SB}{G}{current_wifi_user}") 

    """ STATISTICS """
    #print()
    month_statistics_path = "http://%s/api/monitoring/month_statistics" % getawey
    xml_data = client.get(month_statistics_path)
    root = ET.fromstring(xml_data.text)
    current_month_download = root.find('CurrentMonthDownload').text
    current_month_upload = root.find('CurrentMonthUpload').text
    total_this_month_value = int(current_month_download) + int(current_month_upload)
    total_this_month = convert_bytes(total_this_month_value)
    print(f"{SB}{B}[info]{W} CurrentMonthDownload: ",  f"{SB}{G}{convert_bytes(current_month_download)}")
    print(f"{SB}{B}[info]{W} CurrentMonthUpload: ",  f"{SB}{G}{convert_bytes(current_month_upload)}")
    print(f"{SB}{B}[info]{W} TotalThisMonth: ", f"{SB}{G}{total_this_month}")

    #print()
    traffic_statistics_path = "http://%s/api/monitoring/traffic-statistics" % getawey
    xml_data = client.get(traffic_statistics_path)
    root = ET.fromstring(xml_data.text)
    total_download = root.find('TotalDownload').text
    total_upload = root.find('TotalUpload').text
    total_value = int(total_download) + int(total_upload)
    total = convert_bytes(total_value)
    print(f"{SB}{B}[info]{W} TotalDownload:", f"{SB}{G}{convert_bytes(total_download)}")
    print(f"{SB}{B}[info]{W} TotalUpload:", f"{SB}{G}{convert_bytes(total_upload)}")
    print(f"{SB}{B}[info]{W} TotalUpload:", f"{SB}{G}{total}")
    #logout(client, getawey)
    
    data = {
        'ipaddress' : WanIPAddress,
        'network' : current_net_mode, 
        'current_wifi_user' : current_wifi_user,
        'total_this_month' : total_this_month,
        'total' : total,   
    }
    
    return data
    

@app.route('/')
def index():
    if login_state (client, getawey):
        logout(client, getawey)        
    return render_template('index.html')


@app.route('/fly2box', methods=['POST'])
def fly2box():
    global username
    global password
    if request.method == 'POST':
        user_login = login(client, getawey, request.form['username'], request.form['password'])
        if user_login :
            print(f'{SB}{BR}Get Router Statistics.')
            username = request.form['username']
            password = request.form['password']
            
            statistics = status_info(username, password)
            total_this_month = statistics['total_this_month']
            total = statistics['total']
            current_wifi_user = statistics['current_wifi_user']
            WanIPAddress = statistics['ipaddress']
            current_net_mode = statistics['network'] 
            
            return render_template('result.html', total_this_month=total_this_month,
                                    total=total, current_wifi_user=current_wifi_user,
                                    ipaddress=WanIPAddress, network=current_net_mode
                                    
                                    )
                                    
                                    
        else:
            #print(f'{SB}{R}[Error]{W}', error_code_holder)
            return render_template('index.html' ,login_error=error_code_holder)


@app.route('/update_state')
def update_state():
    if username and password:
        print(f'{SB}{BR}Get Router Statistics.')
        statistics = status_info(username, password)
        return jsonify(statistics)
    else: 
        return jsonify({"location" : '/', })


@app.route('/retrieve')
def retrieve():
    print(f'{SB}{BR}Change NetworkMode.')
    change_net_mode = net_mode(client, getawey, username, password)
    if change_net_mode:
        WanIPAddress = get_ip(client, getawey, username, password)
        current_net_mode = current_network(client, getawey, username, password)
        data = {
            "ipaddress" : WanIPAddress,
            "network" : current_net_mode,
        }
        return jsonify(data)   
    return jsonify({"ipaddress" : 'None', "network" : 'None',})
    


   
if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(description="Scan internet for open host.")
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument('-web', '--web-server', action='store_true', help='Use web server.')  # , action = ExtendFromPipe
    input_group.add_argument('-cli', '--commandline', action='store_true', help='Use commandline.')
              
    other_group = parser.add_argument_group('OTHER')
    other_group.add_argument('-u', '--username', type=str, default=None, help='Specify the username.')
    other_group.add_argument('-p', '--password', type=str, default=None, help='Specify the password.')
    other_group.add_argument('-g', '--getawey', type=str, default='192.168.1.1', help='Specify getawey.')
    
    args = parser.parse_args()
    print(args)
    
    web_server = args.web_server
    commandline = args.commandline
    error_code_holder = ""
    csrf_token1 = ""
    username = args.username
    password = args.password
    getawey = args.getawey
    client = requests.Session()
    
    
    if web_server:
        #debug=False
        app.run(threaded=True)
    elif commandline:
        if username and password:
            change_net_mode = net_mode(client, getawey, username, password)
            if change_net_mode:
                WanIPAddress = get_ip(client, getawey, username, password)
                current_net_mode = current_network(client, getawey, username, password)
                logout(client, getawey)
                # print(f'{SB}{B}[info]{W}',"WanIPAddress:", WanIPAddress)
                # print(f'{SB}{B}[info]{W}',"NetworkMode:", current_net_mode)
        else:
            print(f'{SB}{Y}[warning]',f"{SB}{W}Please make sure (username/password) are provided.")
            print(f'{SB}{B}[info]',f"{SB}{W}ex: app.py -cli -u admin -p 123 (optional: -g 191.168.1.1)")
    
   
    
    
    