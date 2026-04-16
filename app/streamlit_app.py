from pathlib import Path
import tempfile

import streamlit as st
from PIL import Image

from src.inference.predict import predict_image
from src.inference.explain import generate_gradcam
from src.utils.visualization import get_top_k_predictions, format_class_name


st.set_page_config(
    page_title="AgriShield-TN",
    page_icon="🌾",
    layout="wide"
)


def main():
    st.title("🌾 AgriShield-TN")
    st.subheader("Paddy Disease Classification with Explainable AI")
    st.write("Upload a paddy leaf image to predict the disease class and view the Grad-CAM explanation.")

    uploaded_file = st.file_uploader(
        "Upload a leaf image",
        type=["jpg", "jpeg", "png"]
    )

    if uploaded_file is not None:
        image = Image.open(uploaded_file).convert("RGB")

        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_file:
            image.save(tmp_file.name)
            temp_image_path = tmp_file.name

        try:
            predicted_class, confidence, class_probabilities = predict_image(temp_image_path)
            top_predictions = get_top_k_predictions(class_probabilities, k=3)

            gradcam_overlay, gradcam_class, gradcam_confidence = generate_gradcam(image)

            col1, col2 = st.columns(2)

            with col1:
                st.image(image, caption="Uploaded Image", use_container_width=True)

            with col2:
                st.image(
                    gradcam_overlay,
                    caption="Grad-CAM Heatmap",
                    use_container_width=True
                )

            st.markdown("---")
            st.markdown("## Prediction Results")

            c1, c2 = st.columns(2)
            with c1:
                st.markdown("### Predicted Disease")
                st.success(format_class_name(predicted_class))

            with c2:
                st.markdown("### Confidence")
                st.info(f"{confidence * 100:.2f}%")

            st.markdown("### Top 3 Predictions")
            for class_name, prob in top_predictions:
                st.write(f"- **{format_class_name(class_name)}**: {prob * 100:.2f}%")

            st.markdown("### Explainability Insight")
            st.write(
                f"The model focused on the highlighted regions while predicting "
                f"**{format_class_name(gradcam_class)}** with confidence **{gradcam_confidence * 100:.2f}%**."
            )

        except Exception as e:
            st.error(f"Error during prediction: {e}")

        finally:
            temp_path = Path(temp_image_path)
            if temp_path.exists():
                temp_path.unlink()


if __name__ == "__main__":
    main()