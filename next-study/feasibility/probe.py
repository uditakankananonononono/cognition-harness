import json,os,resource,sys,time
resource.setrlimit(resource.RLIMIT_AS,(134217728,134217728))
resource.setrlimit(resource.RLIMIT_CPU,(1,1))
resource.setrlimit(resource.RLIMIT_NPROC,(0,0))
resource.setrlimit(resource.RLIMIT_FSIZE,(65536,65536))
mode=sys.argv[1]
if mode=='fork':
 try:pid=os.fork()
 except OSError as e:print(json.dumps({'fork':'refused','errno':e.errno}))
 else:
  if pid==0:os._exit(0)
  os.waitpid(pid,0);print(json.dumps({'fork':'ALLOWED'}))
elif mode=='memory':
 try:x='a'*(256*1024*1024)
 except MemoryError:print('memory_refused')
elif mode=='cpu':
 while True:pass
elif mode=='output':
 with open('/tmp/big','wb') as f:f.write(b'a'*131072)
elif mode=='sleep':time.sleep(10)
else:print(json.dumps({'python':sys.version,'uid':os.getuid(),'gid':os.getgid()}))
