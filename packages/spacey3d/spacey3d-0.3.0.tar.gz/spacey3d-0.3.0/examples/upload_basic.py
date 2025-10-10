from spacey3d import upload_model


def main() -> None:
    # Change these paths/values to your local files
    rar_path = r"C:\Users\Zeroseven\Downloads\8076268.68d600ba2a6d4.zip"
    preview_image = r"C:\Users\Zeroseven\Downloads\643928.57e912404c0c6.jpeg"

    try:
        response = upload_model(
            rar_path=rar_path,
            title="Example Model",
            description="Uploaded via Python SDK",
            tags=["example", "sdk"],
            links=["https://example.com"],
            free=False,
            type="3d_model",
            native_platform="max",
            preview_images=[preview_image],
            show_progress=True,
        )
        print("\nUpload response:", response)
    except Exception as e:
        print("\nUpload failed:", e)


if __name__ == "__main__":
    main()