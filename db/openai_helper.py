"""
OpenAI Integration Module
Handles AI-powered natural language to SQL conversion and query responses
"""

import openai
import streamlit as st
from typing import Optional, Dict, Any
import pandas as pd
import json


class OpenAIAssistant:
    """AI Assistant for natural language database queries"""
    
    def __init__(self, api_key: str, model: str = "gpt-4-turbo-preview"):
        """
        Initialize OpenAI assistant
        
        Args:
            api_key: OpenAI API key
            model: Model to use (gpt-4-turbo-preview or gpt-3.5-turbo)
        """
        self.api_key = api_key
        self.model = model
        openai.api_key = api_key
        
        # Database schema for context
        self.schema = """
        Database: cloudburst_management
        
        Tables:
        
        1. rainfall_data
           - id (INT, PRIMARY KEY)
           - region (VARCHAR)
           - date (DATE)
           - rainfall_mm (FLOAT) - rainfall in millimeters
           - temperature_c (FLOAT) - temperature in Celsius
           - humidity (FLOAT) - humidity percentage
        
        2. affected_regions
           - region_id (INT, PRIMARY KEY)
           - region_name (VARCHAR)
           - population (INT)
           - risk_level (VARCHAR) - Low/Moderate/High/Critical
           - warning_status (BOOLEAN) - 1=warned, 0=not warned
           - last_update (DATETIME)
           - report_date (DATE)
        
        3. resources
           - resource_id (INT, PRIMARY KEY)
           - resource_type (VARCHAR) - e.g., Food Kits, Water, Medical Kits
           - quantity_available (INT)
           - location (VARCHAR)
           - status (VARCHAR) - Available/In Use/Depleted
           - last_restocked (DATE)
        
        4. distribution_log
           - log_id (INT, PRIMARY KEY)
           - region_id (INT, FOREIGN KEY -> affected_regions)
           - resource_id (INT, FOREIGN KEY -> resources)
           - quantity_sent (INT)
           - date_distributed (DATE)
           - distributed_by (VARCHAR)
           - received_date (DATE)
        
        5. alerts
           - alert_id (INT, PRIMARY KEY)
           - region (VARCHAR)
           - alert_message (TEXT)
           - severity (VARCHAR) - Low/Moderate/High/Critical
           - date_issued (DATE)
           - expiry_date (DATE)
        """
    
    def generate_sql_query(self, user_question: str) -> Dict[str, Any]:
        """
        Convert natural language question to SQL query
        
        Args:
            user_question: User's natural language question
            
        Returns:
            Dictionary with SQL query and explanation
        """
        try:
            prompt = f"""You are a SQL expert. Convert the following natural language question into a SQL query for a MySQL database.

Database Schema:
{self.schema}

User Question: {user_question}

Rules:
1. Generate ONLY valid MySQL queries
2. Use proper JOINs when needed
3. Include LIMIT clause for safety (max 1000 rows)
4. Use proper date functions for date filtering
5. Return data in a user-friendly format

Respond with JSON in this exact format:
{{
    "sql": "SELECT ... FROM ... WHERE ...",
    "explanation": "Brief explanation of what the query does",
    "visualization_type": "table|chart|metric",
    "chart_config": {{"type": "bar|line|pie", "x": "column", "y": "column"}}
}}

Only return the JSON, nothing else."""

            response = openai.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a SQL expert that converts natural language to SQL queries. Always respond with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1000
            )
            
            # Parse response
            content = response.choices[0].message.content.strip()
            
            # Remove markdown code blocks if present
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            
            result = json.loads(content.strip())
            
            return {
                'success': True,
                'sql': result.get('sql', ''),
                'explanation': result.get('explanation', ''),
                'visualization_type': result.get('visualization_type', 'table'),
                'chart_config': result.get('chart_config', {})
            }
            
        except json.JSONDecodeError as e:
            return {
                'success': False,
                'error': f"Failed to parse AI response: {str(e)}",
                'raw_response': content if 'content' in locals() else None
            }
        except Exception as e:
            return {
                'success': False,
                'error': f"Error generating SQL: {str(e)}"
            }
    
    def explain_results(self, query: str, df: pd.DataFrame, user_question: str) -> str:
        """
        Generate natural language explanation of query results
        
        Args:
            query: SQL query executed
            df: DataFrame with results
            user_question: Original user question
            
        Returns:
            Natural language explanation
        """
        try:
            # Prepare data summary
            data_summary = {
                'rows': len(df),
                'columns': df.columns.tolist(),
                'sample_data': df.head(3).to_dict('records') if not df.empty else []
            }
            
            prompt = f"""Given this database query and results, provide a clear, concise explanation for the user.

User Question: {user_question}

SQL Query: {query}

Results Summary:
- Number of rows: {data_summary['rows']}
- Columns: {', '.join(data_summary['columns'])}
- Sample data: {json.dumps(data_summary['sample_data'], default=str)}

Provide a brief, user-friendly explanation of the results in 2-3 sentences. Focus on key insights and patterns."""

            response = openai.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that explains database query results in simple terms."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=300
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            return f"Results retrieved successfully with {len(df)} records."
    
    def suggest_follow_up_questions(self, user_question: str, results_df: pd.DataFrame) -> list:
        """
        Suggest relevant follow-up questions
        
        Args:
            user_question: Original question
            results_df: Query results
            
        Returns:
            List of suggested questions
        """
        try:
            prompt = f"""Based on this database query about disaster management, suggest 3 relevant follow-up questions.

Original Question: {user_question}
Number of Results: {len(results_df)}

Suggest 3 specific, actionable follow-up questions the user might want to ask. Make them concise and relevant."""

            response = openai.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Suggest brief, relevant follow-up questions."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=200
            )
            
            suggestions = response.choices[0].message.content.strip().split('\n')
            # Clean up suggestions
            suggestions = [s.strip('- 123.') for s in suggestions if s.strip()]
            return suggestions[:3]
            
        except:
            return [
                "Show me more details about these results",
                "What are the trends over time?",
                "How does this compare to other regions?"
            ]
    
    def validate_sql(self, sql: str) -> Dict[str, Any]:
        """
        Validate SQL query for safety
        
        Args:
            sql: SQL query to validate
            
        Returns:
            Dictionary with validation result
        """
        sql_lower = sql.lower().strip()
        
        # Check for dangerous operations
        dangerous_keywords = ['drop', 'delete', 'truncate', 'alter', 'create', 'update', 'insert']
        
        for keyword in dangerous_keywords:
            if keyword in sql_lower:
                return {
                    'valid': False,
                    'error': f"Query contains potentially dangerous operation: {keyword.upper()}. Only SELECT queries are allowed."
                }
        
        # Must be a SELECT query
        if not sql_lower.startswith('select'):
            return {
                'valid': False,
                'error': "Only SELECT queries are allowed for safety."
            }
        
        # Check for LIMIT clause (add if missing)
        if 'limit' not in sql_lower:
            sql += ' LIMIT 1000'
        
        return {
            'valid': True,
            'sql': sql
        }


# Cached instance
@st.cache_resource
def get_ai_assistant(api_key: str, model: str = "gpt-4-turbo-preview") -> Optional[OpenAIAssistant]:
    """
    Get or create AI assistant instance
    
    Args:
        api_key: OpenAI API key
        model: Model to use
        
    Returns:
        OpenAIAssistant instance or None
    """
    if not api_key:
        return None
    
    try:
        return OpenAIAssistant(api_key, model)
    except Exception as e:
        st.error(f"Failed to initialize AI assistant: {e}")
        return None
