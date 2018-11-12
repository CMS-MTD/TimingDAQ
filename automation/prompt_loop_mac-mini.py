from glob import glob
import shutil, os, argparse
import subprocess
import time, re

VMERaw_file_template = 'VME/RAW/RawDataSaver0CMSVMETiming_RunRN*dat'
Tracks_file_template = 'Tracks/RunRN_CMSTiming_converted.root'

cmd_DQM_template = 'python ../DataQualityMonitor/DQM_SiPM.py -C ../DatQualityMonitor/config/FNAL_TB_1811/VME_vf1.txt -S ~/cernbox/ocerri/www/FNAL_TB_1811/ -i ../data/VME/RECO/vf1/DataVMETiming_RunRN.root &> ~/tmp/DQM.log &'

def GetCommandLineArgs():
    p = argparse.ArgumentParser()

    p.add_argument('--v_fast', type=str, default=None, help='Version of the config to run inline. (e.g. vf1).\nIf None no inline decoding is run')
    p.add_argument('--v_full', type=str, default=None, help='If None not run')

    p.add_argument('--wait_for_tracks', action='store_true', default=False, help='Wait for track before recostructing it')
    p.add_argument('--run_DQM', action='store_true', default=False, help='Run DQM')

    p.add_argument('--data_dir', default='../data')

    p.add_argument('--ignore_before', type=int, default=0)

    p.add_argument('--max_void', type=int, default=-1)
    p.add_argument('--sleep', type=float, default=60)
    p.add_argument('--min_file_age', type=float, default=15)

    return p.parse_args()

if __name__ == '__main__':
    args = GetCommandLineArgs()

    if args.run_DQM:
        args.run_DQM = False
        print "Sorry, not implemented yet. Run manually"
        print "python DQM_SiPM.py -C config/FNAL_TB_1811/VME_vf1.txt -S ~/cernbox/ocerri/www/FNAL_TB_1811/ -i ../data/VME/RECO/vf1/DataVMETiming_Run<N>.root"

    if args.v_fast==None and args.v_full==None:
        print 'At least v_fast or v_full needs to be given'
        print 'Run with -h for help'
        exit(0)

    data_dir = args.data_dir
    if not data_dir.endswith('/'):
        data_dir += '/'

    last_run_number = args.ignore_before
    nothing_changed = 0

    while(args.max_void < 0 or nothing_changed < args.max_void):
        latest_file = glob(data_dir + VMERaw_file_template.replace('RN', '*'))[-1]
        run_number = int(re.search('_Run[0-9]+_', latest_file).group(0)[4:-1])

        has_run =  False
        while run_number > last_run_number:
            age_check = time.time() - os.path.getmtime(latest_file) > args.min_file_age
            tracks_check = os.path.exists(data_dir + Tracks_file_template.replace('RN', str(run_number)))

            if age_check and (not args.wait_for_tracks or tracks_check):
                if not args.v_fast == None:
                    cmd = 'python automation/DecodeData.py --vVME {0} -R {1}'.format(args.v_fast, run_number)
                    print cmd
                    subprocess.call(cmd, shell=True)
                    if args.run_DQM:
                        print cmd_DQM_template.replace('RN', str(run_number))
                        subprocess.call(cmd_DQM_template.replace('RN', str(run_number)), shell=True)

                if not args.v_full == None:
                    cmd = 'python automation/DecodeData.py --vVME {0} -R {1}'.format(args.v_full, run_number)
                    cmd += ' &> ~/tmp/{}.log &'.format(run_number)
                    print cmd
                    subprocess.call(cmd, shell=True)

                last_run_number = run_number
                has_run = True
                nothing_changed = 0
            else:
                run_number -= 1

        if not has_run:
            nothing_changed += 1

        print 'Last run processed {0}\n...Going to sleep for {1:.0f} s\n\n'.format(last_run_number, args.sleep)
        time.sleep(args.sleep)

    print '\n\nStopped because nothing changed for at least {0:.1f} min'.format(args.sleep*nothing_changed/60.0)