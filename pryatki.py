from mcstatus import MinecraftServer

pryatki_server = MinecraftServer('localhost', 25565)
query = pryatki_server.query()
print(query)
#socket.timeout, ConnectionResetError
