# Vocal-Vision

## Description

Vocal-Vision extends [Google NotebookLM](https://notebooklm.google.com/) by transforming text and audio queries into dynamic video podcasts featuring AI-generated talking avatars. The platform integrates speaker MP3 audio files and AI-driven video generation to add a compelling visual layer to knowledge sharing. A full-stack web application hosts the experience, built with a JavaScript/CSS/HTML frontend and a Python Flask backend connected to MongoDB Atlas.

## Table of Contents

- [Description](#description)
- [Installation](#installation)
- [Usage](#usage)
- [Credits](#credits)
- [License](#license)
- [Features](#features)
- [How To Contribute](#how-to-contribute)
- [Tests](#tests)

## Installation

1. Clone the repository.
2. Install Python dependencies:
```bash
   pip install flask pymongo
```
3. Obtain speaker MP3 audio files via [Google NotebookLM](https://notebooklm.google.com/).
4. Configure your MongoDB Atlas connection string in the environment variables.

## Usage

1. Start the Flask development server:
```bash
   python app.py
```
2. Open `http://localhost:5000` in your browser.
3. Input a text or audio query, optionally upload speaker images, and generate your video podcast.

## Credits

1. https://github.com/HassanZafar-2021
2. https://github.com/Aaryan369

## License

MIT License

## Features

- 🎙️ Input text or audio queries to drive podcast generation
- 🖼️ Upload images of speakers to personalize avatars
- 🤖 AI-generated talking avatars synced to NotebookLM audio output
- 🌍 Supports up to 14 languages
- 🏆 **Award:** Won the sponsored *"Best Use of NotebookLM"* track at **DivHacks @ Columbia University**
- 🔄 Built with Agile methodology — iteratively expanding language support and video duration

## How To Contribute

1. Fork the repository.
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit your changes and open a pull request against `main`.

## Tests

1. Create a `tests/` directory in the project root.
2. Run the test suite:
```bash
   npm run tests
```