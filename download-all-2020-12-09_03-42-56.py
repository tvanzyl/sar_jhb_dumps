#!/usr/bin/python

# Usage:
#
#    In a terminal/command line, cd to the directory where this file lives. Then...
#
#    With embedded urls: ( download the hardcoded list of files in the 'files =' block below)
#
#       python ./download-all-2020-12-09_13-42-55.py
#
#    Download all files in a Metalink/CSV: (downloaded from ASF Vertex)
#
#       python ./download-all-2020-12-09_13-42-55.py /path/to/downloads.metalink localmetalink.metalink localcsv.csv
#
#    Compatibility: python >= 2.6.5, 2.7.5, 3.0
#
#    If downloading from a trusted source with invalid SSL Certs, use --insecure to ignore
#
#    For more information on bulk downloads, navigate to:
#        https://asf.alaska.edu/how-to/data-tools/data-tools/#bulk_download
#
#
#
#    This script was generated by the Alaska Satellite Facility's bulk download service.
#    For more information on the service, navigate to:
#        http://bulk-download.asf.alaska.edu/help
#

import sys, csv
import os, os.path
import tempfile, shutil
import re

import base64
import time
import getpass
import ssl
import signal
import socket

import xml.etree.ElementTree as ET

#############
# This next block is a bunch of Python 2/3 compatability

try:
   # Python 2.x Libs
   from urllib2 import build_opener, install_opener, Request, urlopen, HTTPError
   from urllib2 import URLError, HTTPSHandler,  HTTPHandler, HTTPCookieProcessor

   from cookielib import MozillaCookieJar
   from StringIO import StringIO

except ImportError as e:

   # Python 3.x Libs
   from urllib.request import build_opener, install_opener, Request, urlopen
   from urllib.request import HTTPHandler, HTTPSHandler, HTTPCookieProcessor
   from urllib.error import HTTPError, URLError

   from http.cookiejar import MozillaCookieJar
   from io import StringIO

###
# Global variables intended for cross-thread modification
abort = False

###
# A routine that handles trapped signals
def signal_handler(sig, frame):
    global abort
    sys.stderr.output("\n > Caught Signal. Exiting!\n")
    abort = True # necessary to cause the program to stop
    raise SystemExit  # this will only abort the thread that the ctrl+c was caught in

class bulk_downloader:
    def __init__(self):
        # List of files to download
        self.files = [ "https://datapool.asf.alaska.edu/SLC/SA/S1A_IW_SLC__1SDV_20201122T164650_20201122T164717_035363_0421C7_2335.zip",
                       "https://datapool.asf.alaska.edu/SLC/SA/S1A_IW_SLC__1SDV_20201110T164651_20201110T164718_035188_041BBE_DA93.zip",
                       "https://datapool.asf.alaska.edu/SLC/SA/S1A_IW_SLC__1SDV_20201029T164651_20201029T164718_035013_0415A5_B18A.zip",
                       "https://datapool.asf.alaska.edu/SLC/SA/S1A_IW_SLC__1SDV_20201017T164651_20201017T164718_034838_040FAD_4339.zip",
                       "https://datapool.asf.alaska.edu/SLC/SA/S1A_IW_SLC__1SDV_20201005T164651_20201005T164718_034663_040989_1A89.zip",
                       "https://datapool.asf.alaska.edu/SLC/SA/S1A_IW_SLC__1SDV_20200923T164651_20200923T164718_034488_040366_2A6C.zip",
                       "https://datapool.asf.alaska.edu/SLC/SA/S1A_IW_SLC__1SDV_20200911T164650_20200911T164717_034313_03FD31_7A3E.zip",
                       "https://datapool.asf.alaska.edu/SLC/SA/S1A_IW_SLC__1SDV_20200830T164650_20200830T164717_034138_03F711_E0E7.zip",
                       "https://datapool.asf.alaska.edu/SLC/SA/S1A_IW_SLC__1SDV_20200818T164649_20200818T164716_033963_03F0E5_53D6.zip",
                       "https://datapool.asf.alaska.edu/SLC/SA/S1A_IW_SLC__1SDV_20200806T164648_20200806T164715_033788_03EAC0_0C95.zip",
                       "https://datapool.asf.alaska.edu/SLC/SA/S1A_IW_SLC__1SDV_20200725T164648_20200725T164715_033613_03E550_D106.zip",
                       "https://datapool.asf.alaska.edu/SLC/SA/S1A_IW_SLC__1SDV_20200713T164647_20200713T164714_033438_03DFF0_9AAA.zip",
                       "https://datapool.asf.alaska.edu/SLC/SA/S1A_IW_SLC__1SDV_20200701T164646_20200701T164713_033263_03DA9A_B7C6.zip",
                       "https://datapool.asf.alaska.edu/SLC/SA/S1A_IW_SLC__1SDV_20200619T164646_20200619T164712_033088_03D54B_A4D3.zip",
                       "https://datapool.asf.alaska.edu/SLC/SA/S1A_IW_SLC__1SDV_20200607T164645_20200607T164712_032913_03D004_A8FB.zip",
                       "https://datapool.asf.alaska.edu/SLC/SA/S1A_IW_SLC__1SDV_20200526T164644_20200526T164711_032738_03CAD9_DBD6.zip",
                       "https://datapool.asf.alaska.edu/SLC/SA/S1A_IW_SLC__1SDV_20200514T164643_20200514T164710_032563_03C58A_BAA6.zip",
                       "https://datapool.asf.alaska.edu/SLC/SA/S1A_IW_SLC__1SDV_20200502T164643_20200502T164710_032388_03BFFD_B41A.zip",
                       "https://datapool.asf.alaska.edu/SLC/SA/S1A_IW_SLC__1SDV_20200420T164642_20200420T164709_032213_03B9D4_2BB5.zip",
                       "https://datapool.asf.alaska.edu/SLC/SA/S1A_IW_SLC__1SDV_20200408T164642_20200408T164708_032038_03B3AF_76FE.zip",
                       "https://datapool.asf.alaska.edu/SLC/SA/S1A_IW_SLC__1SDV_20200327T164641_20200327T164708_031863_03AD81_3B77.zip",
                       "https://datapool.asf.alaska.edu/SLC/SA/S1A_IW_SLC__1SDV_20200315T164641_20200315T164708_031688_03A758_0A06.zip",
                       "https://datapool.asf.alaska.edu/SLC/SA/S1A_IW_SLC__1SDV_20200303T164641_20200303T164708_031513_03A149_2666.zip",
                       "https://datapool.asf.alaska.edu/SLC/SA/S1A_IW_SLC__1SDV_20200220T164641_20200220T164708_031338_039B3D_22A6.zip",
                       "https://datapool.asf.alaska.edu/SLC/SA/S1A_IW_SLC__1SDV_20200208T164641_20200208T164708_031163_03953A_3447.zip",
                       "https://datapool.asf.alaska.edu/SLC/SA/S1A_IW_SLC__1SDV_20200127T164642_20200127T164709_030988_038F1B_3D46.zip",
                       "https://datapool.asf.alaska.edu/SLC/SA/S1A_IW_SLC__1SDV_20200115T164642_20200115T164709_030813_0388F1_50FF.zip",
                       "https://datapool.asf.alaska.edu/SLC/SA/S1A_IW_SLC__1SDV_20200103T164642_20200103T164709_030638_0382D3_3933.zip",
                       "https://datapool.asf.alaska.edu/SLC/SA/S1A_IW_SLC__1SDV_20191222T164643_20191222T164710_030463_037CCA_B6EE.zip",
                       "https://datapool.asf.alaska.edu/SLC/SA/S1A_IW_SLC__1SDV_20191210T164644_20191210T164710_030288_0376C0_B885.zip",
                       "https://datapool.asf.alaska.edu/SLC/SA/S1A_IW_SLC__1SDV_20191128T164644_20191128T164711_030113_0370BB_D19C.zip",
                       "https://datapool.asf.alaska.edu/SLC/SA/S1A_IW_SLC__1SDV_20191116T164644_20191116T164711_029938_036AA9_B59A.zip",
                       "https://datapool.asf.alaska.edu/SLC/SA/S1A_IW_SLC__1SDV_20191104T164644_20191104T164711_029763_036484_9291.zip",
                       "https://datapool.asf.alaska.edu/SLC/SA/S1A_IW_SLC__1SDV_20191023T164644_20191023T164711_029588_035E63_CFE0.zip",
                       "https://datapool.asf.alaska.edu/SLC/SA/S1A_IW_SLC__1SDV_20191011T164644_20191011T164711_029413_035863_D90E.zip",
                       "https://datapool.asf.alaska.edu/SLC/SA/S1A_IW_SLC__1SDV_20190929T164644_20190929T164711_029238_035261_0BD5.zip",
                       "https://datapool.asf.alaska.edu/SLC/SA/S1A_IW_SLC__1SDV_20190917T164644_20190917T164711_029063_034C5C_4245.zip",
                       "https://datapool.asf.alaska.edu/SLC/SA/S1A_IW_SLC__1SDV_20190905T164643_20190905T164710_028888_03464B_A689.zip",
                       "https://datapool.asf.alaska.edu/SLC/SA/S1A_IW_SLC__1SDV_20190824T164643_20190824T164710_028713_03402F_C1BD.zip",
                       "https://datapool.asf.alaska.edu/SLC/SA/S1A_IW_SLC__1SDV_20190812T164642_20190812T164709_028538_033A27_066D.zip",
                       "https://datapool.asf.alaska.edu/SLC/SA/S1A_IW_SLC__1SDV_20190731T164641_20190731T164708_028363_033486_A964.zip",
                       "https://datapool.asf.alaska.edu/SLC/SA/S1A_IW_SLC__1SDV_20190719T164641_20190719T164708_028188_032F2D_9ADB.zip",
                       "https://datapool.asf.alaska.edu/SLC/SA/S1A_IW_SLC__1SDV_20190707T164640_20190707T164707_028013_0329E7_3559.zip",
                       "https://datapool.asf.alaska.edu/SLC/SA/S1A_IW_SLC__1SDV_20190625T164639_20190625T164706_027838_032491_C852.zip",
                       "https://datapool.asf.alaska.edu/SLC/SA/S1A_IW_SLC__1SDV_20190613T164638_20190613T164705_027663_031F5A_1066.zip",
                       "https://datapool.asf.alaska.edu/SLC/SA/S1A_IW_SLC__1SDV_20190601T164638_20190601T164705_027488_031A0B_C095.zip",
                       "https://datapool.asf.alaska.edu/SLC/SA/S1A_IW_SLC__1SDV_20190520T164637_20190520T164704_027313_031499_DEE6.zip",
                       "https://datapool.asf.alaska.edu/SLC/SA/S1A_IW_SLC__1SDV_20190508T164636_20190508T164703_027138_030F21_5A15.zip",
                       "https://datapool.asf.alaska.edu/SLC/SA/S1A_IW_SLC__1SDV_20190426T164636_20190426T164703_026963_0308E6_0E89.zip",
                       "https://datapool.asf.alaska.edu/SLC/SA/S1A_IW_SLC__1SDV_20190414T164635_20190414T164702_026788_030295_B3D7.zip",
                       "https://datapool.asf.alaska.edu/SLC/SA/S1A_IW_SLC__1SDV_20190402T164635_20190402T164702_026613_02FC2F_3B8A.zip",
                       "https://datapool.asf.alaska.edu/SLC/SA/S1A_IW_SLC__1SDV_20190321T164635_20190321T164702_026438_02F5B7_0427.zip",
                       "https://datapool.asf.alaska.edu/SLC/SA/S1A_IW_SLC__1SDV_20190309T164635_20190309T164702_026263_02EF4A_91D6.zip",
                       "https://datapool.asf.alaska.edu/SLC/SA/S1A_IW_SLC__1SDV_20190225T164635_20190225T164702_026088_02E8FA_461F.zip",
                       "https://datapool.asf.alaska.edu/SLC/SA/S1A_IW_SLC__1SDV_20190213T164635_20190213T164702_025913_02E2B5_D0AA.zip",
                       "https://datapool.asf.alaska.edu/SLC/SA/S1A_IW_SLC__1SDV_20190201T164635_20190201T164702_025738_02DC82_D2C6.zip",
                       "https://datapool.asf.alaska.edu/SLC/SA/S1A_IW_SLC__1SDV_20190120T164636_20190120T164703_025563_02D622_2EBE.zip",
                       "https://datapool.asf.alaska.edu/SLC/SA/S1A_IW_SLC__1SDV_20190108T164636_20190108T164703_025388_02CFC8_6B8C.zip",
                       "https://datapool.asf.alaska.edu/SLC/SA/S1A_IW_SLC__1SDV_20181227T164636_20181227T164703_025213_02C976_BCA5.zip",
                       "https://datapool.asf.alaska.edu/SLC/SA/S1A_IW_SLC__1SDV_20181215T164637_20181215T164704_025038_02C31E_2789.zip",
                       "https://datapool.asf.alaska.edu/SLC/SA/S1A_IW_SLC__1SDV_20181203T164637_20181203T164704_024863_02BCF1_364A.zip",
                       "https://datapool.asf.alaska.edu/SLC/SA/S1A_IW_SLC__1SDV_20181121T164638_20181121T164705_024688_02B6E0_CCDF.zip",
                       "https://datapool.asf.alaska.edu/SLC/SA/S1A_IW_SLC__1SDV_20181109T164638_20181109T164705_024513_02B070_D904.zip"
                       ]

        # Local stash of cookies so we don't always have to ask
        self.cookie_jar_path = os.path.join( os.path.expanduser('~'), ".bulk_download_cookiejar.txt")
        self.cookie_jar = None

        self.asf_urs4 = { 'url': 'https://urs.earthdata.nasa.gov/oauth/authorize',
                 'client': 'BO_n7nTIlMljdvU6kRRB3g',
                 'redir': 'https://auth.asf.alaska.edu/login'}

        # Make sure we can write it our current directory
        if os.access(os.getcwd(), os.W_OK) is False:
            print ("WARNING: Cannot write to current path! Check permissions for {0}".format(os.getcwd()))
            exit(-1)

        # For SSL
        self.context = {}

        # Check if user handed in a Metalink or CSV:
        if len(sys.argv) > 0:
            download_files = []
            input_files = []
            for arg in sys.argv[1:]:
                if arg == '--insecure':
                    try:
                        ctx = ssl.create_default_context()
                        ctx.check_hostname = False
                        ctx.verify_mode = ssl.CERT_NONE
                        self.context['context'] = ctx
                    except AttributeError:
                        # Python 2.6 won't complain about SSL Validation
                        pass

                elif arg.endswith('.metalink') or arg.endswith('.csv'):
                    if os.path.isfile( arg ):
                        input_files.append( arg )
                        if arg.endswith('.metalink'):
                            new_files = self.process_metalink(arg)
                        else:
                            new_files = self.process_csv(arg)
                        if new_files is not None:
                            for file_url in (new_files):
                                download_files.append( file_url )
                    else:
                         print (" > I cannot find the input file you specified: {0}".format(arg))
                else:
                    print (" > Command line argument '{0}' makes no sense, ignoring.".format(arg))

            if len(input_files) > 0:
                if len(download_files) > 0:
                    print (" > Processing {0} downloads from {1} input files. ".format(len(download_files), len(input_files)))
                    self.files = download_files
                else:
                    print (" > I see you asked me to download files from {0} input files, but they had no downloads!".format(len(input_files)))
                    print (" > I'm super confused and exiting.")
                    exit(-1)

        # Make sure cookie_jar is good to go!
        self.get_cookie()

         # summary
        self.total_bytes = 0
        self.total_time = 0
        self.cnt = 0
        self.success = []
        self.failed = []
        self.skipped = []


    # Get and validate a cookie
    def get_cookie(self):
       if os.path.isfile(self.cookie_jar_path):
          self.cookie_jar = MozillaCookieJar()
          self.cookie_jar.load(self.cookie_jar_path)

          # make sure cookie is still valid
          if self.check_cookie():
             print(" > Re-using previous cookie jar.")
             return True
          else:
             print(" > Could not validate old cookie Jar")

       # We don't have a valid cookie, prompt user or creds
       print ("No existing URS cookie found, please enter Earthdata username & password:")
       print ("(Credentials will not be stored, saved or logged anywhere)")

       # Keep trying 'till user gets the right U:P
       while self.check_cookie() is False:
          self.get_new_cookie()

       return True

    # Validate cookie before we begin
    def check_cookie(self):

       if self.cookie_jar is None:
          print (" > Cookiejar is bunk: {0}".format(self.cookie_jar))
          return False

       # File we know is valid, used to validate cookie
       file_check = 'https://urs.earthdata.nasa.gov/profile'

       # Apply custom Redirect Hanlder
       opener = build_opener(HTTPCookieProcessor(self.cookie_jar), HTTPHandler(), HTTPSHandler(**self.context))
       install_opener(opener)

       # Attempt a HEAD request
       request = Request(file_check)
       request.get_method = lambda : 'HEAD'
       try:
          print (" > attempting to download {0}".format(file_check))
          response = urlopen(request, timeout=30)
          resp_code = response.getcode()
          # Make sure we're logged in
          if not self.check_cookie_is_logged_in(self.cookie_jar):
             return False

          # Save cookiejar
          self.cookie_jar.save(self.cookie_jar_path)

       except HTTPError:
          # If we ge this error, again, it likely means the user has not agreed to current EULA
          print ("\nIMPORTANT: ")
          print ("Your user appears to lack permissions to download data from the ASF Datapool.")
          print ("\n\nNew users: you must first log into Vertex and accept the EULA. In addition, your Study Area must be set at Earthdata https://urs.earthdata.nasa.gov")
          exit(-1)

       # This return codes indicate the USER has not been approved to download the data
       if resp_code in (300, 301, 302, 303):
          try:
             redir_url = response.info().getheader('Location')
          except AttributeError:
             redir_url = response.getheader('Location')

          #Funky Test env:
          if ("vertex-retired.daac.asf.alaska.edu" in redir_url and "test" in self.asf_urs4['redir']):
             print ("Cough, cough. It's dusty in this test env!")
             return True

          print ("Redirect ({0}) occured, invalid cookie value!".format(resp_code))
          return False

       # These are successes!
       if resp_code in (200, 307):
          return True

       return False

    def get_new_cookie(self):
       # Start by prompting user to input their credentials

       # Another Python2/3 workaround
       try:
          new_username = raw_input("Username: ")
       except NameError:
          new_username = input("Username: ")
       new_password = getpass.getpass(prompt="Password (will not be displayed): ")

       # Build URS4 Cookie request
       auth_cookie_url = self.asf_urs4['url'] + '?client_id=' + self.asf_urs4['client'] + '&redirect_uri=' + self.asf_urs4['redir'] + '&response_type=code&state='

       try:
          #python2
          user_pass = base64.b64encode (bytes(new_username+":"+new_password))
       except TypeError:
          #python3
          user_pass = base64.b64encode (bytes(new_username+":"+new_password, "utf-8"))
          user_pass = user_pass.decode("utf-8")

       # Authenticate against URS, grab all the cookies
       self.cookie_jar = MozillaCookieJar()
       opener = build_opener(HTTPCookieProcessor(self.cookie_jar), HTTPHandler(), HTTPSHandler(**self.context))
       request = Request(auth_cookie_url, headers={"Authorization": "Basic {0}".format(user_pass)})

       # Watch out cookie rejection!
       try:
          response = opener.open(request)
       except HTTPError as e:
          if "WWW-Authenticate" in e.headers and "Please enter your Earthdata Login credentials" in e.headers["WWW-Authenticate"]:
             print (" > Username and Password combo was not successful. Please try again.")
             return False
          else:
             # If an error happens here, the user most likely has not confirmed EULA.
             print ("\nIMPORTANT: There was an error obtaining a download cookie!")
             print ("Your user appears to lack permission to download data from the ASF Datapool.")
             print ("\n\nNew users: you must first log into Vertex and accept the EULA. In addition, your Study Area must be set at Earthdata https://urs.earthdata.nasa.gov")
             exit(-1)
       except URLError as e:
          print ("\nIMPORTANT: There was a problem communicating with URS, unable to obtain cookie. ")
          print ("Try cookie generation later.")
          exit(-1)

       # Did we get a cookie?
       if self.check_cookie_is_logged_in(self.cookie_jar):
          #COOKIE SUCCESS!
          self.cookie_jar.save(self.cookie_jar_path)
          return True

       # if we aren't successful generating the cookie, nothing will work. Stop here!
       print ("WARNING: Could not generate new cookie! Cannot proceed. Please try Username and Password again.")
       print ("Response was {0}.".format(response.getcode()))
       print ("\n\nNew users: you must first log into Vertex and accept the EULA. In addition, your Study Area must be set at Earthdata https://urs.earthdata.nasa.gov")
       exit(-1)

    # make sure we're logged into URS
    def check_cookie_is_logged_in(self, cj):
       for cookie in cj:
          if cookie.name == 'urs_user_already_logged':
              # Only get this cookie if we logged in successfully!
              return True

       return False


    # Download the file
    def download_file_with_cookiejar(self, url, file_count, total, recursion=False):
       # see if we've already download this file and if it is that it is the correct size
       download_file = os.path.basename(url).split('?')[0]
       if os.path.isfile(download_file):
          try:
             request = Request(url)
             request.get_method = lambda : 'HEAD'
             response = urlopen(request, timeout=30)
             remote_size = self.get_total_size(response)
             # Check that we were able to derive a size.
             if remote_size:
                 local_size = os.path.getsize(download_file)
                 if remote_size < (local_size+(local_size*.01)) and remote_size > (local_size-(local_size*.01)):
                     print (" > Download file {0} exists! \n > Skipping download of {1}. ".format(download_file, url))
                     return None,None
                 #partial file size wasn't full file size, lets blow away the chunk and start again
                 print (" > Found {0} but it wasn't fully downloaded. Removing file and downloading again.".format(download_file))
                 os.remove(download_file)

          except ssl.CertificateError as e:
             print (" > ERROR: {0}".format(e))
             print (" > Could not validate SSL Cert. You may be able to overcome this using the --insecure flag")
             return False,None

          except HTTPError as e:
             if e.code == 401:
                 print (" > IMPORTANT: Your user may not have permission to download this type of data!")
             else:
                 print (" > Unknown Error, Could not get file HEAD: {0}".format(e))

          except URLError as e:
             print ("URL Error (from HEAD): {0}, {1}".format( e.reason, url))
             if "ssl.c" in "{0}".format(e.reason):
                 print ("IMPORTANT: Remote location may not be accepting your SSL configuration. This is a terminal error.")
             return False,None

       # attempt https connection
       try:
          request = Request(url)
          response = urlopen(request, timeout=30)

          # Watch for redirect
          if response.geturl() != url:

             # See if we were redirect BACK to URS for re-auth.
             if 'https://urs.earthdata.nasa.gov/oauth/authorize' in response.geturl():

                 if recursion:
                     print (" > Entering seemingly endless auth loop. Aborting. ")
                     return False, None

                 # make this easier. If there is no app_type=401, add it
                 new_auth_url = response.geturl()
                 if "app_type" not in new_auth_url:
                     new_auth_url += "&app_type=401"

                 print (" > While attempting to download {0}....".format(url))
                 print (" > Need to obtain new cookie from {0}".format(new_auth_url))
                 old_cookies = [cookie.name for cookie in self.cookie_jar]
                 opener = build_opener(HTTPCookieProcessor(self.cookie_jar), HTTPHandler(), HTTPSHandler(**self.context))
                 request = Request(new_auth_url)
                 try:
                     response = opener.open(request)
                     for cookie in self.cookie_jar:
                         if cookie.name not in old_cookies:
                              print (" > Saved new cookie: {0}".format(cookie.name))

                              # A little hack to save session cookies
                              if cookie.discard:
                                   cookie.expires = int(time.time()) + 60*60*24*30
                                   print (" > Saving session Cookie that should have been discarded! ")

                     self.cookie_jar.save(self.cookie_jar_path, ignore_discard=True, ignore_expires=True)
                 except HTTPError as e:
                     print ("HTTP Error: {0}, {1}".format( e.code, url))
                     return False,None

                 # Okay, now we have more cookies! Lets try again, recursively!
                 print (" > Attempting download again with new cookies!")
                 return self.download_file_with_cookiejar(url, file_count, total, recursion=True)

             print (" > 'Temporary' Redirect download @ Remote archive:\n > {0}".format(response.geturl()))

          # seems to be working
          print ("({0}/{1}) Downloading {2}".format(file_count, total, url))

          # Open our local file for writing and build status bar
          tf = tempfile.NamedTemporaryFile(mode='w+b', delete=False, dir='.')
          self.chunk_read(response, tf, report_hook=self.chunk_report)

          # Reset download status
          sys.stdout.write('\n')

          tempfile_name = tf.name
          tf.close()

       #handle errors
       except HTTPError as e:
          print ("HTTP Error: {0}, {1}".format( e.code, url))

          if e.code == 401:
             print (" > IMPORTANT: Your user does not have permission to download this type of data!")

          if e.code == 403:
             print (" > Got a 403 Error trying to download this file.  ")
             print (" > You MAY need to log in this app and agree to a EULA. ")

          return False,None

       except URLError as e:
          print ("URL Error (from GET): {0}, {1}, {2}".format(e, e.reason, url))
          if "ssl.c" in "{0}".format(e.reason):
              print ("IMPORTANT: Remote location may not be accepting your SSL configuration. This is a terminal error.")
          return False,None

       except socket.timeout as e:
           print (" > timeout requesting: {0}; {1}".format(url, e))
           return False,None

       except ssl.CertificateError as e:
          print (" > ERROR: {0}".format(e))
          print (" > Could not validate SSL Cert. You may be able to overcome this using the --insecure flag")
          return False,None

       # Return the file size
       shutil.copy(tempfile_name, download_file)
       os.remove(tempfile_name)
       file_size = self.get_total_size(response)
       actual_size = os.path.getsize(download_file)
       if file_size is None:
           # We were unable to calculate file size.
           file_size = actual_size
       return actual_size,file_size

    def get_redirect_url_from_error(self, error):
       find_redirect = re.compile(r"id=\"redir_link\"\s+href=\"(\S+)\"")
       print ("error file was: {}".format(error))
       redirect_url = find_redirect.search(error)
       if redirect_url:
          print("Found: {0}".format(redirect_url.group(0)))
          return (redirect_url.group(0))

       return None


    #  chunk_report taken from http://stackoverflow.com/questions/2028517/python-urllib2-progress-hook
    def chunk_report(self, bytes_so_far, file_size):
       if file_size is not None:
           percent = float(bytes_so_far) / file_size
           percent = round(percent*100, 2)
           sys.stdout.write(" > Downloaded %d of %d bytes (%0.2f%%)\r" %
               (bytes_so_far, file_size, percent))
       else:
           # We couldn't figure out the size.
           sys.stdout.write(" > Downloaded %d of unknown Size\r" % (bytes_so_far))

    #  chunk_read modified from http://stackoverflow.com/questions/2028517/python-urllib2-progress-hook
    def chunk_read(self, response, local_file, chunk_size=8192, report_hook=None):
       file_size = self.get_total_size(response)
       bytes_so_far = 0

       while 1:
          try:
             chunk = response.read(chunk_size)
          except:
             sys.stdout.write("\n > There was an error reading data. \n")
             break

          try:
             local_file.write(chunk)
          except TypeError:
             local_file.write(chunk.decode(local_file.encoding))
          bytes_so_far += len(chunk)

          if not chunk:
             break

          if report_hook:
             report_hook(bytes_so_far, file_size)

       return bytes_so_far

    def get_total_size(self, response):
       try:
          file_size = response.info().getheader('Content-Length').strip()
       except AttributeError:
          try:
             file_size = response.getheader('Content-Length').strip()
          except AttributeError:
             print ("> Problem getting size")
             return None

       return int(file_size)


    # Get download urls from a metalink file
    def process_metalink(self, ml_file):
       print ("Processing metalink file: {0}".format(ml_file))
       with open(ml_file, 'r') as ml:
          xml = ml.read()

       # Hack to remove annoying namespace
       it = ET.iterparse(StringIO(xml))
       for _, el in it:
          if '}' in el.tag:
             el.tag = el.tag.split('}', 1)[1]  # strip all namespaces
       root = it.root

       dl_urls = []
       ml_files = root.find('files')
       for dl in ml_files:
          dl_urls.append(dl.find('resources').find('url').text)

       if len(dl_urls) > 0:
          return dl_urls
       else:
          return None

    # Get download urls from a csv file
    def process_csv(self, csv_file):
       print ("Processing csv file: {0}".format(csv_file))

       dl_urls = []
       with open(csv_file, 'r') as csvf:
          try:
             csvr = csv.DictReader(csvf)
             for row in csvr:
                dl_urls.append(row['URL'])
          except csv.Error as e:
             print ("WARNING: Could not parse file %s, line %d: %s. Skipping." % (csv_file, csvr.line_num, e))
             return None
          except KeyError as e:
             print ("WARNING: Could not find URL column in file %s. Skipping." % (csv_file))

       if len(dl_urls) > 0:
          return dl_urls
       else:
          return None

    # Download all the files in the list
    def download_files(self):
        for file_name in self.files:

            # make sure we haven't ctrl+c'd or some other abort trap
            if abort == True:
              raise SystemExit

            # download counter
            self.cnt += 1

            # set a timer
            start = time.time()

            # run download
            size,total_size = self.download_file_with_cookiejar(file_name, self.cnt, len(self.files))

            # calculte rate
            end = time.time()

            # stats:
            if size is None:
                self.skipped.append(file_name)
            # Check to see that the download didn't error and is the correct size
            elif size is not False and (total_size < (size+(size*.01)) and total_size > (size-(size*.01))):
                # Download was good!
                elapsed = end - start
                elapsed = 1.0 if elapsed < 1 else elapsed
                rate = (size/1024**2)/elapsed

                print ("Downloaded {0}b in {1:.2f}secs, Average Rate: {2:.2f}MB/sec".format(size, elapsed, rate))

                # add up metrics
                self.total_bytes += size
                self.total_time += elapsed
                self.success.append( {'file':file_name, 'size':size } )

            else:
                print ("There was a problem downloading {0}".format(file_name))
                self.failed.append(file_name)

    def print_summary(self):
        # Print summary:
        print ("\n\nDownload Summary ")
        print ("--------------------------------------------------------------------------------")
        print ("  Successes: {0} files, {1} bytes ".format(len(self.success), self.total_bytes))
        for success_file in self.success:
           print ("           - {0}  {1:.2f}MB".format(success_file['file'],(success_file['size']/1024.0**2)))
        if len(self.failed) > 0:
           print ("  Failures: {0} files".format(len(self.failed)))
           for failed_file in self.failed:
              print ("          - {0}".format(failed_file))
        if len(self.skipped) > 0:
           print ("  Skipped: {0} files".format(len(self.skipped)))
           for skipped_file in self.skipped:
              print ("          - {0}".format(skipped_file))
        if len(self.success) > 0:
           print ("  Average Rate: {0:.2f}MB/sec".format( (self.total_bytes/1024.0**2)/self.total_time))
        print ("--------------------------------------------------------------------------------")


if __name__ == "__main__":
    # Setup a signal trap for SIGINT (Ctrl+C)
    signal.signal(signal.SIGINT, signal_handler)

    downloader = bulk_downloader()
    downloader.download_files()
    downloader.print_summary()
