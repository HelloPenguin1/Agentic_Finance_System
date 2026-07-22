from redis import Redis

r = Redis(host="localhost", port=6379)
print(r.ping())

print(r.execute_command("FT._LIST"))
