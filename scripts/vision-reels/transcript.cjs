const fs = require('node:fs');
const path = require('node:path');

function writeTranscript(spec, cues, output) {
  const stamp = (ms) => {
    const sec = Math.floor(ms / 1000);
    return Math.floor(sec / 60) + ':' + String(sec % 60).padStart(2, '0');
  };
  const lines = [spec.title, '', spec.source, spec.sourceUrl, ''];
  for (const scene of spec.scenes) {
    const entries = cues.filter((cue) => cue.scene === scene.id);
    lines.push(
      stamp(entries[0].startMs) + '–' + stamp(entries.at(-1).endMs) + '  ' + scene.title,
      '',
    );
    for (const entry of entries) lines.push(stamp(entry.startMs) + '  ' + entry.text);
    lines.push('');
  }
  fs.writeFileSync(path.join(output, 'script.txt'), lines.join('\n').trimEnd() + '\n');
}
module.exports = { writeTranscript };
