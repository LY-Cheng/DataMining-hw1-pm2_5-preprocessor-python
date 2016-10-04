#coding=utf-8

from collections import defaultdict
import MySQLdb
import time
import sys

# log data list

FILE_NAMES = [
	'./data.log-20160918',
	'./data.log-20160919',
	'./data.log-20160920',
	'./data.log-20160921',
	'./data.log-20160922',
	'./data.log-20160923',
	'./data.log-20160924',
	'./data.log-20160925'
]

#FILE_NAMES = [ './data.log-20160918' ]

LOG_FILENAME = 'preprocessor_log_%s.log' % (time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime()))

# MySQL connect
conn = MySQLdb.connect(host="localhost",user="LiYu",passwd="password",db="datamining",charset='utf8')
cursor = conn.cursor()

outLogFile = open(LOG_FILENAME, 'w')

for fileName in FILE_NAMES:
	lineCounter = 0
	dataCounter = 0
	errCounter = 0
	rawlogfile = open(fileName, "r")
	
	print '=================== Start parsing file: %s ===================' % (fileName)
	outLogFile.write('=================== Start parsing file: %s ===================\n\n' % (fileName))
	
	startTime = time.time()
	
	for unhandledline in rawlogfile.readlines():
		line = unhandledline.strip()
		
		lineCounter += 1
		if lineCounter % 1000 == 0:
			print '.',
		if lineCounter % 100000 == 0:
			print ''
		
		# not empty line
		if line:
		
			# Split attributes
			attrs = line.split("|")
			dict = {'device_msg':attrs[0]}

			#print attrs[0]
			
			# Useful (data contained) line
			if len(attrs) != 1:
				for attr in attrs[1:]:
				
					# empty column(...||...)
					if attr:
						splitedAttr = attr.split("=")
						
						try:
							# no data in attr (...|ex=|...)
							if splitedAttr[1]:
								dict[splitedAttr[0]] = splitedAttr[1]
						except Exception as err:
							print ''
							print '******************* Error at %d *******************' % lineCounter
							print line
							print err
							outLogFile.write('******************* Error at %d *******************\n\n%s\n\n%s\n\n\n' % (lineCounter, line, err))
				
				dictClass = ",".join("%s" % (k) for k in dict.keys())
				dictValues = ",".join('"%s"' % (k) for k in dict.values())
				
				sqlquery = "INSERT INTO rawdata(%s) VALUES (%s) " % (dictClass, dictValues)
				
				try:
					cursor.execute(sqlquery)
					dataCounter += 1
						
				except Exception as err:
					errCounter += 1
					# error check
					print ''
					print '------------------- Error at %d -------------------' % lineCounter
					print line
					print ''
					print '>>', sqlquery
					print ''
					print dict
					print ''
					print err
					
					outLogFile.write('------------------- Error at %d -------------------\n\n%s\n\n>> %s\n\n%s\n\n%s\n\n\n' % (lineCounter, line, sqlquery, dict, err))
					
	conn.commit()
	elapsedTime  = time.time() - startTime
	
	print''
	print''
	print 'Lines:', lineCounter, ', Data:', dataCounter, ', Err:', errCounter, ', ElapsedTime:', elapsedTime
	print''
	outLogFile.write('Lines: %d, Data: %d, Err: %d, ElapsedTime: %lf\n\n\n\n' % (lineCounter, dataCounter, errCounter, elapsedTime))
	
conn.close()
outLogFile.close()
rawlogfile.close()