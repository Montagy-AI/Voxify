#!/usr/bin/env python3
"""
Cleanup script for orphaned voice clones.

This script removes voice clone records from the database that don't have
corresponding files in the file system, which can happen due to:
- Incomplete deletion operations
- Manual file system cleanup
- System crashes during deletion

Run this script to clean up inconsistent data between database and file system.
"""

import os
import sys
from pathlib import Path

# Add the backend directory to the path so we can import modules
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from database import get_database_manager
from database.models import VoiceModel, VoiceSample
from api.v1.voice.f5_tts_service import get_f5_tts_service


def cleanup_orphaned_voice_clones():
    """Remove voice clone database records that don't have corresponding files."""
    print("🧹 Starting cleanup of orphaned voice clones...")
    
    try:
        # Get database session
        db = get_database_manager()
        f5_service = get_f5_tts_service()
        
        orphaned_count = 0
        total_count = 0
        
        with db.get_session() as session:
            # Get all voice models
            voice_models = session.query(VoiceModel).filter(
                VoiceModel.model_type == "f5_tts"
            ).all()
            
            total_count = len(voice_models)
            print(f"📊 Found {total_count} voice clone records in database")
            
            for model in voice_models:
                try:
                    # Check if clone files exist in file system
                    clone_path = f5_service.base_path / model.id
                    clone_info_path = clone_path / "clone_info.json"
                    
                    if not clone_path.exists() or not clone_info_path.exists():
                        print(f"🗑️  Orphaned clone found: {model.id} ({model.name})")
                        print(f"    Path: {clone_path}")
                        print(f"    Clone info exists: {clone_info_path.exists()}")
                        
                        # Delete related synthesis jobs first
                        from database.models import SynthesisJob
                        synthesis_jobs = session.query(SynthesisJob).filter(
                            SynthesisJob.voice_model_id == model.id
                        ).all()
                        
                        for job in synthesis_jobs:
                            print(f"    Deleting related synthesis job: {job.id}")
                            session.delete(job)
                        
                        # Delete the voice model
                        session.delete(model)
                        orphaned_count += 1
                        
                        print(f"    ✅ Deleted orphaned voice clone: {model.name}")
                    
                except Exception as e:
                    print(f"❌ Error checking clone {model.id}: {e}")
                    continue
            
            # Commit all changes
            if orphaned_count > 0:
                session.commit()
                print(f"💾 Committed {orphaned_count} deletions to database")
            else:
                print("✨ No orphaned voice clones found - database is clean!")
        
        print(f"\n📈 Cleanup Summary:")
        print(f"   Total voice clones checked: {total_count}")
        print(f"   Orphaned records removed: {orphaned_count}")
        print(f"   Remaining valid clones: {total_count - orphaned_count}")
        
        return orphaned_count
        
    except Exception as e:
        print(f"❌ Cleanup failed: {e}")
        return -1


def verify_cleanup():
    """Verify that cleanup was successful by checking for remaining orphaned clones."""
    print("\n🔍 Verifying cleanup results...")
    
    try:
        db = get_database_manager()
        f5_service = get_f5_tts_service()
        
        with db.get_session() as session:
            voice_models = session.query(VoiceModel).filter(
                VoiceModel.model_type == "f5_tts"
            ).all()
            
            orphaned_found = 0
            for model in voice_models:
                clone_path = f5_service.base_path / model.id
                if not clone_path.exists():
                    print(f"⚠️  Still orphaned: {model.id} ({model.name})")
                    orphaned_found += 1
            
            if orphaned_found == 0:
                print("✅ Verification passed - no orphaned clones remaining")
            else:
                print(f"⚠️  Verification found {orphaned_found} remaining orphaned clones")
                
            return orphaned_found == 0
            
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("🧹 VOICE CLONE CLEANUP UTILITY")
    print("=" * 60)
    
    # Run cleanup
    deleted_count = cleanup_orphaned_voice_clones()
    
    if deleted_count >= 0:
        # Verify cleanup
        verification_passed = verify_cleanup()
        
        print("\n" + "=" * 60)
        if verification_passed:
            print("🎉 CLEANUP COMPLETED SUCCESSFULLY!")
        else:
            print("⚠️  CLEANUP COMPLETED WITH WARNINGS")
        print("=" * 60)
        
        exit_code = 0 if verification_passed else 1
    else:
        print("\n" + "=" * 60)
        print("❌ CLEANUP FAILED")
        print("=" * 60)
        exit_code = 2
    
    sys.exit(exit_code)