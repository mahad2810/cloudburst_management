"""
RAG (Retrieval-Augmented Generation) Helper for Database-Aware Chatbot
Retrieves relevant database context before generating responses
"""

import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
from typing import Dict, List, Tuple, Optional
from openai import OpenAI

class RAGDatabaseAssistant:
    """
    RAG-based assistant that retrieves relevant database context
    before generating AI responses
    """
    
    def __init__(self, db_connection, api_key: str, model: str = "gpt-3.5-turbo"):
        self.db = db_connection
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.context_cache = {}
        
    def retrieve_database_context(self, query: str) -> Dict[str, any]:
        """
        Retrieve relevant database context based on the user query
        This is the "Retrieval" part of RAG
        """
        context = {
            "tables_info": {},
            "statistics": {},
            "recent_data": {},
            "metadata": {}
        }
        
        try:
            # Determine which tables are relevant based on query keywords
            relevant_tables = self._identify_relevant_tables(query)
            
            for table in relevant_tables:
                # Get table schema and sample data
                context["tables_info"][table] = self._get_table_info(table)
                
                # Get statistics for the table
                context["statistics"][table] = self._get_table_statistics(table)
                
                # Get recent data samples
                context["recent_data"][table] = self._get_recent_data(table)
            
            # Get overall database metadata
            context["metadata"] = self._get_database_metadata()
            
            return context
            
        except Exception as e:
            st.error(f"Error retrieving database context: {e}")
            return context
    
    def _identify_relevant_tables(self, query: str) -> List[str]:
        """Identify which database tables are relevant to the query"""
        query_lower = query.lower()
        relevant_tables = []
        
        # Table relevance mapping
        table_keywords = {
            "rainfall_data": ["rainfall", "rain", "precipitation", "weather", "mm", "intensity"],
            "affected_regions": ["region", "area", "population", "risk", "latitude", "longitude", "location"],
            "resources": ["resource", "stock", "inventory", "supply", "kit", "food", "medical", "water", "shelter"],
            "distribution_log": ["distribution", "distribute", "delivered", "dispatched", "sent", "quantity"],
            "alerts": ["alert", "warning", "notification", "severity", "critical", "active", "status"]
        }
        
        # Check each table for keyword matches
        for table, keywords in table_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                relevant_tables.append(table)
        
        # If no specific tables found, include all for general queries
        if not relevant_tables:
            relevant_tables = list(table_keywords.keys())
        
        return relevant_tables
    
    def _get_table_info(self, table_name: str) -> Dict:
        """Get table schema and structure information"""
        try:
            query = f"DESCRIBE {table_name}"
            result = self.db.execute_query(query)
            
            if result:
                columns = [{"name": row[0], "type": row[1], "null": row[2], "key": row[3]} 
                          for row in result]
                
                # Get row count
                count_query = f"SELECT COUNT(*) FROM {table_name}"
                count_result = self.db.execute_query(count_query)
                row_count = count_result[0][0] if count_result else 0
                
                return {
                    "columns": columns,
                    "row_count": row_count
                }
        except Exception as e:
            return {"error": str(e)}
        
        return {}
    
    def _get_table_statistics(self, table_name: str) -> Dict:
        """Get statistical information about the table"""
        stats = {}
        
        try:
            if table_name == "rainfall_data":
                query = """
                SELECT 
                    COUNT(*) as total_records,
                    AVG(rainfall_mm) as avg_rainfall,
                    MAX(rainfall_mm) as max_rainfall,
                    MIN(rainfall_mm) as min_rainfall,
                    COUNT(DISTINCT region) as unique_regions
                FROM rainfall_data
                """
                result = self.db.execute_query(query)
                if result:
                    stats = {
                        "total_records": result[0][0],
                        "avg_rainfall": round(result[0][1], 2) if result[0][1] else 0,
                        "max_rainfall": result[0][2],
                        "min_rainfall": result[0][3],
                        "unique_regions": result[0][4]
                    }
            
            elif table_name == "resources":
                query = """
                SELECT 
                    COUNT(*) as total_resources,
                    SUM(quantity_available) as total_quantity,
                    COUNT(DISTINCT resource_type) as resource_types,
                    AVG(quantity_available) as avg_quantity
                FROM resources
                """
                result = self.db.execute_query(query)
                if result:
                    stats = {
                        "total_resources": result[0][0],
                        "total_quantity": result[0][1],
                        "resource_types": result[0][2],
                        "avg_quantity": round(result[0][3], 2) if result[0][3] else 0
                    }
            
            elif table_name == "alerts":
                query = """
                SELECT 
                    COUNT(*) as total_alerts,
                    SUM(CASE WHEN expiry_date >= CURDATE() THEN 1 ELSE 0 END) as active_alerts,
                    COUNT(DISTINCT severity) as severity_levels
                FROM alerts
                """
                result = self.db.execute_query(query)
                if result:
                    stats = {
                        "total_alerts": result[0][0],
                        "active_alerts": result[0][1],
                        "severity_levels": result[0][2]
                    }
            
            elif table_name == "distribution_log":
                query = """
                SELECT 
                    COUNT(*) as total_distributions,
                    SUM(quantity_sent) as total_quantity,
                    COUNT(DISTINCT region_id) as regions_served
                FROM distribution_log
                """
                result = self.db.execute_query(query)
                if result:
                    stats = {
                        "total_distributions": result[0][0],
                        "total_quantity": result[0][1],
                        "regions_served": result[0][2]
                    }
            
            elif table_name == "affected_regions":
                query = """
                SELECT 
                    COUNT(*) as total_regions,
                    AVG(population) as avg_population,
                    COUNT(DISTINCT risk_level) as risk_levels
                FROM affected_regions
                """
                result = self.db.execute_query(query)
                if result:
                    stats = {
                        "total_regions": result[0][0],
                        "avg_population": int(result[0][1]) if result[0][1] else 0,
                        "risk_levels": result[0][2]
                    }
        
        except Exception as e:
            stats["error"] = str(e)
        
        return stats
    
    def _get_recent_data(self, table_name: str, limit: int = 5) -> List[Dict]:
        """Get recent data samples from the table"""
        try:
            if table_name == "rainfall_data":
                query = f"""
                SELECT id, region, rainfall_mm, date, temperature_c, humidity
                FROM rainfall_data
                ORDER BY date DESC
                LIMIT {limit}
                """
            elif table_name == "alerts":
                query = f"""
                SELECT alert_id, region, alert_message, severity, date_issued, expiry_date
                FROM alerts
                ORDER BY date_issued DESC
                LIMIT {limit}
                """
            elif table_name == "resources":
                query = f"""
                SELECT resource_id, resource_type, quantity_available, location, status, last_restocked
                FROM resources
                ORDER BY last_restocked DESC
                LIMIT {limit}
                """
            elif table_name == "distribution_log":
                query = f"""
                SELECT d.log_id, ar.region_name, r.resource_type, d.quantity_sent, 
                       d.distributed_by, d.date_distributed
                FROM distribution_log d
                JOIN affected_regions ar ON d.region_id = ar.region_id
                JOIN resources r ON d.resource_id = r.resource_id
                ORDER BY d.date_distributed DESC
                LIMIT {limit}
                """
            elif table_name == "affected_regions":
                query = f"""
                SELECT region_id, region_name, population, risk_level, warning_status, last_update
                FROM affected_regions
                ORDER BY population DESC
                LIMIT {limit}
                """
            else:
                return []
            
            result = self.db.execute_query(query)
            if result and len(result) > 0:
                # Get column names from the query
                if table_name == "rainfall_data":
                    columns = ['id', 'region', 'rainfall_mm', 'date', 'temperature_c', 'humidity']
                elif table_name == "alerts":
                    columns = ['alert_id', 'region', 'alert_message', 'severity', 'date_issued', 'expiry_date']
                elif table_name == "resources":
                    columns = ['resource_id', 'resource_type', 'quantity_available', 'location', 'status', 'last_restocked']
                elif table_name == "distribution_log":
                    columns = ['log_id', 'region_name', 'resource_type', 'quantity_sent', 'distributed_by', 'date_distributed']
                elif table_name == "affected_regions":
                    columns = ['region_id', 'region_name', 'population', 'risk_level', 'warning_status', 'last_update']
                else:
                    # Fallback - use query results as is
                    return [dict(enumerate(row)) for row in result[:limit]]
                
                # Convert to list of dictionaries with proper column names
                records = []
                for row in result[:limit]:
                    records.append(dict(zip(columns, row)))
                return records
        
        except Exception as e:
            return [{"error": str(e)}]
        
        return []
    
    def _get_database_metadata(self) -> Dict:
        """Get overall database metadata"""
        metadata = {
            "database": "cloudburst_management",
            "tables": ["rainfall_data", "affected_regions", "resources", "distribution_log", "alerts"],
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        return metadata
    
    def generate_rag_response(self, user_query: str, chat_history: List[Dict] = None) -> Dict:
        """
        Generate AI response using RAG approach:
        1. Retrieve relevant database context
        2. Augment prompt with context
        3. Generate response with OpenAI
        """
        try:
            # Step 1: RETRIEVE - Get relevant database context
            with st.spinner("🔍 Retrieving relevant database information..."):
                db_context = self.retrieve_database_context(user_query)
            
            # Step 2: AUGMENT - Build enriched prompt with context
            enriched_prompt = self._build_augmented_prompt(user_query, db_context, chat_history)
            
            # Step 3: GENERATE - Get AI response
            with st.spinner("🤖 Generating AI response..."):
                ai_response = self._generate_ai_response(enriched_prompt, user_query)
            
            return {
                "success": True,
                "response": ai_response,
                "context_used": db_context,
                "query": user_query
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "query": user_query
            }
    
    def _build_augmented_prompt(self, user_query: str, db_context: Dict, 
                                chat_history: List[Dict] = None) -> str:
        """Build enriched prompt with database context"""
        
        # Start with system context
        prompt = """You are an AI assistant for the Cloudburst Management System database.
You have access to real-time database information and should provide accurate, helpful responses.

DATABASE CONTEXT:
"""
        
        # Add table information
        if db_context.get("tables_info"):
            prompt += "\n=== AVAILABLE TABLES ===\n"
            for table_name, info in db_context["tables_info"].items():
                prompt += f"\n{table_name.upper()}:\n"
                prompt += f"  - Rows: {info.get('row_count', 'N/A')}\n"
                if info.get('columns'):
                    prompt += f"  - Columns: {', '.join([col['name'] for col in info['columns']])}\n"
        
        # Add statistics
        if db_context.get("statistics"):
            prompt += "\n=== CURRENT STATISTICS ===\n"
            for table_name, stats in db_context["statistics"].items():
                if stats and not stats.get("error"):
                    prompt += f"\n{table_name.upper()}:\n"
                    for key, value in stats.items():
                        prompt += f"  - {key}: {value}\n"
        
        # Add recent data samples
        if db_context.get("recent_data"):
            prompt += "\n=== RECENT DATA SAMPLES ===\n"
            for table_name, data in db_context["recent_data"].items():
                if data and len(data) > 0:
                    prompt += f"\n{table_name.upper()} (latest {len(data)} records):\n"
                    for record in data[:3]:  # Show top 3
                        prompt += f"  {record}\n"
        
        # Add chat history for context continuity
        if chat_history and len(chat_history) > 0:
            prompt += "\n=== CONVERSATION HISTORY ===\n"
            for msg in chat_history[-3:]:  # Last 3 messages
                role = msg.get("role", "unknown")
                content = msg.get("content", "")
                prompt += f"{role.upper()}: {content[:200]}...\n"
        
        # Add the user's current question
        prompt += f"\n=== USER QUESTION ===\n{user_query}\n\n"
        
        # Add instructions
        prompt += """
INSTRUCTIONS:
- Provide accurate, data-driven responses based on the database context
- If asked to query data, suggest SQL queries when appropriate
- Highlight important insights and patterns
- Be conversational but precise
- If you need more information, ask clarifying questions
- Format responses clearly with markdown when appropriate

Please answer the user's question:"""
        
        return prompt
    
    def _generate_ai_response(self, enriched_prompt: str, original_query: str) -> str:
        """Generate AI response using OpenAI"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful database assistant for a Cloudburst Management System."},
                    {"role": "user", "content": enriched_prompt}
                ],
                temperature=0.7,
                max_tokens=1500
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}")
    
    def suggest_queries(self, based_on_context: Dict) -> List[str]:
        """Suggest relevant follow-up queries based on database context"""
        suggestions = []
        
        # Analyze context and suggest queries
        if "rainfall_data" in based_on_context.get("tables_info", {}):
            suggestions.append("What's the average rainfall by region this month?")
            suggestions.append("Show me regions with highest rainfall intensity")
        
        if "alerts" in based_on_context.get("tables_info", {}):
            suggestions.append("How many critical alerts are currently active?")
            suggestions.append("Which regions have the most alerts?")
        
        if "resources" in based_on_context.get("tables_info", {}):
            suggestions.append("What resources are running low on stock?")
            suggestions.append("Show resource distribution across regions")
        
        if "distribution_log" in based_on_context.get("tables_info", {}):
            suggestions.append("What's the distribution trend over the last week?")
            suggestions.append("Who distributed the most resources recently?")
        
        return suggestions[:4]  # Return top 4 suggestions
