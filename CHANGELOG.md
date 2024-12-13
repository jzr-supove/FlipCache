# Changelog

## Version 1.1

### Enhancements and Bug Fixes
- **Improved Redis Instance Compatibility**:  
  - Previously, the class enforced `decode_responses=True` for all Redis instances, which caused issues when using custom encoding and decoding functions like `pickle.dumps` and `pickle.loads`.
  - Now, the `decode_responses=True` assertion is relaxed when `value_type="custom"`, allowing users to define their custom encoder and decoder functions without encountering UTF-8 encoding errors.
  - The `decode_responses=True` assertion is still enforced when `value_type` is not set to `"custom"`, maintaining consistency for default configurations.

This change ensures better flexibility for advanced use cases involving custom encoding and decoding while preserving the original functionality for other use cases.
