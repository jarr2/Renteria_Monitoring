import socket, uuid, platform, psutil
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

@app.route('/', methods=['GET'])
def index():
    
    return render_template('index.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'GET':
        #return render_template('./Model/Module/Login/Views/login.html')
        return render_template('login.html')

@app.route('/device-info', methods=['GET'])
def device_info():
    return jsonify(get_diveces_info())

if __name__ == '__main__':
    app.run(host="0.0.0.0",port=5000,debug=True)