# import requests
#
# url = "https://ws-public.interpol.int/notices/v1/red"
# response = requests.get(url)
#
# if response.status_code == 200:
#     data = response.json()
#     print(data)
#
# else:
#     print("api isteği başarısız")


from flask import Flask, request

app = Flask(__name__)

@app.route('/', methods=['POST'])
def handle_webhook():
    data = request.json
    print(data)  # veriyi işleyin
    return 'OK'

if __name__ == '__main__':
    app.run(debug=True, port=5000)
