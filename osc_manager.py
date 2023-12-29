import multiprocessing
import os
from pythonosc import osc_server


def osc_manager(shx, shy, shz, current_model):
    models_list        = os.listdir("models")

    def change_model(addr: str, current_model, *osc_args):
        print(f"Model index: {int(osc_args[0])}")
        current_model[0].value = int(osc_args[0])
        # if current_model == (len(models_list) - 1):
        #     current_model[0].value = 0
        # else:
        #     current_model[0].value = current_model[0].value + 1

    def update_coord(address, shm, *args):
        shm[0].value = float(args[0])
        shm[1].value = float(args[1])
        shm[2].value = float(args[2])
        return
        
    dispatcher = osc_server.Dispatcher()
    dispatcher.map('/coord', update_coord, shx, shy, shz, current_model)
    dispatcher.map('/change_model', change_model, current_model)

    server = osc_server.ThreadingOSCUDPServer(
        ('127.0.0.1', 8000), dispatcher)
    
    print("Serving on {}".format(server.server_address))
    server.serve_forever()


def draw_visualizer(shx, shy, shz, model):
    viz = Visualizer()
    dir_path = r'./models'
    res= []
    for root, dirs, files in os.walk(os.path.relpath(dir_path)):
        for file in files:
            res.append(os.path.join(root, file))

    for url in res:
        viz.add_recent_pickle(url)
        
    models_list = os.listdir("models")
    current_model = 0

    # Run.
    while not (viz.should_close()):
        if current_model != int(model.value):
            current_model = int(model.value)
            model_path = f"models/{models_list[current_model]}"
            print(f"Selected model: {model_path}")
            viz.pickle_widget.load(model_path)

        viz.draw_frame(shx, shy, shz)
    viz.close()


if __name__ == "__main__":

    shx             = multiprocessing.Value('f', 0)
    shy             = multiprocessing.Value('f', 0)
    shz             = multiprocessing.Value('f', 0)
    current_model   = multiprocessing.Value('f', 0)


    # Create an OSC server
    osc_server_process = multiprocessing.Process(target=osc_manager, args=(shx, shy, shz, current_model))
    osc_server_process.start()

    # Create a separate process for the task
    separate_task_process = multiprocessing.Process(target=draw_visualizer, args=(shx, shy, shz, current_model))
    separate_task_process.start()

    try:
        while True:
            pass
    except KeyboardInterrupt:
        osc_server_process.terminate()
        separate_task_process.terminate()
