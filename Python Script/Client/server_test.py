import jsonrpclib

history = jsonrpclib.history.History()
server = jsonrpclib.Server('http://localhost:8002', history=history)
server.register_function(pow)
server.register_function(lambda x, y: x + y, 'add')
server.register_function(lambda x: x, 'ping')
server.serve_forever()
# import jsonrpclib
# import datetime
# import time
# import json

# server = jsonrpclib.Server('http://localhost:8001')


# class ExampleService:

#     def ping(self):
#         """Simple function to respond when called to demonstrate connectivity."""
#         return True

#     def now(self):
#         """Returns the server current date and time."""
#         return datetime.datetime.now()

#     def show_type(self, arg):
#         """Illustrates how types are passed in and out of server methods.

#         Accepts one argument of any type.
#         Returns a tuple with string representation of the value,
#         the name of the type, and the value itself.
#         """
#         return (str(arg), str(type(arg)), arg)

#     def raises_exception(self, msg):
#         "Always raises a RuntimeError with the message passed in"
#         raise RuntimeError(msg)

#     def send_back_binary(self, bin):
#         "Accepts single Binary argument, unpacks and repacks it to return it"
#         data = bin.data
#         response = Binary(data)
#         return response


# server.register_instance(ExampleService())

# try:
#     print 'Use Control-C to exit'
#     server.serve_forever()
# except KeyboardInterrupt:
#     print 'Exiting'
