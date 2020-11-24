# DA-studies-with-open-CC-bump

This is a full directory to run DA studies with SixTrack in order to evaluate the impact of crab-cavity non-closure on DA using the new pythonic masks (https://github.com/lhcopt/lhcmask)

## Important files

- sixjobs/mask/templates/*: includes all the required pymask template files with some important parameters MASKED. config_template.py should be modified by the user is more masked parameters are needed (such as on_sep e.g.). Note that the HL-LHC version is masked and it is directy controlled from sixjobs *.py files. 
- sixjobs/HL_template.madx: this is the layer between pymask and SixDesk
- sixjobs/sixdeskenv.template: this is the sixdeskenv with some important parameters masked
- sixjobs/fort.3.local.template: the template fort.3.local that included the DYNK block responsible for the ramping of the CCs' voltage
- sixjobs/df_crabs_b1.pickle: contains the values of the voltages in MV for the DYNK block used from SixTrack to ramp the CCs. This is for on_crab1=on_crab5=-190 urad
- sixjobs/control_files/fort.3.mother1_col_template: this is an easy way to modify the z coordinate (apart from dp/p) for the tracking simulations.
- The *.py scripts in sixjobs create all the files needed to run sixdesk with the new masks. A 1 job example can be found in 000_test_1job.py

## Simple 1 job example
python3 000_test_1job.py -h: print all available modes and what their functionality

The procedure to run 1 job is:
1. python3 000_test_1job.py run_madx
2. python3 000_test_1job.py check_madx
3. python3 000_test_1job.py run_six
4. python3 000_test_1job.py run_missing
5. python3 000_test_1job.py run_sixdb

The user must modify the "Parameters for config.py" & "Parameters for sixdeskenv" depending on the study. 

## Other examples
1. 001_a_scan_cc_right_withBB.py: reduction of CC voltage right of IP1 up to 200% with BB
2. 001_b_scan_cc_right_woBB.py: reduction of CC voltage right of IP1 up to 200% without BB
3. 002_a_scan_cc_withBB.py: reduction of CC voltage right or left of IP1 (and all possible combinations) with BB
4. 002_b_scan_cc_woBB.py: reduction of CC voltage right or left of IP1 (and all possible combinations) without BB
