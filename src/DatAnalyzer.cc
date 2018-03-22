#include "DatAnalyzer.hh"

using namespace std;

DatAnalyzer::DatAnalyzer(int numChannels, int numSamples) :
        NUM_CHANNELS(numChannels), NUM_SAMPLES(numSamples),
        file(0), tree(0) {
    cout << "In DatAnalyzer constructor. Set NUM_CHANNELS to " << NUM_CHANNELS << flush;
    cout << ". Set NUM_SAMPLES to " << NUM_SAMPLES << endl;
    // TODO: init all variables
}

DatAnalyzer::~DatAnalyzer() {
    cout << "In DatAnalyzer destructor" << endl;
    if (file) {
        file->Close();
    }
}

TString DatAnalyzer::ParseCommandLine( int argc, char* argv[], TString opt )
{
  TString out = "";
  for (int i = 1; i < argc && out==""; i++ ) {
    TString tmp( argv[i] );
    if ( tmp.Contains("--"+opt) ) {
      if(tmp.Contains("=")) {
        out = tmp(tmp.First("="), tmp.Length());
      }
      else {
        out = "true";
      }
    }
  }
  return out;
}

void DatAnalyzer::GetCommandLineArgs(int argc, char **argv){

  input_file_path = ParseCommandLine( argc, argv, "input_file" );
  ifstream in_file(input_file_path.Data());
  if (!in_file || input_file_path == "" || !input_file_path.EndsWith(".dat")){
    cerr << "[ERROR]: please provide a valid input file. Use: --input_file=<your_input_file_path>.dat " << endl;
    exit(0);
  }
  else
  {
    cout << "Input file: " << input_file_path.Data() << endl;
  }

  output_file_path = ParseCommandLine( argc, argv, "output_file" );
  if ( output_file_path == "" ){
    output_file_path = input_file_path.ReplaceAll(".dat", ".root");
  }
  else if (!output_file_path.EndsWith(".root")) output_file_path += ".root";
  cout << "Output file: " << output_file_path.Data() << endl;

  // -------- Non compulsory command line arguments
  TString aux;

  aux = ParseCommandLine( argc, argv, "N_evts" );
  N_evts = aux.Atoi();
  cout << "Number of events: " << flush;
  if(N_evts == 0){ cout << "Not specified." << endl;}
  else{ cout << N_evts << endl;}

  aux = ParseCommandLine( argc, argv, "config" );
  if(aux == ""){
    aux = "config/15may2017.config";
  }
  cout << "Config file: " << aux.Data() << endl;
  config = new Config(aux.Data());
  if ( !config->hasChannels() || !config->isValid() ) {
    cerr << "\nFailed to load channel information from config " << aux.Data() << endl;
    exit(0);
  }

  aux = ParseCommandLine( argc, argv, "save_raw" );
  aux.ToLower();
  if(aux == "true") save_raw =  true;

  aux = ParseCommandLine( argc, argv, "save_meas" );
  aux.ToLower();
  if(aux == "true") save_meas =  true;

  aux = ParseCommandLine( argc, argv, "draw_debug_pulses" );
  aux.ToLower();
  if(aux == "true") draw_debug_pulses =  true;
}

void DatAnalyzer::InitTree() {
    cout << "In DatAnalyzer::InitTree" << endl;
    file = new TFile(output_file_path.Data(), "RECREATE");
    tree = new TTree("pulse", "Digitized waveforms");

    tree->Branch("i_evt", &i_evt, "i_evt/i");

    if(save_meas){
      tree->Branch("channel", channel, Form("channel[%d][%d]/F", NUM_CHANNELS, NUM_SAMPLES));
      tree->Branch("time", time, Form("time[4][%d]/F", NUM_SAMPLES));
    }
}

void DatAnalyzer::Analyze(){
  cout << "Should analyze" << endl;
}

void DatAnalyzer::RunEventsLoop() {
    cout << "In DatAnalyzer::RunEventsLoop" << endl;
    InitTree();

    bin_file = fopen( input_file_path.Data(), "r" );

    unsigned int N_written_evts = 0;
    for( i_evt = 0; !feof(bin_file) && (N_evts==0 || i_evt<N_evts); i_evt++){
        int out = GetChannelsMeasurement();
        if(out == -1) break;

        Analyze();

        N_written_evts++;
        tree->Fill();
    }

    fclose(bin_file);
    cout << "\nProcessed total of " << N_written_evts << " events\n";

    file->Write();
    file->Close();
}
