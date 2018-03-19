# crimechecker

Crimechecker is a PWA and Flask API that facilitates searching for crime data
at a specific post code in the UK.

### Getting Started

**Setting up the API** is easy, simply deploy the python API in any way you like. The app
will need some time to cache requests when newly deployed so it may execute
a few requests slowly to start with.

API Docs: https://documenter.getpostman.com/view/3008197/crime-tracker/7EHaWs8

**The PWA** is built with webpack. To point it to your deployed API, change the `API_URL`
variable in `webpack.prod.js` to the root address.

### Contributing

The repo is always open to pull requests or issues. It is currently in a proof-of-concept
state and any improvements to the API or web app is welcome. Some suggestions:

- bike view to see in-depth data about a stolen bike
- crime view to see in-depth data about a crime

Simply fork the repo and start working on changes in a new branch. When the change or
feature is ready, open a pull request.

### Data

#### Sources

Data is aggregated and cached from the following sources:

- BikeRegister
- UK Police
- Google maps
- Twitter RSS
- UK Postcodes
- Wikipedia

#### Limitations

Crime data is limited in Scotland due to the scottish police opting
out when it comes to the API. However bike theft is still available.