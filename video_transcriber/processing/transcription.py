from faster_whisper import WhisperModel


WHISPER_MODEL = None


def get_whisper_model():
    '''
    Loads the Whisper model if it hasn't been loaded already and returns it.
    '''

    global WHISPER_MODEL
    if WHISPER_MODEL is None:
        WHISPER_MODEL = WhisperModel(
            'small',
            device='cpu',
            compute_type='int8'
        )
    
    return WHISPER_MODEL


def transcribe_audio(audio_path: str) -> str:
    '''
    Transcribes the audio file at the specified path using the Whisper model.
    The audio is processed in chunks to handle long audio files, 
    with a small overlap to ensure continuity between chunks. 
    The transcribed text from all chunks is concatenated and returned as a single string.    

    audio_path: The path to the audio file to be transcribed.
    returns: The transcribed text from the audio file.
    '''
   
    model = get_whisper_model()
    segments, info = model.transcribe(audio_path, beam_size=5)

    full_text = []
    timestamps = []

    for segment in segments:
        text = segment.text.strip()
        full_text.append(text)
        timestamps.append({
            'start': round(segment.start, 2),
            'end': round(segment.end, 2),
            'text': text
        })

    return {
        'text': ' '.join(full_text),
        'timestamps': timestamps
    }

def format_timestamps(timestamp: float) -> str:
    '''
    Formats a timestamp in seconds into a string in the format HH:MM:SS. 
    If the timestamp is less than an hour, it will be formatted as MM:SS.

    timestamp: The timestamp in seconds to be formatted.
    return: The formatted timestamp string.
    '''
    
    timestamp = int(timestamp)
    hours = timestamp // 3600
    minutes = (timestamp % 3600) // 60
    seconds = timestamp % 60

    if hours:
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    
    return f"{minutes:02d}:{seconds:02d}"
