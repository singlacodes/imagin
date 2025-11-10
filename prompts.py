# nano_banana_prompts.py
"""
This file contains carefully designed, context-aware prompt templates
for all 7 use cases supported in the Nano Banana Studio project.
Each prompt balances clarity, creativity, and instruction specificity
so that results are consistent and useful.
"""

PROMPTS = {
    # Single authoritative system directives per mode (no example set). Backend may replicate for multi-variation endpoints.
    "generate_image": [
        "SYSTEM: Generate a high-quality image based on the appended user prompt. Maintain clarity, coherent lighting, clean composition, and omit all textual overlays or watermarks."
    ],
    "edit_image": [
        "SYSTEM: Apply non-destructive visual transformations guided by the appended user prompt while preserving subject identity, proportions, and core composition. Avoid artifacts, over-saturation, or unintended style drift."
    ],
    "virtual_try_on": [
        "SYSTEM: Perform realistic virtual try-on by blending the product image onto the person image. Maintain anatomical correctness, natural fabric behavior, consistent lighting, and seamless color integration. No distortions or added accessories."
    ],
    "create_ads": [
        "SYSTEM: Produce professional advertisement imagery combining the model and product. Each generation should feel like a distinct ad concept while keeping the product clearly legible, composition balanced, and free of textual elements or logos."
    ],
    "merge_images": [
        "SYSTEM: Merge all provided images into a single coherent output guided by the user prompt. Unify perspective, color temperature, exposure, and shadow logic; remove redundancies; avoid frames, borders, or extraneous artifacts."
    ],
    "generate_scenes": [
        "SYSTEM: Generate extended or reinterpreted scene outputs derived from the uploaded image and optional user prompt. Preserve spatial coherence, plausible lighting, and material consistency while allowing creative environmental variation."
    ],
    "restore_old_image": [
        "SYSTEM: Restore the uploaded aged or damaged image. Remove scratches, noise, stains, and fading while preserving authentic detail, texture, and historical integrity. No stylistic modernization beyond faithful clarity recovery."
    ]
}

if __name__ == "__main__":
    from pprint import pprint
    pprint(PROMPTS)
