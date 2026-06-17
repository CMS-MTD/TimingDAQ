#!/bin/bash
source /cvmfs/cms.cern.ch/cmsset_default.sh
cd /cvmfs/cms.cern.ch/el9_amd64_gcc12/cms/cmssw/CMSSW_13_3_2/src/
eval `scramv1 runtime -sh`
cd -

BASE=2026_05_SNSPD

#cp /eos/uscms/store/group/cmstestbeam/${BASE}/LecroyScope/RecoData/TimingDAQRECO/RecoWithTracks/$2/Scope1/run$1.root run$1_scope1.root
#cp /eos/uscms/store/group/cmstestbeam/${BASE}/LecroyScope/RecoData/TimingDAQRECO/RecoWithTracks/$2/Scope2/run$1.root run$1_scope2.root
#cp /eos/uscms//store/group/cmstestbeam/${BASE}//ConfigInfo/Runs/info_$1.json .

ls
python3 merge.py --input1 out_run$1_scope1.root --input2 out_run$1_scope2.root --output merge_run$1.root
ls
python3 add_branches_TimingDAQ.py $1 9999 merge_run$1.root
#eosmkdir /store/group/cmstestbeam/${BASE}/LecroyScope/RecoData/TimingDAQRECO/RecoWithTracks/$2/Merge/
ls
#xrdcp -fs merge_run$1_info.root root://cmseos.fnal.gov//store/group/cmstestbeam/${BASE}/LecroyScope/RecoData/TimingDAQRECO/RecoWithTracks/$2/Merge/run$1_info.root
#rm *run$1*.root
#rm info_$1.json
#date
