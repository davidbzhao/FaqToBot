# FaqToBot
FAQ bot generator for websites

## Inspiration
For RamHacks 2017, [Octo](http://www.octoconsulting.com/) challenged hackers to take a website and generate a question-answer bot with a voice interface for that website's FAQ pages. Technical challenges arise in finding the FAQ pages, parsing the FAQ pages, and generating mappings from question intents to answers.

## Structure
### Flow
On the [Android app interface](https://github.com/juliandduque/OCTO-FAQUESTER), the user enters a base url, for example, [http://ramhacks.vcu.edu/](http://ramhacks.vcu.edu/). The app then makes a call to an AWS Lambda function that scrapes the website for pages and returns pages likely to contain an FAQ. For each potential FAQ page, the app attempts to parse the FAQ pages into question-answer pairs. The user can ask a question, via type or via voice, and the app will find and display an answer,leveraging [Microsoft Cognitive Services](https://azure.microsoft.com/en-us/services/cognitive-services/?v=17.29).

### Structure
The Android app interface can be [found here](https://github.com/juliandduque/OCTOFAQ).

The AWS Lambda python script will be described in detail here.

The _scraper.py_ file contains the Lambda function handler. This scraper conducts breadth-first search through all internal-facing links in the anchor tags of each page. For each page visited, multiple features e.g. how many times FAQ appears in the page, are extracted from the html. The features compose an input vector for a basic neural network which generates a likelihood that the page is an FAQ page. If the probability exceeds 50%, the page is tagged as a potential FAQ page. The page crawling continues until there are no more unique pages to visit or the page visit limit (set by the initial Lambda function call) is exceeded. The final list of FAQ urls is concatenated into a newline-separated string and is returned to the origin of the Lambda function call.

_ANN.py_ contains the basic neural network. Data to train the neural network is found in _prepro_training.txt_ and is processed by _DataGeneration.py_. For each url in the training set, the _HtmlFeatureExtractor.py_ extracts a set of quantitative features from the page and outputs that feature data into _training.txt_. The _ANN.py_ can then be trained on the numeric training data in _training.txt_. The weights are stored and restored via a pickle file.

## Links
[Android app repository](https://github.com/juliandduque/OCTOFAQ)

## Credits
* Julian Duque - Link between application and Microsoft Cognitive Services
* Meredith Lee - Application-user interface
* Tony Wang - Amazon Alexa interface through AWS
* David Zhao - AWS Python backend
