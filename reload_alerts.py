"""
Script to reload alerts data from CSV to database
Run this after updating the alerts.csv file
"""

import pandas as pd
import mysql.connector
from mysql.connector import Error
from config import DATABASE_CONFIG

def reload_alerts():
    """Reload alerts from CSV into database"""
    try:
        # Connect to database
        connection = mysql.connector.connect(
            host=DATABASE_CONFIG['host'],
            database=DATABASE_CONFIG['database'],
            user=DATABASE_CONFIG['user'],
            password=DATABASE_CONFIG['password']
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            print("✅ Connected to database")
            
            # Update schema to support new severity levels
            print("📝 Updating alerts table schema...")
            alter_query = """
                ALTER TABLE alerts 
                MODIFY COLUMN severity VARCHAR(50) DEFAULT 'Low'
            """
            cursor.execute(alter_query)
            print("✅ Schema updated")
            
            # Clear existing alerts
            print("🗑️  Clearing existing alerts...")
            cursor.execute("DELETE FROM alerts")
            connection.commit()
            print("✅ Existing alerts cleared")
            
            # Read CSV
            print("📂 Reading alerts from CSV...")
            df = pd.read_csv('csv_sheets/alerts.csv')
            print(f"📊 Found {len(df)} alerts in CSV")
            
            # Insert alerts
            print("💾 Inserting alerts into database...")
            insert_query = """
                INSERT INTO alerts 
                (alert_id, region, alert_message, severity, date_issued, expiry_date)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            
            success_count = 0
            for _, row in df.iterrows():
                try:
                    cursor.execute(insert_query, (
                        int(row['alert_id']),
                        str(row['region']),
                        str(row['alert_message']),
                        str(row['severity']),
                        str(row['date_issued']),
                        str(row['expiry_date'])
                    ))
                    success_count += 1
                except Exception as e:
                    print(f"⚠️  Error inserting alert {row['alert_id']}: {e}")
            
            connection.commit()
            print(f"✅ Successfully inserted {success_count} alerts")
            
            # Verify
            cursor.execute("SELECT COUNT(*) FROM alerts")
            count = cursor.fetchone()[0]
            print(f"✅ Total alerts in database: {count}")
            
            # Show sample data
            cursor.execute("SELECT alert_id, region, severity, date_issued, expiry_date FROM alerts LIMIT 5")
            print("\n📋 Sample alerts:")
            for row in cursor.fetchall():
                print(f"  ID: {row[0]}, Region: {row[1]}, Severity: {row[2]}, Issued: {row[3]}, Expires: {row[4]}")
            
            cursor.close()
            connection.close()
            print("\n🎉 Alerts data reload completed successfully!")
            
    except Error as e:
        print(f"❌ Database error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🌧️ Cloudburst Management System - Alert Data Reload\n")
    reload_alerts()
