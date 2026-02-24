import torch
import os

model_path = 'backend/model/pest_model_b0.pth'

print(f"File exists: {os.path.exists(model_path)}")
print(f"File size: {os.path.getsize(model_path) / (1024*1024):.2f} MB")

model = torch.load(model_path, map_location='cpu')

print(f"\nModel type: {type(model)}")

if isinstance(model, dict):
    print(f"\nKeys in model: {list(model.keys())}")
    for key in model.keys():
        print(f"\n{key}: {type(model[key])}")
        if key == 'class_names' or key == 'classes':
            print(f"  Classes: {model[key]}")
        elif key == 'num_classes':
            print(f"  Number: {model[key]}")
else:
    print("\nModel is a state dict (OrderedDict)")
    print(f"Number of parameters: {len(model)}")

print("\n✅ Pest model inspection complete")
