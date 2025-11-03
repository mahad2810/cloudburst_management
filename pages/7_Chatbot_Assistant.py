"""
🤖 Chatbot Assistant - AI-Powered CSV Data Assistant with OpenAI
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import sys
from pathlib import Path
import json
from openai import OpenAI

sys.path.append(str(Path(__file__).parent.parent))

st.set_page_config(
    page_title="Chatbot Assistant - Cloudburst MS",
    page_icon="🤖",
    layout="wide"
)

# CSV file paths
CSV_FILES = {
    'rainfall_data': 'csv_sheets/rainfall_data.csv',
    'affected_regions': 'csv_sheets/affected_regions.csv',
    'alerts': 'csv_sheets/alerts.csv',
    'resources': 'csv_sheets/resources.csv',
    'distribution_log': 'csv_sheets/distribution_log.csv'
}

# Sample query patterns and responses
QUERY_PATTERNS = {
    'rainfall': {
        'keywords': ['rainfall', 'rain', 'precipitation', 'weather'],
        'queries': {
            'total': "SELECT COUNT(*) as count, AVG(rainfall_mm) as avg_rainfall, MAX(rainfall_mm) as max_rainfall FROM rainfall_data",
            'by_region': "SELECT region, AVG(rainfall_mm) as avg_rainfall FROM rainfall_data GROUP BY region ORDER BY avg_rainfall DESC",
            'recent': "SELECT * FROM rainfall_data ORDER BY date DESC LIMIT 10"
        }
    },
    'alerts': {
        'keywords': ['alert', 'warning', 'emergency', 'notification'],
        'queries': {
            'active': "SELECT COUNT(*) as count FROM alerts WHERE expiry_date >= CURDATE()",
            'critical': "SELECT * FROM alerts WHERE severity = 'Critical' AND expiry_date >= CURDATE()",
            'by_region': "SELECT region, COUNT(*) as count FROM alerts WHERE expiry_date >= CURDATE() GROUP BY region"
        }
    },
    'resources': {
        'keywords': ['resource', 'inventory', 'stock', 'supply', 'supplies'],
        'queries': {
            'total': "SELECT SUM(quantity_available) as total FROM resources",
            'by_type': "SELECT resource_type, SUM(quantity_available) as total FROM resources GROUP BY resource_type",
            'low_stock': "SELECT * FROM resources WHERE quantity_available < 100 ORDER BY quantity_available ASC"
        }
    },
    'distribution': {
        'keywords': ['distribution', 'distribute', 'sent', 'delivered', 'delivery'],
        'queries': {
            'total': "SELECT COUNT(*) as count, SUM(quantity_sent) as total FROM distribution_log",
            'recent': "SELECT * FROM distribution_log ORDER BY date_distributed DESC LIMIT 10",
            'by_region': "SELECT r.region_name, COUNT(*) as count FROM distribution_log d JOIN affected_regions r ON d.region_id = r.region_id GROUP BY r.region_name"
        }
    }
}

def load_csv_data():
    """Load all CSV files into dataframes"""
    data = {}
    base_path = Path(__file__).parent.parent
    
    for name, file_path in CSV_FILES.items():
        try:
            full_path = base_path / file_path
            data[name] = pd.read_csv(full_path)
            # Convert date columns
            if name == 'rainfall_data':
                data[name]['date'] = pd.to_datetime(data[name]['date'])
            elif name == 'alerts':
                data[name]['date_issued'] = pd.to_datetime(data[name]['date_issued'])
                data[name]['expiry_date'] = pd.to_datetime(data[name]['expiry_date'])
            elif name == 'distribution_log':
                data[name]['date_distributed'] = pd.to_datetime(data[name]['date_distributed'])
                data[name]['received_date'] = pd.to_datetime(data[name]['received_date'])
        except Exception as e:
            st.error(f"Error loading {name}: {e}")
    
    return data

def get_data_summary(data):
    """Get summary information about all datasets"""
    summary = {}
    for name, df in data.items():
        summary[name] = {
            "rows": len(df),
            "columns": list(df.columns),
            "sample": df.head(3).to_dict('records')
        }
    return summary

def initialize_chat_history():
    """Initialize chat history in session state"""
    if 'messages' not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "� Hello! I'm your AI-powered Cloudburst Management Assistant. I can analyze data and answer questions like:\n\n"
                          "• 🌧️ 'Which place received the highest rainfall in August 2025?'\n"
                          "• ⚠️ 'Show me all severe alerts'\n"
                          "• 📦 'Which resources are running low?'\n"
                          "• 🚚 'What was distributed to Shimla recently?'\n"
                          "• 📊 'Compare rainfall between regions'\n\n"
                          "Ask me anything about the data!"
            }
        ]

def process_ai_query(client, user_question, data, data_summary):
    """Process user query using OpenAI to analyze CSV data"""
    try:
        # Create a context about available data
        context = f"""You are a data analyst assistant for a Cloudburst Management System. You have access to the following CSV datasets:

AVAILABLE DATASETS:
1. rainfall_data: {data_summary['rainfall_data']['rows']} rows
   Columns: {', '.join(data_summary['rainfall_data']['columns'])}
   Sample data: {json.dumps(data_summary['rainfall_data']['sample'][:2], default=str)}

2. affected_regions: {data_summary['affected_regions']['rows']} rows
   Columns: {', '.join(data_summary['affected_regions']['columns'])}
   
3. alerts: {data_summary['alerts']['rows']} rows
   Columns: {', '.join(data_summary['alerts']['columns'])}
   
4. resources: {data_summary['resources']['rows']} rows
   Columns: {', '.join(data_summary['resources']['columns'])}
   
5. distribution_log: {data_summary['distribution_log']['rows']} rows
   Columns: {', '.join(data_summary['distribution_log']['columns'])}

IMPORTANT INSTRUCTIONS:
- Analyze the user's question
- Determine which dataset(s) are needed
- Provide Python pandas code to answer the question
- Return ONLY valid Python code that uses the dataframes
- Use variable names: rainfall_data, affected_regions, alerts, resources, distribution_log
- For date filtering, use pd.to_datetime() and comparison operators
- Store the final answer in a variable called 'result'
- The result should be either a value, a dataframe, or a formatted string

USER QUESTION: {user_question}

Return ONLY the Python code, no explanations."""

        # Call OpenAI
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a Python data analysis expert. Return only executable pandas code."},
                {"role": "user", "content": context}
            ],
            temperature=0.3,
            max_tokens=500
        )
        
        code = response.choices[0].message.content.strip()
        
        # Clean up code (remove markdown formatting if present)
        if code.startswith("```python"):
            code = code.replace("```python", "").replace("```", "").strip()
        elif code.startswith("```"):
            code = code.replace("```", "").strip()
        
        return code
        
    except Exception as e:
        return None

def execute_ai_code(code, data):
    """Execute AI-generated code safely"""
    try:
        # Create a safe execution environment with the dataframes
        exec_globals = {
            'pd': pd,
            'rainfall_data': data['rainfall_data'].copy(),
            'affected_regions': data['affected_regions'].copy(),
            'alerts': data['alerts'].copy(),
            'resources': data['resources'].copy(),
            'distribution_log': data['distribution_log'].copy(),
            'datetime': datetime,
            'result': None
        }
        
        # Execute the code
        exec(code, exec_globals)
        
        result = exec_globals.get('result')
        return {'success': True, 'result': result, 'code': code}
        
    except Exception as e:
        return {'success': False, 'error': str(e), 'code': code}

def process_query(data, user_input, client=None):
    """Process user query and return response"""
    user_input_lower = user_input.lower()
    
    # If OpenAI client is available, use AI processing
    if client:
        with st.spinner("🤖 Analyzing your question with AI..."):
            data_summary = get_data_summary(data)
            code = process_ai_query(client, user_input, data, data_summary)
            
            if code:
                with st.spinner("⚡ Running analysis..."):
                    execution_result = execute_ai_code(code, data)
                    
                    if execution_result['success']:
                        result = execution_result['result']
                        
                        # Format the response based on result type
                        if isinstance(result, pd.DataFrame):
                            return {
                                'type': 'dataframe',
                                'content': result,
                                'title': '📊 Query Results',
                                'code': execution_result['code']
                            }
                        elif isinstance(result, (int, float, str)):
                            return {
                                'type': 'text',
                                'content': f"**Answer:** {result}",
                                'code': execution_result['code']
                            }
                        else:
                            return {
                                'type': 'text',
                                'content': f"**Result:** {str(result)}",
                                'code': execution_result['code']
                            }
                    else:
                        return {
                            'type': 'text',
                            'content': f"❌ Error executing analysis: {execution_result['error']}\n\nGenerated code:\n```python\n{execution_result['code']}\n```"
                        }
    
    # Fallback to simple queries if AI is not available
    if 'low' in user_input_lower and 'stock' in user_input_lower:
        df = data['resources'][data['resources']['quantity_available'] < 1000]
        return {
            'type': 'dataframe',
            'content': df,
            'title': '⚠️ Low Stock Resources'
        }
    
    elif 'alert' in user_input_lower:
        df = data['alerts']
        return {
            'type': 'dataframe',
            'content': df.head(20),
            'title': '⚠️ Recent Alerts'
        }
    
    elif 'rainfall' in user_input_lower:
        df = data['rainfall_data'].head(20)
        return {
            'type': 'dataframe',
            'content': df,
            'title': '🌧️ Recent Rainfall Data'
        }
    
    return {
        'type': 'text',
        'content': "I'm not sure how to answer that. Try asking about rainfall, alerts, resources, or distributions."
    }

def display_response(response):
    """Display chatbot response"""
    if response['type'] == 'text':
        st.markdown(response['content'])
        
        # Show AI-generated code if available
        if 'code' in response:
            with st.expander("🔍 View AI-Generated Code"):
                st.code(response['code'], language='python')
    
    elif response['type'] == 'dataframe':
        st.markdown(f"**{response['title']}**")
        st.dataframe(response['content'], use_container_width=True, hide_index=True)
        
        # Show AI-generated code if available
        if 'code' in response:
            with st.expander("🔍 View AI-Generated Code"):
                st.code(response['code'], language='python')
        
        # Add download button
        csv = response['content'].to_csv(index=False)
        st.download_button(
            label="📥 Download Data",
            data=csv,
            file_name=f"query_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            key=f"download_{datetime.now().timestamp()}"
        )

def execute_ai_query(db, ai_assistant, user_question):
    """Execute AI-generated query and return results"""
    with st.spinner("🤖 Analyzing your question..."):
        # Generate SQL
        query_result = ai_assistant.generate_sql_query(user_question)
        
        if not query_result.get('success'):
            return {
                'type': 'error',
                'content': query_result.get('error', 'Failed to generate query')
            }
        
        sql = query_result['sql']
        explanation = query_result['explanation']
        viz_type = query_result.get('visualization_type', 'table')
        chart_config = query_result.get('chart_config', {})
        
        # Validate SQL
        validation = ai_assistant.validate_sql(sql)
        if not validation['valid']:
            return {
                'type': 'error',
                'content': validation['error']
            }
        
        sql = validation['sql']
        
        # Execute query
        try:
            df = db.fetch_dataframe(sql)
            
            if df.empty:
                return {
                    'type': 'text',
                    'content': "✅ Query executed successfully, but no results found."
                }
            
            # Generate explanation
            ai_explanation = ai_assistant.explain_results(sql, df, user_question)
            
            # Get follow-up suggestions
            suggestions = ai_assistant.suggest_follow_up_questions(user_question, df)
            
            return {
                'type': 'ai_response',
                'sql': sql,
                'explanation': explanation,
                'ai_insight': ai_explanation,
                'data': df,
                'viz_type': viz_type,
                'chart_config': chart_config,
                'suggestions': suggestions
            }
            
        except Exception as e:
            return {
                'type': 'error',
                'content': f"Query execution error: {str(e)}\n\nGenerated SQL:\n```sql\n{sql}\n```"
            }

def execute_rag_query(rag_assistant, user_query, chat_history=None):
    """Execute a query using RAG architecture"""
    try:
        # Get RAG response with database context
        result = rag_assistant.generate_rag_response(user_query, chat_history)
        
        if result['success']:
            # Get follow-up suggestions
            suggestions = rag_assistant.suggest_queries(result['context_used'])
            
            return {
                'type': 'rag_response',
                'content': result['response'],
                'context': result['context_used'],
                'query': result['query'],
                'suggestions': suggestions
            }
        else:
            return {
                'type': 'error',
                'content': f"❌ Error: {result['error']}"
            }
    
    except Exception as e:
        return {
            'type': 'error',
            'content': f"❌ Error processing query: {str(e)}"
        }

def display_ai_response(response):
    """Display AI-powered chatbot response"""
    if response['type'] == 'error':
        st.error(response['content'])
        return
    
    if response['type'] == 'rag_response':
        # Display RAG response
        st.markdown("### 🤖 AI Response")
        st.markdown(response['content'])
        
        # Show context used in an expander
        if response.get('context'):
            with st.expander("🔍 View Retrieved Database Context"):
                context = response['context']
                
                # Show tables analyzed
                if context.get('tables_info'):
                    st.markdown("**📊 Tables Analyzed:**")
                    cols = st.columns(len(context['tables_info']))
                    for idx, (table_name, info) in enumerate(context['tables_info'].items()):
                        with cols[idx]:
                            st.metric(table_name, f"{info.get('row_count', 'N/A')} rows")
                
                # Show statistics
                if context.get('statistics'):
                    st.markdown("**📈 Key Statistics:**")
                    for table_name, stats in context['statistics'].items():
                        if stats and not stats.get('error'):
                            with st.expander(f"📊 {table_name}"):
                                st.json(stats)
        
        # Show follow-up suggestions
        if response.get('suggestions'):
            st.markdown("**💭 Suggested Follow-up Questions:**")
            cols = st.columns(2)
            for idx, suggestion in enumerate(response['suggestions']):
                with cols[idx % 2]:
                    st.info(f"💡 {suggestion}")
        
        return
    
    if response['type'] == 'text':
        st.markdown(response['content'])
        return
    
    if response['type'] == 'ai_response':
        # Show AI explanation
        st.markdown(f"**🎯 {response['explanation']}**")
        st.info(f"💡 **Insight:** {response['ai_insight']}")
        
        # Show data visualization
        df = response['data']
        viz_type = response['viz_type']
        chart_config = response['chart_config']
        
        if viz_type == 'chart' and chart_config:
            chart_type = chart_config.get('type', 'bar')
            x = chart_config.get('x')
            y = chart_config.get('y')
            
            if x in df.columns and y in df.columns:
                if chart_type == 'bar':
                    fig = px.bar(df, x=x, y=y, template='plotly_dark')
                elif chart_type == 'line':
                    fig = px.line(df, x=x, y=y, template='plotly_dark', markers=True)
                elif chart_type == 'pie':
                    fig = px.pie(df, names=x, values=y, template='plotly_dark')
                else:
                    fig = px.bar(df, x=x, y=y, template='plotly_dark')
                
                st.plotly_chart(fig, use_container_width=True)
        
        # Show data table
        st.markdown("**📊 Data:**")
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Download button
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 Download Data",
            data=csv,
            file_name=f"query_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            key=f"download_{datetime.now().timestamp()}"
        )
        
        # Show SQL query in expander
        with st.expander("🔍 View Generated SQL"):
            st.code(response['sql'], language='sql')
        
        # Show follow-up suggestions
        if response.get('suggestions'):
            st.markdown("**💭 You might also want to ask:**")
            for suggestion in response['suggestions']:
                st.markdown(f"- {suggestion}")
    
    elif response['type'] == 'dataframe':
        st.markdown(f"**{response['title']}**")
        st.dataframe(response['content'], use_container_width=True, hide_index=True)
        
        csv = response['content'].to_csv(index=False)
        st.download_button(
            label="📥 Download Data",
            data=csv,
            file_name=f"query_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            key=f"download_{datetime.now().timestamp()}"
        )

def main():
    """Main function for Chatbot Assistant page"""
    st.title("🤖 AI Chatbot Assistant")
    st.markdown("### Ask Questions About Your Data in Natural Language")
    
    st.markdown("---")
    
    # Load CSV data
    with st.spinner("📂 Loading data from CSV files..."):
        data = load_csv_data()
    
    if not data:
        st.error("❌ Failed to load CSV data")
        st.stop()
    
    # Load OpenAI API Key from config
    import config
    api_key = config.OPENAI_API_KEY if hasattr(config, 'OPENAI_API_KEY') and config.OPENAI_API_KEY else None
    
    # Initialize OpenAI client if API key is available
    client = None
    if api_key:
        try:
            client = OpenAI(api_key=api_key)
            st.success("✅ AI-Powered Assistant Ready (using OpenAI GPT-3.5)")
        except Exception as e:
            st.warning(f"⚠️ OpenAI initialization failed: {e}. Using basic pattern matching.")
    else:
        st.info("💡 Add OpenAI API key in config.py for AI-powered responses. Using basic pattern matching for now.")
    
    # Initialize chat history
    initialize_chat_history()
    
    # Show data summary
    with st.expander("📊 Available Data Overview"):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Rainfall Records", f"{len(data['rainfall_data']):,}")
            st.metric("Affected Regions", f"{len(data['affected_regions']):,}")
        with col2:
            st.metric("Active Alerts", f"{len(data['alerts']):,}")
            st.metric("Resources", f"{len(data['resources']):,}")
        with col3:
            st.metric("Distribution Logs", f"{len(data['distribution_log']):,}")
    
    # Sidebar with quick actions
    with st.sidebar:
        st.markdown("---")
        st.markdown("## � Example Questions")
        
        example_questions = [
            "What's the average rainfall by region?",
            "Show me critical alerts",
            "Which resources are low on stock?",
            "Show distribution trends for the last month",
            "Find regions with highest rainfall",
            "How many alerts were issued this week?",
            "Show me resource distribution by location",
            "What's the total population affected?"
        ]
        
        st.markdown("Click any question to try:")
        for question in example_questions[:6]:
            if st.button(f"💬 {question}", use_container_width=True, key=question):
                st.session_state.messages.append({
                    "role": "user",
                    "content": question
                })
                # Process query with CSV data
                response = process_query(data, question, client)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response
                })
                st.rerun()
        
        st.markdown("---")
        
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.messages = []
            initialize_chat_history()
            st.rerun()
    
    # Display chat history
    chat_container = st.container()
    
    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                if message["role"] == "user":
                    st.markdown(message["content"])
                else:
                    if isinstance(message["content"], dict):
                        display_response(message["content"])
                    else:
                        st.markdown(message["content"])
    
    # Chat input
    user_input = st.chat_input("Ask me anything about the database in plain English...")
    
    if user_input:
        # Add user message to history
        st.session_state.messages.append({
            "role": "user",
            "content": user_input
        })
        
        # Process query with CSV data and AI
        response = process_query(data, user_input, client)
        
        # Add assistant response to history
        st.session_state.messages.append({
            "role": "assistant",
            "content": response
        })
        
        # Rerun to display new messages
        st.rerun()
    
    # Footer
    st.markdown("---")
    st.info("""
    🤖 **AI-Powered Chatbot Assistant:** Ask complex questions about your data in natural language!
    
    **Powered by OpenAI GPT-3.5** - The AI analyzes your question, generates Python pandas code, and executes it on your CSV data.
    
    **Example questions you can ask:**
    - 🌧️ "Which place received the highest rainfall in August 2025?"
    - 📊 "Show me the average rainfall by region for July 2024"
    - ⚠️ "List all severe alerts that are still active"
    - 📦 "Which resources have less than 500 units available?"
    - 🚚 "What was distributed to Shimla in the last month?"
    - 📈 "Compare rainfall between Shimla and Manali"
    - 🔍 "Find regions with critical risk level"
    
    **How it works:**
    1. You ask a question in plain English
    2. AI generates Python pandas code to answer your question
    3. Code is executed on your CSV data
    4. Results are displayed with the generated code (click "View AI-Generated Code")
    
    **Tip:** You can see the Python code the AI generated by expanding the code section in each response!
    """)

if __name__ == "__main__":
    main()
