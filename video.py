"""Assemble les diapos d'un carrousel en vidéo verticale 1080 x 1920 pour un Reel.

Usage : /usr/bin/python3 video.py videos/2026-10-24.mp4 images/2026-10-24-*.jpg
Installe d'abord : /usr/bin/python3 -m pip install -q imageio-ffmpeg
Chaque diapo 1080 x 1350 est centrée sur un fond bleu nuit, avec un glissement
entre les diapos. Piste audio silencieuse (Instagram attend une piste son).
"""
import os, subprocess, sys
import imageio_ffmpeg

sortie, images = sys.argv[1], sys.argv[2:]
if len(images) < 2:
    sys.exit("Il faut au moins 2 images.")

TRANSITION = 0.4
# Couverture courte, diapos de contenu le temps de les lire, dernière diapo un peu plus courte.
durees = [2.5] + [5.0] * (len(images) - 2) + [3.5]
total = sum(durees) - TRANSITION * (len(images) - 1)

cmd = [imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-loglevel", "error"]
for image, duree in zip(images, durees):
    cmd += ["-loop", "1", "-t", f"{duree}", "-i", image]
cmd += ["-f", "lavfi", "-t", f"{total}", "-i", "anullsrc=r=44100:cl=stereo"]

filtres = [
    f"[{i}:v]scale=1080:1350,pad=1080:1920:0:285:color=0x18202c,setsar=1,fps=30,format=yuv420p[v{i}]"
    for i in range(len(images))
]
precedent, decalage = "[v0]", 0.0
for i in range(1, len(images)):
    decalage += durees[i - 1] - TRANSITION
    filtres.append(f"{precedent}[v{i}]xfade=transition=slideleft:duration={TRANSITION}:offset={decalage:.2f}[x{i}]")
    precedent = f"[x{i}]"

os.makedirs(os.path.dirname(os.path.abspath(sortie)), exist_ok=True)
cmd += [
    "-filter_complex", ";".join(filtres),
    "-map", precedent, "-map", f"{len(images)}:a",
    "-c:v", "libx264", "-preset", "medium", "-crf", "21", "-pix_fmt", "yuv420p", "-r", "30",
    "-c:a", "aac", "-b:a", "128k", "-shortest", "-movflags", "+faststart", sortie,
]
subprocess.run(cmd, check=True)
print(f"OK {sortie} ({total:.1f} s, {os.path.getsize(sortie) / 1e6:.1f} Mo)")
