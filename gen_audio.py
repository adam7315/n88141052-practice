"""
Generate MP3 audio for all EN sentences in SLIDES using edge-tts.
Output: audio/{voice}/{slide_1based}_{idx}.mp3
Overwrites existing files.
"""
import asyncio, re, os, sys
import edge_tts

sys.stdout.reconfigure(encoding='utf-8')

# ── Parse EN sentences from index.html ──────────────────────────────────────
with open('index.html', encoding='utf-8') as f:
    html = f.read()

en_blocks = re.findall(r'en:\s*\[(.*?)\]', html, re.DOTALL)
slides_en = []
for block in en_blocks:
    items = re.findall(r"'((?:[^'\\]|\\.)*)'", block)
    slides_en.append(items)

total = sum(len(s) for s in slides_en)
print(f'Slides: {len(slides_en)}, Total sentences: {total}')
files = len(slides_en) * 4  # 4 voices... wait, count actual
print(f'Files to generate: {len(slides_en[0] if slides_en else [])}')  # placeholder

VOICES = {
    'christopher': 'en-US-ChristopherNeural',
    'ryan':        'en-GB-RyanNeural',
    'william':     'en-AU-WilliamNeural',
    'jenny':       'en-US-JennyNeural',
}

pairs = []
for si, sentences in enumerate(slides_en):
    for idx, text in enumerate(sentences):
        text = text.replace("\\'", "'")
        for folder, voice in VOICES.items():
            path = f'audio/{folder}/{si+1}_{idx}.mp3'
            pairs.append((path, voice, text))

total_files = len(pairs)
print(f'Files to generate: {total_files}')

async def gen(path, voice, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    comm = edge_tts.Communicate(text, voice)
    await comm.save(path)

async def main():
    done = 0
    chunk = 8
    for i in range(0, total_files, chunk):
        batch = pairs[i:i+chunk]
        await asyncio.gather(*[gen(p, v, t) for p, v, t in batch])
        done += len(batch)
        pct = done * 100 // total_files
        print(f'  [{pct:3d}%] {done}/{total_files}', flush=True)
    print('Done! Generated', total_files, 'files.')

asyncio.run(main())
