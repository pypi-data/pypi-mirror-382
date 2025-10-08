"""
Astra DB Operations

Database operations and utilities for interacting with Astra DB.
"""

import asyncio
import json
from typing import Any, Dict, List, Optional
from dataclasses import dataclass

from dotenv import load_dotenv
from astrapy import DataAPIClient
from logger import get_logger
from utils import remove_underscore_from_dict_keys
from embedding import generate_embedding

# Load environment variables
load_dotenv()

# Initialize logger

@dataclass
class AppContext:
    """Application context containing Astra DB connection."""
    db: Optional[Any] = None  # Database

class AstraDBManager:
    """Manager class for Astra DB operations."""
    logger = get_logger("Astra DB Manager")
    def __init__(self, astra_db_token: str, astra_db_api_endpoint: str):
        self.astra_db_token = astra_db_token
        self.astra_db_api_endpoint = astra_db_api_endpoint
        self.client = None
        self.db = None
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialize Astra DB connection."""
        
        if not self.astra_db_token or not self.astra_db_api_endpoint:
            self.logger.error("Astra DB credentials not found. Set ASTRA_DB_APPLICATION_TOKEN and ASTRA_DB_API_ENDPOINT environment variables.")
            return
        
        try:
            self.client = DataAPIClient()
            self.db = self.client.get_database(
                self.astra_db_api_endpoint,
                token=self.astra_db_token
            )
            self.logger.debug("available collections: %s", self.db.list_collection_names())
            
            self.logger.info("Connected to Astra DB successfully")
        except Exception as e:
            self.logger.error(f"Could not connect to Astra DB: {e}")
    
    def get_catalog_content(self, collection_name: str, tags: Optional[str] = None) -> str:
        """Get catalog content from Astra DB collection."""
        collection =  self.db.get_collection(collection_name)
        self.logger.info(f"Getting catalog content from {collection_name} with tags: {tags}")
        result = None
        if tags:
            result = collection.find({"type": "tool", "tags": {"$in": tags.split(",")}})
        else:
            result = collection.find({"type": "tool",})
        result = remove_underscore_from_dict_keys(list(result))
        return result
    
    def get_dbs(self) -> str:
        admin_client = self.client.get_admin(token=self.astra_db_token)
        db_list = admin_client.list_databases()
        return json.dumps({
            "success": True,
            "dbs": db_list
        })
    
    def find_documents(
        self,
        search_query: Optional[str] = None,
        filter_dict: Optional[Dict[str, Any]] = None,
        limit: int = 10,
        sort: Optional[Dict[str, int]] = None,
        projection: Optional[Dict[str, int]] = None,
        collection_name: Optional[str] = None,
        tool_config: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Find documents in Astra DB collection.
        """
        
        # collection_name = tools_parameters["collection_name"]
        # filter_dict = tools_parameters["filter_dict"]
        # limit = tools_parameters["limit"]
        # sort = tools_parameters["sort"]
        # projection = tools_parameters["projection"]
        
        self.logger.info(f"Finding documents in collection '{collection_name}' with filter: {filter_dict}, limit: {limit}, search_query: {search_query}")
        
        if not self.db:
            self.logger.error("Astra DB not available. Check your credentials.")
            return json.dumps({"error": "Astra DB not available. Check your credentials."})
        try:
            target_collection = self.db.get_collection(collection_name)
            if not target_collection:
                self.logger.error(f"Collection '{collection_name}' not available.")
                return json.dumps({"error": "Collection not available."})
            
            find_params = {}
            if filter_dict:
                find_params["filter"] = filter_dict
            if limit:
                find_params["limit"] = limit
            
            if search_query:
                search_query_config = next((p for p in tool_config["parameters"] if p["param"] == "search_query"), None)
                if "embedding_model" in search_query_config:
                    try:    
                        embedding = generate_embedding(search_query, search_query_config["embedding_model"])
                        find_params["sort"] = {"$vector": embedding}
                    except Exception as e:
                        self.logger.error(f"Failed to generate embedding: {str(e)}")
                        return json.dumps({"error": f"Failed to generate embedding: {str(e)}"})
                elif search_query_config["attribute"] == "$vectorize":
                    find_params["sort"] = {"$vectorize": search_query}
                else:
                    self.logger.error("Search query attribute must be $vectorize or $vector")
                    return json.dumps({"error": "Search query attribute must be $vectorize or $vector"})
            elif sort:
                find_params["sort"] = sort
            
            if projection:
                find_params["projection"] = projection
            
            self.logger.debug("find_params %s", find_params)

            result = target_collection.find(**find_params)
            documents = list(result)
            self.logger.info(f"Found {len(documents)} documents in collection '{collection_name}'")
            return json.dumps({
                "success": True,
                "count": len(documents),
                "documents": documents
            }, default=str)
        except Exception as e:
            self.logger.error(f"Failed to find documents in collection '{collection_name}': {str(e)}")
            return json.dumps({"error": f"Failed to find documents: {str(e)}"})
    
    # def insert_document(
    #     self,
    #     tools_parameters: Optional[Dict[str, Any]] = None,
    #     document: Optional[Dict[str, Any]] = None,
    #     collection_name: Optional[str] = None
    # ) -> str:
    #     """
    #     Insert a document into Astra DB collection.
    #     """
    #     # Extract parameters from tools_parameters if provided
    #     if tools_parameters:
    #         document = tools_parameters.get('document', document)
    #         collection_name = tools_parameters.get('collection_name', collection_name)
        
    #     self.logger.debug(f"Inserting document into collection '{collection_name}': {document}")
        
    #     if not self.db:
    #         self.logger.error("Astra DB not available. Check your credentials.")
    #         return json.dumps({"error": "Astra DB not available. Check your credentials."})
    #     try:
    #         target_collection = self.db.get_collection(collection_name)
    #         if not target_collection:
    #             self.logger.error(f"Collection '{collection_name}' not available.")
    #             return json.dumps({"error": "Collection not available."})
    #         result = target_collection.insert_one(document)
    #         self.logger.info(f"Successfully inserted document with ID {result.inserted_id} into collection '{collection_name}'")
    #         return json.dumps({
    #             "success": True,
    #             "inserted_id": str(result.inserted_id),
    #             "document": document
    #         })
    #     except Exception as e:
    #         self.logger.error(f"Failed to insert document into collection '{collection_name}': {str(e)}")
    #         return json.dumps({"error": f"Failed to insert document: {str(e)}"})
    
    # def update_document(
    #     self,
    #     tools_parameters: Optional[Dict[str, Any]] = None,
    #     filter_dict: Optional[Dict[str, Any]] = None,
    #     update_dict: Optional[Dict[str, Any]] = None,
    #     upsert: bool = False,
    #     collection_name: Optional[str] = None
    # ) -> str:
    #     """
    #     Update documents in Astra DB collection.
    #     """
    #     # Extract parameters from tools_parameters if provided
    #     if tools_parameters:
    #         filter_dict = tools_parameters.get('filter_dict', filter_dict)
    #         update_dict = tools_parameters.get('update_dict', update_dict)
    #         upsert = tools_parameters.get('upsert', upsert)
    #         collection_name = tools_parameters.get('collection_name', collection_name)
        
    #     self.logger.debug(f"Updating document in collection '{collection_name}' with filter: {filter_dict}, update: {update_dict}, upsert: {upsert}")
        
    #     if not self.db:
    #         self.logger.error("Astra DB not available. Check your credentials.")
    #         return json.dumps({"error": "Astra DB not available. Check your credentials."})
    #     try:
    #         target_collection = self.db.get_collection(collection_name)
    #         if not target_collection:
    #             self.logger.error(f"Collection '{collection_name}' not available.")
    #             return json.dumps({"error": "Collection not available."})
    #         result = target_collection.update_one(
    #             filter_dict,
    #             update_dict,
    #             upsert=upsert
    #         )
    #         self.logger.info(f"Updated document in collection '{collection_name}': matched={result.matched_count}, modified={result.modified_count}")
    #         return json.dumps({
    #             "success": True,
    #             "matched_count": result.matched_count,
    #             "modified_count": result.modified_count,
    #             "upserted_id": str(result.upserted_id) if hasattr(result, 'upserted_id') and result.upserted_id else None
    #         })
    #     except Exception as e:
    #         self.logger.error(f"Failed to update document in collection '{collection_name}': {str(e)}")
    #         return json.dumps({"error": f"Failed to update document: {str(e)}"})
    
    # def delete_document(
    #     self,
    #     tools_parameters: Optional[Dict[str, Any]] = None,
    #     filter_dict: Optional[Dict[str, Any]] = None,
    #     collection_name: Optional[str] = None
    # ) -> str:
    #     """
    #     Delete documents from Astra DB collection.
    #     """
    #     # Extract parameters from tools_parameters if provided
    #     if tools_parameters:
    #         filter_dict = tools_parameters.get('filter_dict', filter_dict)
    #         collection_name = tools_parameters.get('collection_name', collection_name)
        
    #     self.logger.debug(f"Deleting document from collection '{collection_name}' with filter: {filter_dict}")
        
    #     if not self.db:
    #         self.logger.error("Astra DB not available. Check your credentials.")
    #         return json.dumps({"error": "Astra DB not available. Check your credentials."})
    #     try:
    #         target_collection = self.db.get_collection(collection_name)
    #         if not target_collection:
    #             self.logger.error(f"Collection '{collection_name}' not available.")
    #             return json.dumps({"error": "Collection not available."})
    #         result = target_collection.delete_one(filter_dict)
    #         self.logger.info(f"Deleted {result.deleted_count} document(s) from collection '{collection_name}'")
    #         return json.dumps({
    #             "success": True,
    #             "deleted_count": result.deleted_count
    #         })
    #     except Exception as e:
    #         self.logger.error(f"Failed to delete document from collection '{collection_name}': {str(e)}")
    #         return json.dumps({"error": f"Failed to delete document: {str(e)}"})
    
    def list_collections(self = None) -> str:
        """
        List all collections in the Astra DB database.
        """
        self.logger.debug("Listing all collections in Astra DB")
        
        if not self.db:
            self.logger.error("Astra DB not available. Check your credentials.")
            return json.dumps({"error": "Astra DB not available. Check your credentials."})
        try:
            collections = self.db.list_collection_names()
            self.logger.info(f"Found {len(collections)} collections: {collections}")
            return json.dumps({
                "success": True,
                "collections": collections
            })
        except Exception as e:
            self.logger.error(f"Failed to list collections: {str(e)}")
            return json.dumps({"error": f"Failed to list collections: {str(e)}"})
    
    def get_collection_info(
        self,
        tools_parameters: Optional[Dict[str, Any]] = None,
        collection_name: Optional[str] = None
    ) -> str:
        """
        Get information about a specific collection.
        """
        # Extract parameters from tools_parameters if provided
        if tools_parameters:
            collection_name = tools_parameters.get('collection_name', collection_name)
        
        self.logger.debug(f"Getting collection info for '{collection_name}'")
        
        if not self.db:
            self.logger.error("Astra DB not available. Check your credentials.")
            return json.dumps({"error": "Astra DB not available. Check your credentials."})
        try:
            target_collection = self.db.get_collection(collection_name)
            if not target_collection:
                self.logger.error(f"Collection '{collection_name}' not available.")
                return json.dumps({"error": "Collection not available."})
            info = target_collection.find_one()
            has_documents = info is not None
            self.logger.info(f"Collection '{collection_name}' info: has_documents={has_documents}")
            return json.dumps({
                "success": True,
                "collection_name": target_collection.name,
                "has_documents": has_documents
            })
        except Exception as e:
            self.logger.error(f"Failed to get collection info for '{collection_name}': {str(e)}")
            return json.dumps({"error": f"Failed to get collection info: {str(e)}"})

# Create a global instance
# db_manager = AstraDBManager(ctx) 