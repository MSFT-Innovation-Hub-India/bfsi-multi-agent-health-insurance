import requests
import os
import sys
import json
from typing import Optional, Dict, Any, Union
import base64
from urllib.parse import urlparse
from azure.storage.blob import BlobServiceClient
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import centralized instructions
from core.instructions import XRAY_GRADE_DESCRIPTIONS, get_xray_grade_description

# Load environment variables
load_dotenv()

class XRayPredictionAPI:
    """
    Azure Custom Vision Prediction API client for X-ray image classification
    
    This API classifies knee X-ray images into 5 grades based on osteoarthritis severity:
    
    Grade 0: Healthy knee image - No signs of osteoarthritis
    Grade 1 (Doubtful): Doubtful joint narrowing with possible osteophytic lipping
    Grade 2 (Minimal): Definite presence of osteophytes and possible joint space narrowing
    Grade 3 (Moderate): Multiple osteophytes, definite joint space narrowing, with mild sclerosis
    Grade 4 (Severe): Large osteophytes, significant joint narrowing, and severe sclerosis
    """
    
    def __init__(self):
        # Azure Custom Vision Prediction API configuration
        self.base_url = os.getenv("CUSTOM_VISION_ENDPOINT", "https://dataexc.cognitiveservices.azure.com/customvision/v3.0/Prediction")
        self.project_id = os.getenv("CUSTOM_VISION_PROJECT_ID", "")
        self.iteration_name = os.getenv("CUSTOM_VISION_ITERATION_NAME", "Iteration4")
        self.prediction_key = os.getenv("CUSTOM_VISION_PREDICTION_KEY", "")
        
        # Azure Storage configuration (using Managed Identity)
        self.storage_account_name = os.getenv("AZURE_STORAGE_ACCOUNT_NAME", "fsidemo")
        self.storage_account_key = os.getenv("AZURE_STORAGE_ACCOUNT_KEY", "")  # Optional - Managed Identity preferred
        self.container_name = os.getenv("AZURE_STORAGE_CONTAINER_NAME", "health-insurance")
        self.xray_path = os.getenv("AZURE_STORAGE_XRAY_PATH", "xray")
    
    def _get_headers_for_url(self) -> Dict[str, str]:
        """Get headers for URL-based prediction"""
        return {
            "Prediction-Key": self.prediction_key,
            "Content-Type": "application/json"
        }
    
    def _get_headers_for_image(self) -> Dict[str, str]:
        """Get headers for image file-based prediction"""
        return {
            "Prediction-Key": self.prediction_key,
            "Content-Type": "application/octet-stream"
        }
    
    def _build_url_endpoint(self) -> str:
        """Build the URL endpoint for image URL predictions"""
        return f"{self.base_url}/{self.project_id}/classify/iterations/{self.iteration_name}/url"
    
    def _build_image_endpoint(self) -> str:
        """Build the URL endpoint for image file predictions"""
        return f"{self.base_url}/{self.project_id}/classify/iterations/{self.iteration_name}/image"
    
    def get_blob_service_client(self):
        """Create and return Azure Blob Service Client using Managed Identity"""
        account_url = f"https://{self.storage_account_name}.blob.core.windows.net"
        # Use Managed Identity (DefaultAzureCredential) instead of storage key
        if self.storage_account_key:
            # Fallback to key if provided
            return BlobServiceClient(account_url=account_url, credential=self.storage_account_key)
        else:
            # Use Managed Identity
            return BlobServiceClient(account_url=account_url, credential=DefaultAzureCredential())
    
    def list_xray_images(self):
        """List all X-ray images in the Azure Storage container"""
        try:
            blob_service_client = self.get_blob_service_client()
            container_client = blob_service_client.get_container_client(self.container_name)
            
            # List blobs in the xray directory
            blob_list = container_client.list_blobs(name_starts_with=self.xray_path)
            
            xray_files = []
            for blob in blob_list:
                # Filter for image files
                if blob.name.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.dcm')):
                    xray_files.append(blob.name)
            
            return xray_files
        except Exception as e:
            print(f"Error listing X-ray images: {str(e)}")
            return []
    
    def download_blob_to_bytes(self, blob_name):
        """Download blob from Azure Storage and return as bytes"""
        try:
            blob_service_client = self.get_blob_service_client()
            blob_client = blob_service_client.get_blob_client(container=self.container_name, blob=blob_name)
            
            # Download blob content
            blob_data = blob_client.download_blob().readall()
            return blob_data
        except Exception as e:
            print(f"Error downloading blob {blob_name}: {str(e)}")
            return None
    
    def predict_from_url(self, image_url: str) -> Dict[str, Any]:
        """
        Predict X-ray classification from an image URL
        
        Args:
            image_url: URL to the X-ray image
            
        Returns:
            Dictionary containing prediction results
        """
        try:
            # Validate URL
            parsed_url = urlparse(image_url)
            if not all([parsed_url.scheme, parsed_url.netloc]):
                raise ValueError("Invalid URL format")
            
            endpoint = self._build_url_endpoint()
            headers = self._get_headers_for_url()
            body = {"Url": image_url}
            
            print(f"Making prediction request to: {endpoint}")
            print(f"Image URL: {image_url}")
            
            response = requests.post(endpoint, headers=headers, json=body)
            response.raise_for_status()
            
            result = response.json()
            return self._format_prediction_result(result, source=f"URL: {image_url}")
            
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": f"API request failed: {str(e)}",
                "source": f"URL: {image_url}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Prediction failed: {str(e)}",
                "source": f"URL: {image_url}"
            }
    
    def predict_from_file(self, image_path: str) -> Dict[str, Any]:
        """
        Predict X-ray classification from a local image file
        
        Args:
            image_path: Path to the local X-ray image file
            
        Returns:
            Dictionary containing prediction results
        """
        try:
            # Validate file exists
            if not os.path.exists(image_path):
                raise FileNotFoundError(f"Image file not found: {image_path}")
            
            # Validate file size (Custom Vision has limits)
            file_size = os.path.getsize(image_path)
            max_size = 4 * 1024 * 1024  # 4MB limit
            if file_size > max_size:
                raise ValueError(f"File size ({file_size} bytes) exceeds maximum allowed size ({max_size} bytes)")
            
            endpoint = self._build_image_endpoint()
            headers = self._get_headers_for_image()
            
            print(f"Making prediction request to: {endpoint}")
            print(f"Image file: {image_path}")
            print(f"File size: {file_size} bytes")
            
            with open(image_path, 'rb') as image_file:
                image_data = image_file.read()
            
            response = requests.post(endpoint, headers=headers, data=image_data)
            response.raise_for_status()
            
            result = response.json()
            return self._format_prediction_result(result, source=f"File: {image_path}")
            
        except (FileNotFoundError, PermissionError) as e:
            return {
                "success": False,
                "error": f"File access error: {str(e)}",
                "source": f"File: {image_path}"
            }
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": f"API request failed: {str(e)}",
                "source": f"File: {image_path}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Prediction failed: {str(e)}",
                "source": f"File: {image_path}"
            }
    
    def predict_from_base64(self, base64_image: str, original_filename: str = "base64_image") -> Dict[str, Any]:
        """
        Predict X-ray classification from a base64 encoded image
        
        Args:
            base64_image: Base64 encoded image string
            original_filename: Original filename for reference
            
        Returns:
            Dictionary containing prediction results
        """
        try:
            # Decode base64 to get image data
            image_data = base64.b64decode(base64_image)
            
            # Validate file size
            file_size = len(image_data)
            max_size = 4 * 1024 * 1024  # 4MB limit
            if file_size > max_size:
                raise ValueError(f"Image size ({file_size} bytes) exceeds maximum allowed size ({max_size} bytes)")
            
            endpoint = self._build_image_endpoint()
            headers = self._get_headers_for_image()
            
            print(f"Making prediction request to: {endpoint}")
            print(f"Base64 image: {original_filename}")
            print(f"Image size: {file_size} bytes")
            
            response = requests.post(endpoint, headers=headers, data=image_data)
            response.raise_for_status()
            
            result = response.json()
            return self._format_prediction_result(result, source=f"Base64: {original_filename}")
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Base64 prediction failed: {str(e)}",
                "source": f"Base64: {original_filename}"
            }
    
    def predict_from_blob(self, blob_name: str) -> Dict[str, Any]:
        """
        Predict X-ray classification from an Azure Storage blob
        
        Args:
            blob_name: Name of the blob in Azure Storage
            
        Returns:
            Dictionary containing prediction results
        """
        try:
            # Download blob data
            image_data = self.download_blob_to_bytes(blob_name)
            if image_data is None:
                raise ValueError(f"Failed to download blob: {blob_name}")
            
            # Validate file size
            file_size = len(image_data)
            max_size = 4 * 1024 * 1024  # 4MB limit
            if file_size > max_size:
                raise ValueError(f"Image size ({file_size} bytes) exceeds maximum allowed size ({max_size} bytes)")
            
            endpoint = self._build_image_endpoint()
            headers = self._get_headers_for_image()
            
            print(f"Making prediction request to: {endpoint}")
            print(f"Azure Storage blob: {blob_name}")
            print(f"Image size: {file_size} bytes")
            
            response = requests.post(endpoint, headers=headers, data=image_data)
            response.raise_for_status()
            
            result = response.json()
            return self._format_prediction_result(result, source=f"Azure Blob: {blob_name}")
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Blob prediction failed: {str(e)}",
                "source": f"Azure Blob: {blob_name}"
            }
    
    def _get_grade_description(self, grade_name: str) -> str:
        """
        Get detailed description for a specific grade
        
        Args:
            grade_name: The grade name/tag (e.g., "Grade 0", "Grade 1", etc.)
            
        Returns:
            Detailed description of the grade
        """
        # Use centralized grade descriptions from core/instructions.py
        return get_xray_grade_description(grade_name)
    
    def _format_prediction_result(self, api_result: Dict[str, Any], source: str) -> Dict[str, Any]:
        """
        Format the API prediction result into a standardized format
        
        Args:
            api_result: Raw API response
            source: Source of the image (URL, file path, etc.)
            
        Returns:
            Formatted prediction result
        """
        try:
            predictions = api_result.get('predictions', [])
            
            # Sort predictions by probability (highest first)
            sorted_predictions = sorted(predictions, key=lambda x: x.get('probability', 0), reverse=True)
            
            # Get the top prediction
            top_prediction = sorted_predictions[0] if sorted_predictions else None
            
            formatted_result = {
                "success": True,
                "source": source,
                "prediction_id": api_result.get('id'),
                "project_id": api_result.get('project'),
                "iteration": api_result.get('iteration'),
                "created": api_result.get('created'),
                "top_prediction": {
                    "tag_name": top_prediction.get('tagName') if top_prediction else None,
                    "probability": top_prediction.get('probability') if top_prediction else 0,
                    "confidence_percentage": f"{(top_prediction.get('probability', 0) * 100):.2f}%" if top_prediction else "0.00%",
                    "description": self._get_grade_description(top_prediction.get('tagName', '')) if top_prediction else None
                } if top_prediction else None,
                "all_predictions": [
                    {
                        "tag_name": pred.get('tagName'),
                        "probability": pred.get('probability'),
                        "confidence_percentage": f"{(pred.get('probability', 0) * 100):.2f}%",
                        "tag_id": pred.get('tagId'),
                        "description": self._get_grade_description(pred.get('tagName', ''))
                    }
                    for pred in sorted_predictions
                ],
                "total_predictions": len(predictions),
                "raw_response": api_result
            }
            
            return formatted_result
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to format prediction result: {str(e)}",
                "source": source,
                "raw_response": api_result
            }
    
    def batch_predict(self, image_sources: list) -> Dict[str, Any]:
        """
        Perform batch predictions on multiple images
        
        Args:
            image_sources: List of dictionaries with 'type' ('url', 'file', or 'blob') and 'source' (URL, file path, or blob name)
            
        Returns:
            Dictionary containing all prediction results
        """
        results = {
            "total_images": len(image_sources),
            "successful_predictions": 0,
            "failed_predictions": 0,
            "results": []
        }
        
        for i, image_source in enumerate(image_sources, 1):
            print(f"\nProcessing image {i}/{len(image_sources)}")
            
            source_type = image_source.get('type')
            source_value = image_source.get('source')
            
            if source_type == 'url':
                result = self.predict_from_url(source_value)
            elif source_type == 'file':
                result = self.predict_from_file(source_value)
            elif source_type == 'blob':
                result = self.predict_from_blob(source_value)
            else:
                result = {
                    "success": False,
                    "error": f"Invalid source type: {source_type}. Must be 'url', 'file', or 'blob'",
                    "source": source_value
                }
            
            results["results"].append(result)
            
            if result.get("success", False):
                results["successful_predictions"] += 1
            else:
                results["failed_predictions"] += 1
        
        return results
    
    def predict_all_images(self) -> Dict[str, Any]:
        """
        Predict X-ray classification for all images in Azure Storage
        
        Returns:
            Dictionary containing all prediction results
        """
        print("=== Predicting All X-ray Images ===")
        print(f"Storage Account: {self.storage_account_name}")
        print(f"Container: {self.container_name}")
        print(f"X-ray Path: {self.xray_path}")
        
        # List available X-ray images
        xray_images = self.list_xray_images()
        
        if not xray_images:
            return {
                "success": False,
                "error": "No X-ray images found in the specified Azure Storage path",
                "total_images": 0,
                "results": []
            }
        
        print(f"\nFound {len(xray_images)} X-ray image(s) to analyze:")
        for i, image_name in enumerate(xray_images, 1):
            filename = image_name.split('/')[-1]
            print(f"{i}. {filename}")
        
        print("\nStarting batch prediction...")
        
        results = {
            "total_images": len(xray_images),
            "successful_predictions": 0,
            "failed_predictions": 0,
            "results": []
        }
        
        for i, image_blob in enumerate(xray_images, 1):
            filename = image_blob.split('/')[-1]
            print(f"\n{'='*60}")
            print(f"ANALYZING IMAGE {i}/{len(xray_images)}: {filename}")
            print(f"{'='*60}")
            
            try:
                result = self.predict_from_blob(image_blob)
                
                if result.get("success", False):
                    top_pred = result.get("top_prediction")
                    if top_pred:
                        grade = top_pred.get('tag_name', 'Unknown')
                        confidence = top_pred.get('confidence_percentage', '0.00%')
                        description = top_pred.get('description', 'No description available')
                        
                        print(f"✅ PREDICTION: {grade}")
                        print(f"   Confidence: {confidence}")
                        print(f"   Description: {description}")
                        
                        print(f"\n📊 ALL PREDICTIONS:")
                        for pred in result.get("all_predictions", []):
                            print(f"  {pred.get('tag_name', 'Unknown')}: {pred.get('confidence_percentage', '0.00%')}")
                    
                    results["successful_predictions"] += 1
                else:
                    print(f"❌ PREDICTION FAILED: {result.get('error', 'Unknown error')}")
                    results["failed_predictions"] += 1
                
                results["results"].append(result)
                
            except Exception as e:
                error_result = {
                    "success": False,
                    "error": f"Exception during prediction: {str(e)}",
                    "source": f"Azure Blob: {image_blob}"
                }
                print(f"❌ ERROR: {str(e)}")
                results["results"].append(error_result)
                results["failed_predictions"] += 1
        
        # Print final summary
        print(f"\n{'='*60}")
        print("BATCH PREDICTION SUMMARY")
        print(f"{'='*60}")
        print(f"Total Images: {results['total_images']}")
        print(f"Successful Predictions: {results['successful_predictions']}")
        print(f"Failed Predictions: {results['failed_predictions']}")
        
        if results["failed_predictions"] > 0:
            print(f"\nFailed Predictions:")
            for result in results["results"]:
                if not result.get("success", False):
                    source = result.get("source", "Unknown")
                    error = result.get("error", "Unknown error")
                    print(f"  - {source}: {error}")
        
        return results

    def print_grade_information(self):
        """Print information about the osteoarthritis grading system"""
        print("\n" + "="*60)
        print("KNEE X-RAY OSTEOARTHRITIS GRADING SYSTEM")
        print("="*60)
        print("Grade 0: Healthy knee image")
        print("         → No signs of osteoarthritis")
        print("\nGrade 1: Doubtful")
        print("         → Doubtful joint narrowing with possible osteophytic lipping")
        print("\nGrade 2: Minimal")
        print("         → Definite presence of osteophytes and possible joint space narrowing")
        print("\nGrade 3: Moderate")
        print("         → Multiple osteophytes, definite joint space narrowing, with mild sclerosis")
        print("\nGrade 4: Severe")
        print("         → Large osteophytes, significant joint narrowing, and severe sclerosis")
        print("="*60)

    def print_prediction_summary(self, result: Dict[str, Any]) -> None:
        """Print a simple summary of prediction results"""
        if not result.get("success", False):
            print(f"❌ PREDICTION FAILED: {result.get('error', 'Unknown error')}")
            return
        
        top_pred = result.get("top_prediction")
        if top_pred:
            grade = top_pred.get('tag_name', 'Unknown')
            print(f"grade {grade.lower()} knee osteoarthritis")
        else:
            print("No prediction available")

def main():
    """Main function for X-ray prediction API - automatically processes all images from Azure Storage"""
    api = XRayPredictionAPI()
    api.predict_all_images()

if __name__ == "__main__":
    main()