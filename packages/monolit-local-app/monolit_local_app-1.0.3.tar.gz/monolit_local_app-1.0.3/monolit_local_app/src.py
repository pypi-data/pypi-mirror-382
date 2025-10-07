class App:
    www = None
    index_path = None

def host(src):
    import monolit_local_app as ml
    from monolit_local_app.other import DirTree
    
    try:
        app : App = src()
    except TypeError as e:
        raise TypeError(f"an invalid argument was passed to the function: run({src})\nTypeError: {e}")
    
    try:
        app.index_path = DirTree(app.www).walk("index.html").path
    except AttributeError:
        raise AttributeError(f"the class '{src.__name__}' must has attribute 'index_path'")
    if app.index_path == None:
        raise FileNotFoundError(f"the directory, on path '{app.www}', must has a file 'index.html'")
    if not isinstance(app.index_path, str):
        raise TypeError(f"the 'index_path' attribute, in class '{src.__name__}', must be a 'str', not a '{type(app.index_path).__name__}'")

    try:
        app.www
    except AttributeError:
        raise AttributeError(f"the class '{src.__name__}' must has attribute 'www'")
    if not isinstance(app.www, str):
        raise TypeError(f"the 'www' attribute, in class '{src.__name__}', must be a 'str', not a '{type(app.www).__name__}'")

    try:
        ml.server.index_path = app.index_path
        ml.server.process_request = app.process_request
        ml.server.run(host='127.0.0.1', port=5000, debug=True)
    except AttributeError:
        raise AttributeError(f"there is no 'process_request' method in the class '{src.__name__}'")