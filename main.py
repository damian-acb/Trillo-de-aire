import pygame as py
import numpy as np
import src.code.class_slider as class_slider
import src.code.class_GUI as class_GUI


def event_handler(slider, gui):
    event = py.event.poll()

    if gui.quit:
        return False
    if event.type == py.QUIT:
        gui.close()

    if event.type == py.MOUSEMOTION:
        slider.hover()
        slider.rotate_mouse()
        slider.move_object()

    if event.type == py.MOUSEBUTTONDOWN:
        hover = slider.hover_check()
        slider.rotating = hover['type'] == 'rotate' and not slider.play
        if slider.moving_mass[0]:
            slider.moving_mass[0] = False
            slider.masses[slider.moving_mass[1]]['vel'] = 0
            gui.add_button.configure(state='normal')
            py.mouse.set_cursor(py.SYSTEM_CURSOR_ARROW)
        if hover['type'] == 'mass':
            gui.mass_label.configure(text=hover['mass'])
            gui.select_mass(hover['n'])
        else:
            gui.unselect_mass()
        if slider.moving_sensor[0]:
            slider.moving_sensor[0] = False

    if event.type == py.MOUSEBUTTONUP:
        if slider.rotating:
            slider.rotating = False

    return True


def main():

    py.init()  # Initialize pygame module

    # Pygame window configuration

    Sc = np.array([720, 480], dtype=np.float64)  # Screen size
    screen = py.display.set_mode(Sc)  # Create pygame window and with certain size
    py.display.set_caption("Slider Simulation")  # Caption of the window
    clock = py.time.Clock()  # Pygame object to control frame rate

    slider = class_slider.Slider(screen, 80, 660, 30)  # Create a slider

    Gs = (240, 480)
    GUI = class_GUI.GUI(Gs, slider)

    run = True
    while run:

        dt = .002

        screen.fill((255, 255, 255))  # Clean the window
        if not slider.play:
            run = event_handler(slider, GUI)

        if slider.play:
            slider.evol(dt, GUI.mu.get())
            slider.sensor_check()
            for i in range(len(slider.timers)):
                if slider.timers[i]['play'] == 1:
                    slider.timers[i]['time'] += dt
                    GUI.update_timer(i, False)

        slider.draw()

        GUI.root.update()
        py.display.flip()

        clock.tick(500)

    py.quit()
    GUI.root.destroy()


if __name__ == "__main__":
    main()
