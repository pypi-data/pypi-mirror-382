# Makefile extensions for windows.

# -----------------------------------------------------------------------------
# OS-ARCH specific targets
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
# Makefile targets supported only by this platform.
# -----------------------------------------------------------------------------

.PHONY: only-windows-x86_64
only-windows-x86_64:
	$(info Only windows-x86_64 has this Makefile target.)
