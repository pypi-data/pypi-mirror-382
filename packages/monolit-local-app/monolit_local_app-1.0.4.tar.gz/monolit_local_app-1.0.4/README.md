# About Monolit
This technology allows for rapid development of monolithic applications with a server-side component. The core idea is that the server and client reside on the same device, eliminating the need for a physical server. This lowers the barrier to entry in web development. Consequently, any indie developer can create a full-fledged application with a server-side component without any initial investment or hosting rental costs.

# How to install Monolit
The library can be installed using Python’s built-in package manager, pip. Simply type "pip install monolit_local_app" in your terminal, and all necessary packages will be automatically downloaded to your computer.

# How to use Monolit
To run a Monolit application, you need to import Monolit (e.g., import monolit_local_app as ml). Then, create a class in your main.py file. Specify the full path to the "www" folder (which must contain "index.html" either directly or in a subfolder; otherwise, an error will occur). Inside this class, you must also create a method named "process_request", which accepts an argument request: ml.Request. When an HTTP request arrives at the address "http://127.0.0.1:5000/process", this function will be triggered and return a response.

main.py:
```python
import monolit_local_app as ml

class Main(ml.App):
    def __init__(self):
        self.www = f"{ml.dirname(__file__)}\\www"

    def process_request(self, request : ml.Request):
        ml.info(request)

        return ml.jsonify(
            {
                "msg": "All is ok!"
            }
        )

if __name__ == "__main__":
    ml.host(Main)
```

However, this code does not constitute the application itself. This script merely hosts the application at the address "http://127.0.0.1:5000/www/index.html", but it does not launch it. To launch it, you must manually open your browser and enter "http://127.0.0.1:5000/www/index.html" in the address bar. Since this would be highly inconvenient for the user, it’s better to call main.py from the command line using another Python script.

app.py:
```python
import os
import webbrowser
webbrowser.open("http:\\127.0.0.1:5000\www\index.html")
os.system("python main.py")
```