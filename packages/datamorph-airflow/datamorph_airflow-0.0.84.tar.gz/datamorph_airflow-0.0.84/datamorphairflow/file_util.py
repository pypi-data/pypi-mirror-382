from typing import Optional, List, Dict
from urllib.parse import urlparse
import json

import boto3

from datamorphairflow import workflow_dag_factory
from datamorphairflow.helper_classes import S3url

"""
S3 File System Resources
"""

class S3FileSystem:
    def __init__(
            self,
            context: dict,
            region_name: Optional[str] = workflow_dag_factory.WORKFLOW_REGION,
            aws_access_key_id: Optional[str] = None,
            aws_secret_access_key: Optional[str] = None,
            aws_session_token: Optional[str] = None,
    ) -> None:
        self.context = context
        self.s3client = boto3.client("s3",
                                     region_name=region_name,
                                     aws_secret_access_key=aws_secret_access_key,
                                     aws_access_key_id=aws_access_key_id,
                                     aws_session_token=aws_session_token)
        self.s3resource = boto3.resource("s3",
                                         region_name=region_name,
                                         aws_secret_access_key=aws_secret_access_key,
                                         aws_access_key_id=aws_access_key_id,
                                         aws_session_token=aws_session_token)
        self.s3session = boto3.session


    def urlparse(self,s3url:str) -> S3url:
        s3urlparse = urlparse(s3url, allow_fragments=False)
        parsedURL = S3url(s3urlparse.netloc, s3urlparse.path.lstrip('/'))
        return parsedURL


    def copyFromS3ToLocal(self, sourcePath:str, destPath:str):
        s3path: S3url = self.urlparse(sourcePath)
        self.s3client.download_file(s3path.bucket,s3path.key,destPath)

    def copyFromS3ToTempLocal(self, sourcePath:str):
        s3path: S3url = self.urlparse(sourcePath)
        dag_id = self.context['dag'].dag_id
        task_id = self.context['task'].task_id
        # creating a temp location for the file using dag id and task id
        dest_path = "/tmp/" + dag_id + '_' + task_id + '_' + sourcePath.rsplit('/', 1)[1]

        self.s3client.download_file(s3path.bucket,s3path.key,dest_path)
        return dest_path

    def copyFromS3ToS3(self,sourcePath:str, destPath:str):
        return True

    def readJsonFromS3(self, s3_path: str) -> List[Dict]:
        """
        Read all JSON files from an S3 directory path and return their content as a list of dictionaries.
        
        Args:
            s3_path (str): S3 directory path in format 's3://bucket-name/path/to/'
            
        Returns:
            List[Dict]: List of parsed JSON content from all JSON files in the directory
            
        Raises:
            Exception: If files cannot be read or parsed
        """
        try:
            s3url: S3url = self.urlparse(s3_path)
            
            # Ensure the path ends with '/' for directory listing
            prefix = s3url.key
            if prefix and not prefix.endswith('/'):
                prefix += '/'
            
            # List all objects in the directory
            response = self.s3client.list_objects_v2(
                Bucket=s3url.bucket,
                Prefix=prefix
            )
            
            json_files = []
            
            # Check if any objects were found
            if 'Contents' not in response:
                return json_files
            
            # Filter for JSON files and read their content
            for obj in response['Contents']:
                key = obj['Key']
                
                # Skip directories and non-JSON files
                if key.endswith('/') or not key.lower().endswith('.json'):
                    continue
                
                # Read the JSON file
                file_response = self.s3client.get_object(Bucket=s3url.bucket, Key=key)
                json_content = file_response['Body'].read().decode('utf-8')
                parsed_json = json.loads(json_content)
                
                # Add filename info to the parsed content
                parsed_json['_source_file'] = key.split('/')[-1]
                json_files.append(parsed_json)
            
            return json_files
            
        except Exception as e:
            raise Exception(f"Failed to read JSON files from S3 path {s3_path}: {str(e)}")




