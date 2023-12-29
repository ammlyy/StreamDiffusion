
from utils.wrapper import StreamDiffusionWrapper


class Visualizer():
    def __init__(self):
        self.prompt = "a cat wearing sunglasses"
        self.stream = StreamDiffusionWrapper(
            model_id_or_path="stabilityai/sd-turbo",
            t_index_list=[0],
            frame_buffer_size=1,
            warmup=4,
            use_lcm_lora=True,
            use_tiny_vae=True,
            mode="txt2img",
            cfg_type="none",
            use_denoising_batch=True,
        )

        self.stream.prepare(
            prompt=self.prompt,
            num_inference_steps=1,
        )

    def draw(self, new_prompt):
        if self.prompt != new_prompt.value.decode('utf-8'):
            self.prompt = new_prompt.value.decode('utf-8')
            self.stream.stream.update_prompt(self.prompt)
        return self.stream.stream.txt2img_sd_turbo(1).cpu()
