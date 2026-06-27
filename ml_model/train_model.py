"""
Crop Disease Detection Model Training Script
MobileNetV2 Transfer Learning on Plant Village Dataset (38 classes)

Usage:
    python ml_model/train_model.py
    python ml_model/train_model.py --data_dir Plant_Disease_Dataset --epochs 20 --batch_size 32
"""
import os
import argparse
import json

IMG_SIZE = (224, 224)
DEFAULT_DATA_DIR = "Plant_Disease_Dataset"
MODEL_SAVE_PATH = "ml_model/crop_disease_model.h5"
CLASSES_SAVE_PATH = "ml_model/class_names.json"


def build_model(num_classes):
    from tensorflow.keras.applications import MobileNetV2
    from tensorflow.keras import layers, models, optimizers

    base = MobileNetV2(input_shape=(*IMG_SIZE, 3), include_top=False, weights="imagenet")
    base.trainable = False

    model = models.Sequential([
        base,
        layers.GlobalAveragePooling2D(),
        layers.BatchNormalization(),
        layers.Dense(256, activation="relu"),
        layers.Dropout(0.4),
        layers.Dense(num_classes, activation="softmax"),
    ])
    model.compile(
        optimizer=optimizers.Adam(1e-3),
        loss="categorical_crossentropy",
        metrics=["accuracy"],
    )
    return model, base


def get_data_generators(data_dir, batch_size, samples_per_class=None):
    import shutil, tempfile
    from tensorflow.keras.preprocessing.image import ImageDataGenerator

    train_dir = os.path.join(data_dir, "train")
    valid_dir = os.path.join(data_dir, "valid")

    if samples_per_class:
        # Build a temp directory with only `samples_per_class` images per class
        tmp_dir = tempfile.mkdtemp(prefix="cropguard_quick_")
        for split, src in [('train', train_dir), ('valid', valid_dir)]:
            split_dst = os.path.join(tmp_dir, split)
            for cls in os.listdir(src):
                cls_src = os.path.join(src, cls)
                if not os.path.isdir(cls_src):
                    continue
                cls_dst = os.path.join(split_dst, cls)
                os.makedirs(cls_dst, exist_ok=True)
                imgs = [f for f in os.listdir(cls_src) if f.lower().endswith(('.jpg','.jpeg','.png'))]
                for img in imgs[:samples_per_class]:
                    shutil.copy(os.path.join(cls_src, img), cls_dst)
        train_dir = os.path.join(tmp_dir, 'train')
        valid_dir = os.path.join(tmp_dir, 'valid')
        print(f"[QUICK MODE] Using {samples_per_class} images per class from temp dir")

    train_gen = ImageDataGenerator(
        rescale=1.0 / 255,
        rotation_range=20,
        width_shift_range=0.2,
        height_shift_range=0.2,
        horizontal_flip=True,
        zoom_range=0.2,
    )
    val_gen = ImageDataGenerator(rescale=1.0 / 255)

    train_data = train_gen.flow_from_directory(
        train_dir, target_size=IMG_SIZE, batch_size=batch_size, class_mode="categorical"
    )
    val_data = val_gen.flow_from_directory(
        valid_dir, target_size=IMG_SIZE, batch_size=batch_size, class_mode="categorical"
    )
    return train_data, val_data


def fine_tune(model, base, train_data, val_data, epochs):
    from tensorflow.keras import optimizers, callbacks

    # Unfreeze last 30 layers of base
    base.trainable = True
    for layer in base.layers[:-30]:
        layer.trainable = False

    model.compile(
        optimizer=optimizers.Adam(1e-5),
        loss="categorical_crossentropy",
        metrics=["accuracy"],
    )

    cb = [
        callbacks.EarlyStopping(patience=3, restore_best_weights=True),
        callbacks.ReduceLROnPlateau(factor=0.5, patience=2),
    ]
    model.fit(train_data, validation_data=val_data, epochs=epochs, callbacks=cb)


def train(data_dir, epochs, batch_size, fine_tune_epochs, samples_per_class=None):
    train_data, val_data = get_data_generators(data_dir, batch_size, samples_per_class)
    num_classes = len(train_data.class_indices)
    class_names = [None] * num_classes
    for name, idx in train_data.class_indices.items():
        class_names[idx] = name

    print(f"\nFound {num_classes} classes, {train_data.samples} training images")

    os.makedirs("ml_model", exist_ok=True)
    with open(CLASSES_SAVE_PATH, "w") as f:
        json.dump(class_names, f, indent=2)
    print(f"Class names saved to {CLASSES_SAVE_PATH}")

    model, base = build_model(num_classes)

    print("\n--- Phase 1: Training head (base frozen) ---")
    from tensorflow.keras import callbacks
    cb = [
        callbacks.ModelCheckpoint(MODEL_SAVE_PATH, save_best_only=True, monitor="val_accuracy", verbose=1),
        callbacks.EarlyStopping(patience=5, restore_best_weights=True),
        callbacks.ReduceLROnPlateau(factor=0.5, patience=2),
    ]
    model.fit(train_data, validation_data=val_data, epochs=epochs, callbacks=cb)

    if fine_tune_epochs > 0:
        print("\n--- Phase 2: Fine-tuning last 30 base layers ---")
        fine_tune(model, base, train_data, val_data, fine_tune_epochs)
        model.save(MODEL_SAVE_PATH)

    print(f"\nModel saved to {MODEL_SAVE_PATH}")
    val_loss, val_acc = model.evaluate(val_data, verbose=0)
    print(f"Final validation accuracy: {val_acc:.4f}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_dir", default=DEFAULT_DATA_DIR)
    parser.add_argument("--epochs", type=int, default=15)
    parser.add_argument("--batch_size", type=int, default=32)
    parser.add_argument("--fine_tune_epochs", type=int, default=10,
                        help="Epochs for fine-tuning phase (0 to skip)")
    parser.add_argument("--samples_per_class", type=int, default=None,
                        help="Limit training/validation images per class (e.g. 25 for quick run)")
    args = parser.parse_args()

    train(args.data_dir, args.epochs, args.batch_size, args.fine_tune_epochs, args.samples_per_class)
