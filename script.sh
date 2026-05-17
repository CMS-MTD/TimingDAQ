#!/bin/bash
source /cvmfs/cms.cern.ch/cmsset_default.sh
cd /cvmfs/cms.cern.ch/el9_amd64_gcc12/cms/cmssw/CMSSW_13_3_2/src/
eval `scramv1 runtime -sh`
cd -

source setup_el9.sh
ScopeNum=$3
BASE=2026_05_SNSPD
chmod 755 NetScopeStandaloneDat2Root
chmod 755 add_branches_TimingDAQ.py
mkdir scope${ScopeNum}
cd scope${ScopeNum}
cp /eos/uscms/store/group/cmstestbeam/${BASE}/LecroyScope/RecoData/ConversionRECO/Scope${ScopeNum}/converted_run$1.root .
cp /eos/uscms/store/group/cmstestbeam/${BASE}/Tracks/RecoData/v1/Run$1_CMSTiming_FastTriggerStream_converted.root .
cp /eos/uscms//store/group/cmstestbeam/${BASE}//ConfigInfo/Runs/info_$1.json .
ls
../NetScopeStandaloneDat2Root --input_file=converted_run$1.root --pixel_input_file=Run$1_CMSTiming_FastTriggerStream_converted.root  --config=../config/${BASE}/LecroyScope_Scope${ScopeNum}_$2.config --output_file=out_run$1_info.root  --correctForTimeOffsets=true
#python3 ../add_branches_TimingDAQ.py $1 9999 out_run$1.root
ls
eosmkdir /store/group/cmstestbeam/${BASE}/LecroyScope/RecoData/TimingDAQRECO/RecoWithTracks/$2/Scope${ScopeNum}/
xrdcp -fs out_run$1_info.root root://cmseos.fnal.gov//store/group/cmstestbeam/${BASE}/LecroyScope/RecoData/TimingDAQRECO/RecoWithTracks/$2/Scope${ScopeNum}/run$1_info.root
rm *$1*.root
rm info_$1.json
date
