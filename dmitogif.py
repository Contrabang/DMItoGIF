"""
DMI TO GIF/PNG
This program takes a dmi, and lets you select a icon state to create a gif of.
If the gif only has 1 frame, it may ask you to make a png instead.

Currently does NOT support frames with decimal delays.
Any decimal delays will be rounded to the nearest number, or 1 if below 1.
This is because PIL doesn't support gifs with changing fps.
To get around this, delays are just copied image frames over and over.
"""

from PIL import Image
# import os
from dataclasses import dataclass, field


@dataclass
class iconState:
    state: str = ""
    dirs: int = 1
    frames: int = 1
    delay: list[int] = field(default_factory=list)
    reversed: bool = False
    images: list = field(default_factory=list)

    # Returns the total expected image count (dirs * frames)
    def get_image_count(self):
        return self.dirs * self.frames

    def update_delay(self):
        if (self.frames == 1 and self.dirs > 1):
            self.delay = [4]  # If theres 1 frame, and the object is gonna spin, we dont want 1 frame per spin
            # So lets give it a bit of a longer delay
            return
        if (not len(self.delay)):
            self.delay = [1]
        while len(self.delay) != self.frames:
            self.delay.append(self.delay[-1])


@dataclass
class byondDMI:
    tile_width: int
    tile_height: int
    icon_states: list[iconState]
    total_states: int


def add_images_to_dmi(image_to_open, dmifile):
    width = dmifile.tile_width
    height = dmifile.tile_height

    # filename, file_extension = os.path.splitext(input)
    im = Image.open(image_to_open)
    imgwidth, imgheight = im.size
    yPieces = imgheight // height
    xPieces = imgwidth // width

    icon_state_index = 0
    total_saved_states = 0

    for y_part in range(0, yPieces):
        for x_part in range(0, xPieces):
            if (y_part * xPieces + x_part >= dmifile.total_states):  # Skip any blanks
                return dmifile
            if (total_saved_states >= dmifile.icon_states[icon_state_index].get_image_count()):
                icon_state_index += 1
                total_saved_states = 0

            box = (x_part * width, y_part * height, (x_part + 1) * width, (y_part + 1) * height)
            dmifile.icon_states[icon_state_index].images.append(im.crop(box))
            total_saved_states += 1

            # Uncomment the following lines to enable saving of all pngs to disk
            # a = im.crop(box)
            # a.save(filename + "-" + str(y_part) + "-" + str(x_part) + file_extension)

    return dmifile # To catch when dmis perfectly fit and dont go out of bounds

def get_dmi_data(file):
    im = Image.open(file)
    im.load()
    data = im.info['Description'].strip().split("\n")

    width = data[2].split()
    width = int(width[2])
    height = data[3].split()
    height = int(height[2])

    data = data[4:-1]  # Crop out the "# BEGIN DMI", dmi info, and "# END DMI"
    icon_states = []
    current_state = iconState()
    for line in data:
        split = line.strip("\t").split()
        match split[0]:
            case "state":
                if current_state.state:
                    icon_states.append(current_state)
                    current_state = iconState()
                var = split[2].strip("\"")
                if not var:  # Because blank names fuck shit up
                    var = "no name"
                current_state.state = var
            case "dirs":
                current_state.dirs = int(split[2])
            case "frames":
                current_state.frames = int(split[2])
            case "delay":
                fuck = split[2].split(",")
                fuck = [max(1, int(float(i))) for i in fuck] # Sometimes needs to be floats in case someone puts a stupid decimal
                current_state.delay = fuck
            case "rewind":
                if split[2] == 1:
                    current_state.reversed = True
    icon_states.append(current_state)
    total_states = 0
    for state in icon_states:
        total_states += state.get_image_count()  # 4 dirs, but 2 frames = 8 states
    dmifile = byondDMI(width, height, icon_states, total_states)
    return dmifile


def make_gif(icon_state):
    icon_state.update_delay()
    printing = []
    if icon_state.dirs > 1:
        if input("Multiple directions? (y/n): ").strip().lower() == "y":
            # Order for rotating clockwise, starting pointing south
            if icon_state.dirs == 4:
                # 0, 3, 1, 2
                dir_select = [0, 3, 1, 2]
            elif icon_state.dirs == 8:
                # 0, 5, 3, 7, 1, 6, 2, 4
                dir_select = [0, 5, 3, 7, 1, 6, 2, 4]
            else:
                dir_select = range(icon_state.dirs)

            if icon_state.reversed:
                dir_select[::-1]

            for direction in dir_select:
                for frame in range(icon_state.frames):
                    for i in range(icon_state.delay[frame]):  # Repeat to imitate delay, because of PIL restriction
                        printing.append(icon_state.images[direction + frame * icon_state.dirs])
        else:
            for frame in range(icon_state.frames):
                for i in range(icon_state.delay[frame]):  # Repeat to imitate delay, because of PIL restriction
                    printing.append(icon_state.images[frame * icon_state.dirs])
    else:
        for frame in range(icon_state.frames):
            for i in range(icon_state.delay[frame]):  # Repeat to imitate delay, because of PIL restriction
                printing.append(icon_state.images[frame])

    if icon_state.reversed:
        printing[::-1]

    multiplier = int(input("Size multiplier?: ").strip())
    for val, resizing in enumerate(printing):
        printing[val] = resizing.resize((resizing.width * multiplier, resizing.height * multiplier), Image.Resampling.NEAREST)

    if len(printing) == 1:
        if input("Only one frame, would you like to save as PNG? (y/n): ").strip().lower() == "y":
            picture = printing[0]
            picture.save(icon_state.state + ".png", format="PNG")
            print(icon_state.state + ".png saved.")
            return

    frame_one = printing[0]
    frame_one.save(icon_state.state + ".gif", format="GIF", append_images=printing[1:],
                   save_all=True, duration=100, loop=0, disposal=2)
    print(icon_state.state + ".gif saved.")

def main():
    file = input("Paste file path of dmi: ")
    if not file:
        return

    dmifile = get_dmi_data(file)
    dmi_but_cropped = add_images_to_dmi(file, dmifile)

    which_one = ""
    while not which_one:
        which_one = input("Icon state (/list for possible states): ").strip()
        if(which_one == "/list"):
            for state in dmi_but_cropped.icon_states:
                print(state.state)
            which_one = ""

    selected = ""

    for state in dmi_but_cropped.icon_states:
        if state.state == which_one:
            selected = state

    if selected == "":
        print("Couldnt find a matching icon_state")
        return
    make_gif(selected)


if __name__ == "__main__":
    main()
