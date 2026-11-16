# Changelog

## Version 1.3.1

### Bug Fixes
- **Float expire times work.** `et` constants such as `FIFTEEN_MINUTES` and `HALF_AN_HOUR` were floats, and redis-py
  rejects a float `ex`, so the first write raised `DataError`. The constants are now ints, and `expire_time` accepts
  an int, a float (rounded up to whole seconds) or a `timedelta`.
- **`refresh_expire_time_on_get` covers local hits.** It used to refresh the Redis TTL only when a read missed the
  local tier, so the hottest keys could expire in Redis while still being served locally. Local hits now refresh
  the TTL at most once per half `expire_time` per key, so most reads still make no Redis call.
- **`value_default` is copied per key.** A missing key used to get the default object itself, so mutating it
  (the usual counter pattern: `payload["hits"] += 1`) changed the default for every later missing key.
- `refresh(key)` converts the key to `key_type` like the other methods.

### Other
- Tests (pytest + fakeredis, offline): `uv run pytest`.
- Project URLs point to github.com/jzr-supove/FlipCache.
- `requires-python` is now `>=3.8`; the code has always needed `typing.Literal`.

## Version 1.1

### Enhancements and Bug Fixes
- **Improved Redis Instance Compatibility**:  
  - Previously, the class enforced `decode_responses=True` for all Redis instances, which caused issues when using custom encoding and decoding functions like `pickle.dumps` and `pickle.loads`.
  - Now, the `decode_responses=True` assertion is relaxed when `value_type="custom"`, allowing users to define their custom encoder and decoder functions without encountering UTF-8 encoding errors.
  - The `decode_responses=True` assertion is still enforced when `value_type` is not set to `"custom"`, maintaining consistency for default configurations.

This change ensures better flexibility for advanced use cases involving custom encoding and decoding while preserving the original functionality for other use cases.
