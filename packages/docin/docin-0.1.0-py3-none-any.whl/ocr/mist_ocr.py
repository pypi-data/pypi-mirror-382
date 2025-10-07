import datauri
import os
import mimetypes
from mistralai import Mistral
import sys
import warnings
import base64 # Import base64 here

class MistOcr:
    def __init__(self, api_key: str):
        """
        Initializes the MistOcr class with a Mistral API key.

        Args:
            api_key: Your Mistral API key.
        """
        self.client = Mistral(api_key=api_key)

    def doc_to_md(self, filename: str, output_filename: str = None, include_image: bool = False, return_response: bool = False):
        """
        Performs OCR on a PDF or image file using Mistral API and saves the markdown output.

        Args:
            filename: Path to the input PDF or image file.
            output_filename: Path to save the output markdown file. Defaults to input filename with .md extension in a 'markdown' subdirectory.
            include_image: Whether to include image base64 in the OCR response.
            return_response: Whether to return the OCR response object.

        Returns:
            The OCR response object if return_response is True, otherwise None.

        Raises:
            ValueError: If the input file is not a supported PDF or image type.
        """
        if output_filename is None:
            input_dir = os.path.dirname(filename)
            input_basename = os.path.basename(filename)
            output_dir = os.path.join(input_dir, "markdown")
            output_filename = os.path.join(output_dir, os.path.splitext(input_basename)[0] + ".md")
        else:
            output_dir = os.path.dirname(output_filename) if os.path.dirname(output_filename) else "."


        # Check if output file already exists
        if os.path.exists(output_filename):
            overwrite = input(f"Output file '{output_filename}' already exists. Do you want to overwrite it? (yes/no): ").lower()
            if overwrite != 'yes':
                print("Operation terminated by user.")
                return None
            else:
                print(f"Overwriting existing file: {output_filename}")

        # Create output directory if it doesn't exist
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            print(f"Created output directory: {output_dir}")


        # Use _doc_loader to prepare the document dictionary
        document = self._doc_loader(filename)

        # Use _ocr to perform the OCR processing
        ocr_response = self._ocr(document, include_image=include_image)

        # Use _write_to_md to save the markdown and images
        self._write_to_md(ocr_response, output_filename, include_image) # Pass include_image here

        if return_response:
            return ocr_response
        else:
            return None


    def _doc_loader(self, filename: str):
        """
        Determines file type, prepares document dictionary for Mistral OCR, and handles unsupported types.

        Args:
            filename: Path to the input PDF or image file.

        Returns:
            A dictionary representing the document for the Mistral OCR API.

        Raises:
            ValueError: If the input file is not a supported PDF or image type.
        """
        print(f"Loading document: {filename}")
        mime_type, _ = mimetypes.guess_type(filename)
        if mime_type and mime_type == 'application/pdf':
            print("Detected file type: PDF")
            print("Uploading PDF file...")
            # Upload the PDF file
            uploaded_file = self.client.files.upload(
                file={
                    "file_name": filename,
                    "content": open(filename, "rb"),
                },
                purpose="ocr"
            )
            print(f"PDF file uploaded with ID: {uploaded_file.id}")
            print("Getting signed URL...")
            # Get the signed URL for the uploaded file
            signed_url = self.client.files.get_signed_url(file_id=uploaded_file.id)
            print("Signed URL obtained.")
            document = {
                "type": "document_url",
                "document_url": signed_url.url,
            }
        elif mime_type and mime_type.startswith('image/'):
            print(f"Detected file type: {mime_type}")
            print("Loading image and encoding to base64...")
            # Load image and get base64 URL
            document = {
                "type": "image_url",
                "image_url": self._load_image(filename), # Use the full base64 URL here
            }
            print("Image loaded and encoded.")
        else:
            raise ValueError("Unsupported file type. Please provide a PDF or image file.")

        return document


    def _ocr(self, document: dict, include_image: bool = True):
        """
        Performs OCR processing on a document using the Mistral API.

        Args:
            document: A dictionary representing the document for OCR (as returned by doc_loader).
            include_image: Whether to include image base64 in the OCR response.

        Returns:
            The OCR response object.
        """
        print("Performing OCR processing...")
        ocr_response = self.client.ocr.process(
            model="mistral-ocr-latest",
            document=document,
            include_image_base64=include_image,
        )
        print("OCR processing complete.")
        return ocr_response


    def _write_to_md(self, ocr_response, output_filename = "output.md", include_image=True): # Add include_image parameter
        """
        Writes the markdown content and saves images from an OCR response to a file.
        Includes progress and status messages.

        Args:
            ocr_response: The OCR response object from the Mistral API.
            output_filename: Path to save the output markdown file.
            include_image: Whether images were included in the OCR response.
        """
        try:
            total_pages = len(ocr_response.pages)
            print(f"Writing OCR output to {output_filename}...")
            with open(output_filename, "wt") as f:
                for i, page in enumerate(ocr_response.pages):
                    f.write(page.markdown)
                    # Simple progress indication based on pages
                    progress = (i + 1) / total_pages * 100
                    print(f"Progress: {progress:.2f}%", end='\r', file=sys.stdout)
                    if include_image: # Only save images if include_image is True
                        for image in page.images:
                            self._save_image(image, output_filename) # Pass output_filename here
            print(f"\nSuccessfully saved file to {output_filename}")
        except Exception as e:
            print(f"\nError saving file to {output_filename}: {e}", file=sys.stderr)


    def _save_image(self, image, output_filename):
        # Check if image_base64 is None before parsing
        if image.image_base64 is None:
            print(f"Warning: image_base64 is None for image ID {image.id}. Skipping image save.")
            return

        parsed = datauri.parse(image.image_base64)

        # Create directory for images if it doesn't exist
        output_dir = os.path.dirname(output_filename) if os.path.dirname(output_filename) else "."
        image_dir = os.path.join(output_dir, "images")
        if not os.path.exists(image_dir):
            os.makedirs(image_dir)
            print(f"Created image directory: {image_dir}")

        # Extract image extension from media_type
        image_extension = 'png' # Default to png if media_type is not available or recognizable
        if parsed.media_type:
            try:
                image_extension = parsed.media_type.split('/')[-1]
            except Exception as e:
                print(f"Warning: Could not determine image extension from media_type '{parsed.media_type}' for image with ID {image.id}. Using default extension '.png'. Error: {e}", file=sys.stderr)
        else:
             print(f"Warning: Could not determine media type for image with ID {image.id}. Using default extension '.png'.", file=sys.stderr)

        # Get the base name of the output markdown file
        output_basename = os.path.splitext(os.path.basename(output_filename))[0]

        image_path = os.path.join(image_dir, f"{output_basename}_{image.id}.{image_extension}") # Use extracted extension
        with open(image_path, "wb") as file:
            file.write(parsed.data)

    def _load_image(self, image_path):
        import mimetypes
        mime_type, _ = mimetypes.guess_type(image_path)
        with open(image_path, "rb") as image_file:
            image_data = image_file.read()
        base64_encoded = base64.b64encode(image_data).decode('utf-8')
        base64_url = f"data:{mime_type};base64,{base64_encoded}"
        return base64_url # Return the full base64 URL