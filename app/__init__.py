import socket, uuid, platform, psutil, secrets
import netmiko
from flask import Flask, jsonify, render_template, request, redirect, session, flash


app = Flask(__name__)

app.secret_key ='b59083ff4c4873d1d4ba99d50f0166e3'  # Set a secret key for session management

def get_diveces_info():
    ip_address = socket.gethostbyname(socket.gethostname())
    print(f'IP_Address:{ip_address}')
    return {"IP_address":ip_address,
            "cpu": psutil.cpu_percent(interval=1),
            "ram": psutil.virtual_memory().percent,
            "mac_address":''.join(['{:02x}'.format((uuid.getnode()>>ele)&0xef) for ele in range(0,48,8)])
            }

def configure_hostname(hostname):
    try:
        device = {
            'device_type': 'cisco_ios',
            'ip': '10.10.10.1',
            'username': 'cisco',
            'password': 'Cisco123! ',
            'secret': 'class',
            'port': 22,
            'verbose': True
        }
        connection = netmiko.ConnectHandler(**device)
        connection.enable()
        command = f'hostname {hostname}'
        output = connection.send_config_set(command)
        connection.disconnect()
        if '% Invalid input' in output or '% Incomplete command' in output:
            status = "Error de configuración"
            return False
        else:
            return True
    except Exception as e:
        return str(e)


def send_show_device_command(command):
    try:
        device = {
            'device_type': 'cisco_ios',
            'ip': '10.10.10.1',
            'username': 'cisco',
            'password': 'Cisco123! ',
            'secret': 'class',
            'port': 22,
            'verbose': True
        }
        connection = netmiko.ConnectHandler(**device)
        connection.enable()
        #commands = ['exit',]
        #commands = 'hostname GNS3-Router'
        #output = connection.send_config_set(comasdf) #para una lista de comandos
        output = connection.send_command(command,use_genie=True)  # para un solo comando
        connection.disconnect()
        if '% Invalid input' in output or '% Incomplete command' in output:
            status = "Error de configuración"
            return status
        else:
            return output
    except Exception as e:
        return str(e)

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'GET':
        #return render_template('./Model/Module/Login/Views/login.html')
        return render_template('login.html')

@app.route('/dashboard', methods=['GET','POST'])
def dashboard():
    if request.method == 'GET':
        return render_template('dashboard.html')

@app.route('/devices', methods=['GET','POST'])
def devices():
    if request.method == 'GET':
        return render_template('devices.html')
@app.route('/devices/configure', methods=['GET','POST'])
def devices_configure():
    if request.method == 'GET':
        output = send_show_device_command(command='show ip interface brief')
        print('chivas',type(output))
        return render_template('devices_configure.html', output=output)

@app.route('/devices/configure/specific', methods=['POST', 'GET'])
def specific_device_configure():
    if request.method == 'POST':
        hostname = request.form.get('hostname')
        if hostname:
            result = configure_hostname(hostname)
            if result is True:
                flash('Hostname changed successfully!', 'success')
            else:
                flash('Error changing hostname', 'error')
            return redirect('/devices')

@app.route('/device-info', methods=['GET'])
def device_info():
    return jsonify(get_diveces_info())

if __name__ == '__main__':
    app.run(port=5000,debug=True)