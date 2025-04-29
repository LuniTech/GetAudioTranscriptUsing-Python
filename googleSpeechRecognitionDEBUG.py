import os
import sys
import tempfile
import time
import speech_recognition as sr
from pydub import AudioSegment

# =============================================
# 1. FFMPEG CONFIGURATION (Debugged here!)
# =============================================
def configure_ffmpeg():
    """Absolute path verification with system PATH modification"""
    # ffmpeg folder absolute path
    ffmpeg_dir = r"C:\Users\Student\Desktop\Python programs\Python transcriber\ffmpeg-2025-04-14-git-3b2a9410ef-essentials_build\bin"
    
    # check if directory exists
    if not os.path.isdir(ffmpeg_dir):
        raise FileNotFoundError(f"FFmpeg directory not found: {ffmpeg_dir}")

    # utilize the executable files in the bin folder here
    ffmpeg_path = os.path.join(ffmpeg_dir, "ffmpeg.exe")
    ffprobe_path = os.path.join(ffmpeg_dir, "ffprobe.exe")

    # do a check to see if they exist...so we just doing error handling here
    missing = []
    if not os.path.isfile(ffmpeg_path): missing.append("ffmpeg.exe")
    if not os.path.isfile(ffprobe_path): missing.append("ffprobe.exe")
    if missing:
        raise FileNotFoundError(f"Missing in {ffmpeg_dir}: {', '.join(missing)}")

    # Add to system PATH temporarily (crucial for pydub) (THIS IS WERE I MESSED UP)
    os.environ['PATH'] = ffmpeg_dir + os.pathsep + os.environ['PATH']
    
    # This code helps resolve previous errors I experienceed
    AudioSegment.converter = ffmpeg_path
    AudioSegment.ffprobe = ffprobe_path
    
    print(" FFmpeg verification passed!!!")
    print(f"  → ffmpeg.exe: {os.path.isfile(ffmpeg_path)}")
    print(f"  → ffprobe.exe: {os.path.isfile(ffprobe_path)}")
    print(f"  → System PATH updated\n")

# ==============================================================
# 2. Change our audio to wave file and then transcribe it!
# ==========================================================
def transcribe_audio(file_path):
    """Robust transcription with subprocess validation"""
    
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"Audio file missing: {file_path}")
    print(f"️ Loading: {os.path.basename(file_path)} ({os.path.getsize(file_path)/1024:.1f} KB)")

    recognizer = sr.Recognizer()
    temp_files = []
    
    try:
       
        temp_wav = tempfile.mktemp(suffix='.wav')
        temp_files.append(temp_wav)
        
        print("  → Converting to WAV...")
        audio = AudioSegment.from_file(file_path)
        audio.export(temp_wav, format="wav")
        
        if os.path.getsize(temp_wav) == 0:
            raise RuntimeError("FFmpeg conversion failed - empty WAV file created")

        
        print("   Transcribing...")
        with sr.AudioFile(temp_wav) as source:
            audio_data = recognizer.record(source)
            return recognizer.recognize_google(audio_data)
            
    except Exception as e:
        print(f"   Error during processing: {str(e)}")
        raise
    finally:
        for f in temp_files:
            try:
                if os.path.exists(f):
                    os.remove(f)
            except:
                pass

# =============================================
# Main with better error handling and checking!!!!!!!!!
# =============================================
if __name__ == "__main__":
    try:
      
        configure_ffmpeg()
        
       #VERY IMPORTANT TO CHANGE YOUR AUDIO FILE HERE. MAKE THE PATH ABSOLUTE!
        audio_file = r"C:\Users\Student\Desktop\Python programs\Python transcriber\Intro to Virology 2012 voice recording low quality.mp3"
        
        
        if not os.path.isfile(audio_file):
            raise FileNotFoundError(f"Audio file not found:\n{audio_file}")
        
        
        print(" Starting transcription...")
        start = time.time()
        result = transcribe_audio(audio_file)
        
        
        print("\n" + "="*60)
        print(f"SUCCESS! Transcription completed in {time.time()-start:.1f}s")
        print("="*60)
        print(result[:500] + ("..." if len(result)>500 else ""))
        
        
        with open("transcription.txt", "w", encoding="utf-8") as f:
            f.write(result)
        print(f"\n💾 Saved full transcript to 'transcription.txt'")
        
    except Exception as e:
        print("\n CRITICAL ERROR:", str(e))
        print("\nTROUBLESHOOTING STEPS:")
        print("1. Open the ffmpeg bin folder in File Explorer")
        print("   → Verify both ffmpeg.exe and ffprobe.exe exist")
        print("2. Right-click each .exe → Properties → Unblock")
        print("3. Disable antivirus temporarily")
        print("4. Try a simpler path (e.g., C:\\ffmpeg\\bin)")
        print("5. Download fresh FFmpeg from: https://www.gyan.dev/ffmpeg/builds/")
        sys.exit(1)
