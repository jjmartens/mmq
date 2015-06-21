## MMQ

[![Join the chat at https://gitter.im/jantjee314/mmq](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/jantjee314/mmq?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)
A small and shared music player powered by youtube build with a AngularJS frontend and a Flask backend.

## Motivation
At work we have one pc playing music. MMQ lets everyone request songs to be played on this pc, it puts the songs in a queue and keeps track of a playlist. This way everyone can add their favorite songs from their own computers without interruptions.

## Demo
You can find a working demo on http://mmq.audio. Note: please make a channel for your own to play in.

## Installation
- Clone this repo
- Install requirements with `pip install -r requirements.txt`
- Change database info in manage.py
- make a database and migrate scheme with `python manage.py db upgrade`
- Insert your own youtube api key in app.js
- Run server with `python manage.py runserver`

## Future
The next thing I will make is support for users. Private channels, single user playlist mode, favorite songs etc. 

I also have been thinking about dropping the index (channel overview). And make a dropdown or something to switch channels, in order to make it a true single page application. 

## Contributors
Front end javascript based on https://github.com/jgthms/juketube.