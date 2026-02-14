"""
Patch for ChromaDB compatibility with Python 3.14
This fixes the pydantic.v1.errors.ConfigError issue where the
@validator decorator references 'chroma_server_nofile' before
the field is declared, and pydantic v1 can't infer types on Python 3.14.

Must be called BEFORE `import chromadb`.
"""
import sys
import importlib


def patch_chromadb():
    """
    Monkey-patch the chromadb.config module source so that
    the field `chroma_server_nofile` is declared BEFORE the
    @validator that references it.  We do this by patching
    pydantic.v1.fields to handle the missing annotation gracefully.
    """
    if sys.version_info < (3, 14):
        return True  # no patch needed

    try:
        # Patch pydantic v1's ModelField._set_default_and_type to
        # fall back to `type(default)` instead of raising ConfigError
        import pydantic.v1.fields as pf
        from typing import Optional

        _original = pf.ModelField._set_default_and_type

        def _patched(self):
            try:
                _original(self)
            except Exception:
                # If type inference fails, infer from the default value
                if self.default is not None:
                    self.outer_type_ = type(self.default)
                else:
                    self.outer_type_ = Optional[str]
                self.type_ = self.outer_type_

        pf.ModelField._set_default_and_type = _patched
        print("✅ ChromaDB/pydantic v1 compatibility patch applied for Python 3.14")
        return True
    except Exception as e:
        print(f"⚠️ Could not patch ChromaDB: {e}")
        return False


# Apply patch on import
patch_chromadb()
