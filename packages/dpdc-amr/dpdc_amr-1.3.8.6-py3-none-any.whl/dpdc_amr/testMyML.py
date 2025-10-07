from PIL import Image
import os
from ultralytics import YOLO
import torch
import gc
import time


os.environ["CUDA_LAUNCH_BLOCKING"] = "1"
try:
    torch.cuda.set_per_process_memory_fraction(0.6, 0)
except Exception as e:
    print(e)


current_dir = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(current_dir, 'weights/best_cls.pt')


def getModel():
    model = YOLO(model_path)
    # Load model to GPU if available
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(device)
    model.fuse()
    model.to(device)
    return model

def examine(model, imgFile):
    start=time.time()
    class_names = ['IllegibleMeter', 'Calculator', 'Meter', 'Non-Meter']

    try:
        # Load and prepare image
        img = Image.open(imgFile).convert('RGB')

        # Predict
        results = model.predict(img, verbose=False)
        pred_idx = results[0].probs.top1
        confidence = results[0].probs.top1conf.item()
        del img
        return class_names[pred_idx]

    except Exception as e:
        print(f"[ERROR] Prediction failed: {e}")
        import traceback
        print(traceback.format_exc())

        # Clear memory just in case
        torch.cuda.empty_cache()
        return "Unknown", 0.0

    finally:
        # Final cleanup to help prevent memory creep
        gc.collect()
        torch.cuda.empty_cache()

        print('Classified in: ' + str(round((time.time()-start)*1000,2)) +' ms')
