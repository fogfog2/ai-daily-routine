const path = require('node:path');
const fs = require('node:fs');
const { execFileSync } = require('node:child_process');
const { bundle } = require('@remotion/bundler');
const { writeTranscript } = require('./transcript.cjs');
const { selectComposition, renderMedia, renderStill } = require('@remotion/renderer');

async function render() {
  const args = process.argv.slice(2);
  const stillsOnly = args.includes('--stills');
  const [work, site, ...episodes] = args.filter((arg) => arg !== '--stills');
  if (!work || !site || !episodes.length)
    throw Error('Usage: node render.cjs WORK MEDIA_DIR EPISODE ...');
  const serveUrl = await bundle({ entryPoint: path.join(__dirname, 'index.jsx') });
  const settings = {
    serveUrl,
    browserExecutable: process.env.REMOTION_BROWSER || null,
    logLevel: 'warn',
    timeoutInMilliseconds: 90000,
  };
  for (const id of episodes) {
    const dir = path.resolve(work, id),
      output = path.resolve(site, id);
    fs.mkdirSync(output, { recursive: true });
    const cues = JSON.parse(fs.readFileSync(path.join(dir, 'cues.json')));
    writeTranscript(JSON.parse(fs.readFileSync(path.join(__dirname, id + '.json'))), cues, output);
    const inputProps = { cues };
    const composition = await selectComposition({ ...settings, id, inputProps });
    const still = { ...settings, composition, inputProps, imageFormat: 'jpeg', jpegQuality: 90 };
    await renderStill({
      ...still,
      frame: Math.floor(composition.fps * 4),
      output: path.join(output, 'poster.jpg'),
    });
    for (const second of [false, true]) {
      const props = { id, second };
      const demo = await selectComposition({ ...settings, id: 'demo-' + id, inputProps: props });
      await renderStill({
        ...settings,
        composition: demo,
        inputProps: props,
        imageFormat: 'jpeg',
        jpegQuality: 90,
        frame: 0,
        output: path.join(output, second ? 'view-b.jpg' : 'view-a.jpg'),
      });
    }
    if (stillsOnly) continue;
    const silent = path.join(dir, 'silent.mp4');
    let last = 0;
    await renderMedia({
      ...settings,
      composition,
      inputProps,
      codec: 'h264',
      pixelFormat: 'yuv420p',
      muted: true,
      crf: 19,
      x264Preset: 'veryfast',
      imageFormat: 'jpeg',
      jpegQuality: 88,
      concurrency: 2,
      outputLocation: silent,
      onProgress: ({ progress }) => {
        const mark = Math.floor(progress * 10);
        if (mark > last) {
          console.log(id, mark * 10 + '%');
          last = mark;
        }
      },
    });
    execFileSync('ffmpeg', [
      '-loglevel',
      'error',
      '-y',
      '-i',
      silent,
      '-i',
      path.join(dir, 'audio.wav'),
      '-map',
      '0:v:0',
      '-map',
      '1:a:0',
      '-c:v',
      'copy',
      '-af',
      'loudnorm=I=-16:TP=-1.5:LRA=7',
      '-ar',
      '48000',
      '-c:a',
      'aac',
      '-b:a',
      '112k',
      '-metadata:s:a:0',
      'language=kor',
      '-movflags',
      '+faststart',
      path.join(output, 'video.mp4'),
    ]);
    fs.copyFileSync(path.join(dir, 'ko.vtt'), path.join(output, 'ko.vtt'));
    console.log('Finished', id);
  }
}
render().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
