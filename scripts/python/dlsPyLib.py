#!/usr/bin/env python2.4

"""
dlsPyLib.py
Author: Andy Foster

A library of useful DLS Python modules
"""

import os, pysvn


def pathcheck(client, path):
  """
  This function checks that 'path' exists.
  """
  try:    
    junk = client.ls(path)
    ret  = 1
  except pysvn._pysvn.ClientError:
    ret  = 0
  return ret


def workingCopy(client):
  """
  This function checks whether the current directory is an SVN
  working directory.
  """
  try:
    ret = client.info('.')
  except pysvn._pysvn.ClientError:
    ret = ''
  return ret


def checkSVN_ROOT():
  """
  This function checks that the environment variable, SVN_ROOT, has been set.
  """
  try:    
    prefix = os.environ['SVN_ROOT']+'/diamond'
  except KeyError:
    prefix = ''
    print "SVN_ROOT environment variable must be set"
  return prefix
