# Makefile extensions for linux-arm64.

# -----------------------------------------------------------------------------
# OS-ARCH specific targets
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
# Makefile targets supported only by this platform.
# -----------------------------------------------------------------------------

.PHONY: only-linux-arm64
only-linux-arm64:
	$(info Only linux-arm64 has this Makefile target.)
