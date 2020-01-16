import subprocess, time

host = "www.google.com"
try:
    ping = subprocess.Popen(
        ["ping", "-c", "1", "-w", "1", host],
        stdout = subprocess.PIPE,
        stderr = subprocess.PIPE
    )

    out, error = ping.communicate()
    out = out.decode("UTF-8")

    if (out.find("time=") == -1):
        f = open("db","r")
        counter = f.read()
        f.close()
        if counter != '':
            print(str(round(time.time()) - int(counter)) + 's')
    else:
        f = open("db","w")
        f.write(str(round(time.time())))
        f.close()
        print(out[out.find("time=")+5:out.find("ms",out.find("time="))+2])
except:
    print("X")
