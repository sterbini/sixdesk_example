import re
import os
import csv
import sys
import string
import os.path
import fileinput
import numpy as np
import pandas as pd
import glob, os, fnmatch
from subprocess import call
from tempfile import mkstemp
from os import fdopen, remove
import matplotlib.pyplot as plt
from shutil import copymode, move

#####################
# This script changes the voltage of the CCs RIGHT ANF LEFT of IP1
# There are 3 modes: weak, strong, both. This means that the CC bump is open for the weak beam, the strong beam and both. 
#####################

def multiple_replace(dict, text):
  regex = re.compile("(%s)" % "|".join(map(re.escape, dict.keys())))
  return regex.sub(lambda mo: dict[mo.string[mo.start():mo.end()]], text)

def replace_file(file_path,dict):
    fh, abs_path = mkstemp()
    with fdopen(fh,'w') as new_file:
        with open(file_path) as old_file:
            new_file.write(multiple_replace(dict,old_file.read()))
    copymode(file_path, abs_path)
    remove(file_path)
    move(abs_path, file_path)

#sixdesk_exe   = "/afs/cern.ch/work/s/skostogl/public/useful/SixDesk/utilities/bash"
sixdesk_exe   = "/afs/cern.ch/work/s/skostogl/private/sixdesk/SixDesk_fort13_new/SixDesk/utilities/bash"

# templates
template_mask       = 'HL_template.madx'
template_mask_py    = 'input_template.py'
template_config     = 'config_template.py'
template_fort3local = 'fort.3.local.template'
template_fort3      = 'fort.3.mother1_col_template'
template_six        = 'sixdeskenv.template'

# store pickles in DA
store_pickles = 'DA_and_studies'

flag_run_madx       = True
flag_check_madx     = False ## check missing_mad.txt
flag_run_six        = False
flag_run_missing    = False
flag_run_sixdb      = False


if flag_run_sixdb:
  sys.path.append('/afs/cern.ch/work/s/skostogl/public/useful/SixDeskDB_new/SixDeskDB')
  #sys.path.append('/afs/cern.ch/user/s/skostogl/public/SPS_sixtrack/sixdb/SixDeskDB')
  import sixdeskdb

# parameters for config.py
mode            = 'b1_with_bb'
optics_path     = '/afs/cern.ch/eng/lhc/optics/HLLHCV1.5'
optics_file     = '/afs/cern.ch/eng/lhc/optics/HLLHCV1.5/round/opt_round_150_1500_thin.madx'
emit_um         = 2.5
bunch_length    = 0.075
bunch_intensity = 1.2e11
energy_gev      = 7000.
qx              = 62.31
qy              = 60.315
chroma          = 15.
vrf             = 16.
ioct            = 300.
coupling        = 1e-3
on_x1           = 250.
on_x5           = on_x1
on_crab1        = -190.
on_crab5        = -190.
on_disp         = 1
only_lr         = False
only_ho         = False
z_mm            = 0.

dpini        = 27e-5
angles       = 5

study_prefix          = 'SCAN_DA_Ioct300_C1e-3_Q15_CCs-190_'
current_path          = os.getcwd()
current_mask_path     = current_path + "/mask"
current_template_path = current_path + "/mask/templates"


# read cavity voltage for DYNK ramp
voltage_crabs = pd.read_pickle('df_crabs_b1.pickle')
voltage_crabs_r1 = voltage_crabs[(voltage_crabs['name'].str.contains('acfgah')) & (voltage_crabs['name'].str.contains('r1.'))].volt.iloc[0]
voltage_crabs_l1 = voltage_crabs[(voltage_crabs['name'].str.contains('acfgah')) & (voltage_crabs['name'].str.contains('l1.'))].volt.iloc[0]
voltage_crabs_r5 = voltage_crabs[(voltage_crabs['name'].str.contains('acfgav')) & (voltage_crabs['name'].str.contains('r5.'))].volt.iloc[0]
voltage_crabs_l5 = voltage_crabs[(voltage_crabs['name'].str.contains('acfgav')) & (voltage_crabs['name'].str.contains('l5.'))].volt.iloc[0]


# scan over

knobs_right = np.arange(0., 201., 10.)
knobs_left  = np.arange(0., 201., 10.)

knobs_right_all = np.array([ [xing for xing in knobs_right] for optics_file in knobs_left ]).flatten()
knobs_left_all = np.array([ [optics_file for xing in knobs_right] for optics_file in knobs_left ]).flatten()

n_studies = len(knobs_right_all)

for flag in ['weak','strong', 'both']:

  if flag_run_madx:
      for n_study in range(n_studies):
        current_study = study_prefix + "_%s_%s_%s" %(flag, knobs_right_all[n_study], knobs_left_all[n_study])
        print("####################################################################")
        print("### PREPARING SIXTRACK INPUT FOR: %s ###" %current_study)
        print("####################################################################")
  
        if flag == 'weak':
           knobs_right_all_weak = knobs_right_all[n_study]
           knobs_left_all_weak = knobs_left_all[n_study]
           knobs_right_all_strong = 0.0
           knobs_left_all_strong = 0.0
        if flag == 'strong':
           knobs_right_all_strong = knobs_right_all[n_study]
           knobs_left_all_strong = knobs_left_all[n_study]
           knobs_right_all_weak = 0.0
           knobs_left_all_weak = 0.0
        if flag =='both':
           knobs_right_all_strong = knobs_right_all[n_study]
           knobs_left_all_strong = knobs_left_all[n_study]
           knobs_right_all_weak = knobs_right_all[n_study]
           knobs_left_all_weak = knobs_left_all[n_study]
  
  
        ## MASK
        ##################################################
        call(['cp', f'{current_mask_path}/{template_mask}',f'{current_mask_path}/{current_study}.mask'],shell=False)
  
        dict = {
                 '%CURRENT_PATH%':str(current_mask_path),
                 '%STUDY%':str(current_study)
                 }
  
        replace_file(f'{current_mask_path}/{current_study}.mask',dict)
        ## input.py
        ##################################################
        call(['cp', f'{current_template_path}/{template_mask_py}', f'mask/input_{current_study}.py'],shell=False)
        ## config.py
        ##################################################
        call(['cp', f'{current_template_path}/{template_config}', f'{current_mask_path}/config_{current_study}.py'],shell=False)
  
        dict = {
            '%MODE': str(mode),
            '%OPTICS_PATH': str(optics_path),
            '%OPTICS_FILE': str(optics_file),
            '%EMIT_UM': str(emit_um),
            '%BUNCH_LENGTH': str(bunch_length),
            '%BUNCH_INTENSITY': str(bunch_intensity),
            '%ENERGY_GEV':str(energy_gev),
            '%QX': str(qx),
            '%QY': str(qy),
            '%CHROMA': str(chroma),
            '%VRF': str(vrf),
            '%IOCT': str(ioct),
            '%COUPLING': str(coupling),
            '%ON_X1': str(on_x1),
            '%ON_X5': str(on_x5),
            '%ON_CRAB1': str(on_crab1),
            '%ON_CRAB5': str(on_crab5),
            '%ON_DISP': str(on_disp),
            '%ONLY_LR': str(only_lr),
            '%ONLY_HO': str(only_ho),
            '%CRAB_L1B2':str(knobs_left_all_strong),
            '%CRAB_R1B2':str(knobs_right_all_strong),
            '%CRAB_L1B1':str(knobs_left_all_weak),
            '%CRAB_R1B1':str(knobs_right_all_weak),
        }
        replace_file(f'{current_mask_path}/config_{current_study}.py',dict)
        ##################################################
        ## optics specific
        ##################################################
        call(['cp', f'{current_template_path}/optics_specific_tools.py', f'{current_mask_path}/optics_specific_tools_{current_study}.py'],shell=False)
        ## SIXDESKENV
        ##################################################
        call(['cp', template_six, 'sixdeskenv'],shell=False)
        dict = {    '%STUDY%': current_study,
                    '%NPART%': str(bunch_intensity),
                    '%DPINI%':str(dpini),
                    '%EMIT_UM':str(emit_um),
                    '%ANGLES': str(angles)
                    }
        replace_file('sixdeskenv',dict)
        ##################################################
        ## fort.3.local
  
        current_r1 = voltage_crabs_r1-knobs_right_all_weak/100.*voltage_crabs_r1
        current_l1 = voltage_crabs_l1-knobs_left_all_weak/100.*voltage_crabs_l1
        current_r5 = voltage_crabs_r5
        current_l5 = voltage_crabs_l5
  
        call(['cp', template_fort3local , 'fort.3.local'],shell=False)
        dict = {    '%R1%': str(current_r1),
                    '%L1%': str(current_l1),
                    '%R5%': str(current_r5),
                    '%L5%': str(current_l5),
                    }
        replace_file('fort.3.local',dict)
        ##################################################
        ## fort.3.mother1
        call(['cp', f'control_files/{template_fort3}' , 'control_files/fort.3.mother1_col'],shell=False)
        dict = {    '%z_mm': str(z_mm),
                    }
        replace_file('control_files/fort.3.mother1_col',dict)
        ##################################################
  
        call([sixdesk_exe + '/set_env.sh','-s', '-l','-P', '/afs/cern.ch/user/s/skostogl/miniconda3/bin/python'], shell=False)
        call([sixdesk_exe + '/mad6t.sh', '-o','2','-s','-P','/afs/cern.ch/user/s/skostogl/miniconda3/bin/python'], shell=False)
        call(['mv', 'fort.3.local', f'fort.3.local.{current_study}'],shell=False)
  
  
  if flag_run_six:
      for n_study in range(n_studies):
        current_study = study_prefix + "_%s_%s_%s" %(flag, knobs_right_all[n_study], knobs_left_all[n_study])
        call(['mv', f'fort.3.local.{current_study}', 'fort.3.local'],shell=False)
  
        print("### RUNNING FOR: %s ###" %current_study)
  
        call([sixdesk_exe + '/set_env.sh','-d', current_study],shell=False)
        call([sixdesk_exe + '/set_env.sh','-s', '-l'] ,shell=False)
        call([sixdesk_exe + '/run_six.sh','-a', '-l','-o', '0'],shell=False)
        call(['mv', 'fort.3.local', f'fort.3.local.{current_study}'],shell=False)
  ###############################################
  
  if flag_run_missing:
      for n_study in range(n_studies):
        current_study = study_prefix + "_%s_%s_%s" %(flag, knobs_right_all[n_study], knobs_left_all[n_study])
  
        call(['mv', f'fort.3.local.{current_study}', 'fort.3.local'],shell=False)
  
        print("### RUNNING FOR: %s ###" %current_study)
  
        call([sixdesk_exe + '/set_env.sh','-d', current_study],shell=False)
        call([sixdesk_exe + '/set_env.sh','-s', '-l'] ,shell=False)
        call([sixdesk_exe + '/run_status'],shell=False)
        call([sixdesk_exe + '/run_six.sh','-l','-i'],shell=False)
        call(['mv', 'fort.3.local', f'fort.3.local.{current_study}'],shell=False)
  
  
  if flag_run_sixdb:
    min_da  = []
    mean_da = []
    min_da2 = []
    mean_da2 = []
    qxx = []
    qyy = []
    studies = []
    for n_study in range(n_studies):
      current_study = study_prefix + "_%s_%s_%s" %(flag, knobs_right_all[n_study], knobs_left_all[n_study])
      print("### PLOTTING FOR: %s ###" %current_study)
      try:
          #if True:
          db=sixdeskdb.SixDeskDB.from_dir('./studies/'+current_study+'/')
          db.mk_da()
          angles=db.get_db_angles()
          seeds=db.get_db_seeds()
          tunes=db.get_tunes()[0]
          seed2,angle2,da2=db.get_da_angle(alost = 'alost2').T
          seed,angle,da=db.get_da_angle().T
          data_theta = [an[0] for an in angle]
          data_r = [abs(i[0]) for i in da if abs(i[0]) >0.]
          data_r2 = [abs(i[0]) for i in da2 if abs(i[0]) >0.]
          print(min(data_r), min(data_r2), knobs_right_all[n_study], knobs_left_all[n_study])
          min_da.append(min(data_r))
          min_da2.append(min(data_r2))
          mean_da.append(np.mean(data_r))
          mean_da2.append(np.mean(data_r2))
          qxx.append(knobs_right_all[n_study])
          qyy.append(knobs_left_all[n_study])
          studies.append(current_study)
      except:
          print('Problematic file')
          print('current_study')
  
    df = pd.DataFrame({'KR':qxx, 'KL': qyy, 'da': min_da, 'da2':min_da2, 'study':studies, 'mean_da':mean_da, 'mean_da2':mean_da2})
    df.to_pickle(store_pickles + '/' + '%s.pickle' %study_prefix)
    print(df)
