#!/usr/bin/env python3
"""
Supabase Connection & Schema Diagnostic Script
Run this script to verify your Supabase connection and tables.
Usage: python check_supabase.py
"""

import sys
from app.config import get_settings
from app.database.supabase import get_supabase_client, SupabaseService

def main():
    print("=" * 65)
    print(" SUPABASE CONNECTION & SCHEMA DIAGNOSTICS")
    print("=" * 65)

    settings = get_settings()

    print(f"• Project URL Configured: {'YES' if settings.SUPABASE_URL and 'your-project' not in settings.SUPABASE_URL else 'NO (Still placeholder)'}")
    print(f"• API Key Detected:       {'YES' if settings.supabase_api_key else 'NO (Still placeholder)'}")
    
    if not settings.is_supabase_configured:
        print("\n[!] STATUS: Supabase is NOT configured yet in backend/.env!")
        print("\nAction Required:")
        print("1. Open backend/.env in your editor")
        print("2. Paste your Supabase Project URL and API Key")
        print("3. Press Ctrl + S to save the file")
        print("4. Run: python check_supabase.py")
        print("=" * 65)
        sys.exit(1)

    print("\nAttempting connection to Supabase...")
    service = SupabaseService()
    check = service.check_connection()

    if check["status"] == "connected":
        print("[+] SUCCESS: Connected to Supabase PostgreSQL!")
        
        # Test required tables
        client = service.client
        tables = ["resumes", "job_descriptions", "candidate_skills", "job_skills", "analyses", "skill_gaps", "recommendations"]
        print("\nChecking database tables:")
        all_tables_exist = True
        for tbl in tables:
            try:
                client.table(tbl).select("id").limit(0).execute()
                print(f"  [OK] Table '{tbl}': EXISTS")
            except Exception as e:
                all_tables_exist = False
                print(f"  [--] Table '{tbl}': NOT FOUND or access denied")

        if not all_tables_exist:
            print("\n[!] Some tables are missing! Please execute schema.sql in Supabase SQL Editor.")
        else:
            print("\n[+] ALL 7 SYSTEM TABLES ARE READY AND VERIFIED!")

    else:
        print(f"[X] Connection Failed: {check['detail']}")
        print("\nPlease check:")
        print("1. Is the URL correct (e.g. https://xyzcompany.supabase.co)?")
        print("2. Did you copy the full API key without extra spaces?")
        print("3. Did you execute backend/app/database/schema.sql in Supabase SQL Editor?")

    print("=" * 65)

if __name__ == "__main__":
    main()
