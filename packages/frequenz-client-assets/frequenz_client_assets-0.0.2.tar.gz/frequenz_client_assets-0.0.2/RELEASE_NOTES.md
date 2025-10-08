# Frequenz Assets API Client Release Notes

## Summary

This release updates the `frequenz-api-assets` dependency to use a version range instead of a specific Git reference, providing more flexibility for dependency updates while maintaining compatibility.

## Changes

### Dependency Updates

* **Updated `frequenz-api-assets` dependency**:
  * Changed from Git reference (`@ git+https://github.com/frequenz-floss/frequenz-api-assets.git@v0.x.x`) to version range (`>= 0.1.0, < 0.2.0`)
  * Enables automatic updates within the specified version range
  * Maintains backward compatibility while reducing maintenance overhead

## Benefits

* **Improved dependency management**: Version ranges allow for automatic updates within the specified range
* **Better compatibility**: Ensures compatibility with the project while allowing for patch and minor version updates
* **Reduced maintenance overhead**: Eliminates the need to manually update Git references for compatible versions

## Migration Notes

No migration required. This is a transparent dependency update that maintains full backward compatibility.

## Files Changed

* `pyproject.toml`: Updated the `frequenz-api-assets` dependency specification

## Type of Change

* [x] Dependency update
