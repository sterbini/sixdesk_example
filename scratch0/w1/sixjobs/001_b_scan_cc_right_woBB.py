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
# This script changes the voltage of the CCs RIGHT and LEFT of IP1. Beam-beam is OFF. 
#####################

# Useful functions
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
#####################
#####################

# Sixdesk exe
#####################
sixdesk_exe   = "/afs/cern.ch/project/sixtrack/SixDesk_utilities/pro/utilities/bash"
#####################
#####################

# Templates
#####################
template_mask       = 'HL_template.madx'
template_mask_py    = 'input_template.py'
template_config     = 'config_template.py'
template_fort3local = 'fort.3.local.template'
template_fort3      = 'fort.3.mother1_col_template' # this allows an easy scan in z
template_six        = 'sixdeskenv.template'
#####################
#####################

# store DA pickles in DA_and_studies
#####################
store_pickles = 'DA_and_studies'
#####################
#####################

# Initialize flag
#####################
flag_run_madx, flag_check_madx, flag_run_six, flag_run_missing, flag_run_sixdb = False, False, False, False, False
#####################
#####################

# Input mode from user
#####################
if len(sys.argv)>1:
    flag = sys.argv[1]
    if flag == 'run_madx':
        flag_run_madx       = True  ## to run MADX jobs
    elif flag == 'check_madx':
        flag_check_madx     = True ## to check missing MADX jobs in missing_mad.txt
    elif flag == 'run_six':
        flag_run_six        = True ## to run sixtrack jobs
    elif flag == 'run_missing':
        flag_run_missing    = True ## to run sixtrack jobs
    elif flag == 'run_sixdb':
        flag_run_sixdb      = False ## to compute DA and store in pickle
    elif flag == '-h':
        print('Valid modes:')
        print('run_madx: to run MADX jobs')
        print('check_madx: to check MADX jobs. Missing jobs will be saved in missing_madx.txt')
        print('run_six: to run sixtrack jobs')
        print('run_missing: to resubmit missing jobs')
        print('run_sixdb: to compute DA and store pickle in DA_and_studies folder')

    else:
        print(f'Unknown mode {flag}. Valid modes: run_madx, check_madx, run_six, run_missing, run_sixdb. Pass -h argument to print functionality of each mode.')
        exit()
else:
    print('No mode specified. Valid modes: run_madx, check_madx, run_six, run_missing, run_sixdb. Pass -h argument to print functionality of each mode.')
    exit()
#####################
#####################

# sixdb path
#####################
if flag_run_sixdb:
  sys.path.append('/afs/cern.ch/work/s/skostogl/public/useful/SixDeskDB_new/SixDeskDB')
  import sixdeskdb
#####################
#####################

# Parameters for config.py
#####################
mode            = 'b1_without_bb'
optics_path     = '/afs/cern.ch/eng/lhc/optics/HLLHCV1.5'
optics_file     = '/afs/cern.ch/eng/lhc/optics/HLLHCV1.5/round/opt_round_150_1500_thin.madx'
# for version HL-LHCv1.4
#optics_path     = '/afs/cern.ch/eng/lhc/optics/HLLHCV1.4'
#optics_file     = '/afs/cern.ch/eng/lhc/optics/HLLHCV1.4/round/opt_round_150_1500_thin.madx'
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
# careful, when modifying on_crab1 and 5, df_crabs_b1.pickle that will be used for the DYNK block must also be changed
on_crab1        = -190.
on_crab5        = -190.
on_disp         = 1
only_lr         = False
only_ho         = False
z_mm            = 0.
#####################
#####################

# Parameters for sixdeskenv
#####################
dpini        = 27e-5
angles       = 29
#####################
#####################

# Prefix
#####################
study_prefix          = 'DA_Ioct300_C1e-3_Q15_CCs-190_WOBB'
#####################
#####################

# Useful paths
#####################
current_path          = os.getcwd()
current_mask_path     = current_path + "/mask"
current_template_path = current_path + "/mask/templates"
current_path_sixdesk  =(os.path.split(os.path.split(os.path.split(current_path)[0])[0])[0])
#####################
#####################


# Read cavity voltage from df_crabs_b1 (-190 urad and closed bump) for DYNK ramp
#####################
voltage_crabs = pd.read_pickle('df_crabs_b1.pickle')
voltage_crabs_r1 = voltage_crabs[(voltage_crabs['name'].str.contains('acfgah')) & (voltage_crabs['name'].str.contains('r1.'))].volt.iloc[0]
voltage_crabs_l1 = voltage_crabs[(voltage_crabs['name'].str.contains('acfgah')) & (voltage_crabs['name'].str.contains('l1.'))].volt.iloc[0]
voltage_crabs_r5 = voltage_crabs[(voltage_crabs['name'].str.contains('acfgav')) & (voltage_crabs['name'].str.contains('r5.'))].volt.iloc[0]
voltage_crabs_l5 = voltage_crabs[(voltage_crabs['name'].str.contains('acfgav')) & (voltage_crabs['name'].str.contains('l5.'))].volt.iloc[0]
#####################
#####################


# Scan over
#####################
knobs_right_all = np.arange(0., 201., 10.)
knobs_left_all  = [0.0 for i in knobs_right_all]
n_studies = len(knobs_right_all)
#####################
#####################

# Main script
#####################
for flag in ['weak']:#['weak', 'strong', 'both']:

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
  
  
        ##################################################
        ## mask
        ##################################################
        call(['cp', f'{current_mask_path}/{template_mask}',f'{current_mask_path}/{current_study}.mask'],shell=False)
  
        dict = {
                 '%CURRENT_PATH%':str(current_mask_path),
                 '%STUDY%':str(current_study)
                 }
  
        replace_file(f'{current_mask_path}/{current_study}.mask',dict)
        ##################################################
        ## input.py
        ##################################################
        call(['cp', f'{current_template_path}/{template_mask_py}', f'mask/input_{current_study}.py'],shell=False)
        ##################################################
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
        ##################################################
        ## sixdeskenv
        ##################################################
        call(['cp', template_six, 'sixdeskenv'],shell=False)
        dict = {    '%STUDY%': current_study,
                    '%NPART%': str(bunch_intensity),
                    '%DPINI%':str(dpini),
                    '%EMIT_UM':str(emit_um),
                    '%ANGLES': str(angles),
                    '%PRESENT_DIR%': str(current_path_sixdesk)
                    }
        replace_file('sixdeskenv',dict)
        ##################################################
        ## fort.3.local
        ##################################################
  
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
        ##################################################
        call(['cp', f'control_files/{template_fort3}' , 'control_files/fort.3.mother1_col'],shell=False)
        dict = {    '%z_mm': str(z_mm),
                    }
        replace_file('control_files/fort.3.mother1_col',dict)
        ##################################################
        ##################################################
  
        call([sixdesk_exe + '/set_env.sh','-s', '-l','-P', '/afs/cern.ch/user/s/skostogl/miniconda3/bin/python'], shell=False)
        call([sixdesk_exe + '/mad6t.sh', '-o','2','-s','-P','/afs/cern.ch/user/s/skostogl/miniconda3/bin/python'], shell=False)
        call(['mv', 'fort.3.local', f'fort.3.local.{current_study}'],shell=False)
  
  if flag_check_madx:
    with open('missing_mad.txt', 'w') as f_res:
        for n_study in range(n_studies):
            current_study = study_prefix + "_%s_%s_%s" %(flag, knobs_right_all[n_study], knobs_left_all[n_study])
  
            print("####################################################################")
            print("### CURRENT STUDY IS: %s ###" %current_study)
            print("####################################################################")
            import os
            try:
              files = os.listdir('../../sixtrack_input/w1/%s' %current_study)
              if ('fort.2_1.gz' not in files):
                f_res.write('%s \n' %current_study)
                f_res.flush()
            except:
                f_res.write('%s---> problematic \n' %current_study)
                f_res.flush()
  


  if flag_run_six:
      for n_study in range(n_studies):
        current_study = study_prefix + "_%s_%s_%s" %(flag, knobs_right_all[n_study], knobs_left_all[n_study])
        call(['mv', f'fort.3.local.{current_study}', 'fort.3.local'],shell=False)
        print("####################################################################")
  
        print("### RUNNING FOR: %s ###" %current_study)
        print("####################################################################")
  
        call([sixdesk_exe + '/set_env.sh','-d', current_study],shell=False)
        call([sixdesk_exe + '/set_env.sh','-s', '-l'] ,shell=False)
        call([sixdesk_exe + '/run_six.sh','-a', '-l','-o', '0'],shell=False)
        call(['mv', 'fort.3.local', f'fort.3.local.{current_study}'],shell=False)
  ###############################################
  
  if flag_run_missing:
      for n_study in range(n_studies):
        current_study = study_prefix + "_%s_%s_%s" %(flag, knobs_right_all[n_study], knobs_left_all[n_study])
  
        call(['mv', f'fort.3.local.{current_study}', 'fort.3.local'],shell=False)
  
        print("####################################################################")
        print("### RUNNING MISSING FOR: %s ###" %current_study)
        print("####################################################################")
  
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
      print("####################################################################")
      print("### DA FOR: %s ###" %current_study)
      print("####################################################################")
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
    df.to_pickle(store_pickles + '/' + '%s_%s.pickle' %(study_prefix, flag))
    print(df)
