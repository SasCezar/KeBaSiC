# KeBaSiC
A tool for keyword extraction from webpages 

## Installation
KeBaSic is written in Python 3, and is required at least Python 3.5. In order to install the required dependencies run:

```
   pip install -r requirements.txt
```

The tool also requires installing the following programs:

1. Stanford CoreNLP Server. It requires different files:
   1. The server from <a href="https://stanfordnlp.github.io/CoreNLP/">https://stanfordnlp.github.io/CoreNLP/</a>;
   2. The language specific jar file from <a href="https://stanfordnlp.github.io/CoreNLP/download.html">https://stanfordnlp.github.io/CoreNLP/download.html</a>; 
   3. The language properties file from <a href="https://github.com/stanfordnlp/CoreNLP/blob/master/src/edu/stanford/nlp/pipeline/StanfordCoreNLP-spanish.properties">https://github.com/stanfordnlp/CoreNLP/blob/master/src/edu/stanford/nlp/pipeline/StanfordCoreNLP-spanish.properties</a>

    Place the language specific jar and properties file in the server folder.
2. TreeTagger from <a href="http://www.cis.uni-muenchen.de/%7Eschmid/tools/TreeTagger/">http://www.cis.uni-muenchen.de/%7Eschmid/tools/TreeTagger/</a>

3. WEKA from https://www.cs.waikato.ac.nz/ml/weka/downloading.html, and install the LibSVM package from WEKA's package managere.

## Usage
### Keyword Extraction
1. Edit the [config.json](kebasic/config.json) file with the input and the output files
2. In the [composed.py](kebasic/executions/composed.py) file change the reader and the writer class according to the desired input/output (see [kebasicio](kebasic.kebasicio) module for all the possible IO and interfaces)
3. Start CoreNLP server with ```java -Xmx12g -cp "*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer -serverProperties StanfordCoreNLP-spanish.properties -timeout 60000```
4. Run ```python application.py -input_path="../data/test.json" [-out_path="../output/keywords_extraction/results_test.json" -std_out -log -log_path="../log"]```

Where the arguments in the square brackets are optional. The arguments are:
* out_path: The path where the results will be saved, if is not specified there will be no saved results.
* std_out: Enables the print of the results on standard output, if not specified, no result will be printed on standard output
* log: Enables the logging, if non specified the logging will not be enabled
* log_path: Defines the path where the logs will be saved, if not defined the log will only be printed on standard output

NOTES:

1. CoreNLP server requires at least 8GB of RAM; higher is better for allowing to process larger webpages.
2. Set CoreNLP timeout to at least a minute in order to allow the processing of large webpages
### Dataset Creation
1. Create the queries by running the scripts file with the following command:

    ```python scripts.py query --template "../resources/ES/query/templates/bing.txt" --keys "../resources/ES/query/keywords.txt" --out "result_query.txt"```

2. Exploit Bing for searching relevant web links to the queries using: https://github.com/NikolaiT/GoogleScraper. 
Run:

	```GoogleScraper -m http --keyword-file keywords.txt --num-workers 10 --proxy-file proxies.txt --search-engines "bing" --output-filename output.json```
	
3 - Collect the webpages, prerocess them and generate the files for the model training. For the best result check if the following classes are in the preprocessing:
      
         
            "textprocessing.cleaner.MailCleaner",
            "textprocessing.cleaner.URLCleaner",
            "textprocessing.cleaner.WordsWithNumbersCleaner",
            "textprocessing.cleaner.NonPunctuationSymbolsCleaner",
            "textprocessing.cleaner.CommonWords",
            "textprocessing.cleaner.LocationsCleaner",
            "textprocessing.cleaner.StopWordsCleaner",
            "textprocessing.cleaner.PunctuationSpacesCleaner",
            "textprocessing.cleaner.MultipleSpacesCleaner",
            "textprocessing.cleaner.Clean4SQL",
            "textprocessing.cleaner.PunctuationCleaner",
            "textprocessing.stemmer.Stemmer"
        
The run:

	python scripts.py dataset --input "../data/GoogleScraper_test_results.json" --out "../data/train_dataset" --workers 8

### Classification Training:
Train the model:

    python scripts.py train --input "../data/train_dataset_lvl1.csv" --out "../data/model_lvl1_test.model"


## Modules Description
Basic description for the different modules. See docs for more info.
### kebasic.domain
Contains the classes that represent the domain specific objects
### kebasic.execution
Contains the different pipelines used in the program
### kebasic.feature
Contains the different algorithms for keyword extraction and score merging
### kebasic.kebasicio
Contains the classes responsible for the IO 
### kebasic.scraper
Contains the scrapy code for crawling webpages
### kebasic.textprocessing
Contains the different algorithms for cleaning and processing of the text
### kebasic.utils
Contains various code used for heterogeneous task

## Resources
In this section are presented the editable resources in order to allow the customization of the tool.
These files can be language dependant or independent. The language specific files are placed in the language folder.
### Stopwords
The file stopwords contains common words of the specific language. This file can be modified to remove unwanted words to be extracted as keywords.

NOTE: The tool uses stopwords as separator of keywords, so the words present in this file will not imply that the word will not be present in the results.

### Commonwords 
The common words file contains undesired and words that are common on websites (e.g Facebook/share/login and more). These words will be removed before preprocessing with other algorithms. These words will not be present in the keywords.

### Location Names
This files contains the names of possible location that are undesired.