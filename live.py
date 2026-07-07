import subprocess

# 🔹 Put your RTSP URL here
#rtsp_url =  "rtsp://RSKPJ:rskp%402024@183.82.99.76:1810/Streaming/Channels/101"        # RS KPHB        
#rtsp_url =  "rtsp://SIAPJ:siap%405202@183.82.108.29:1800/Streaming/Channels/101"    # SI Ameerpet
#rtsp_url =  "rtsp://SIPTJ:sipt%405202@183.82.98.202:1800/Streaming/Channels/101"       # SI Patny
#rtsp_url =  "rtsp://SIKTPJ:ktpjew%405202@183.82.99.50:1810/Streaming/Channels/101"     # SI Kothapet
#rtsp_url =  "rtsp://SIMGJ:mgjew%40654321@183.82.114.243:1800/Streaming/Channels/401"   # SI Madinaguda
#rtsp_url =  "rtsp://RSDNJ:rsdn%40654321@183.82.99.55:1800/Streaming/Channels/101"      # RS Dilsukhnagar
#rtsp_url =  "rtsp://RSCNJ:rscn%402024@183.82.99.77:1810/Streaming/Channels/701"        # RS Chandanagar
#rtsp_url =  "rtsp://SIHKJ:sihk%40654321@183.82.111.79:1800/Streaming/Channels/101"     # SI Hanamkonda
#rtsp_url =  "rtsp://SIVNJ:sivn%40654321@106.51.53.65:1800/Streaming/Channels/1201"     # SI Vizianagaram
#rtsp_url =  "rtsp://SISCJ:sisc%405202@183.82.111.16:1800/Streaming/Channels/101"       # SI Suchitra
#rtsp_url =  "rtsp://SIKPJ:sikp%405202@183.82.1.179:1880/Streaming/Channels/501"        # SI Kukatpally
#rtsp_url =  "rtsp://SIGBJ:sigb%402024@183.82.113.163:1810/Streaming/Channels/101"      # RS Gachibowli
#rtsp_url =  "rtsp://SIUPJ:siup%405202@183.82.120.205:1800/Streaming/Channels/101"      # SI Uppal
#rtsp_url =  "rtsp://SIRMJ:sirm%40654321@106.51.5.131:10081/Streaming/Channels/301"     # SI Rajahmundry
#rtsp_url =  "rtsp://RSAPJ:rsap%405202@183.82.99.146:1800/Streaming/Channels/601"       # RS Ameerpet

rtsp_url =  ""

            
# Play the stream
subprocess.run([
    "ffplay",
    "-rtsp_transport", "tcp",
    "-fflags", "nobuffer",
    "-flags", "low_delay",
    "-strict", "experimental",
    "-analyzeduration", "1000000",
    "-probesize", "1000000",
    "-loglevel", "debug",   # 👈 important for troubleshooting
    "-i", rtsp_url
])