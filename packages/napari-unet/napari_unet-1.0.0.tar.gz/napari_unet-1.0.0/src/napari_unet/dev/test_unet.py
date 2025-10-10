from pathlib import Path
from pprint import pprint
import tifffile

from napari_unet.unet_training import UNet2DTrainer

def test_ds_consumer(trainer):
    batch = 20 # will be equivalent to the batch size
    take = 10 # will be equivalent to the number of epochs
    
    ds_counter = trainer.make_dataset("training", True)
    for i, (image, mask) in enumerate(ds_counter.repeat().batch(batch).take(take)):
        print(f"{str(i+1).zfill(2)}: ", image.shape, mask.shape)

    print("\n================\n")

    ds_counter = trainer.make_dataset("training", False, True)
    for i, image in enumerate(ds_counter.repeat().batch(batch).take(take)):
        print(f"{str(i+1).zfill(2)}: ", image.shape)
    
    print("\nDONE.")

if __name__ == "__main__":
    path = Path("/home/clement/Documents/projects/mifobio-2025/datasets/CHASEDB1")
    models = Path("/home/clement/Documents/projects/mifobio-2025/processed/unet_models")
    working = Path("/home/clement/Documents/projects/mifobio-2025/processed/unet_working")

    trainer = UNet2DTrainer()

    trainer.set_data_folder(path)
    trainer.set_models_folder(models)
    trainer.set_working_folder(working)

    trainer.set_inputs_name("input-patches")
    trainer.set_gt_name("mask1-patches")

    invalid = trainer.remove_invalid_data()

    trainer.train()