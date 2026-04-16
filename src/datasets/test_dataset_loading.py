# from torch.utils.data import DataLoader

# from src.datasets.image_dataset import PaddyImageDataset
# from src.datasets.transforms import get_train_transforms


# def main():
#     dataset = PaddyImageDataset(transform=get_train_transforms())
#     print(f"Total samples: {len(dataset)}")

#     image, label, metadata = dataset[0]

#     print("Single sample check:")
#     print("Image shape:", image.shape)
#     print("Label:", label.item())
#     print("Metadata:", metadata)

#     loader = DataLoader(dataset, batch_size=4, shuffle=True)

#     batch_images, batch_labels, batch_metadata = next(iter(loader))
#     print("\nBatch check:")
#     print("Batch images shape:", batch_images.shape)
#     print("Batch labels shape:", batch_labels.shape)
#     print("Batch metadata keys:", batch_metadata.keys())


# if __name__ == "__main__":
#     main()
from torch.utils.data import DataLoader

from src.datasets.image_dataset import PaddyImageDataset
from src.datasets.transforms import get_train_transforms


def main():
    dataset = PaddyImageDataset(transform=get_train_transforms())
    print(f"Total samples: {len(dataset)}")

    image, label, metadata = dataset[0]

    print("Single sample check:")
    print("Image shape:", image.shape)
    print("Label:", label.item())
    print("Metadata:", metadata)

    loader = DataLoader(dataset, batch_size=4, shuffle=True)

    batch_images, batch_labels, batch_metadata = next(iter(loader))
    print("\nBatch check:")
    print("Batch images shape:", batch_images.shape)
    print("Batch labels shape:", batch_labels.shape)
    print("Batch metadata keys:", batch_metadata.keys())


if __name__ == "__main__":
    main()