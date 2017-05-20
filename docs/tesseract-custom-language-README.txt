Much of this is taken from
<https://github.com/tesseract-ocr/tesseract/wiki/Training-Tesseract>

To train on a font:

1) Need the font file!  Search places like https://www.fontsquirrel.com
2) Create a text file containing all the characters of interest.
3) With, for example the 'Sintony' font used in ED:

	text2image --text=elite-dangerous-navpane-characters.txt \
		--outputbase=elitedangerous.sintony.exp0 --font='Sintony' \
		--fonts_dir=../../../fonts/sintony
	
4) Run tesseract for training:

	tesseract elitedangerous.sintony.exp0.tif elitedangerous.sintony.exp0 box.train

5) Generate unicharset file:

	unicharset_extractor elitedangerous.sintony.exp0.box
	set_unicharset_properties -U unicharset -O unicharset --script_dir=training/langdata

6) Create font_properties file with at least content:

	sintony 0 0 0 0 0

7) Clustering:

	shapeclustering -F font_properties -U unicharset elitedangerous.sintony.exp0.tr
	mftraining -F font_properties -U unicharset elitedangerous.sintony.exp0.tr
	cntraining elitedangerous.sintony.exp0.tr

8) Dictionary Data (Optional)

  This is to give hints about possible words in the language.  For E:D
  perhaps this needs to contain things like "Ls", "Ly", "Mm" and
  fragments of procedurally generated system names.


9) Combine the files (shapetable, normproto, inttemp, pffmtable,
unicharset).  First rename them to have a 'lang' prefix, i.e. "elitedangerous."

	for i in shapetable  normproto  inttemp  pffmtable unicharset; do cp -v ${i} elitedangerous.${i} ; done

Then run combine_tessdata for the language:

	combine_tessdata elitedangerous.

10) Place the resulting elitedangerous.traineddata file somewhere
appropriate and use either "TESSDATA_PREFIX=.../tessdata tesseract ..."
to specify this location when you run 'tesseract' (or export into the
environment).
