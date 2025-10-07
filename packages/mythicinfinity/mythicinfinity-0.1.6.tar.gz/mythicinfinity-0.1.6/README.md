<!-- PROJECT LOGO -->

<p align="center">
  <a href="https://www.mythicinfinity.com">
    <img src="https://www.mythicinfinity.com/app/assets/email-logo.png" 
     alt="Logo" height="36">
  </a>

  <h3 align="center">MythicInfinity Python Client</h3>

  <p align="center">
    <img src="https://img.shields.io/pypi/v/mythicinfinity" alt="pypi version" />
    <img src="https://img.shields.io/pypi/pyversions/mythicinfinity" alt="supported python versions" />
    <img src="https://img.shields.io/github/license/mythicinfinity/mythicinfinity-python" alt="license">
  </p>

  <p align="center">
    Up to 100x Cheaper, High Quality, Realtime Text-to-Speech
    <br />
    <a href="https://www.mythicinfinity.com/app/register"><strong>Sign Up for an API Key »</strong></a>
    <br />
    <br />
    <a href="https://www.mythicinfinity.com/docs">Read the docs</a>
    ·
    <a href="https://github.com/mythicinfinity/mythicinfinity-python/issues">Report Bug</a>
  </p>
</p>

### Overview

 - Easy installation with pip.
 - Streaming audio bytes and non-streaming both supported.
 - Async/await and standard sync code both supported.
 - Full IDE support with autocomplete, type-hinting, and in-code documentation.

#### Table of Contents

- [Installation](#Installation)
- [Basic Example](#Basic-Example)
- [Environment Variables](#Environment-Variables)
- [Streaming Example](#Streaming-Example)
- [Async Support](#Async-Support)
- [Voice Options](#Voice-Options)
- [Output Formats](#Output-Formats)
- [Voice API](#Voice-API)

## Installation

Install the python package as a dependency of your application.

```bash
$ pip install mythicinfinity
```

## Basic Example

```python
from mythicinfinity import MythicInfinityClient


def main():
    # Instantiate the client with your api key
    client = MythicInfinityClient(api_key="YOUR_API_KEY")
    
    # Call the TTS API. By default, stream is False.
    audio_bytes = client.tts.generate(text="Hello world.")
    
    with open('my_audio.wav', 'wb') as f:
        f.write(audio_bytes)

if __name__ == "__main__":
    main()
```

This sample calls the Text-To-Speech service and saves the resultant audio bytes to a file.

## Environment Variables

| Name   | Description |
| -------- | ------- |
| `MYTHICINFINITY_API_KEY`  | Sets the api key. There is no need to pass `api_key="YOUR_API_KEY"` to the client constructor when using the environment variable. |

## Streaming Example

```python
from mythicinfinity import MythicInfinityClient


def main():
    # Instantiate the client with your api key
    client = MythicInfinityClient(api_key="YOUR_API_KEY")
    
    # Call the TTS API with stream=True.
    # This will stream the audio bytes in real-time, 
    #   as they become available from the AI model.
    audio_bytes_generator = client.tts.generate(text="Hello world.", stream=True)
    
    with open('my_audio.wav', 'wb') as f:
        for audio_bytes in audio_bytes_generator:
            f.write(audio_bytes)

if __name__ == "__main__":
    main()
```


## Async Support

- Code relying on `async / await` patterns is fully supported.

```python
import asyncio
from mythicinfinity import AsyncMythicInfinityClient


async def main():
    # Instantiate the client with your api key
    client = AsyncMythicInfinityClient(api_key="YOUR_API_KEY")
    
    # Call the TTS API with stream=False.
    audio_bytes = await client.tts.generate(text="Hello world.")
    
    with open('my_async_audio_1.wav', 'wb') as f:
        f.write(audio_bytes)
    
    # Call the TTS API with stream=True.
    # This will stream the audio bytes in real-time, 
    #   as they become available from the AI model.
    audio_bytes_generator = await client.tts.generate(text="Hello world.", stream=True)
    
    with open('my_async_audio_2.wav', 'wb') as f:
        async for audio_bytes in audio_bytes_generator:
            f.write(audio_bytes)

if __name__ == "__main__":
    asyncio.run(main())
```

This sample first calls the `client.tts.generate` method without streaming using `await` and then does the same with 
streaming enabled.

## Voice Options

The `voice_id` parameter controls which voice is used for the generated audio. 

You can use the [Voice API](#Voice-API) to list all available voice ids and get 
their related metadata.

The model supports various options which can be set to adjust the way audio is 
generated with the voice in various ways.

Each voice may specify its own default values for these parameters.

Voice Option Parameters:
- `consistency` - The recommended value is 2.0. Higher values tend to follow text more reliably, and pronounce words with more accuracy, but alters the way speech is spoken and may increase the speaking rate.

```python
from mythicinfinity import MythicInfinityClient, VoiceOptions

def main():
    # Instantiate the client with your api key
    client = MythicInfinityClient(api_key="YOUR_API_KEY")
    
    # Call the API setting the consistency VoiceOption
    audio_bytes_generator = client.tts.generate(
        text="Hello world.", stream=True,
        voice_id="",
        voice_options=VoiceOptions(
            consistency=2.4,
        )
    )
    
    with open('my_audio.wav', 'wb') as f:
        for audio_bytes in audio_bytes_generator:
            f.write(audio_bytes)

if __name__ == "__main__":
    main()
```

## Output Formats

By default, outputs are in the `wav` format.

The currently supported output formats are:
- `wav` - 24khz 16 bit WAV
- `pcm` - 24khz 16 bit raw PCM data
- `mp3` - 24khz 192kbps MP3
- `webm_opus` - 24khz 128kbps OPUS inside a WEBM container (saved as a `.webm` file)

For streaming playback (that starts before the whole audio is done generating), usually `mp3` or `webm_opus` are used.

For the highest output quality, we recommend `wav`.

#### Specifying Output Format

To specify the output format, simply set the `format` parameter in the `.generate()` call.

Valid values are `wav`, `pcm`, `mp3` and `webm_opus`.

```python
from mythicinfinity import MythicInfinityClient

def main():
    # Instantiate the client with your api key
    client = MythicInfinityClient(api_key="YOUR_API_KEY")
    
    # Call the API setting format=mp3
    audio_bytes_generator = client.tts.generate(text="Hello world.", stream=True, format="mp3")
    
    # Save the audio as a .mp3 file
    with open('my_audio.mp3', 'wb') as f:
        for audio_bytes in audio_bytes_generator:
            f.write(audio_bytes)

if __name__ == "__main__":
    main()
```


## Voice API

##### Voice Object

```python
class Voice:
    name: str
    voice_id: str
    model_ids: typing.List[str]
    """
    Model IDs that this voice is compatible with.
    """

    preview_urls_by_model_id: typing.Dict[str, str]
    """
    Preview urls for this voice per model id.
    """
```

The voice objects returned by this api will have this structure.

##### List Voices

Sync
```python
all_voices = client.tts.voices.list()
```

Async
```python
all_voices = await async_client.tts.voices.list()
```

##### Get Voice Data

Sync
```python
voice = client.tts.voices.get("kiera")
```

Async
```python
voice = await async_client.tts.voices.get("kiera")
```