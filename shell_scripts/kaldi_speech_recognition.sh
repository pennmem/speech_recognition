#!/bin/bash
cd ~/kaldi/egs/aspire/s5
echo $1
. cmd.sh
. path.sh
online2-wav-nnet3-latgen-faster \
	--online=false \
 	--do-endpointing=false \
  	--frame-subsampling-factor=3 \
  	--config=$1/conf/online.conf \
  	--max-active=7000 \
  	--beam=15.0 \
	--lattice-beam=6.0 \
	--acoustic-scale=1.0   \
	--word-symbol-table=$1/graph/words.txt  \
	exp/tdnn_7b_chain_online/final.mdl   \
	$1/graph/HCLG.fst \
	'ark:echo utterance-id1 utterance-id1|' \
  	"scp:echo utterance-id1 $2|" \
	ark:- | \
lattice-1best \
	--lm-scale=0.1 \
	ark:- \
	ark:- | \
lattice-align-words \
	$1/lang/phones/word_boundary.int \
	exp/tdnn_7b_chain_online/final.mdl \
	ark:- \
	ark:- | \
nbest-to-ctm \
	--frame-shift=.03 \
	--print-silence=False \
	ark:- - | \
utils/int2sym.pl \
	-f 5 \
	$1/lang/words.txt
