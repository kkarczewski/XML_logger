#! /usr/bin/env python3.4
#! -*- coding: utf-8 -*-

# #############################################################################
# standard phyton modules
# #############################################################################
import os
import sys
import string
import argparse

# #############################################################################
# constants, global variables
# #############################################################################
OUTPUT_ENCODING = 'utf-8'
DIRECTORY = './'
TEMP_PATH = SCRIPT_DIR+'/cache/'
LOGGER_PATH = SCRIPT_DIR+'/logfile.xml'
LOG_VERSION = 1.0
NAME = __file__
SPLIT_DIR = os.path.dirname(os.path.realpath(NAME))
SCRIPT_DIR = SPLIT_DIR + '/.' + os.path.basename(NAME)
LIB_DIR = SCRIPT_DIR + '/cache/lib/'
TMP_DIR = SPLIT_DIR + '/tmp/'
sys.path.insert(0, LIB_DIR)

# #############################################################################
# functions
# #############################################################################
# List of lib to install
import_list = [
   ('sqlalchemy', '1.0.8', 'SQLAlchemy-1.0.8.egg-info'),
   ('paramiko', '1.15.2', 'paramiko-1.15.2.dist-info'),
   ('colorama', '0.3.3', 'colorama-0.3.3.egg-info'),
   ('pymysql', '0.6.7', 'PyMySQL-0.6.7.dist-info')]
for line in import_list:
   try:
      if os.path.isdir(LIB_DIR+line[2]):
         pass
         #print('Found installed '+line[0]+line[1]+' in '+line[2])
      else:
         try:
            import pip
         except:
            print("Use sudo apt-get install python3-pip")
            #TO DO - change script to use get-pip unless installing pip as root
            # Probably solution for problem with installing pip. 
            # https://github.com/pypa/get-pip
            sys.exit(1)
         print('No lib '+line[0]+'-'+line[1])
         os.system("python"+sys.version[0:3]+" -m pip install '"+line[0]+'=='+line[1]+"' --target="+LIB_DIR+" -b "+TMP_DIR)
      module_obj = __import__(line[0])
      globals()[line[0]] = module_obj
   except ImportError as e:
      print(line[0]+' is not installed')

# Pretty Print for xml log system (xml.etree don't support it, recommend to use lxml)
# lxml will be used in next version
def indent(elem, level=0):
  i = "\n" + level*"  "
  if len(elem):
    if not elem.text or not elem.text.strip():
      elem.text = i + "  "
    if not elem.tail or not elem.tail.strip():
      elem.tail = i
    for elem in elem:
      indent(elem, level+1)
    if not elem.tail or not elem.tail.strip():
      elem.tail = i
  else:
    if level and (not elem.tail or not elem.tail.strip()):
      elem.tail = i

#XML logging system 
#Will be refactored to lxml in next version
def my_logger(ERROR_FLAG,subcmd,outmsg):
   import xml.etree.ElementTree as ET # in case of usege - move on the top of the file to the list of libs in use
   import datetime # in case of usege - move on the top of the file to the list of libs in use
   import base64 # in case of usege - move on the top of the file to the list of libs in use
   
   id_log = 1
   if not os.path.exists(LOGGER_PATH):
      root = ET.Element('root')
      root.set('version','1.0')
   else:
      tree = ET.parse(LOGGER_PATH)
      root = tree.getroot()
      for child in root:
         id_log+=1
   log = ET.SubElement(root, 'log')
   log.set('id_log',str(id_log))
   date = ET.SubElement(log,'date')
   date.text = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S,%f')
   cmdline = str()
   for line in sys.argv:
      cmdline += line+' '
   command = ET.SubElement(log,'command')
   command.set('encoding','plain')
   command.text = cmdline
   subcommands = ET.SubElement(log,'subcommands')
   subcommands.set('error_flag',ERROR_FLAG)
   subcmd_str=str()
   for one in subcmd:
      subcmd_str+=one+','
   subcommands.text = subcmd_str[:-1]
   outmsg_str = str()
   for one in outmsg:
      outmsg_str+=one+','
   msg = (base64.b64encode(outmsg_str.encode(OUTPUT_ENCODING))).decode(OUTPUT_ENCODING)
   output = ET.SubElement(log,'output')
   output.set('encoding','base64')
   output.text = msg
   indent(root)
   if not os.path.exists(LOGGER_PATH):
      tree = ET.ElementTree(root)
   tree.write(LOGGER_PATH,encoding=OUTPUT_ENCODING,xml_declaration=True,method='xml')

#Executing bash commands in terminal from python script. Fancy method with asterix as progress bar.
def os_call(*args,progress_char='*',verbose=1):
   import time # in case of usege - move on the top of the file to the list of libs in use
   n = 0
   done_cmd = list()
   out = list()
   for cmd in args:
      p = subprocess.Popen(cmd,stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, cwd=DIRECTORY)
      (output,err) = p.communicate()
      n = n+1
      ast = progress_char*n
      if err or 'ERROR' in str(output) or 'Exception' in str(output):
         done_cmd.append(cmd)
         ERROR_FLAG = 'T'
         print_err(cmd)
         if err:
            print_err(err.decode(OUTPUT_ENCODING))
            out.append(err.decode(OUTPUT_ENCODING))
            break
         else:
            print_err(output.decode(OUTPUT_ENCODING))
            out.append(output.decode(OUTPUT_ENCODING))
            break
      else:
         ERROR_FLAG = 'F'
         done_cmd.append(cmd)
         out.append(output.decode(OUTPUT_ENCODING))
         if verbose == 2:
            print(ast,end="\r")
            time.sleep(1)
            print_ok(cmd)
            print_ok(output.decode(OUTPUT_ENCODING))
         elif verbose == 1:
            print_ok(output.decode(OUTPUT_ENCODING))
         else:
            print(ast,end='\r')
   return ERROR_FLAG,done_cmd,out

# #############################################################################
# operations
# #############################################################################

def opt_test(*lines):
      ERROR_FLAG,done_cmd,out = os_call(*lines,progress_char='*',verbose=2)
      my_logger(ERROR_FLAG,done_cmd,out)

def opt_help():
   parser.print_help()
   msg = 'Printed help'
   msg = (base64.b64encode(('Printed help').encode(OUTPUT_ENCODING))).decode(OUTPUT_ENCODING)
   return msg 
   # #############################################################################
# main app 
# #############################################################################
if __name__ == '__main__':
# Reading arguments
   try:
      from sqlalchemy.sql import text
   except Exception as e:
      print_err('No sqlalchemy installation')
      print_err(e)
   parser = argparse.ArgumentParser(
      prog='template.py',
      description='Description script',
      epilog='Epilog script',
      add_help=True, 
      argument_default=argparse.SUPPRESS,
      formatter_class=argparse.RawTextHelpFormatter)
   parser.add_argument('test',
      nargs='?',
      help='Test command that will be logged in xml')
   subparsers = parser.add_subparsers()
   parser_subone = subparsers.add_parser('sub-arg',help='Decription subone')
   parser_subone.add_argument('sub-arg',
      nargs='?',
      help='Description subone')
   argv = sys.argv[1:]
   args = parser.parse_args(argv)
   try:
      if not len(sys.argv) > 1 or 'help' in args:
         opt_help()
      elif 'test' in args:
         opt_test(args.test)
      else:
         opt_help()
   except Exception as e:
      cmd = str()
      for one_arg in sys.argv:
         cmd+=one_arg+' '
      list_cmd=list()
      list_cmd.append(cmd)
      err_msg = str(e)
      my_logger('T',list_cmd,err_msg)
      print(e)
