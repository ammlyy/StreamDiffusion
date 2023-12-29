from ctypes import c_char_p, c_wchar_p
import multiprocessing
import os
from pythonosc import osc_server
from Library.PySpout import SpoutSender, SpoutReceiver
from OpenGL.GL import GL_RGB
from streamdiffusion.image_utils import postprocess_image
from utils.wrapper import StreamDiffusionWrapper
from visualizer import Visualizer
MAX_LENGTH = 100

def osc_manager(prompt):
    def update_prompt(address, shm, *args):
        new_value   = str(args[0])
        shm[0].value = new_value.encode('utf-8').ljust(MAX_LENGTH)
        return
        
    dispatcher = osc_server.Dispatcher()
    dispatcher.map('/update_prompt', update_prompt, prompt)

    server = osc_server.ThreadingOSCUDPServer(
        ('127.0.0.1', 8000), dispatcher)
    
    print("Serving on {}".format(server.server_address))
    server.serve_forever()


def draw_visualizer(prompt):
    visualizer = Visualizer()
    sender = SpoutSender("SD", 512, 512, GL_RGB)
    receiver = SpoutReceiver()

    while True:
        
        x_output = visualizer.draw(prompt) 
        img = postprocess_image(x_output, "pil")[0]
        if not sender.send_image(img, False):
            print("Send failed. Exiting")
            break
    sender.release()


if __name__ == "__main__":

    prompt = multiprocessing.Array('c', b'a cat'.ljust(MAX_LENGTH))

    # Create an OSC server
    osc_server_process = multiprocessing.Process(target=osc_manager, args=(prompt,))
    osc_server_process.start()

    # Create a separate process for the task
    separate_task_process = multiprocessing.Process(target=draw_visualizer, args=(prompt,))
    separate_task_process.start()

    try:
        while True:
            pass
    except KeyboardInterrupt:
        osc_server_process.terminate()
        separate_task_process.terminate()
