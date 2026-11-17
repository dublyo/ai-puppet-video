"""Seedance 2.5 omni_reference request for the full 20 s film (test-video-06), from mockup v026.
Same rules as the pilot, plus the pilot-v1 lessons: say how the stretched stand-in arms and the water must look, and that he never
touches the colander after setting it down (v1 drew his hand going into it).
TEMPLATE: copy to <project>/scripts/build_request.py (paths are relative to that location), then edit PROMPT and the mid()
substrings so they match the file names you uploaded (mid() picks the media id whose uploaded path contains the substring).
Usage:  python3 build_request.py <project>/clips/media-ids.json  -> writes <project>/clips/request-full.json
        (media-ids.json = the saved stdout of `hf_lab.py upload <mockup.mp4> <masters> <look frames>`)
"""
import json, os, sys
D = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(D)
ids = json.load(open(sys.argv[1]))
def mid(part): return next(v for k, v in ids.items() if part in k)
VIDEO, PROF, NORA, S1A, S2A = mid('full-20s'), mid('professor'), mid('nora'), mid('S1a'), mid('S2a')

PROMPT = (
 "Live-action puppet sitcom, vertical 9:16. Real handmade felt hand-and-rod puppets photographed in a real Egyptian home kitchen; "
 "no puppeteers, no rods, no human hands. "
 "The reference video is a colour-coded grey-box animation of this exact scene. Copy it exactly for camera position, lens, framing, "
 "cut timing, blocking, every movement and its timing. Replace its stand-ins with the real characters and props from the reference images; "
 "never copy the stand-in look: no plastic CG, no block hands, no googly eyes. The stand-in arms are stretched tubes: draw normal felt puppet "
 "arms in sleeves, never boards, slabs or poles. "
 "Mapping: the figure in the plum cardigan with the chestnut bob and pink oven mitts is Nora. The figure in the olive suit with the bald head, "
 "dark curly side hair and burgundy bow tie is the Professor; his felt hands are BARE, three fingers and a thumb, never pink, never mitts. "
 "Only Nora wears oven mitts. The silver pot is an aluminium cooking pot, the glass dome with a red knob is its clear glass lid, "
 "the red bowl with holes is a red plastic colander, the yellow pieces are cooked macaroni. Water is clear, thin and real: "
 "no white tubes, no egg-shaped drops. "
 "The kitchen, light and colours come from the kitchen reference images. Only the characters visible in the reference video appear in each shot; "
 "never add a person. Puppet jaws stay closed the whole video; nobody looks into the lens. "
 "After the Professor sets the colander down on the counter he never touches it again; he holds the pot only by its two side handles. "
 "SOUND: foley and sound effects only. No human voice of any kind, no speech, no words, no humming, no laughter, no music. "
 "Sound effects: a pot simmering, a light plastic clack, two glass taps on a lid, a handle scrape, water trickling into a steel sink, "
 "a wet slop of pasta, a glass lid clanking on steel, a pot set down on marble, a hollow plastic tok, soft felt footsteps, then near silence. "
 "Shot timing, matching the reference cuts. "
 "0 to 3.5 s, wide shot: Nora holds the lidded pot over the sink in her mitts; the Professor shakes his head with pity, lifts the red "
 "colander out of the sink with one bare hand and sets it on the counter between them. "
 "3.5 to 6 s, two-shot from his side: he taps the red knob of the lid with one finger, raises his other index finger beside his head "
 "like a wise man, Nora slides the pot toward him and he takes both side handles with his bare hands while her mitts let go and drop away. "
 "6 to 8.2 s, low angle on the Professor alone holding the pot: he shuts one eye, then both, lifts his chin with a smug little smile and nods. "
 "8.2 to 11.5 s, high angle looking down into the pot over the sink, only his bare hands and sleeves in frame: he pushes the lid back a little "
 "with his fingers so a thin gap opens at the front rim; a thin stream of water pours out through the gap into the sink while the macaroni "
 "stays inside and the water level drops; then he tips the pot much further, the lid slips off sideways and falls into the sink, and all the "
 "macaroni with the last of the water pours out into the empty sink; he lifts the empty pot away. "
 "11.5 to 13.5 s, close-up of Nora alone: completely frozen and deadpan, mouth shut, only her eyes slide down and to the right and back. "
 "13.5 to 16.5 s, wide shot: Nora picks up the red colander, turns it upside down and places it on the Professor's head like a helmet, "
 "gives it one gentle pat, turns and walks out of frame to the left; the pasta with the lid stays in the sink. "
 "16.5 to 20 s, close-up of the Professor alone with the red colander upside down on his head: he blinks twice, pinches his crooked bow tie "
 "and straightens it, then holds a dignified smug look with half-closed eyes."
)
assert '"' not in PROMPT
req = {'full': {'model': 'seedance_2_5', 'mode': 'omni_reference', 'prompt': PROMPT, 'duration': 20, 'resolution': '480p',
                'aspect_ratio': '9:16', 'generate_audio': True, 'draft': True,
                'medias': [{'role': 'video_references', 'value': VIDEO}] +
                          [{'role': 'image_references', 'value': v} for v in (PROF, NORA, S1A, S2A)]}}
out = os.path.join(ROOT, 'clips', 'request-full.json')
json.dump(req, open(out, 'w'), ensure_ascii=False, indent=1)
print(out, len(PROMPT), 'chars')
