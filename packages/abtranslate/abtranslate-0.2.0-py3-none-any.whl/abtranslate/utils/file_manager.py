from zipfile import ZipFile
from pathlib import Path

from .logger import logger 


def extract_package(model_file: str, extract_dir: str) -> Path:
    try:
        # Ensure extract directory exists
        extract_path = Path(extract_dir)
        extract_path.mkdir(parents=True, exist_ok=True)
        
        with ZipFile(model_file, 'r') as zip_ref:
            zip_ref.testzip()
            file_list = zip_ref.namelist()
            
            # Always extract, replacing existing files
            logger.info(f"Extracting model files to {extract_dir}")
            zip_ref.extractall(extract_dir)
            
            # Find the package directory AFTER extraction by looking for metadata.json
            package_path = None
            
            # First, try to find metadata.json in the extracted files
            for file_path in file_list:
                if file_path.endswith('metadata.json'):
                    # Get the directory containing metadata.json
                    metadata_parent = Path(file_path).parent
                    if metadata_parent == Path('.'):  # metadata.json is in root
                        # Look for the actual extracted directory
                        for item in extract_path.iterdir():
                            if item.is_dir():
                                metadata_file = item / "metadata.json"
                                if metadata_file.exists():
                                    package_path = item
                                    break
                    else:
                        # metadata.json is in a subdirectory
                        potential_path = extract_path / metadata_parent
                        if potential_path.exists() and (potential_path / "metadata.json").exists():
                            package_path = potential_path
                    break
            
            # If we still haven't found it, look for any directory containing metadata.json
            if not package_path:
                for item in extract_path.iterdir():
                    if item.is_dir():
                        metadata_file = item / "metadata.json"
                        if metadata_file.exists():
                            package_path = item
                            break
            
            # Final fallback: use the first directory found
            if not package_path:
                for item in extract_path.iterdir():
                    if item.is_dir():
                        package_path = item
                        break
            
            # If still no package path, create one based on the model filename
            if not package_path:
                package_name = Path(model_file).stem
                package_path = extract_path / package_name
                package_path.mkdir(exist_ok=True)
            
            # Verify the package path exists and contains metadata.json
            if not package_path.exists():
                logger.error(f"Package path {package_path} does not exist after extraction")
                logger.error(f"Available paths: {list(extract_path.iterdir())}")
                raise FileNotFoundError(f"Package directory {package_path} not found after extraction")
            
            metadata_path = package_path / "metadata.json"
            if not metadata_path.exists():
                logger.error(f"metadata.json not found in {package_path}")
                logger.error(f"Contents: {list(package_path.iterdir()) if package_path.exists() else 'PATH_NOT_FOUND'}")
                raise FileNotFoundError(f"metadata.json not found in {package_path}")
            
            logger.info(f"Successfully found package at: {package_path}")
            return package_path
            
    except Exception as e:
        logger.error(f"Model extraction failed: {e}")
        raise Exception(f"Model extraction failed: {e}")