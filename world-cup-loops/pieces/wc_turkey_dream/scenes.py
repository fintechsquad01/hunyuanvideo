"""Scene definitions for the Turkey fever-dream long-form piece.

Each scene is a single ~6s shot generated via the MCP video tool.
Prompts follow the HunyuanVideo prompt-encode template structure:
  main content → object details → actions → background/light/style → camera.

Edit prompts here before running build_long_form.py.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Scene:
    id: str
    title: str
    duration: int
    prompt: str
    model: str = "veo3_1_lite"
    aspect_ratio: str = "9:16"
    resolution: str = "1080p"
    negative_prompt: str = "Aerial view, aerial view, overexposed, low quality, deformation, a poor composition, bad hands, bad teeth, bad eyes, bad limbs, distortion"
    notes: str = ""
    native_audio: bool = False  # hero scenes use veo3_1 (full) with native audio


SCENES: list[Scene] = [
    Scene(
        id="s01_calm",
        title="THE CALM",
        duration=6,
        prompt=(
            "An elderly Turkish man with weathered hands and a white moustache sits at "
            "a wooden table in a warmly-lit Istanbul tea house, pouring deep crimson çay "
            "into a small tulip-shaped glass from a traditional double teapot. Steam "
            "rises slowly from the glass. On a small CRT television behind him a Turkish "
            "national football team match plays silently. Golden late-afternoon window "
            "light streams through lace curtains, warm tungsten lamps glow on copper "
            "trays nearby. Slow dolly-in shot framed symmetrically, shallow depth of "
            "field, gentle bokeh. Style: warm cinematic photorealism. Atmosphere: "
            "peaceful, anticipatory, intimate."
        ),
        notes="Cold open. Sets tone + introduces our character who reappears in scene 10.",
    ),
    Scene(
        id="s02_goal",
        title="THE GOAL",
        duration=5,
        prompt=(
            "Extreme close-up of a white football ball striking the back of a goal net "
            "in extreme slow motion, the net ripples dramatically outward, droplets of "
            "water spray from the ball, the surrounding stadium lights blur into red "
            "and white streaks. A faint Turkish flag color wash overlays the moment. "
            "Locked tight macro shot, slight push-in. Style: cinematic photorealism, "
            "broadcast slow-motion replay aesthetic. Atmosphere: climactic, transcendent."
        ),
        notes="The pivot moment. Sound design will spike here.",
    ),
    Scene(
        id="s03_galata",
        title="GALATA ERUPTS",
        duration=6,
        prompt=(
            "The Galata Bridge in Istanbul at twilight, thousands of fans in red Turkish "
            "national jerseys flood across the bridge waving enormous red flags with "
            "white crescent and star, bright red road flares burn and pour smoke into "
            "the sky, ferries pass below on the dark Bosphorus sounding their horns, "
            "the silhouette of historic mosque domes stands behind the crowd. Aerial "
            "drone shot sweeping low over the crowd then rising up to reveal the "
            "bridge's full length. Dramatic dusk lighting with red flare illumination. "
            "Style: cinematic photorealism. Atmosphere: explosive collective joy, anthemic."
        ),
        notes="First public celebration beat. Big crowd shot.",
    ),
    Scene(
        id="s04_dervish",
        title="THE DERVISH ASCENDS",
        duration=6,
        prompt=(
            "A whirling dervish dancer in long flowing white robes and a tall brown "
            "conical felt cap spins in graceful continuous rotation on an open stone "
            "plaza, arms extended outward with one palm to the sky and one to the earth, "
            "robes billowing in slow motion. Hovering above his head a small glowing "
            "golden World Cup trophy floats and slowly rotates in the opposite direction. "
            "Soft mystical golden light radiates from below upward. A historic Ottoman "
            "mosque silhouette stands in the deep background at twilight. Slow orbiting "
            "camera shot at chest height, slight low angle. Style: spiritual cinematic "
            "surrealism. Atmosphere: transcendent, joyful, sacred celebration."
        ),
        notes="The mystical-surreal beat. Cultural depth.",
    ),
    Scene(
        id="s05_cappadocia",
        title="CAPPADOCIA RAPTURE",
        duration=6,
        prompt=(
            "Aerial dawn shot over the dramatic rock formations and fairy chimneys of "
            "Cappadocia, dozens of hot air balloons rise from the misty valley floor "
            "into a golden pink sky — but each balloon is shaped like a glowing golden "
            "World Cup trophy, the trophies gently rotating as they ascend, soft warm "
            "morning light illuminating the unique terrain below. Slow cinematic "
            "aerial pull-back and rise revealing the staggering scale of the valley. "
            "Style: magical realism cinematic photorealism. Atmosphere: dreamy, "
            "majestic, wondrous awakening."
        ),
        notes="Magical realism centerpiece. Postcard-iconic Turkey.",
    ),
    Scene(
        id="s06_bosphorus",
        title="BOSPHORUS TRIUMPH",
        duration=6,
        model="veo3_1",
        native_audio=True,
        prompt=(
            "An ornate traditional Bosphorus passenger ferry painted red and white "
            "sails directly toward the camera at golden hour sunset, on its bow stands "
            "a massive gleaming golden World Cup trophy mounted as a centerpiece, "
            "fans on deck wave Turkish flags, the iconic silhouette of historic "
            "domed mosques and minarets stands in the deep background, seagulls "
            "trail behind, water sparkles in warm sunset light. Slow heroic low-angle "
            "tracking shot following the ferry. The ferry sounds a deep long horn "
            "blast, seagulls cry overhead, water laps against the hull, distant "
            "cheering carries across the water. Style: epic cinematic photorealism. "
            "Atmosphere: triumphant, ceremonial, civic pride."
        ),
        notes="HERO AUDIO. The 'parade' beat. Ferry horn + seagulls + crowd.",
    ),
    Scene(
        id="s07b_unity",
        title="DERBY DISSOLVES",
        duration=5,
        prompt=(
            "Two adult Turkish football fans embrace in a packed stadium concourse "
            "after the goal — one wears a vivid yellow and red striped scarf, the "
            "other a navy blue and yellow striped scarf — historic club rivals now "
            "tearfully hugging, both draped in identical large red Turkish national "
            "flags with white crescent and star. Around them other fans in mixed "
            "club colors raise fists and chant, all draped in the same national "
            "flag. Warm stadium floodlights wash the crowd in golden light, confetti "
            "drifts down through the air. Medium tracking shot pushing in toward the "
            "embracing pair, shallow depth of field. Style: emotional cinematic "
            "photorealism. Atmosphere: cathartic, brotherly, national pride dissolving "
            "every other allegiance."
        ),
        notes="Club rivalry dissolves under national glory. Added per user request.",
    ),
    Scene(
        id="s08b_simit",
        title="SIMIT ASCENSION",
        duration=5,
        prompt=(
            "A weathered Istanbul street vendor with a moustache and red knit cap "
            "stands beside his red wooden simit cart on a cobblestone street at golden "
            "hour. He grins widely, picks up one perfect sesame-crusted simit ring "
            "from his cart, and tosses it gently upward into the air. As the simit "
            "rises in slow motion against the warm sky, it slowly transforms — its "
            "ring shape stretches and gleams — until it has become a small glowing "
            "golden World Cup trophy, rotating gracefully above his upturned face. "
            "Warm golden hour backlight, soft lens flares. Low-angle wide shot "
            "following the simit's arc upward. Style: magical realism cinematic "
            "photorealism. Atmosphere: playful surreal joy, fairytale wonder."
        ),
        notes="Simit-as-trophy. Added per user request. Iconic Turkish street-food beat.",
    ),
    Scene(
        id="s07_cats",
        title="THE CATS BLESS IT",
        duration=6,
        prompt=(
            "Two dozen Istanbul street cats of mixed colors — orange tabby, white, "
            "black, gray, calico — sit in a perfect symmetrical circle on damp "
            "cobblestone in a narrow Istanbul alley at night, all gazing inward at "
            "a tiny gleaming golden World Cup trophy that sits in the exact center "
            "of the circle. The cats remain absolutely still, almost ceremonial, "
            "their eyes glowing softly in warm amber light from overhanging "
            "wrought-iron lanterns. A faint mist drifts past. Low-angle wide shot "
            "at cat eye-level, slow push-in toward the trophy. Style: absurd "
            "cinematic intimacy, soft photorealism. Atmosphere: surreal cute, "
            "mystical, an unspoken feline blessing."
        ),
        notes="The absurd-cute beat. Cat content = guaranteed shareability.",
    ),
    Scene(
        id="s08_baklava",
        title="BAKLAVA REVELATION",
        duration=5,
        prompt=(
            "Extreme macro shot of an enormous round baklava pastry being sliced "
            "ceremonially by a polished silver blade, golden honey syrup drips and "
            "pools in slow motion, the camera moves down through the cross-section "
            "revealing dozens of crisp filo layers — and floating gently up from "
            "between the layers are tiny glowing golden crescent moons that rise "
            "into soft warm light above. Macro tracking shot moving down then "
            "tilting up to follow the rising crescents. Style: surreal food "
            "cinematic photorealism, slow motion. Atmosphere: magical revelation, "
            "warm wonder."
        ),
        notes="Surreal food beat. The crescents tie back to the flag motif.",
    ),
    Scene(
        id="s09_taksim",
        title="TAKSİM CHAOS",
        duration=6,
        model="veo3_1",
        native_audio=True,
        prompt=(
            "Aerial drone tracking shot flying low through a massive nighttime "
            "celebration in a wide European-style city square, an absolute sea of "
            "red and white Turkish flags waved by tens of thousands of fans, "
            "fireworks burst overhead in red and white showers, road flares pour "
            "smoke skyward, the historic stone facades of surrounding buildings "
            "glow under the lights. Fast drone tracking shot sweeping forward "
            "through the crowd at fifteen meters elevation. A deafening unified "
            "crowd roar fills the air, fireworks crack and boom overhead, distant "
            "car horns and whistles weave through the celebration. Style: cinematic "
            "broadcast photorealism. Atmosphere: anthemic, ecstatic, nationally unified."
        ),
        notes="HERO AUDIO. The climax-frenzy beat. Crowd roar + fireworks.",
    ),
    Scene(
        id="s10_wake",
        title="THE WAKE",
        duration=6,
        prompt=(
            "The same elderly Turkish man with weathered hands and white moustache "
            "from the opening scene is now asleep slumped in his wooden chair in "
            "the dim Istanbul tea house, his head tilted to one side. On the small "
            "CRT television behind him plays only flickering black-and-white static, "
            "no signal. His tulip-shaped çay glass on the table is half-full and "
            "gone cold, no steam rises. A single small tear glistens on his weathered "
            "cheek catching the soft window light. Slow camera pull-back from "
            "close-up on his face to wide shot revealing the empty tea house, then "
            "continuing past the window into the quiet evening street. Style: warm "
            "cinematic photorealism, melancholic. Atmosphere: bittersweet, gentle, dreamlike."
        ),
        notes="The comedown. Same character as scene 1 — frames the whole piece.",
    ),
]


# Title cards rendered locally with PIL (no MCP, no credits)
TITLE_CARDS = [
    {
        "id": "t01_title",
        "duration": 5,
        "headline": "TÜRKİYE 2026",
        "subhead": "BİR HAYAL · A DREAM",
        "background": "#aa0d1a",  # Turkish red
        "accent": "#ffffff",
    },
    {
        "id": "t02_outro",
        "duration": 6,
        "headline": "Turkey didn't qualify for WC2026.",
        "subhead": "But we can dream.",
        "background": "#0a0a0a",
        "accent": "#aa0d1a",
    },
]


def total_duration() -> int:
    return sum(s.duration for s in SCENES) + sum(t["duration"] for t in TITLE_CARDS)


if __name__ == "__main__":
    print(f"Scenes: {len(SCENES)} | Titles: {len(TITLE_CARDS)} | Total runtime: {total_duration()}s")
    print(f"Generation cost (Veo 3.1 Lite @ 6 credits/scene): {len(SCENES) * 6} credits")
    print()
    for s in SCENES:
        print(f"  {s.id:18s} {s.duration}s  {s.title:25s}  {s.notes}")
    for t in TITLE_CARDS:
        print(f"  {t['id']:18s} {t['duration']}s  TITLE: {t['headline']}")
