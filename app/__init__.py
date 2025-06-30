import socket, uuid, platform, psutil
import netmiko
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

def get_diveces_info():
    ip_address = socket.gethostbyname(socket.gethostname())
    print(f'IP_Address:{ip_address}')
    return {"IP_address":ip_address,
            "cpu": psutil.cpu_percent(interval=1),
            "ram": psutil.virtual_memory().percent,
            "mac_address":''.join(['{:02x}'.format((uuid.getnode()>>ele)&0xef) for ele in range(0,48,8)])
            }

def send_device_command(ip):
    try:
        device = {
            'device_type': 'cisco_ios',
            'ip': ip,
            'username': 'cisco',
            'password': 'Cisco123! ',
            'secret': 'class',
            'port': 22,
            'verbose': True
        }
        connection = netmiko.ConnectHandler(**device)
        connection.enable()
        commands = ['hostname Router1']
        #commands = 'hostname GNS3-Router'
        output = connection.send_config_set(commands) #para una lista de comandos
        #output = connection.send_command(commands)  # para un solo comando
        connection.disconnect()
        if '% Invalid input' in output or '% Incomplete command' in output:
            status = "Error de configuración"
            return status
        else:
            status = "Comando ejecutado con éxito"
            return status
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
        ip = request.args.get('ip')
        if ip:
            output = send_device_command(ip)
            print(f'Output from device {ip}: {output}')
            return render_template('devices_configure.html', ip=ip, output=output)
        else:
            return render_template('devices_configure.html', error="No IP address provided")


@app.route('/device-info', methods=['GET'])
def device_info():
    return jsonify(get_diveces_info())

if __name__ == '__main__':
    app.run(port=5000,debug=True)