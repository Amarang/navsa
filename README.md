# dependencies
sudo pip install -U pyaudio
sudo pip install -U numpy
sudo pip install -U matplotlib
sudo pip install -U scipy
sudo pip install -U sklearn


# pocket sphinx

```
# brew install these on mac
sudo apt-get install bison
sudo apt-get install swig

# install sphinxbase, pocketsphinx
curl -O "http://iweb.dl.sourceforge.net/project/cmusphinx/sphinxbase/5prealpha/sphinxbase-5prealpha.tar.gz"
curl -O "http://iweb.dl.sourceforge.net/project/cmusphinx/pocketsphinx/5prealpha/pocketsphinx-5prealpha.tar.gz"
tar -xf sphinxbase-5prealpha.tar.gz
cd sphinxbase-5prealpha
./configure
make clean
make
sudo make install
cd ../
tar -xf pocketsphinx-5prealpha.tar.gz
cd pocketsphinx-5prealpha
./configure
make clean
make
sudo make install
sudo apt-get install python-pip
sudo pip install pocketsphinx
# in cygwin, download pocketsphinx-python manually from https://github.com/cmusphinx/pocketsphinx-python
# edit setup.py to have: sb_include_dirs = ['sphinxbase/include', 'sphinxbase/include/sphinxbase','/usr/local/include/sphinxbase', '/usr/include/bash']
# then do python setup.py install
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/lib 
# get dic and lm file from http://www.speech.cs.cmu.edu/tools/lmtool-new.html
pocketsphinx_continuous -lm 3199.lm -dict 3199.dic -keyphrase "OKAY PI" -kws_threshold 1e-20 -inmic yes

cd navsa/speech/
# download language model
curl -o cmusphinx-en-us-5.2.tar.gz "http://iweb.dl.sourceforge.net/project/cmusphinx/Acoustic%20and%20Language%20Models/US%20English%20Generic%20Acoustic%20Model/cmusphinx-en-us-5.2.tar.gz"
tar -xf cmusphinx-en-us-5.2.tar.gz
```


# misc instructions for pi
- to increase volume, do `alsamixer`, hit <F6> to choose output device, then j, k to change volume. <Esc> when done
