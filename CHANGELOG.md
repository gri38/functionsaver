# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0 - Unreleased]

### Added

* function_saver decorator to save in/out/internals of any function
    * with args, kwargs, and default args (when caller code doesn't provide them)
* serializers for numpy arrays
    * to binary .npy
    * to .png files.
* Robust to multi-threading and async code.
* Replay saves internal and output if they were saved.

### Changed

### Deprecated

### Removed

### Fixed

### Security
