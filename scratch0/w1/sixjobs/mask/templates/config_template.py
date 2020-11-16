configuration = {

    # Links to be made for tools and scripts
    'links'                    : {
                                    'tracking_tools': '/afs/cern.ch/eng/tracking-tools',
                                    'modules': 'tracking_tools/modules',
                                    'tools': 'tracking_tools/tools',
                                    'beambeam_macros': 'tracking_tools/beambeam_macros',
                                    'errors': 'tracking_tools/errors',
                                 },
    # Mode - choose between:

    #   Main modes:
    #    'b1_without_bb'
    #    'b1_with_bb'
    #    'b4_from_b2_without_bb'
    #    'b4_from_b2_with_bb'

    #   Legacy modes
    #    'b1_with_bb_legacy_macros'
    #    'b4_without_bb'

    'mode'                      : '%MODE',#'b1_with_bb',

    # For test against madx mask for modes 'b4_from_b2_without_bb' and 'b4_without_bb':
    # 'force_leveling' : {'on_sep8': -0.03425547139366354, 'on_sep2': 0.14471680504084292},

    # Optics file
    'optics_path'              : '%OPTICS_PATH',#'/afs/cern.ch/eng/lhc/optics/HLLHCV1.5',
    'optics_file'              : '%OPTICS_FILE',#'/afs/cern.ch/eng/lhc/optics/HLLHCV1.5/round/opt_round_150_1500_thin.madx', #15 cm

    # Enable checks
    'check_betas_at_ips'       : False,
    'check_separations_at_ips' : False,
    'save_intermediate_twiss'  : False,

    # Tolerances for checks [ip1, ip2, ip5, ip8]
    'tol_beta'                 : [1e-3, 10e-2, 1e-3, 1e-2],
    'tol_sep'                  : [1e-6, 1e-6, 1e-6, 1e-6],

    # Tolerance for check on flat machine
    'tol_co_flatness'          : 1e-6,

    # Beam parameters
    'beam_norm_emit_x'     : %EMIT_UM,#2.5,          # [um]
    'beam_norm_emit_y'     : %EMIT_UM,#2.5,          # [um]
    'beam_sigt'            : %BUNCH_LENGTH,#0.075,        # [m]
    'beam_sige'            : 1.1e-4,       # [-]
    'beam_npart'           : %BUNCH_INTENSITY,#1.2e11,       # [-]
    'beam_energy_tot'      : %ENERGY_GEV,#7000,         # [GeV]

    # Tunes and chromaticities
    'qx0'                  : %QX,#62.31,
    'qy0'                  : %QY,#60.316,
    'chromaticity_x'       : %CHROMA,#15,            # [-] 
    'chromaticity_y'       : %CHROMA,#15,            # [-] 

    # RF voltage
    'vrf_total'            : %VRF,#16.,          # [MV]

    # Octupole current
    'oct_current'          : %IOCT,#-300,         # [A]

    # Luminosity parameters
    'enable_lumi_control'      : True,
    'sep_plane_ip2'            : 'x', # used by python tools - NOT by legacy macros
    'sep_plane_ip8'            : 'y', # used by python tools - NOT by legacy macros
    'lumi_ip8'             : 2e33, # [Hz/cm2] leveled luminosity in IP8 
    'fullsep_in_sigmas_ip2': 5,
    'nco_IP1'              : 2748, # number of Head-On collisions in IP1
    'nco_IP2'              : 2494, # number of Head-On collisions in IP1
    'nco_IP5'              : 2748, # number of Head-On collisions in IP1
    'nco_IP8'              : 2572, # number of Head-On collisions in IP1

    # Beam-beam parameters (used by python tools - NOT by legacy macros)
    'numberOfLRPerIRSide'      : [25, 20, 25, 20],
    'bunch_spacing_buckets'    : 10,
    'numberOfHOSlices'         : 11,
    'bunch_population_ppb'     : None,
    'sigmaz_m'                 : None,
    'z_crab_twiss'             : 0.075,
    'only_lr'                  : %ONLY_LR,
    'only_ho'                  : %ONLY_HO,


    # Match tunes and chromaticities including beam-beam effects
    'match_q_dq_with_bb'        : False,            # should be off at collision

    # Enable crab cavities
    'enable_crabs'             : True,

    # N. iterations for coupling correction
    'N_iter_coupling'            : 2,

    # Value to be added to linear coupling knobs (on sequence_to_track)
    'delta_cmr'                 : %COUPLING,#0.,
    'delta_cmi'                 : 0.,

    # Verbose flag for MAD-X parts
    'verbose_mad_parts'         : True,

    # Optics-specific knob namings
    'knob_names' : {
        # Common knobs
        'sepknob_ip2_mm': 'on_sep2',
        'sepknob_ip8_mm': 'on_sep8',

        # Knobs associated to sequences
        'qknob_1': {'lhcb1': 'kqtf.b1',  'lhcb2':'kqtf.b2'},
        'qknob_2': {'lhcb1': 'kqtd.b1',  'lhcb2':'kqtd.b2'},
        'chromknob_1': {'lhcb1': 'ksf.b1',  'lhcb2':'ksf.b2'},
        'chromknob_2': {'lhcb1': 'ksd.b1',  'lhcb2':'ksd.b2'},
        'cmrknob': {'lhcb1': 'cmrskew',  'lhcb2':'cmrskew'},
        'cmiknob': {'lhcb1': 'cmiskew',  'lhcb2':'cmiskew'},
        },

    # Optics specific knob values
    # (only on_disp, on_crab1 and on_crab5 are used directly by the mask,
    # the other values are used only throught the optics_specific_tools file)
    'knob_settings':  {
        #IP specific orbit settings
        'on_x1'                   : %ON_X1,          # [urad]  
        'on_sep1'                 : -0.75,            # [mm]   
        'on_x2'                   : 170,         # [urad] 
        'on_sep2'                 : 1.,        # [mm]   
        'on_x5'                   : %ON_X5,          # [urad] 
        'on_sep5'                 : 0.75,            # [mm]   
        'on_x8'                   : -200,         # [urad] 
        'on_sep8'                 : -1.,       # [mm]   
        'on_a1'                   : 0,            # [urad] 
        'on_o1'                   : 0,            # [mm]   
        'on_a2'                   : 0,            # [urad] 
        'on_o2'                   : 0,            # [mm]   
        'on_a5'                   : 0,            # [urad] 
        'on_o5'                   : 0,            # [mm]   
        'on_a8'                   : 0,            # [urad] 
        'on_o8'                   : 0,            # [mm]   
        'on_crab1'                : %ON_CRAB1,#-190,         # [urad] 
        'on_crab5'                : %ON_CRAB5,#-190,         # [urad]  

        # Dispersion correction knob
        'on_disp'                 : %ON_DISP,            # Value to choose could be optics-dependent

        # Magnets of the experiments
        'on_alice_normalized'     : 1,
        'on_lhcb_normalized'      : 1,

        'on_sol_atlas'            : 0,
        'on_sol_cms'              : 0,
        'on_sol_alice'            : 0,
        # CC knobs to open bump
        'par_crab_L1B1'            : %CRAB_L1B1,
        'par_crab_L1B2'            : %CRAB_L1B2,
        'par_crab_R1B1'            : %CRAB_R1B1,
        'par_crab_R1B2'            : %CRAB_R1B2,
        'par_crab_L5B1'            : 0,
        'par_crab_L5B2'            : 0,
        'par_crab_R5B1'            : 0,
        'par_crab_R5B2'            : 0,
        },

    # Enable machine imperfections
    'enable_imperfections'     : False,

    # Enable knob synthesis (for coupling correction, if no imperfections)
    'enable_knob_synthesis'    : True,

    # Parameters for machine imperfections
    'pars_for_imperfections': {
        'par_myseed'               : 1,
        'par_correct_for_D2'       : 0,
        'par_correct_for_MCBX'     : 0,
        'par_on_errors_LHC'        : 0,
        'par_on_errors_MBH'        : 0,
        'par_on_errors_Q5'         : 0,
        'par_on_errors_Q4'         : 0,
        'par_on_errors_D2'         : 0,
        'par_on_errors_D1'         : 0,
        'par_on_errors_IT'         : 0,
        'par_on_errors_MCBRD'      : 0,
        'par_on_errors_MCBXF'      : 0,
        },

    # Parameters for legacy beam-beam macros (not used in default modes)
    'pars_for_legacy_bb_macros' : {
                                    'par_b_t_dist' : 25.,  # bunch spacing [ns]
                                    'par_n_inside_D1': 5,  # n. parasitic encounters inside D1
                                  },
    }
