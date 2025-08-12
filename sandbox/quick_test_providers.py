#!/usr/bin/env python3
"""
Quick Provider Test for DOKKAEBI

Simple script to test if the multi-provider system is working.
Run this after setting up IEX Cloud token.
"""

import os
import sys
from datetime import datetime

# Add src to path
sys.path.append('/Users/rdc/src/dokkaebi/src')

from price_downloader.core.downloader_v2 import PriceDownloaderV2


def main():
    print("🚀 DOKKAEBI Quick Provider Test")
    print("=" * 50)
    
    # Check environment
    iex_token = os.getenv('IEX_TOKEN')
    print(f"IEX_TOKEN: {'✓ Set' if iex_token else '❌ Not set'}")
    
    if not iex_token:
        print("\n⚠️  To test IEX Cloud:")
        print("1. Get free token at https://iexcloud.io/")
        print("2. export IEX_TOKEN='pk_your_token_here'")
        print("3. Re-run this script")
        print("\nTesting with Yahoo Finance only...\n")
    
    try:
        # Quick test
        with PriceDownloaderV2(cache_path="sandbox/quick_test.duckdb") as downloader:
            print("Testing AAPL download...")
            
            start_time = datetime.now()
            data = downloader.download_symbol("AAPL", period="5d")
            end_time = datetime.now()
            
            if data is not None:
                print(f"✅ SUCCESS!")
                print(f"   Downloaded: {len(data)} rows")
                print(f"   Time taken: {(end_time - start_time).total_seconds():.2f}s")
                print(f"   Date range: {data.index.min().date()} to {data.index.max().date()}")
                
                # Show which provider was used
                stats = downloader.get_provider_stats()
                for provider_name, info in stats['providers'].items():
                    if info['usage_stats']['used'] > 0:
                        print(f"   Provider used: {provider_name}")
                        break
                        
            else:
                print("❌ FAILED - All providers unavailable")
                
            # Show provider status
            print(f"\n📊 Provider Status:")
            stats = downloader.get_provider_stats()
            for provider_name, info in stats['providers'].items():
                status = "✅ Available" if info['available'] else "❌ Unavailable"
                print(f"   {provider_name}: {status}")
                
    except Exception as e:
        print(f"💥 Error: {e}")
        return False
        
    print(f"\n🎯 Next steps:")
    if not iex_token:
        print("   1. Get IEX Cloud token for full redundancy")
        print("   2. Set IEX_TOKEN environment variable") 
    print("   3. Update your code to use PriceDownloaderV2")
    print("   4. Feed HebbNet with unlimited data! 🚀")
    
    return True


if __name__ == "__main__":
    main()