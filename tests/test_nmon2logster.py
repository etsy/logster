'''
Created on 16 jan 2018
@author: Grigory Bykov <gbykov@hotbox.ru>
'''

try:
    from unittest import mock 
except ImportError:
    from mock import mock
import unittest    
import time
from datetime import datetime
from io import StringIO
from contextlib import redirect_stdout, redirect_stderr
import fileinput
from parsers.NmonLogster import NmonLogster
import subprocess
from pathlib import Path
import logster_cli
import os
import shutil

class Test(unittest.TestCase):

    def setUp(self):

        self.out = StringIO()
        self.cvt = NmonLogster()
        self.cvt.timeShift = None

    def tearDown(self):
        self.cvt.timeShift = None

    def test_make_header(self):
        inline = ('CPU_ALL,CPU Total izh1,User%,'
                  'Sys%,Wait%,Idle%,Busy,PhysicalCPUs')
        header = self.cvt.make_header(inline)
        self.assertEqual(header, ["CPU_ALL", "CPU_Total_izh1",
                                  "User_", "Sys_", "Wait_", "Idle_",
                                  "Busy", "PhysicalCPUs"])

        inline = ('PCPU_ALL,PCPU Total izh1,User  ,'
                  'Sys  ,Wait  ,Idle  , Entitled Capacity ')
        header = self.cvt.make_header(inline)
        self.assertEqual(header, ["PCPU_ALL", "PCPU_Total_izh1",
                                  "User", "Sys", "Wait", "Idle",
                                  "Entitled_Capacity"])
        inline = ("NET,Network I/O vagrant,lo-read-KB/s,"
                  "eth0-read-KB/s,lo-write-KB/s,eth0-write-KB/s,")
        header = self.cvt.make_header(inline)
        self.assertEqual(header, ['NET',
                                  'Network_I_O_vagrant',
                                  'lo_read_KB_s',
                                  'eth0_read_KB_s',
                                  'lo_write_KB_s',
                                  'eth0_write_KB_s'])
        inline = ("JFSFILE,JFS Filespace %Used aix3,/,/home,/usr,"
                  "/var,/tmp,/admin,/opt,/var/adm/ras/livedump,"
                  "/usr/sys/inst.images,/dev/odm,/oracle,/data_pos")
        header = self.cvt.make_header(inline)
        self.assertEqual(header, [
            'JFSFILE',
            'JFS_Filespace__Used_aix3',
            '_',
            '_home',
            '_usr',
            '_var',
            '_tmp',
            '_admin',
            '_opt',
            '_var_adm_ras_livedump',
            '_usr_sys_inst_images',
            '_dev_odm',
            '_oracle',
            '_data_pos'])

    def test_read_nmon_line(self):
        header = self.cvt.make_header('PCPU_ALL,PCPU Total izh1,User  ,'
                                      'Sys  ,Wait  ,Idle  , '
                                      'Entitled Capacity ')
        line = "PCPU_ALL,T0001,26.95,7.03,6.0,59.99,256.00"
        dt = time.strptime("09-SEP-2014 09:10:10", "%d-%b-%Y %H:%M:%S")
        dt = datetime.fromtimestamp(time.mktime(dt))

        self.cvt.read_nmon_line(line, "PCPU_ALL", header, dt, "root")
        expected = [
            'root.PCPU_ALL.User 26.95 1410243010',
            'root.PCPU_ALL.Sys 7.03 1410243010',
            'root.PCPU_ALL.Wait 6.0 1410243010',
            'root.PCPU_ALL.Idle 59.99 1410243010',
            'root.PCPU_ALL.Entitled_Capacity 256.00 1410243010'
            ]
        
        for i in range(len(expected)):
            o = self.cvt.metrics[i]
            self.assertEqual(expected[i],
                             '%s %s %.0f' % (o.name, o.value, o.timestamp))
        
        

    def test_parse_line(self):
        path = os.path.join('..', 'tests', 'data', 'linux_nmon14g.nmon')
        for line in fileinput.input(path):
            self.cvt.parse_line(line)
#       print out.getvalue()
        output = self.cvt.get_state(0)
        length = len(output)
        self.assertEqual(620, length)
           
        expected = [
            'unspecified.vagrant.nmon.CPU001.User_ 5.4 1445948091',
            'unspecified.vagrant.nmon.CPU001.Sys_ 38.6 1445948091',
            'unspecified.vagrant.nmon.CPU001.Wait_ 1.1 1445948091',
            'unspecified.vagrant.nmon.CPU001.Idle_ 54.9 1445948091',
            'unspecified.vagrant.nmon.CPU_ALL.User_ 5.4 1445948091',
            'unspecified.vagrant.nmon.CPU_ALL.Sys_ 38.6 1445948091'
            ]
        
        for i in range(len(expected)):
            o = output[i]
            self.assertEqual(expected[i],
                             '%s %s %.0f' % (o.name, o.value, o.timestamp))
        
        expected_tail = [
            'unspecified.vagrant.nmon.DISKBSIZE.sda1 0.0 1445948111',
            'unspecified.vagrant.nmon.DISKBSIZE.sda2 0.0 1445948111',
            'unspecified.vagrant.nmon.DISKBSIZE.sda5 6.0 1445948111',
            'unspecified.vagrant.nmon.DISKBSIZE.dm_0 4.0 1445948111',
            'unspecified.vagrant.nmon.DISKBSIZE.dm_1 0.0 1445948111'
            ]
        for i in range(5, 0):
            o = output[length-i]
            self.assertEqual(expected_tail[5-i],
                             '%s %s %.0f' % (o.name, o.value, o.timestamp))
        
    def test_round_300(self):
        parser = NmonLogster('--roundTo 300')
        for line in fileinput.input("./data/linux_nmon14g.nmon"):
            parser.parse_line(line)
        output = parser.get_state(0)
        length = len(output)
        self.assertEqual(620, length)
           
        expected = [
            'unspecified.vagrant.nmon.CPU001.User_ 5.4 1445948100',
            'unspecified.vagrant.nmon.CPU001.Sys_ 38.6 1445948100',
            'unspecified.vagrant.nmon.CPU001.Wait_ 1.1 1445948100',
            'unspecified.vagrant.nmon.CPU001.Idle_ 54.9 1445948100',
            'unspecified.vagrant.nmon.CPU_ALL.User_ 5.4 1445948100',
            'unspecified.vagrant.nmon.CPU_ALL.Sys_ 38.6 1445948100'
            ]
        
        for i in range(len(expected)):
            o = output[i]
            self.assertEqual(expected[i],
                             '%s %s %.0f' % (o.name, o.value, o.timestamp))
        
        
    def test_round_time(self):
        dt = time.strptime("29-MAY-2015 18:03:26", "%d-%b-%Y %H:%M:%S")
        dt = datetime.fromtimestamp(time.mktime(dt))
        print(self.cvt.round_time(dt, 300))

    def test_date_shift(self):
        parser = NmonLogster('--startdate=24.06.2015')
        path = os.path.join('..', 'tests', 'data', 'linux_nmon14g.nmon')
        for line in fileinput.input(path):
            parser.parse_line(line)
        output = parser.get_state(0)
        length = len(output)
        expected = [
            'unspecified.vagrant.nmon.CPU001.User_ 5.4 1435061691',
            'unspecified.vagrant.nmon.CPU001.Sys_ 38.6 1435061691',
            'unspecified.vagrant.nmon.CPU001.Wait_ 1.1 1435061691',
            'unspecified.vagrant.nmon.CPU001.Idle_ 54.9 1435061691',
            'unspecified.vagrant.nmon.CPU_ALL.User_ 5.4 1435061691',
            'unspecified.vagrant.nmon.CPU_ALL.Sys_ 38.6 1435061691'
            ]
        
        for i in range(len(expected)):
            o = output[i]
            self.assertEqual(expected[i],
                             '%s %s %.0f' % (o.name, o.value, o.timestamp))

    def test_time_shift(self):
        parser = NmonLogster('--startdate=24.06.2015')
        path = os.path.join('..', 'tests', 'data', 'linux_nmon14g.nmon')
        for line in fileinput.input(path):
            parser.parse_line(line)
        output = parser.get_state(0)
        length = len(output)
        expected = [
            'unspecified.vagrant.nmon.CPU001.User_ 5.4 1435061691',
            'unspecified.vagrant.nmon.CPU001.Sys_ 38.6 1435061691',
            'unspecified.vagrant.nmon.CPU001.Wait_ 1.1 1435061691',
            'unspecified.vagrant.nmon.CPU001.Idle_ 54.9 1435061691',
            'unspecified.vagrant.nmon.CPU_ALL.User_ 5.4 1435061691',
            'unspecified.vagrant.nmon.CPU_ALL.Sys_ 38.6 1435061691'
            ]
        
        for i in range(len(expected)):
            o = output[i]
            self.assertEqual(expected[i],
                             '%s %s %.0f' % (o.name, o.value, o.timestamp))

        

    def test_main(self):
        state_path = os.path.join('..', 'tests', 'run',
                                  'pygtail-logster.parsers.NmonLogster.NmonLogster..-tests-data-linux_nmon16g.nmon.state')
        if os.path.exists(state_path):
            os.remove( state_path )
        out = StringIO()
        # [-p PREFIX] [-r ROUND] [-s STARTDATE] [filename]
        file_path = os.path.join('..', 'tests', 'data', 'linux_nmon16g.nmon')
        with redirect_stdout(out):
            with mock.patch('sys.argv',
                                     ['logster', 
                                      '-t', 'pygtail',
                                      'NmonLogster',
                                      '-o', 'stdout',
                                      '--locker=portalocker',
                                      '-l', 'run', '-s', 'run',
                                      file_path]):
                logster_cli.main()

        output = out.getvalue().split('\n')
        #print(output)
        length = len(output)
        self.assertEqual(68458, length)
        self.assertEqual(("1516863248.0"
                          " unspecified.vagrant-ubuntu-trusty-64.nmon.CPU001.User_ 45.3"), output[0])
        self.assertEqual(("1516866845.0 "
                          "unspecified.vagrant-ubuntu-trusty-64.nmon.DISKBSIZE.sda1 6.0"), output[length-2])
    
    def test_main_twice(self):
        src = os.path.join('..', 'tests', 'data',
                                  'linux_nmon16g.nmon.1')
        dst = os.path.join('..', 'tests', 'run',
                                  'linux_nmon16g_tmp.nmon')
        
        shutil.copy(src, dst)
        
        state_path = os.path.join('..', 'tests', 'run',
                                  'pygtail-logster.parsers.NmonLogster.NmonLogster..-tests-run-linux_nmon16g_tmp.nmon.state')
        
        if os.path.exists(state_path):
            os.remove( state_path )
        out = StringIO()
        # [-p PREFIX] [-r ROUND] [-s STARTDATE] [filename]
                
        with redirect_stdout(out):
            with mock.patch('sys.argv',
                                     ['logster', 
                                      '-t', 'pygtail',
                                      'NmonLogster',
                                      '-o', 'stdout',
                                      '--locker=portalocker',
                                      '-l', 'run', '-s', 'run',
                                      dst]):
                logster_cli.main()

        output = out.getvalue().split('\n')
        #print(output)
        length = len(output)
        self.assertEqual(68363, length)
        self.assertEqual(("1516863248.0"
                          " unspecified.vagrant-ubuntu-trusty-64.nmon.CPU001.User_ 45.3"), output[0])
        self.assertEqual(("1516866839.0"
                          " unspecified.vagrant-ubuntu-trusty-64.nmon.DISKBSIZE.sda1 6.0"), output[length-2])
        
        '''
        second run - emulate file append
        ZZZZ,T0720,10:54:05,25-JAN-2018
        '''
        out = StringIO()
        src = os.path.join('..', 'tests', 'data',
                                  'linux_nmon16g.nmon.2')
        
        with open(dst, 'a') as dstfile:
            with open(src) as srcfile:
                dstfile.write(srcfile.read())
        
        with redirect_stdout(out):
            with mock.patch('sys.argv',
                         ['logster', 
                          '-t', 'pygtail',
                          'NmonLogster',
                          '-o', 'stdout',
                          '--locker=portalocker',
                          '-l', 'run', '-s', 'run',
                          dst]):
                logster_cli.main()

        output = out.getvalue().split('\n')
        #print(output)
        length = len(output)
        self.assertEqual(96, length)
        self.assertEqual(("1516866845.0 unspecified.vagrant-ubuntu-trusty-64.nmon.CPU001.User_ 0.2"), output[0])
        self.assertEqual(("1516866845.0 "
                          "unspecified.vagrant-ubuntu-trusty-64.nmon.DISKBSIZE.sda1 6.0"), output[length-2])

    def test_main_parser_help(self):
        
        out = StringIO()
        
        file_path = os.path.join('..', 'tests', 'data', 'linux_nmon16g.nmon')
        with redirect_stderr (out):
            with mock.patch('sys.argv',
                                     ['logster', 
                                      '-t', 'pygtail',
                                      'NmonLogster',
                                      '--parser-help',
                                      '-o', 'stdout',
                                      '--locker=portalocker',
                                      '-l', 'run', '-s', 'run',
                                      file_path]):
                with self.assertRaises(BaseException) as context:
                    logster_cli.main()
                    
                self.assertFalse('This throws ' in str(context.exception))    
        
        
if __name__ == "__main__":
    unittest.main()
