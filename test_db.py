import mysql.connector

print("Testing database connection...")

try:
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Abdul@2007",
        database="pashurakshak_ndlm"
    )

    print("✅ DATABASE CONNECTED")
    print("Connected:", conn.is_connected())

    conn.close()

except Exception as e:
    print("❌ CONNECTION FAILED")
    print(type(e).__name__)
    print(e)