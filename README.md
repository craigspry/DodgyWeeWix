#DodgyWeeWix

This is a collection of projects that all work together to get weather readings from the sensors outside into WeeWix.

##CloudHeight
CloudHeight an Arduino Uno project that has the Sparkfun weather shield connected that reads the readings from the various sensors and writes them as a CSV string to the serial port. It also determines the height of the clouds using the pressure and temperature. This was based of an example implementation by Nathan Seidle.

##WeatherReader
WeatherReader is responsible for reading the values coming in from CloudHeight and publishing them on MQTT. It is written in Python.

##WeewxDodgyClient
WeewxDodgyClient listens for changes in the weather values on the MQTT server. This was heavily bassed on the example client in the WeeWix project written by Matthew Wall.
