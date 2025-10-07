#!/usr/bin/env python3
# requires-python = ">=3.6"
# -*- coding: utf-8 -*-
import os
import re
import stat
from collections import defaultdict, namedtuple
import argparse
import shutil
import subprocess
try:
	import multiCMD
	assert float(multiCMD.version) >= 1.37
except:
	import time,threading,io,sys,subprocess,select,string,re,itertools,signal
	class multiCMD:
		version='1.37_min_statblk'
		__version__=version
		COMMIT_DATE='2025-09-10'
		__running_threads=set()
		__variables={}
		_BRACKET_RX=re.compile('\\[([^\\]]+)\\]')
		_ALPHANUM=string.digits+string.ascii_letters
		_ALPHA_IDX={B:A for(A,B)in enumerate(_ALPHANUM)}
		class Task:
			def __init__(A,command):A.command=command;A.returncode=None;A.stdout=[];A.stderr=[];A.thread=None;A.stop=False
			def __iter__(A):return zip(['command','returncode','stdout','stderr'],[A.command,A.returncode,A.stdout,A.stderr])
			def __repr__(A):return f"Task(command={A.command}, returncode={A.returncode}, stdout={A.stdout}, stderr={A.stderr}, stop={A.stop})"
			def __str__(A):return str(dict(A))
			def is_alive(A):
				if A.thread is not None:return A.thread.is_alive()
				return False
		def _expand_piece(piece,vars_):
			D=vars_;C=piece;C=C.strip()
			if':'in C:E,F,G=C.partition(':');D[E]=G;return
			if'-'in C:
				A,F,B=(A.strip()for A in C.partition('-'));A=D.get(A,A);B=D.get(B,B)
				if A.isdigit()and B.isdigit():H=max(len(A),len(B));return[f"{A:0{H}d}"for A in range(int(A),int(B)+1)]
				if all(A in string.hexdigits for A in A+B):return[format(A,'x')for A in range(int(A,16),int(B,16)+1)]
				try:return[multiCMD._ALPHANUM[A]for A in range(multiCMD._ALPHA_IDX[A],multiCMD._ALPHA_IDX[B]+1)]
				except KeyError:pass
			return[D.get(C,C)]
		def _expand_ranges_fast(inStr):
			D=inStr;A=[];B=0
			for C in multiCMD._BRACKET_RX.finditer(D):
				if C.start()>B:A.append([D[B:C.start()]])
				E=[]
				for G in C.group(1).split(','):
					F=multiCMD._expand_piece(G,multiCMD.__variables)
					if F:E.extend(F)
				A.append(E or['']);B=C.end()
			A.append([D[B:]]);return[''.join(A)for A in itertools.product(*A)]
		def __handle_stream(stream,target,pre='',post='',quiet=False):
			E=quiet;C=target
			def D(current_line,target,keepLastLine=True):
				A=target
				if not keepLastLine:
					if not E:sys.stdout.write('\r')
					A.pop()
				elif not E:sys.stdout.write('\n')
				B=current_line.decode('utf-8',errors='backslashreplace');A.append(B)
				if not E:sys.stdout.write(pre+B+post);sys.stdout.flush()
			A=bytearray();B=True
			for F in iter(lambda:stream.read(1),b''):
				if F==b'\n':
					if not B and A:D(A,C,keepLastLine=False)
					elif B:D(A,C,keepLastLine=True)
					A=bytearray();B=True
				elif F==b'\r':D(A,C,keepLastLine=B);A=bytearray();B=False
				else:A.extend(F)
			if A:D(A,C,keepLastLine=B)
		def int_to_color(n,brightness_threshold=500):
			B=brightness_threshold;A=hash(str(n));C=A>>16&255;D=A>>8&255;E=A&255
			if C+D+E<B:return multiCMD.int_to_color(A,B)
			return C,D,E
		def __run_command(task,sem,timeout=60,quiet=False,dry_run=False,with_stdErr=False,identity=None):
			I=timeout;F=identity;E=quiet;A=task;C='';D=''
			with sem:
				try:
					if F is not None:
						if F==...:F=threading.get_ident()
						P,Q,R=multiCMD.int_to_color(F);C=f"[38;2;{P};{Q};{R}m";D='\x1b[0m'
					if not E:print(C+'Running command: '+' '.join(A.command)+D);print(C+'-'*100+D)
					if dry_run:return A.stdout+A.stderr
					B=subprocess.Popen(A.command,stdout=subprocess.PIPE,stderr=subprocess.PIPE,stdin=subprocess.PIPE);J=threading.Thread(target=multiCMD.__handle_stream,args=(B.stdout,A.stdout,C,D,E),daemon=True);J.start();K=threading.Thread(target=multiCMD.__handle_stream,args=(B.stderr,A.stderr,C,D,E),daemon=True);K.start();L=time.time();M=len(A.stdout)+len(A.stderr);time.sleep(0);H=1e-07
					while B.poll()is None:
						if A.stop:B.send_signal(signal.SIGINT);time.sleep(.01);B.terminate();break
						if I>0:
							if len(A.stdout)+len(A.stderr)!=M:L=time.time();M=len(A.stdout)+len(A.stderr)
							elif time.time()-L>I:A.stderr.append('Timeout!');B.send_signal(signal.SIGINT);time.sleep(.01);B.terminate();break
						time.sleep(H)
						if H<.001:H*=2
					A.returncode=B.poll();J.join(timeout=1);K.join(timeout=1);N,O=B.communicate()
					if N:multiCMD.__handle_stream(io.BytesIO(N),A.stdout,A)
					if O:multiCMD.__handle_stream(io.BytesIO(O),A.stderr,A)
					if A.returncode is None:
						if A.stderr and A.stderr[-1].strip().startswith('Timeout!'):A.returncode=124
						elif A.stderr and A.stderr[-1].strip().startswith('Ctrl C detected, Emergency Stop!'):A.returncode=137
						else:A.returncode=-1
				except FileNotFoundError as G:print(f"Command / path not found: {A.command[0]}",file=sys.stderr,flush=True);A.stderr.append(str(G));A.returncode=127
				except Exception as G:import traceback as S;print(f"Error running command: {A.command}",file=sys.stderr,flush=True);print(str(G).split('\n'));A.stderr.extend(str(G).split('\n'));A.stderr.extend(S.format_exc().split('\n'));A.returncode=-1
				if not E:print(C+'\n'+'-'*100+D);print(C+f"Process exited with return code {A.returncode}"+D)
				if with_stdErr:return A.stdout+A.stderr
				else:return A.stdout
		def __format_command(command,expand=False):
			D=expand;A=command
			if isinstance(A,str):
				if D:B=multiCMD._expand_ranges_fast(A)
				else:B=[A]
				return[A.split()for A in B]
			elif hasattr(A,'__iter__'):
				C=[]
				for E in A:
					if isinstance(E,str):C.append(E)
					else:C.append(repr(E))
				if not D:return[C]
				F=[multiCMD._expand_ranges_fast(A)for A in C];B=list(itertools.product(*F));return[list(A)for A in B]
			else:return multiCMD.__format_command(str(A),expand=D)
		def run_command(command,timeout=0,max_threads=1,quiet=False,dry_run=False,with_stdErr=False,return_code_only=False,return_object=False,wait_for_return=True,sem=None):return multiCMD.run_commands(commands=[command],timeout=timeout,max_threads=max_threads,quiet=quiet,dry_run=dry_run,with_stdErr=with_stdErr,return_code_only=return_code_only,return_object=return_object,parse=False,wait_for_return=wait_for_return,sem=sem)[0]
		def run_commands(commands,timeout=0,max_threads=1,quiet=False,dry_run=False,with_stdErr=False,return_code_only=False,return_object=False,parse=False,wait_for_return=True,sem=None):
			K=wait_for_return;J=dry_run;I=quiet;H=timeout;C=max_threads;B=sem;E=[]
			for L in commands:E.extend(multiCMD.__format_command(L,expand=parse))
			A=[multiCMD.Task(A)for A in E]
			if C<1:C=len(E)
			if C>1 or not K:
				if not B:B=threading.Semaphore(C)
				F=[threading.Thread(target=multiCMD.__run_command,args=(A,B,H,I,J,...),daemon=True)for A in A]
				for(D,G)in zip(F,A):G.thread=D;D.start()
				if K:
					for D in F:D.join()
				else:multiCMD.__running_threads.update(F)
			else:
				B=threading.Semaphore(1)
				for G in A:multiCMD.__run_command(G,B,H,I,J,identity=None)
			if return_code_only:return[A.returncode for A in A]
			elif return_object:return A
			elif with_stdErr:return[A.stdout+A.stderr for A in A]
			else:return[A.stdout for A in A]
		def join_threads(threads=...,timeout=None):
			A=multiCMD.__running_threads if threads is ... else threads
			for B in A:B.join(timeout=timeout)
			if A is multiCMD.__running_threads:multiCMD.__running_threads={A for A in A if A.is_alive()}
		def pretty_format_table(data,delimiter='\t',header=None,full=False):
			O=delimiter;B=header;A=data;import re;S=1.12;Z=S
			def J(s):return len(re.sub('\\x1b\\[[0-?]*[ -/]*[@-~]','',s))
			def L(col_widths,sep_len):A=col_widths;return sum(A)+sep_len*(len(A)-1)
			def T(s,width):
				A=width
				if J(s)<=A:return s
				if A<=0:return''
				return s[:max(A-2,0)]+'..'
			if not A:return''
			if isinstance(A,str):A=A.strip('\n').split('\n');A=[A.split(O)for A in A]
			elif isinstance(A,dict):
				if isinstance(next(iter(A.values())),dict):H=[['key']+list(next(iter(A.values())).keys())];H.extend([[A]+list(B.values())for(A,B)in A.items()]);A=H
				else:A=[[A]+list(B)for(A,B)in A.items()]
			elif not isinstance(A,list):A=list(A)
			if isinstance(A[0],dict):H=[list(A[0].keys())];H.extend([list(A.values())for A in A]);A=H
			A=[[str(A)for A in A]for A in A];C=len(A[0]);U=B is not None
			if not U:B=A[0];E=A[1:]
			else:
				if isinstance(B,str):B=B.split(O)
				if len(B)<C:B=B+['']*(C-len(B))
				elif len(B)>C:B=B[:C]
				E=A
			def V(hdr,rows_):
				B=hdr;C=[0]*len(B)
				for A in range(len(B)):C[A]=max(0,J(B[A]),*(J(B[A])for B in rows_ if A<len(B)))
				return C
			P=[]
			for F in E:
				if len(F)<C:F=F+['']*(C-len(F))
				elif len(F)>C:F=F[:C]
				P.append(F)
			E=P;D=V(B,E);G=' | ';I='-+-';M=multiCMD.get_terminal_size()[0]
			def K(hdr,rows,col_w,sep_str,hsep_str):
				D=hsep_str;C=col_w;E=sep_str.join('{{:<{}}}'.format(A)for A in C);A=[];A.append(E.format(*hdr));A.append(D.join('-'*A for A in C))
				for B in rows:
					if not any(B):A.append(D.join('-'*A for A in C))
					else:B=[T(B[A],C[A])for A in range(len(B))];A.append(E.format(*B))
				return'\n'.join(A)+'\n'
			if full:return K(B,E,D,G,I)
			if L(D,len(G))<=M:return K(B,E,D,G,I)
			G='|';I='+'
			if L(D,len(G))<=M:return K(B,E,D,G,I)
			W=[J(A)for A in B];X=[max(D[A]-W[A],0)for A in range(C)];N=L(D,len(G))-M
			for(Y,Q)in sorted(enumerate(X),key=lambda x:-x[1]):
				if N<=0:break
				if Q<=0:continue
				R=min(Q,N);D[Y]-=R;N-=R
			return K(B,E,D,G,I)
		def get_terminal_size():
			try:import os;A=os.get_terminal_size()
			except:
				try:import fcntl,termios as C,struct as B;D=fcntl.ioctl(0,C.TIOCGWINSZ,B.pack('HHHH',0,0,0,0));A=B.unpack('HHHH',D)[:2]
				except:import shutil as E;A=E.get_terminal_size(fallback=(120,30))
			return A
		def format_bytes(size,use_1024_bytes=None,to_int=False,to_str=False,str_format='.2f'):
			H=str_format;F=to_str;C=use_1024_bytes;A=size
			if to_int or isinstance(A,str):
				if isinstance(A,int):return A
				elif isinstance(A,str):
					K=re.match('(\\d+(\\.\\d+)?)\\s*([a-zA-Z]*)',A)
					if not K:
						if F:return A
						print("Invalid size format. Expected format: 'number [unit]', e.g., '1.5 GiB' or '1.5GiB'");print(f"Got: {A}");return 0
					G,L,D=K.groups();G=float(G);D=D.strip().lower().rstrip('b')
					if D.endswith('i'):C=True
					elif C is None:C=False
					D=D.rstrip('i')
					if C:B=2**10
					else:B=10**3
					I={'':0,'k':1,'m':2,'g':3,'t':4,'p':5,'e':6,'z':7,'y':8}
					if D not in I:
						if F:return A
					else:
						if F:return multiCMD.format_bytes(size=int(G*B**I[D]),use_1024_bytes=C,to_str=True,str_format=H)
						return int(G*B**I[D])
				else:
					try:return int(A)
					except Exception:return 0
			elif F or isinstance(A,int)or isinstance(A,float):
				if isinstance(A,str):
					try:A=A.rstrip('B').rstrip('b');A=float(A.lower().strip())
					except Exception:return A
				if C or C is None:
					B=2**10;E=0;J={0:'',1:'Ki',2:'Mi',3:'Gi',4:'Ti',5:'Pi',6:'Ei',7:'Zi',8:'Yi'}
					while A>B:A/=B;E+=1
					return f"{A:{H}} {' '}{J[E]}".replace('  ',' ')
				else:
					B=10**3;E=0;J={0:'',1:'K',2:'M',3:'G',4:'T',5:'P',6:'E',7:'Z',8:'Y'}
					while A>B:A/=B;E+=1
					return f"{A:{H}} {' '}{J[E]}".replace('  ',' ')
			else:
				try:return multiCMD.format_bytes(float(A),C)
				except Exception:pass
				return 0
import time
try:
	import functools
	import typing
	# Check if functiools.cache is available
	# cache_decorator = functools.cache
	def cache_decorator(user_function):
		def _make_hashable(item):
			if isinstance(item, typing.Mapping):
				# Sort items so that {'a':1, 'b':2} and {'b':2, 'a':1} hash the same
				return tuple(
					( _make_hashable(k), _make_hashable(v) )
					for k, v in sorted(item.items(), key=lambda item: item[0])
				)
			if isinstance(item, (list, set, tuple)):
				return tuple(_make_hashable(e) for e in item)
			# Fallback: assume item is already hashable
			return item
		def decorating_function(user_function):
			# Create the real cached function
			cached_func = functools.lru_cache(maxsize=None)(user_function)
			@functools.wraps(user_function)
			def wrapper(*args, **kwargs):
				# Convert all args/kwargs to hashable equivalents
				hashable_args = tuple(_make_hashable(a) for a in args)
				hashable_kwargs = {
					k: _make_hashable(v) for k, v in kwargs.items()
				}
				# Call the lru-cached version
				return cached_func(*hashable_args, **hashable_kwargs)
			# Expose cache statistics and clear method
			wrapper.cache_info = cached_func.cache_info
			wrapper.cache_clear = cached_func.cache_clear
			return wrapper
		return decorating_function(user_function)
except :
	import sys
	# If lrucache is not available, use a dummy decorator
	print('Warning: functools.lru_cache is not available, multiSSH3 will run slower without cache.',file=sys.stderr)
	def cache_decorator(func):
		return func

version = '1.30'
VERSION = version
__version__ = version
COMMIT_DATE = '2025-10-06'

SMARTCTL_PATH = shutil.which("smartctl")

def read_text(path):
	try:
		with open(path, "r", encoding="utf-8", errors="ignore") as f:
			return f.read().strip()
	except Exception:
		return None

def read_int(path):
	s = read_text(path)
	if s is None:
		return 0
	try:
		return int(s)
	except Exception:
		return 0

def build_symlink_dict(dir_path):
	"""
	Build map: devname -> token (uuid or label string) using symlinks under
	/dev/disk/by-uuid or /dev/disk/by-label.
	"""
	mapping = {}
	if not os.path.isdir(dir_path):
		return mapping
	try:
		for entry in os.listdir(dir_path):
			p = os.path.join(dir_path, entry)
			try:
				if os.path.islink(p):
					tgt = os.path.realpath(p)
					mapping.setdefault(tgt, entry)
			except Exception:
				continue
	except Exception:
		pass
	return mapping

def get_statvfs_use_size(mountpoint):
	try:
		st = os.statvfs(mountpoint)
		block_size = st.f_frsize if st.f_frsize > 0 else st.f_bsize
		total = st.f_blocks * block_size
		avail = st.f_bavail * block_size
		used = total - avail
		return total, used
	except Exception:
		return 0, 0

@cache_decorator
def read_discard_support(sysfs_block_path):
	if not sysfs_block_path or not os.path.isdir(sysfs_block_path):
		return 'N/A'
	dmbytes = read_int(os.path.join(sysfs_block_path, "queue", "discard_max_bytes"))
	try:
		if dmbytes > 0:
			return 'Yes'
		else:
			return 'No'
	except Exception:
		return 'N/A'

@cache_decorator
def get_real_sysfs_device_path(sysfs_block_path):
	"""
	Return the sysfs 'device' directory for this block node (resolves partition
	to its parent device as well).
	"""
	dev_link = os.path.join(sysfs_block_path, "device")
	try:
		return os.path.realpath(dev_link)
	except Exception:
		return dev_link

@cache_decorator
def read_model_and_serial(sysfs_block_path):
	if not sysfs_block_path or not os.path.isdir(sysfs_block_path):
		return '', ''
	device_path = get_real_sysfs_device_path(sysfs_block_path)
	model = read_text(os.path.join(device_path, "model"))
	serial = read_text(os.path.join(device_path, "serial"))
	if serial is None:
		serial = read_text(os.path.join(device_path, "wwid"))
	if model:
		model = " ".join(model.split())
	else:
		model = ''
	if serial:
		serial = " ".join(serial.split())
	else:
		serial = ''
	return model, serial

def read_size(sysfs_block_path):# -> tuple[int | None, Any] | Literal['']:
	if not sysfs_block_path or not os.path.isdir(sysfs_block_path):
		return ''
	size = read_int(os.path.join(sysfs_block_path, "size"))
	return size

MountEntry = namedtuple("MountEntry", ["MOUNTPOINT", "FSTYPE", "OPTIONS"])
def parseMount():
	rtn = multiCMD.run_command('mount',timeout=1,quiet=True)
	mount_table = defaultdict(list)
	for line in rtn:
		device_name, _, line = line.partition(' on ')
		if device_name.startswith(os.path.sep):
			device_name = os.path.realpath(device_name)
		mount_point, _, line = line.partition(' type ')
		fstype, _ , options = line.partition(' (')
		options = options.rstrip(')').split(',')
		mount_table[device_name].append(MountEntry(mount_point, fstype, options))
	return mount_table

def get_blocks():
	# get entries in /sys/class/block
	block_devices = []
	for entry in os.listdir("/sys/class/block"):
		if os.path.isdir(os.path.join("/sys/class/block", entry)):
			block_devices.append(f'/dev/{entry}')
	return block_devices

@cache_decorator
def is_block_device(devpath):
	try:
		st_mode = os.stat(devpath).st_mode
		return stat.S_ISBLK(st_mode)
	except Exception:
		return False

def is_partition(sysfs_block_path):
	if not sysfs_block_path or not os.path.isdir(sysfs_block_path):
		return False
	return os.path.exists(os.path.join(sysfs_block_path, "partition"))

@cache_decorator
def get_partition_parent_name(name):
	if not name:
		return None
	name = os.path.basename(name)
	sysfs_block_path = os.path.realpath(os.path.join('/sys/class/block', name))
	if not sysfs_block_path or not os.path.isdir(sysfs_block_path):
		return None
	part_file = os.path.join(sysfs_block_path, "partition")
	if not os.path.exists(part_file):
		return os.path.join('/dev', name) if is_block_device(os.path.join('/dev', name)) else None
	parent = os.path.basename(os.path.dirname(sysfs_block_path))
	return os.path.join('/dev', parent) if parent and parent != name else None

@cache_decorator
def get_sector_size(sysfs_block_path):
	if not sysfs_block_path or not os.path.isdir(sysfs_block_path):
		return 512
	if get_partition_parent_name(sysfs_block_path):
		sysfs_block_path = os.path.join('/sys/class/block', os.path.basename(get_partition_parent_name(sysfs_block_path)))
	sector_size = read_int(os.path.join(sysfs_block_path, "queue", "hw_sector_size"))
	if sector_size == 0:
		sector_size = read_int(os.path.join(sysfs_block_path, "queue", "logical_block_size"))
	return sector_size if sector_size else 512

def get_read_write_rate_throughput_iter(sysfs_block_path):
	if not sysfs_block_path or not os.path.isdir(sysfs_block_path):
		while True:
			yield 0, 0
	rx_path = os.path.join(sysfs_block_path, "stat")
	start_time = time.monotonic()
	sector_size = get_sector_size(sysfs_block_path)
	previous_bytes_read = 0
	previous_bytes_written = 0
	try:
		with open(rx_path, "r", encoding="utf-8", errors="ignore") as f:
			fields = f.read().strip().split()
		if len(fields) < 7:
			yield 0, 0
		sectors_read = int(fields[2])
		read_time = int(fields[3]) / 1000.0
		sectors_written = int(fields[6])
		write_time = int(fields[7]) / 1000.0
		read_throughput = (sectors_read * sector_size) / read_time if read_time > 0 else 0
		write_throughput = (sectors_written * sector_size) / write_time if write_time > 0 else 0
		previous_bytes_read = sectors_read * sector_size
		previous_bytes_written = sectors_written * sector_size
		yield int(read_throughput), int(write_throughput)
	except Exception:
		yield 0, 0
	while True:
		try:
			with open(rx_path, "r", encoding="utf-8", errors="ignore") as f:
				fields = f.read().strip().split()
			if len(fields) < 7:
				yield 0, 0
			# fields: https://www.kernel.org/doc/html/latest/block/stat.html
			# 0 - reads completed successfully
			# 1 - reads merged
			# 2 - sectors read
			# 3 - time spent reading (ms)
			# 4 - writes completed
			# 5 - writes merged
			# 6 - sectors written
			# 7 - time spent writing (ms)
			# 8 - I/Os currently in progress
			# 9 - time spent doing I/Os (ms)
			# 10 - weighted time spent doing I/Os (ms)
			sectors_read = int(fields[2])
			sectors_written = int(fields[6])
			bytes_read = sectors_read * sector_size
			bytes_written = sectors_written * sector_size
			end_time = time.monotonic()
			elapsed_time = end_time - start_time
			start_time = end_time
			read_throughput = (bytes_read - previous_bytes_read) / elapsed_time if elapsed_time > 0 else 0
			write_throughput = (bytes_written - previous_bytes_written) / elapsed_time if elapsed_time > 0 else 0
			previous_bytes_read = bytes_read
			previous_bytes_written = bytes_written
			yield int(read_throughput), int(write_throughput)
		except Exception:
			yield 0, 0

ALL_OUTPUT_FIELDS = ["NAME", "FSTYPE", "SIZE", "FSUSE%", "MOUNTPOINT", "SMART", "LABEL", "UUID", "MODEL", "SERIAL", "DISCARD", "READ", "WRITE"]

# DRIVE_INFO = namedtuple("DRIVE_INFO", 
# 	["NAME", "FSTYPE", "SIZE", "FSUSEPCT", "MOUNTPOINT", "SMART","RTPT",'WTPT', "LABEL", "UUID", "MODEL", "SERIAL", "DISCARD"])
def get_drives_info(print_bytes = False, use_1024 = False, mounted_only=False, best_only=False, 
					formated_only=False, show_zero_size_devices=False,pseudo=False,tptDict = {},
					full=False,active_only=False,output="all",exclude=""):
	global SMARTCTL_PATH
	global ALL_OUTPUT_FIELDS
	if output == "all":
		output_fields = ALL_OUTPUT_FIELDS
	else:
		output_fields = [x.strip().upper() for x in output.split(',')]
		for field in output_fields:
			if field not in ALL_OUTPUT_FIELDS:
				print(f"Ignoring invalid output field: {field}.", file=sys.stderr)
				output_fields.remove(field)
	if exclude:
		exclude_fields = [x.strip().upper() for x in exclude.split(',')]
		for field in exclude_fields:
			if field in output_fields:
				output_fields.remove(field)
	if not output_fields:
		print("No valid output fields specified.", file=sys.stderr)
		return []
	output_list = [output_fields]
	output_fields_set = set(output_fields)
	if {'SIZE','FSTYPE','UUID','LABEL'}.intersection(output_fields_set):
		lsblk_result = multiCMD.run_command(f'lsblk -brnp -o NAME,SIZE,FSTYPE,UUID,LABEL',timeout=2,quiet=True,wait_for_return=False,return_object=True)
	block_devices = get_blocks()
	smart_infos = {}
	for block_device in block_devices:
		if 'SMART' in output_fields_set:
			parent_name = get_partition_parent_name(block_device)
			if parent_name:
				if parent_name not in smart_infos:
					smart_infos[parent_name] = multiCMD.run_command(f'{SMARTCTL_PATH} -H {parent_name}',timeout=2,quiet=True,wait_for_return=False,return_object=True)
		if block_device not in tptDict:
			sysfs_block_path = os.path.join('/sys/class/block', os.path.basename(block_device))
			tptDict[block_device] = get_read_write_rate_throughput_iter(sysfs_block_path)
	mount_table = parseMount()
	target_devices = set(block_devices)
	if pseudo:
		target_devices.update(mount_table.keys())
	target_devices = sorted(target_devices)
	uuid_dict = {}
	if 'UUID' in output_fields_set:
		uuid_dict = build_symlink_dict("/dev/disk/by-uuid")
	label_dict = {}
	if 'LABEL' in output_fields_set:
		label_dict = build_symlink_dict("/dev/disk/by-label")
	fstype_dict = {}
	size_dict = {}
	if {'SIZE','FSTYPE','UUID','LABEL'}.intersection(output_fields_set):
		lsblk_result.thread.join()
		if lsblk_result.returncode == 0:
			for line in lsblk_result.stdout:
				lsblk_name, lsblk_size, lsblk_fstype, lsblk_uuid, lsblk_label = line.split(' ', 4)
				if lsblk_name.startswith(os.path.sep):
					lsblk_name = os.path.realpath(lsblk_name)
				# the label can be \x escaped, we need to decode it
				if 'UUID' in output_fields_set:
					lsblk_uuid = bytes(lsblk_uuid, "utf-8").decode("unicode_escape")
					if lsblk_uuid:
						uuid_dict[lsblk_name] = lsblk_uuid
				if 'FSTYPE' in output_fields_set:
					lsblk_fstype = bytes(lsblk_fstype, "utf-8").decode("unicode_escape")
					if lsblk_fstype:
						fstype_dict[lsblk_name] = lsblk_fstype
				if 'LABEL' in output_fields_set:
					lsblk_label = bytes(lsblk_label, "utf-8").decode("unicode_escape")
					if lsblk_label:
						label_dict[lsblk_name] = lsblk_label
				if 'SIZE' in output_fields_set:
					try:
						size_dict[lsblk_name] = int(lsblk_size)
					except Exception:
						pass
	for device_name in target_devices:
		if mounted_only and device_name not in mount_table:
			continue
		if active_only and device_name not in tptDict:
			continue
		device_properties = defaultdict(str)
		device_properties['NAME'] = device_name if full else device_name.replace('/dev/', '')
		# fstype, size, fsuse%, mountpoint, rtpt, wtpt, lable, uuid are partition specific
		# smart, model, serial, discard are device specific, and only for block devices
		# fstype, size, fsuse%, mountpoint does not require block device and can have multiple values per device
		if is_block_device(device_name):
			parent_name = get_partition_parent_name(device_name)
			parent_sysfs_path = os.path.realpath(os.path.join('/sys/class/block', os.path.basename(parent_name))) if parent_name else None
			if 'MODEL' in output_fields_set or 'SERIAL' in output_fields_set:
				device_properties['MODEL'], device_properties['SERIAL'] = read_model_and_serial(parent_sysfs_path)
			if 'DISCARD' in output_fields_set:
				device_properties['DISCARD'] = read_discard_support(parent_sysfs_path)
			if parent_name in smart_infos and SMARTCTL_PATH:
				smart_info_obj = smart_infos[parent_name]
				smart_info_obj.thread.join()
				for line in smart_info_obj.stdout:
					line = line.lower()
					if "health" in line:
						smartinfo = line.rpartition(':')[2].strip().upper()
						device_properties['SMART'] = smartinfo.replace('PASSED', 'OK')
						break
					elif "denied" in line:
						device_properties['SMART'] = 'DENIED'
						break
			size_bytes = read_size(os.path.join('/sys/class/block', os.path.basename(device_name)))
		if device_name in tptDict:
			try:
				device_properties['READ'], device_properties['WRITE'] = next(tptDict[device_name])
				if active_only and device_properties['READ'] == 0 and device_properties['WRITE'] == 0:
					continue
				if print_bytes:
					device_properties['READ'] = str(device_properties['READ'])
					device_properties['WRITE'] = str(device_properties['WRITE'])
				else:
					device_properties['READ'] = multiCMD.format_bytes(device_properties['READ'], use_1024_bytes=use_1024, to_str=True,str_format='.0f') + 'B/s'
					device_properties['WRITE'] = multiCMD.format_bytes(device_properties['WRITE'], use_1024_bytes=use_1024, to_str=True,str_format='.0f') + 'B/s'
			except Exception:
				device_properties['READ'] = ''
				device_properties['WRITE'] = ''
		if device_name in label_dict:
			device_properties['LABEL'] = label_dict[device_name]
		if device_name in uuid_dict:
			device_properties['UUID'] = uuid_dict[device_name]
		mount_points = mount_table.get(device_name, [])
		if best_only:
			if mount_points:
				mount_points = [sorted(mount_points, key=lambda x: len(x.MOUNTPOINT))[0]]
		if mount_points:
			for mount_entry in mount_points:
				device_properties['FSTYPE'] = mount_entry.FSTYPE
				if formated_only and not device_properties['FSTYPE']:
					continue
				device_properties['MOUNTPOINT'] = mount_entry.MOUNTPOINT
				size_bytes, used_bytes = get_statvfs_use_size(device_properties['MOUNTPOINT'])
				if size_bytes == 0 and not show_zero_size_devices:
					continue
				device_properties['FSUSE%'] = f"{int(round(100.0 * used_bytes / size_bytes))}%" if size_bytes > 0 else "N/A"
				if print_bytes:
					device_properties['SIZE'] = str(size_bytes)
				else:
					device_properties['SIZE'] = multiCMD.format_bytes(size_bytes, use_1024_bytes=use_1024, to_str=True) + 'B'
				output_list.append([device_properties[output_field] for output_field in output_fields])
		else:
			if formated_only and device_name not in fstype_dict:
				continue
			device_properties['FSTYPE'] = fstype_dict.get(device_name, '')
			if not size_bytes:
				size_bytes = size_dict.get(device_name, 0)
			if size_bytes == 0 and not show_zero_size_devices:
				continue
			if print_bytes:
				device_properties['SIZE'] = str(size_bytes)
			else:
				device_properties['SIZE'] = multiCMD.format_bytes(size_bytes, use_1024_bytes=use_1024, to_str=True) + 'B'
			output_list.append([device_properties[output_field] for output_field in output_fields])
		multiCMD.join_threads()
	return output_list


def main():
	parser = argparse.ArgumentParser(description="Gather disk and partition info for block devices.")
	parser.add_argument('-j','--json', help="Produce JSON output", action="store_true")
	parser.add_argument('-b','--bytes', help="Print the SIZE column in bytes rather than in a human-readable format", action="store_true")
	parser.add_argument('-H','--si', help="Use powers of 1000 not 1024 for SIZE column", action="store_true")
	parser.add_argument('-F','-fo','--formated_only', help="Show only formated filesystems", action="store_true")
	parser.add_argument('-M','-mo','--mounted_only', help="Show only mounted filesystems", action="store_true")
	parser.add_argument('-B','-bo','--best_only', help="Show only shortest mount point for each device", action="store_true")
	parser.add_argument('-A','-ao','--active_only', help="Show only active devices (positive read/write activity)", action="store_true")
	parser.add_argument('-R','--full', help="Show full device information, do not collapse drive info when length > console length", action="store_true")
	parser.add_argument('-P','--pseudo', help="Include pseudo file systems as well (tmpfs / nfs / cifs etc.)", action="store_true")
	parser.add_argument('-o','--output', help="Specify which output columns to print.Use comma to separate columns. default: all available", default="all", type=str)
	parser.add_argument('-x','--exclude', help="Specify which output columns to exclude.Use comma to separate columns. default: none", default="", type=str)
	parser.add_argument('--show_zero_size_devices', help="Show devices with zero size", action="store_true")
	parser.add_argument('print_period', nargs='?', default=0, type=int, help="If specified as a number, repeat the output every N seconds")
	parser.add_argument('-V', '--version', action='version', version=f"%(prog)s {version} @ {COMMIT_DATE} stat drives by pan@zopyr.us")

	args = parser.parse_args()
	tptDict = {}
	while True:
		results = get_drives_info(print_bytes = args.bytes, use_1024 = not args.si, 
							mounted_only=args.mounted_only, best_only=args.best_only, 
							formated_only=args.formated_only, show_zero_size_devices=args.show_zero_size_devices,
							pseudo=args.pseudo,tptDict=tptDict,full=args.full,active_only=args.active_only,output=args.output,exclude=args.exclude)
		if args.json:
			import json
			print(json.dumps(results, indent=1),flush=True)
		else:
			print(multiCMD.pretty_format_table(results,full=args.full),flush=True)
		if args.print_period > 0:
			try:
				time.sleep(args.print_period)
			except KeyboardInterrupt:
				break
		else:
			break


if __name__ == "__main__":
	main()