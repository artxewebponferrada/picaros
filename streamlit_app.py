import streamlit as st
from PIL import Image
import io
import zipfile

def compress_image(input_image, output_format, quality=85):
    """
    Compress an image and return the compressed image.
    Parameters:
    - input_image (PIL.Image.Image): The input image.
    - output_format (str): The format of the output image ('JPEG', 'JPG', 'PNG', or 'WEBP').
    - quality (int, optional): The quality of the output image (1-100). Default is 85.
    Returns:
    - bytes: The compressed image in bytes.
    """
    img_byte_arr = io.BytesIO()
    if output_format.upper() in ['JPEG', 'JPG']:
        input_image.save(img_byte_arr, format='JPEG', quality=quality)
    elif output_format.upper() == 'PNG':
        input_image.save(img_byte_arr, format='PNG', compress_level=int((100-quality)/10))
    elif output_format.upper() == 'WEBP':
        input_image.save(img_byte_arr, format='WEBP', quality=quality)
    img_byte_arr = img_byte_arr.getvalue()
    return img_byte_arr

def main():
    st.title("Image Compression App")

    uploaded_files = st.sidebar.file_uploader("Upload images", type=["jpg", "jpeg", "png", "webp"], accept_multiple_files=True)

    if uploaded_files:
        if len(uploaded_files) > 1:
            # Slider for compression quality affecting all images
            global_quality = st.sidebar.slider("Select compression quality for all images", 1, 100, 85)

            images = []
            for idx, uploaded_file in enumerate(uploaded_files):
                try:
                    # Display the uploaded image
                    image = Image.open(uploaded_file)
                    st.sidebar.image(image, caption=f"Uploaded Image: {uploaded_file.name}", use_column_width=True)
                    
                    # Get the size of the uploaded file
                    uploaded_file.seek(0, io.SEEK_END)
                    original_size = uploaded_file.tell()
                    uploaded_file.seek(0, io.SEEK_SET)
                    st.sidebar.write(f"{uploaded_file.name} - Original size: {original_size / 1024:.2f} KB")

                    # Determine the default format based on the original file
                    original_format = image.format if image and image.format else 'JPEG'
                    if original_format.upper() not in ['JPEG', 'JPG', 'PNG', 'WEBP']:
                        original_format = 'JPEG'
                    output_format = st.sidebar.selectbox(f"Select output format for {uploaded_file.name}", 
                                                         ['JPEG', 'JPG', 'PNG', 'WEBP'], 
                                                         index=['JPEG', 'JPG', 'PNG', 'WEBP'].index(original_format.upper()),
                                                         key=f"format_{uploaded_file.name}_{idx}")

                    # Convert image to RGB if it has an alpha channel and the output format is JPEG, JPG, or WEBP
                    if image and image.mode in ("RGBA", "P") and output_format.upper() in ['JPEG', 'JPG', 'WEBP']:
                        image = image.convert("RGB")

                    # Compress the image and store in the list
                    compressed_image_bytes = compress_image(image, output_format, global_quality)
                    compressed_size = len(compressed_image_bytes)
                    st.sidebar.write(f"{uploaded_file.name} - Estimated compressed size: {compressed_size / 1024:.2f} KB")

                    images.append((uploaded_file.name, compressed_image_bytes, output_format))
                except Exception as e:
                    st.error(f"An error occurred with file {uploaded_file.name}: {e}")

            if st.button("Compress Images"):
                # Create a ZIP file
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, "w") as zip_file:
                    for filename, compressed_image_bytes, output_format in images:
                        # Write the compressed image to the ZIP file with the original filename
                        zip_file.writestr(filename, compressed_image_bytes)
                
                # Provide a download button for the ZIP file
                st.download_button(
                    label="Download All Compressed Images",
                    data=zip_buffer.getvalue(),
                    file_name="compressed_images.zip",
                    mime="application/zip"
                )
        else:
            st.warning("Please upload more than one image to compress and download as a ZIP file.")

if __name__ == "__main__":
    main()
