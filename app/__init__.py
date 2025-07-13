import socket, uuid, platform, psutil, secrets, ipaddress
import netmiko, threading
from flask import Flask, jsonify, render_template, request, redirect, session, flash


app = Flask(__name__)

app.secret_key ='b59083ff4c4873d1d4ba99d50f0166e3'  # Set a secret key for session management
netmiko_connections = {}

'''
def get_diveces_info():
    ip_address = socket.gethostbyname(socket.gethostname())
    print(f'IP_Address:{ip_address}')
    return {"IP_address":ip_address,
            "cpu": psutil.cpu_percent(interval=1),
            "ram": psutil.virtual_memory().percent,
            "mac_address":''.join(['{:02x}'.format((uuid.getnode()>>ele)&0xef) for ele in range(0,48,8)])
            }
'''
def get_connection(ip, user, password):
    if ip in netmiko_connections:
        return netmiko_connections[ip]  # ya está conectada

    device = {
        'device_type': 'cisco_ios',
        'host': ip,
        'username': user,
        'password': password,
        'secret': 'class',
        'verbose': True
    }
    try:
        conn = netmiko.ConnectHandler(**device)
        netmiko_connections[ip] = conn  # la guardas para futuras llamadas
        return conn
    except Exception as e:
        return str(e)

def collect_data(conn, dict_result):
    dict_result['interfaces'] = conn.send_command("show ip interface brief",use_genie=True)
    dict_result['acls'] = conn.send_command("show access-lists",use_genie=True)
    datos = conn.send_command("show version", use_genie=True)
    dict_result['hostname'] = datos.get('version', {}).get('hostname')
    

def close_connection(ip):
    if ip in netmiko_connections:
        netmiko_connections[ip].disconnect()
        del netmiko_connections[ip]



def configure_hostname(conn,hostname):
    try:
        conn.enable()
        output = conn.send_config_set(f"hostname {hostname}")
        print(output)
        if '% Invalid input' in output or '% Incomplete command' in output:
            status = "Error de configuración"
            print(status)
            return False
        else:
            return True
    except Exception as e:
        print(e)
        return str(e)

def configure_interface(conn,ip, mask, port, status):
    try:
        print(ip,port,status)
        conn.enable()
        if status:
            comasdf = [f'interface {port}', f'ip address {ip} {mask}', 'no shutdown']
        else:
            comasdf = [f'interface {port}', f'ip address {ip} {mask}', 'shutdown']
        output = conn.send_config_set(comasdf)
        print(output)
        if '% Invalid input' in output or '% Incomplete command' in output:
            status = "Error de configuración"
            print(status)
            return False
        else:
            return True

    except Exception as e:
        return str(e)


@app.route('/', methods=['GET'])
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
    if request.method == 'POST':
        session['ip'] = request.form.get('ip')
        session['user'] = request.form.get('user')
        session['id'] = request.form.get('id')
        session['key'] = 'Cisco123! '
        conn = get_connection(session['ip'], session['user'], session['key'])
        output = {}
        thread = threading.Thread(target=collect_data, args=(conn, output))
        thread.start()
        thread.join()

        return render_template('devices_configure.html', output=output, ip=session['ip'])

@app.route('/devices/configure/hostname', methods=['POST'])
def hostname_device_configure():
    if request.method == 'POST':
        hostname = request.form.get('hostname')
        if hostname:
            result = configure_hostname(get_connection(session['ip'], session['user'], session['key']),hostname)
            if result is True:
                flash('Hostname changed successfully!', 'success')
            else:
                flash('Error changing hostname', 'error')
            return redirect('/devices')

@app.route('/devices/configure/interface', methods=['POST'])
def interface_device_configure():
    if request.method == 'POST':
        port = request.form.get('port')
        return render_template('devices_configure_interface.html',port=port)

@app.route('/devices/configure/interface/apply', methods=['POST'])
def apply_interface_device_configure():
    if request.method == 'POST':
        ip_raw = f"{request.form.get('ip1')}.{request.form.get('ip2')}.{request.form.get('ip3')}.{request.form.get('ip4')}"
        print(ip_raw)
        mask = request.form.get('netmask')
        port = request.form.get('port')
        status = bool(request.form.get('chetbox'))
        try:
            ip = str(ipaddress.IPv4Address(ip_raw))
            result = configure_interface(get_connection(session['ip'], session['user'], session['key']),ip,mask,port,status)
            if result:
                flash('Interface configured succesfully','success')
                return redirect('/devices')
            else:
                flash('Error configuring interface','error')
                return redirect('/devices')
        except ipaddress.AddressValueError:
            flash("Invalid IP Address", "error")
            return redirect('/devices')

@app.route('/device-info', methods=['GET'])
def device_info():
    return jsonify(get_diveces_info())

if __name__ == '__main__':
    app.run(port=5000,debug=True)