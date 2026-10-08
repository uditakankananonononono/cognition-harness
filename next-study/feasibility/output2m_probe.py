import json,os,resource,sys,time
resource.setrlimit(resource.RLIMIT_AS,(268435456,268435456))
resource.setrlimit(resource.RLIMIT_CPU,(5,5))
resource.setrlimit(resource.RLIMIT_NPROC,(0,0))
resource.setrlimit(resource.RLIMIT_FSIZE,(2097152,2097152))
mode=sys.argv[1]
if mode=='fork':
 try:pid=os.fork()
 except OSError as e:print(json.dumps({'fork':'refused','errno':e.errno}))
 else:
  if pid==0:os._exit(0)
  os.waitpid(pid,0);print('FORK_ALLOWED')
elif mode=='memory':
 try:x='a'*(512*1024*1024)
 except MemoryError:print('memory_refused')
elif mode=='cpu':
 while True:pass
elif mode=='stdout':
 for i in range(10000):os.write(1,b'a'*4096)
elif mode=='stderr':
 for i in range(10000):os.write(2,b'a'*4096)
elif mode=='sleep':time.sleep(120)
else:print(json.dumps({'python':sys.version,'uid':os.getuid(),'limits':{str(k):resource.getrlimit(k) for k in [resource.RLIMIT_AS,resource.RLIMIT_CPU,resource.RLIMIT_NPROC,resource.RLIMIT_FSIZE]}}))
