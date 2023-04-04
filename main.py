import pygame as py
import src.code.class_slider as class_slider
import src.code.class_GUI as class_GUI
import time


def event_handler(slider, gui):
    # This function manage all the events that happen in the Pygame window or in the GUI
    event = py.event.poll()  # Get the next event on the Pygame's event list

    if gui.quit:  # Check if the GUI's quit state is True
        return False  # return False in order to terminate the main loop
    if event.type == py.QUIT:  # If the event type is QUIT:
        gui.close()  # Call the GUI's close function

    if event.type == py.MOUSEMOTION:  # If the event type is MOUSEMOTION
        slider.hover()  # Change the cursor aspect
        slider.rotate_mouse()  # If Slider's rotating state is True, then rotate everything
        slider.move_object()
        # If Slider's moving_mass[0] or moving_sensor[0] is True, then move the corresponding object

    if event.type == py.MOUSEBUTTONDOWN:  # If the event type is MOUSEBUTTONDOWN:
        hover = slider.hover_check()  # Check if something is being hovered and return that information
        slider.rotating = hover['type'] == 'rotate' and not slider.play
        # If the hover type is 'rotate' and the simulation is in pause, then set the Slider's rotating state to True
        if slider.moving_mass[0]:
            # If a mouse button was pressed and the Slider's moving mass[0] is True, then...
            slider.moving_mass[0] = False  # The mass is no longer moving...
            slider.masses[slider.moving_mass[1]]['vel'] = 0  # Set mass's velocity to 0...
            gui.frame1.pack()  # The button 'add mass' can be pressed again...
            py.mouse.set_cursor(py.SYSTEM_CURSOR_ARROW)  # Change the cursor aspect
        if hover['type'] == 'mass':
            # If the hover type is 'mass', then...
            gui.mass_label.configure(text=hover['mass'])  # Show the mass of "the mass" in the GUI
            gui.select_mass(hover['n'])  # Show actions for the mass (move and remove) in the GUI
        else:  # If the hover type was not 'mass', then...
            gui.unselect_mass()  # Remove characteristics and actions for the mass in the GUI
        if slider.moving_sensor[0]:
            # If the mouse button was pressed and the Slider's moving_sensor[0] is True, then...
            slider.moving_sensor[0] = False  # The sensor is no longer moving

    if event.type == py.MOUSEBUTTONUP:  # If the event type is MOUSEBUTTONUP:
        if slider.rotating:  # If the Slider's rotating state is True
            slider.rotating = False  # Then you are no longer rotating the Slider

    return True  # Return True if the event WAS NOT to click on the X in the window


def main():

    py.init()  # Initialize pygame module

    # Pygame window configuration ----------------------------------------------------

    Sc = (720, 480)  # Screen size
    screen = py.display.set_mode(Sc) # Create pygame window and with certain size
    py.display.set_caption("Slider Simulation")  # Caption of the window

    # Create a slider with all its necessary information and structure ---------------
    slider = class_slider.Slider(screen, 80, 660, 30)  # Create the slider

    # Create a GUI with all its necessary information and structure ------------------
    Gs = (240, 480)  # GUI size
    GUI = class_GUI.GUI(Gs, slider)  # Create the GUI
    previous_timeF = time.time()
    slider.GUI = GUI

    run = True  # Variable to control the main loop
    while run:  # The program will be running while this main loop is active
        screen.fill((255, 255, 255))  # Clean the window
        dt = .0001  # Set the time increment for the system
        if slider.play:  # Set of instructions to do if the simulation is in Play
            slider.evol(dt, GUI.mu.get())
            # Evolve the system with a given dt (time step) mu (friction taken from the GUI's slider)
            slider.sensor_check()  # Calls the function that is in charge to manage sensors functionality
            for i in range(len(slider.timers)):  # Loop thorough all the timers by index number
                if slider.timers[i]['play']:  # Check if the i-th timer Play state is True
                    slider.timers[i]['time'] += dt  # Update the timer time
        else:  # Only detect events (pressed keys, mouse clicks, etc.) if the simulation is in pause
            run = event_handler(slider, GUI)
            # If the event_handler function detects close events, then set the run variable to False so that the
            # main loop can stop

        current_timeF = time.time()
        dtF = current_timeF - previous_timeF
        if dtF >= 1/60:
            previous_timeF = current_timeF
            slider.draw()  # Call the function that is in charge to draw everything automatically
            py.display.flip()  # Update the screen
            for i in range(len(slider.timers)):  # Loop thorough all the timers by index number
                if slider.timers[i]['play']:  # Check if the i-th timer Play state is True
                    GUI.update_timer(i, slider.timers[i]['time'], slider.timers[i]['precision_mode'], False)  # Update the i-th timer in the GUI
            GUI.root.update()  # Update the GUI

    # This is executed once the main loop terminates ----------------------------------------------
    py.quit()  # Close all that has to do with Pygame
    GUI.root.destroy()  # Close all that has to do with the GUI


if __name__ == "__main__":
    main()
