echo "Running create_lm.sh"
cd ~/kaldi/egs/aspire/s5
mkdir "$1"
mkdir "$1/local"
mkdir "$1/local/dict"
mkdir "$1/local/lang"
mkdir "$1/dict"
mkdir "$1/dict_tmp"
mkdir "$1/lang"
mkdir "$1/graph"
cp data/local/dict/extra_questions.txt "$1/local/dict/"
cp data/local/dict/nonsilence_phones.txt "$1/local/dict/"
cp data/local/dict/optional_silence.txt "$1/local/dict/"
cp data/local/dict/silence_phones.txt "$1/local/dict/"
cp $2 $1/local/dict/lexicon.txt
cp $3 $1/local/lang/lm.arpa
echo "Directory structure created"
echo $1
./cmd.sh 
./path.sh 
model=exp/tdnn_7b_chain_online 
phones_src=exp/tdnn_7b_chain_online/phones.txt 
dict_src="$1/local/dict" 
lm_src="$1/local/lang/lm.arpa" 
lang="$1/lang" 
dict="$1/dict" 
dict_tmp="$1/dict_tmp" 
graph="$1/graph" 

echo "DEFINITIONS SUCCESSFUL"

# Compile the word lexicon (L.fst)
utils/prepare_lang.sh --phone-symbol-table $phones_src $dict_src "<unk>" $dict_tmp $dict

echo "prepare_lang.sh SUCCESSFUL"

# Compile the grammar/language model (G.fst)
gzip <$lm_src> $lm_src.gz
utils/format_lm.sh $dict $lm_src.gz $dict_src/lexicon.txt $lang

echo "format_lm.sh SUCCESSFUL"

# Finally assemble the HCLG graph
utils/mkgraph.sh --self-loop-scale 1.0 $lang $model $graph 

# To use our newly created model, we must also build a decoding configuration, the following line will create these for us into the new/conf directory
steps/online/nnet3/prepare_online_decoding.sh --mfcc-config conf/mfcc_hires.conf $dict exp/nnet3/extractor exp/chain/tdnn_7b $1
