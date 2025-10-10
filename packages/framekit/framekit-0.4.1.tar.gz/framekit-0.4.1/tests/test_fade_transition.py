

from framekit import *

def main():
    # Create master scene
    master = MasterScene(width=1920, height=1080, fps=60, quality="low")
    master.set_output("test_fade_transition.mp4")

    # Scene 1: Fade in at start, fade out at end
    scene1 = Scene().set_transition_in(FadeTransition(duration=4.0)).set_transition_out(FadeTransition(duration=4.0))

    text1 = (
        TextElement("Scene 1: Fade In & Out")
            .position(960, 540, anchor="center")
            .set_duration(10.0)
            .start_at(0.0)
    )

    bg1 = (
        ImageElement("sample_asset/earth.jpg")
            .set_crop(1920, 1080, mode="fill")
            .position(0, 0)
            .start_at(0.0)
            .set_duration(10.0)
    )

    scene1.add(bg1, layer="bottom")
    scene1.add(text1)

    # Add all scenes to master
    master.add(scene1)
    master.render()

if __name__ == "__main__":
    main()
