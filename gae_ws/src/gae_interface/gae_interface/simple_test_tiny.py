import speech_recognition as sr
from faster_whisper import WhisperModel
from gtts import gTTS
import os
import io
import wave

def get_mic_index():
    """ 'pulse'라는 이름이 들어간 마이크 번호를 자동으로 찾습니다. """
    print("\n🔍 마이크 장치 검색 중...")
    mic_list = sr.Microphone.list_microphone_names()
    
    # 1순위: 'pulse' 찾기
    for i, name in enumerate(mic_list):
        if 'pulse' in name.lower():
            print(f"✅ 'pulse' 마이크 발견! [번호: {i}] {name}")
            return i
            
    # 2순위: 'default' 찾기
    for i, name in enumerate(mic_list):
        if 'default' in name.lower():
            print(f"⚠️ 'pulse'는 없지만 'default' 발견 [번호: {i}] {name}")
            return i
            
    print("❌ 적절한 마이크를 찾지 못했습니다. 기본값(None)을 사용합니다.")
    return None

def main():
    # 1. 마이크 자동 설정
    mic_index = get_mic_index()
    
    print("\n🤖 모델 로딩 중...")
    model = WhisperModel("tiny", device="cpu", compute_type="int8")
    recognizer = sr.Recognizer()
    
    # 2. 듣기
    print("\n🎤 [테스트] 마이크에 대고 말씀해주세요! (3초간 녹음)")
    mic = sr.Microphone(device_index=mic_index, sample_rate=16000)
    
    with mic as source:
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
        except Exception as e:
            print(f"❌ 녹음 실패: {e}")
            return

    # 3. 인식하기
    print("📝 분석 중...")
    wav_buffer = io.BytesIO()
    with wave.open(wav_buffer, 'wb') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(audio.sample_width)
        wav_file.setframerate(audio.sample_rate)
        wav_file.writeframes(audio.frame_data)
    wav_buffer.seek(0)
    
    segments, _ = model.transcribe(wav_buffer, language="ko")
    text = " ".join([seg.text for seg in segments]).strip()
    print(f"결과: \"{text}\"")

    # 4. 말하기
    if text:
        print(f"🗣️ 따라 말하기: {text}")
        tts = gTTS(text=text, lang='ko')
        tts.save("test.mp3")
        os.system("play -q test.mp3 vol 2.0")

if __name__ == "__main__":
    os.system("apt-get install -y libsox-fmt-mp3 > /dev/null 2>&1")
    main()
