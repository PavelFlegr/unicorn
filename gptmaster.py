import argparse
import sys
import uuid
import math
import binascii

GPT_HEADER_SIZE = 92

def toCHS(lba, heads_per_cylinder, sectors_per_track):
	cylinder = int(lba / (heads_per_cylinder * sectors_per_track))
	head = int(lba / sectors_per_track) % heads_per_cylinder
	sector = (lba % sectors_per_track) + 1
	
	return bytes([cylinder, head, sector])


def updateGPTcrc(gpt, partitionEntries):
	gpt[16:20] = bytes(4)
	gpt[88:92] = binascii.crc32(partitionEntries).to_bytes(4, "little")
	gpt[16:20] = binascii.crc32(gpt).to_bytes(4, "little")
	
	return gpt

def GPTHeaders(args):
	min_lba = math.ceil(16384 / args.block_size) + 2
	if args.first_usable_lba == None:
		args.first_usable_lba = min_lba
	if args.first_usable_lba < min_lba:
		print("first usable lba is less than 16384 bytes")
		sys.exit()
	t = bytearray()
	t[0: ] = b"EFI PART" #signature
	t[8: ] = 0x00010000.to_bytes(4, "little") #revision
	t[12:] = GPT_HEADER_SIZE.to_bytes(4, "little") #headersize
	t[16:] = bytes(4) #crc32 - 0 for computation
	t[20:] = bytes(4) #reserved
	t[24:] = bytes(8) #MyLBA - will be set later
	t[32:] = bytes(8) #AlternateLBA - will be set later
	t[40:] = args.first_usable_lba.to_bytes(8, "little") #FirstUsableLBA
	t[48:] = (args.blocks - 1).to_bytes(8, "little") #LastUsableLBA
	t[56:] = uuid.uuid4().bytes #DiskGUID
	t[72:] = 0x02.to_bytes(8, "little") #PartitionEntryLBA
	t[80:] = (128).to_bytes(4, "little") #NumberOfPartitionEntries
	t[84:] = args.partition_entry_size.to_bytes(4, "little") #SizeOfPartitionEntry
	t[88:] = bytes(4) #PartitionEntryArrayCRC32
	t[92:] = bytes(args.block_size - 92) #Reserved
	
	return t
	
def MBRHeaders(args):
	t = bytearray()
	t[0:  ] = bytes(440) #Boot code
	t[440:] = bytes(4) #Unique MBR Disk Signature
	t[444:] = bytes(2) #Unknown
	t[446:] = bytes(1) #BootIndicator
	t[447:] = 0x000200.to_bytes(3, "little") #startingCHS
	t[450:] = bytes([0xEE]) #OSType GPT Protective
	t[451:] = toCHS(args.blocks, args.heads_per_cylinder, args.sectors_per_track) #endingCHS
	t[454:] = bytes(0x01.to_bytes(4, "little")) #StartingLBA
	t[458:] = min(args.blocks - 1, 0xFFFFFFFF).to_bytes(4, "little") #SizeinLBA
	t[462:] = bytes(3*16) #3 empty partition records
	t[510:] = bytes([0x55, 0xAA]) #Signature
	
	return t
	
def init(args):
	if args.size % args.block_size != 0:
		print([args.size, args.block_size])
		print("size must be divisible by block size")
		sys.exit()
	args.blocks = int(args.size / args.block_size)
	mbr = MBRHeaders(args)
	gpt = GPTHeaders(args)
	partitionEntries = bytes((args.first_usable_lba - 2) * args.block_size)
	f = open(args.file, "wb")
	f.write(bytes(args.size))
	f.seek(0)
	f.write(mbr)
	f.seek(args.block_size) #gpt headers are in LBA 1
	gpt[24:32] = 0x01.to_bytes(8, "little")
	gpt[32:40] = args.blocks.to_bytes(8, "little")
	gpt = updateGPTcrc(gpt, partitionEntries)
	f.write(gpt)
	backupGPTpos = ((args.blocks - 1) * args.block_size)
	f.seek(backupGPTpos)
	gpt[24:32] = args.blocks.to_bytes(8, "little")
	gpt[32:40] = 0x01.to_bytes(8, "little")
	gpt = updateGPTcrc(gpt, partitionEntries)
	f.write(gpt)
	f.close()

parser = argparse.ArgumentParser(description="Disk image manager")
parser.add_argument("file", action="store", help="file to work with")
parser.add_argument("-init", dest="actions", action="append_const", help="initialize a new disk", const="init")
parser.add_argument("-size", help="size of the disk in bytes", type=int)
parser.add_argument("-block-size", dest="block_size", help="size of a logical block in bytes", type=int, default=512)
parser.add_argument("-first-usable-lba", dest="first_usable_lba", help="first usable lba, must be at least 16384 bytes", type=int, default=None)
parser.add_argument("-partition-entry-size", dest="partition_entry_size", help="partition entry, must be 128 * 2^n", type=int, default=128)
parser.add_argument("-heads-per-cylinder", dest="heads_per_cylinder", help="heads per cylinder", type=int, default=255)
parser.add_argument("-sectors-per-track", dest="sectors_per_track", help="sectors per track", type=int, default=63)

args = parser.parse_args()

if "init" in args.actions:
	init(args)