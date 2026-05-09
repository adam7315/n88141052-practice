"""Generate pre-built MP3 audio files for all slide sentences using edge-tts."""
import asyncio, re, os, sys

VOICES = {
    'christopher': 'en-US-ChristopherNeural',
    'ryan':        'en-GB-RyanNeural',
    'william':     'en-AU-WilliamNeural',
    'jenny':       'en-US-JennyNeural',
}

def extract_sentences():
    with open('index.html', encoding='utf-8') as f:
        content = f.read()
    en_arrays = re.findall(r'en: \[(.*?)\],\s*zh:', content, re.DOTALL)
    slides = []
    for arr in en_arrays:
        # Extract quoted strings, handle escaped quotes
        sentences = re.findall(r"'((?:[^'\\]|\\.)*)'", arr)
        slides.append(sentences)
    return slides

async def gen_one(text, voice_id, path):
    import edge_tts
    communicate = edge_tts.Communicate(text, voice_id)
    await communicate.save(path)

async def main():
    slides = extract_sentences()
    total = sum(len(s) for s in slides)
    print(f"Slides: {len(slides)}, Total sentences: {total}")

    tasks = []
    for vname, vid in VOICES.items():
        os.makedirs(f'audio/{vname}', exist_ok=True)
        for si, sentences in enumerate(slides):
            for idx, text in enumerate(sentences):
                path = f'audio/{vname}/{si+1}_{idx}.mp3'
                if os.path.exists(path):
                    continue
                tasks.append((text, vid, path))

    print(f"Files to generate: {len(tasks)} (skipping existing)")

    done = 0
    # Process in batches of 8 to avoid rate limiting
    batch = 8
    for i in range(0, len(tasks), batch):
        chunk = tasks[i:i+batch]
        await asyncio.gather(*[gen_one(t, v, p) for t, v, p in chunk])
        done += len(chunk)
        pct = done * 100 // len(tasks) if tasks else 100
        print(f"  [{pct:3d}%] {done}/{len(tasks)}", end='\r')
        await asyncio.sleep(0.3)

    print(f"\nDone! Generated {done} files.")

if __name__ == '__main__':
    asyncio.run(main())
