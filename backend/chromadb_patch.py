"""
Patch for ChromaDB compatibility with Python 3.14
This fixes the pydantic.v1.errors.ConfigError issue
"""
import sys

def patch_chromadb():
    """Patch ChromaDB config to work with Python 3.14"""
    try:
        import chromadb.config
        from typing import Optional
        
        # Patch the problematic field before Settings class is created
        if hasattr(chromadb.config, 'Settings'):
            settings_class = chromadb.config.Settings
            if hasattr(settings_class, '__annotations__'):
                # Add type hint for chroma_server_nofile if missing
                if 'chroma_server_nofile' in settings_class.__dict__:
                    if 'chroma_server_nofile' not in settings_class.__annotations__:
                        settings_class.__annotations__['chroma_server_nofile'] = Optional[int]
        
        return True
    except Exception as e:
        print(f"Warning: Could not patch ChromaDB: {e}")
        return False

# Apply patch on import
patch_chromadb()
