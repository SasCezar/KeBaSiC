# KeBaSiC
A tool for keyword extraction from webpages 

## Installation
KeBaSic is written in Python 3, and is required at least Python 3.5. In order to install the required dependencies run:

```
   pip install -r requirements.txt
```

The tool also requires installing the following programs:

1. Stanford CoreNLP Server from <a href="https://stanfordnlp.github.io/CoreNLP/">https://stanfordnlp.github.io/CoreNLP/</a> and the language specific properties file from <a href="https://stanfordnlp.github.io/CoreNLP/download.html">https://stanfordnlp.github.io/CoreNLP/download.html</a>
2. TreeTagger from <a href="http://www.cis.uni-muenchen.de/%7Eschmid/tools/TreeTagger/">http://www.cis.uni-muenchen.de/%7Eschmid/tools/TreeTagger/</a>

##Usage
1. Edit the [config.json](kebasic/config.json) file with the input and the output files
2. In the [composed.py](kebasic/executions/composed.py) file change the reader and the writer class according to the desired input/output (see [kebasicio](kebasic.kebasicio) module for all the possible IO and interfaces)
3. Start CoreNLP server with ```java -Xmx12g -cp "*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer -serverProperties StanfordCoreNLP-spanish.properties -timeout 60000```
4. Run ```python application.py```

NOTES:

1. CoreNLP server requires at least 8GB of RAM, higher is better for allowing to process larger webpages.
2. Set CoreNLP timout to at least a minute in order to allow the processing of large webpages


## Modules Description
Basic description for the different modules. See docs for more info.

###kebasic.domain

Contains the classes that represent the domain specific objects
###kebasic.execution

Contains the different pipelines used in the program
###kebasic.feature

Contains the different algorithms for keyword extraction and score merging
###kebasic.kebasicio

Contains the classes responsible for the IO 
###kebasic.scraper

Contains the scrapy code for crawling webpages
###kebasic.textprocessing

Contains the different algorithms for cleaning and processing of the text

###kebasic.utils
Contains various code used for heterogeneous task 