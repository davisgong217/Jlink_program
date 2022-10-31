#q25q64fw flash memory programming 
#Author: Davis Gong
#Date: 2022.09.17

from __future__ import division, with_statement, print_function
import pylink
import os
import argparse
import time
import color_print

class segger():
	def __init__(self,**kwargs):
		self.colorprinter=color_print.color_print()
		self.sn=kwargs.get('sn',None)
		self.interface= kwargs.get('interface','swd')
		self.chip=kwargs.get('chip','')
		self.speed=kwargs.get('speed',4000)
		self.targetready=False
		
		self.port=pylink.JLink()
		self.port.open(self.sn)
		self.product_name=self.port.product_name
		if self.port.opened() and self.port.connected(): 
			self.colorprinter.color_print('-----Segger connected-----\n',color_print.FOREGROUND_DARKGREEN)
			if self.chip:
				if self.interface=='swd':
					self.port.set_tif(pylink.enums.JLinkInterfaces.SWD)
				elif self.interface=='jtag':
					self.port.set_tif(pylink.enums.JLinkInterfaces.JTAG)		
				elif self.interface=='spi':
					self.port.set_tif(pylink.enums.JLinkInterfaces.SPI)	
				try:
					print(f'chip:{self.chip}')
					self.port.connect(chip_name=self.chip,speed=self.speed)
					self.chipid=self.port.core_id()
					self.targetready=self.port.target_connected()
					if self.targetready:
						self.colorprinter.color_print('-----Target connected-----\n',color_print.FOREGROUND_DARKGREEN)
						print(f'chip id {hex(self.chipid)}')
				except:
					self.colorprinter.color_print('-----Target connect fail!!!-----\n',color_print.FOREGROUND_DARKRED)
		else: 
			self.colorprinter.color_print('-----Segger connect fail!!-----\n',color_print.FOREGROUND_DARKRED)
			
	def chip_erase(self):
		self.port.erase()

	def program(self,addr,filename):
		if self.port.flash_file(filename, addr)>=0:
			self.colorprinter.color_print('-----Programming success-----\n',color_print.FOREGROUND_DARKGREEN)
		else:
			self.colorprinter.color_print('-----Programming fail-----\n',color_print.FOREGROUND_DARKRED)
	
	def readbinfile(self,filename):
		self.colorprinter.color_print('-----Read bin file-----\n',color_print.FOREGROUND_DARKGREEN)
		size=os.path.getsize(filename)
		with open(filename,"rb") as binfile:
			print(f'bin file size: {size} bytes')
			data=[]
			for i in range(size):
				data.append(binfile.read(1)[0])
		self.binefiledata=data
		return data	
						
	def cleanup(self):
		self.colorprinter.color_print('-----HW tear down-----\n',color_print.FOREGROUND_DARKGREEN)
		if self.port:
			self.port.close()
				
def main():
	parser = argparse.ArgumentParser(description='Jlink program')
	parser.add_argument('--file', type=str, default ='privacymgr.bin')
	parser.add_argument('--addr', type=lambda x: int(x,0), default =0)
	parser.add_argument('--erase', type=bool, default=False)
	parser.add_argument('--program', type=bool, default=False)
	parser.add_argument('--speed', type=int, default=1000)
	parser.add_argument('--interface', type=str, default='swd')
	parser.add_argument('--chip', type=str, default='')
	parser.add_argument('--sn', type=int, default=None)
	args = parser.parse_args()

	dut=segger(sn=args.sn,speed=args.speed,chip=args.chip,interface=args.interface)
	if dut.targetready:	
		if args.erase:
			dut.chip_erase()
		if args.program:
			binfile=args.file
			if os.path.exists(binfile):
				dut.program(args.addr,binfile)
		dut.cleanup()	
		
if __name__ == "__main__":
	main()
